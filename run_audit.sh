#!/usr/bin/env bash
set -euo pipefail

# Assume this script is in the src directory and work from that location
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"

# we do not need shellcheck to follow source
# shellcheck disable=SC1090
source "$PROJECT_ROOT/scripts/include.sh"

exec_in_container ./scripts/audit.sh "$@"
