FROM mcr.microsoft.com/dotnet/sdk:8.0

# dotnet-script lets us run a single .csx file LeetCode-style, no project boilerplate.
RUN dotnet tool install -g dotnet-script \
    && useradd -ms /bin/bash runner \
    && mkdir -p /home/runner/.dotnet/tools \
    && cp -r /root/.dotnet/tools/. /home/runner/.dotnet/tools/ \
    && chown -R runner:runner /home/runner/.dotnet

ENV PATH="/home/runner/.dotnet/tools:${PATH}"
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1 \
    DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1

# Pre-warm: run a no-op script so first submission doesn't pay JIT startup cost.
RUN echo 'Console.WriteLine("ok");' > /tmp/warmup.csx \
    && dotnet script /tmp/warmup.csx \
    && rm /tmp/warmup.csx

WORKDIR /workspace
RUN chmod 777 /workspace
USER runner

CMD ["dotnet", "script", "/workspace/solution.csx"]
