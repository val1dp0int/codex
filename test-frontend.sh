#!/bin/bash
# Run all frontend tests
set -euxo pipefail

cd "$(dirname "$0")"/frontend

npm run test:unit
