#!/bin/bash
# Combine arch specific images into a multiarch image
set -euo pipefail
REPO=docker.io/ajslater/codex
ARCH_REPO=docker.io/ajslater/codex-arch
ARCHES=(x86_64 aarch64) # aarch32)

pip3 install --upgrade pip
pip3 install --requirement builder-requirements.txt
PKG_VERSION=$(./version.sh)
VERSION_TAG=$REPO:$PKG_VERSION
echo "Creating $VERSION_TAG"
AMEND_TAGS=()
for arch in "${ARCHES[@]}"; do
    AMEND_TAGS+=("--amend $ARCH_REPO:${PKG_VERSION}-${arch}")
done

# shellcheck disable=2068
docker manifest create \
    "${VERSION_TAG}" \
    ${AMEND_TAGS[@]}

docker manifest push "$VERSION_TAG"

if [[ $PKG_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]$ ]]; then
    # If the version is just numbers push it as latest
    LATEST_TAG="$REPO:latest"
    echo "Creating $LATEST_TAG."
    # shellcheck disable=2068
    docker manifest create \
        $LATEST_TAG \
        ${AMEND_TAGS[@]}

    docker manifest push $LATEST_TAG
fi
