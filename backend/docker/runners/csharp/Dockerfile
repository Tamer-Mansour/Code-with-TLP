FROM mcr.microsoft.com/dotnet/sdk:8.0

# dotnet-script lets us run a single .csx file LeetCode-style, no project boilerplate.
RUN dotnet tool install -g dotnet-script \
    && useradd -ms /bin/bash runner \
    && mkdir -p /home/runner/.dotnet/tools \
    && cp -r /root/.dotnet/tools/. /home/runner/.dotnet/tools/ \
    && chown -R runner:runner /home/runner/.dotnet

ENV PATH="/home/runner/.dotnet/tools:${PATH}"
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1

WORKDIR /workspace
USER runner

CMD ["dotnet", "script", "/workspace/solution.csx"]
