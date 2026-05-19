"""Run untrusted user code inside throwaway Docker containers.

Files are injected via put_archive (no volume mounts) so this works correctly
when the backend itself runs inside Docker with the host socket mounted.
"""

from __future__ import annotations

import io
import tarfile
import time
import uuid
from dataclasses import dataclass
from typing import ClassVar

from app.core.config import settings


@dataclass
class RunResult:
    exit_code: int
    stdout: str
    stderr: str
    runtime_ms: int
    timed_out: bool
    out_of_memory: bool
    error: str | None = None  # set when execution itself failed (no Docker, image missing, etc.)


class CodeRunnerError(RuntimeError):
    pass


class CodeRunner:
    """Docker-backed code runner using put_archive instead of volume mounts."""

    # Extra seconds added to the container timeout for languages with slow startup.
    LANG_STARTUP_OVERHEAD_SEC: ClassVar[dict[str, int]] = {
        "csharp": 15,  # dotnet script JIT + warmup
        "java": 3,     # JVM startup
    }

    # Extra env vars injected per language (suppress noise, fix first-run issues).
    LANG_ENV: ClassVar[dict[str, dict[str, str]]] = {
        "csharp": {
            "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
            "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
            "DOTNET_NOLOGO": "1",
        },
    }

    LANG_SPEC: ClassVar[dict[str, dict]] = {
        "python": {
            "image_key": "runner_image_python",
            "filename": "solution.py",
            "cmd": "python -u /workspace/solution.py < /workspace/input.txt",
        },
        "javascript": {
            "image_key": "runner_image_node",
            "filename": "solution.js",
            "cmd": "node /workspace/solution.js < /workspace/input.txt",
        },
        "typescript": {
            "image_key": "runner_image_node",
            "filename": "solution.ts",
            "cmd": "tsx /workspace/solution.ts < /workspace/input.txt",
        },
        "java": {
            "image_key": "runner_image_java",
            "filename": "Main.java",
            "cmd": "cd /workspace && javac Main.java && java -cp /workspace Main < /workspace/input.txt",
        },
        "csharp": {
            "image_key": "runner_image_csharp",
            "filename": "solution.csx",
            "cmd": "dotnet script /workspace/solution.csx < /workspace/input.txt",
        },
    }

    def __init__(self) -> None:
        self._client = None
        self._docker_import_error: Exception | None = None
        if settings.docker_enabled:
            try:
                import docker  # type: ignore

                self._client = docker.from_env()
            except Exception as exc:  # pragma: no cover - depends on host
                self._docker_import_error = exc

    @property
    def available(self) -> bool:
        return self._client is not None

    def supported_languages(self) -> list[str]:
        return list(self.LANG_SPEC.keys())

    def run(
        self,
        language: str,
        code: str,
        stdin: str = "",
        time_limit_ms: int | None = None,
        memory_limit_mb: int | None = None,
    ) -> RunResult:
        if language not in self.LANG_SPEC:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="",
                runtime_ms=0,
                timed_out=False,
                out_of_memory=False,
                error=f"Unsupported language: {language}",
            )

        if not self.available:
            reason = "Docker is disabled" if not settings.docker_enabled else f"Docker unavailable: {self._docker_import_error}"
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="",
                runtime_ms=0,
                timed_out=False,
                out_of_memory=False,
                error=reason,
            )

        spec = self.LANG_SPEC[language]
        image = getattr(settings, spec["image_key"])
        base_sec = max(1, int((time_limit_ms or settings.runner_default_timeout_sec * 1000) / 1000) + 1)
        timeout_sec = base_sec + self.LANG_STARTUP_OVERHEAD_SEC.get(language, 0)
        memory_mb = memory_limit_mb or settings.runner_default_memory_mb

        return self._run_container(
            image=image,
            command=spec["cmd"],
            filename=spec["filename"],
            code=code,
            stdin=stdin or "",
            timeout_sec=timeout_sec,
            memory_mb=memory_mb,
            extra_env=self.LANG_ENV.get(language, {}),
        )

    # --- internals ---

    def _build_archive(self, filename: str, code: str, stdin: str) -> bytes:
        """Pack solution file + input.txt into a tar archive for put_archive."""
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tar:
            for name, content in ((filename, code), ("input.txt", stdin)):
                data = content.encode("utf-8")
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(data))
        return buf.getvalue()

    def _run_container(
        self,
        image: str,
        command: str,
        filename: str,
        code: str,
        stdin: str,
        timeout_sec: int,
        memory_mb: int,
        extra_env: dict[str, str] | None = None,
    ) -> RunResult:
        import docker  # type: ignore
        from docker.errors import ImageNotFound  # type: ignore

        client = self._client
        assert client is not None

        name = f"runner-{uuid.uuid4().hex[:12]}"
        try:
            container = client.containers.create(
                image=image,
                command=["sh", "-c", command],
                name=name,
                working_dir="/workspace",
                network_mode="none",
                mem_limit=f"{memory_mb}m",
                memswap_limit=f"{memory_mb}m",
                cpu_period=100000,
                cpu_quota=int(settings.runner_default_cpu * 100000),
                pids_limit=128,
                security_opt=["no-new-privileges"],
                environment=extra_env or {},
            )
        except ImageNotFound:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="",
                runtime_ms=0,
                timed_out=False,
                out_of_memory=False,
                error=f"Runner image not found: {image}. Build it from docker/runners/.",
            )
        except Exception as exc:
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="",
                runtime_ms=0,
                timed_out=False,
                out_of_memory=False,
                error=f"Docker create failed: {exc}",
            )

        # Inject files directly — no volume mounts needed.
        try:
            archive = self._build_archive(filename, code, stdin)
            container.put_archive("/workspace", archive)
        except Exception as exc:
            try:
                container.remove(force=True)
            except Exception:
                pass
            return RunResult(
                exit_code=1,
                stdout="",
                stderr="",
                runtime_ms=0,
                timed_out=False,
                out_of_memory=False,
                error=f"Failed to inject files into container: {exc}",
            )

        start = time.perf_counter()
        timed_out = False
        out_of_memory = False
        try:
            try:
                container.start()
            except Exception as exc:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
                return RunResult(
                    exit_code=1, stdout="", stderr="",
                    runtime_ms=0, timed_out=False, out_of_memory=False,
                    error=f"Container start failed: {exc}",
                )

            try:
                result = container.wait(timeout=timeout_sec)
                exit_code = int(result.get("StatusCode", 1))
            except Exception:
                timed_out = True
                exit_code = 124
                try:
                    container.kill()
                except Exception:
                    pass

            runtime_ms = int((time.perf_counter() - start) * 1000)

            try:
                stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
                stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
            except Exception:
                stdout = ""
                stderr = ""

            try:
                state = client.api.inspect_container(container.id).get("State", {})
                out_of_memory = bool(state.get("OOMKilled"))
            except Exception:
                pass

            return RunResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                runtime_ms=runtime_ms,
                timed_out=timed_out,
                out_of_memory=out_of_memory,
            )
        finally:
            try:
                container.remove(force=True)
            except Exception:
                pass


code_runner = CodeRunner()
