"""Grade a submission by running it against every test case for an exercise."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.exercise import Exercise, TestCase
from app.models.submission import Submission, SubmissionStatus, TestCaseResult
from app.services.code_runner import RunResult, code_runner


def _normalize(s: str) -> str:
    """Lenient comparison: ignore trailing whitespace per line and trailing newlines overall."""
    return "\n".join(line.rstrip() for line in (s or "").splitlines()).rstrip("\n")


def _classify(run: RunResult) -> SubmissionStatus:
    if run.error:
        return SubmissionStatus.internal_error
    if run.timed_out:
        return SubmissionStatus.time_limit_exceeded
    if run.out_of_memory:
        return SubmissionStatus.memory_limit_exceeded
    if run.exit_code != 0:
        return SubmissionStatus.runtime_error
    return SubmissionStatus.accepted


def grade_submission(db: Session, submission: Submission, exercise: Exercise) -> Submission:
    """Run the submission against all test cases and persist results.

    Mutates and returns the submission, but does NOT commit — the caller commits.
    """
    test_cases: list[TestCase] = list(exercise.test_cases)
    submission.total_tests = len(test_cases)
    submission.status = SubmissionStatus.running

    if not test_cases:
        submission.status = SubmissionStatus.internal_error
        submission.error_message = "Exercise has no test cases"
        return submission

    total_weight = sum(max(1, tc.weight) for tc in test_cases) or 1
    earned = 0
    passed = 0
    total_runtime = 0
    aggregate_stdout: list[str] = []
    aggregate_stderr: list[str] = []
    worst_status: SubmissionStatus = SubmissionStatus.accepted

    for tc in test_cases:
        run = code_runner.run(
            language=submission.language,
            code=submission.code,
            stdin=tc.stdin,
            time_limit_ms=exercise.time_limit_ms,
            memory_limit_mb=exercise.memory_limit_mb,
        )
        total_runtime += run.runtime_ms

        status = _classify(run)
        is_pass = status == SubmissionStatus.accepted and _normalize(run.stdout) == _normalize(tc.expected_stdout)
        if not is_pass and status == SubmissionStatus.accepted:
            status = SubmissionStatus.wrong_answer

        if is_pass:
            passed += 1
            earned += max(1, tc.weight)
        elif worst_status == SubmissionStatus.accepted:
            worst_status = status

        if not tc.is_hidden:
            aggregate_stdout.append(run.stdout)
            if run.stderr:
                aggregate_stderr.append(run.stderr)

        db.add(
            TestCaseResult(
                submission=submission,
                test_case=tc,
                passed=is_pass,
                actual_stdout=run.stdout if not tc.is_hidden else None,
                stderr=run.stderr if not tc.is_hidden else None,
                runtime_ms=run.runtime_ms,
                error=run.error,
                is_hidden=tc.is_hidden,
            )
        )

        # Fast-fail on internal errors so we don't burn time on a broken runner.
        if status == SubmissionStatus.internal_error:
            submission.error_message = run.error
            break

    submission.passed_tests = passed
    submission.runtime_ms = total_runtime
    submission.score = round((earned / total_weight) * exercise.points, 2)
    submission.status = SubmissionStatus.accepted if passed == len(test_cases) else worst_status
    submission.stdout = "\n---\n".join(aggregate_stdout) if aggregate_stdout else None
    submission.stderr = "\n---\n".join(aggregate_stderr) if aggregate_stderr else None
    return submission
