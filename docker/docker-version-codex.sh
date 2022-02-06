#!/bin/bash
# Get the final runnable codex image version
set -euo pipefail
source .env.build
VERSION=${PKG_VERSION}
if [ "${CIRCLECI:-}" ]; then
    ARCH=$(./docker/docker-arch.sh)
    VERSION=${VERSION}-${ARCH}
fi
echo "$VERSION"