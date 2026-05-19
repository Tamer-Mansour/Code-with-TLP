#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "Building python runner..."
docker build -t studying-runner-python:latest "$HERE/python"

echo "Building node runner..."
docker build -t studying-runner-node:latest "$HERE/node"

echo "Building java runner..."
docker build -t studying-runner-java:latest "$HERE/java"

echo "Building csharp runner..."
docker build -t studying-runner-csharp:latest "$HERE/csharp"

echo "All runner images built."
