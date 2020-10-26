#!/usr/bin/env bash
set -uo pipefail

source "scripts/include.sh"

# to stop tests faling in CI (as there are none yet)
# @todo remove when tests written
exit 0

coverage run -m pytest
exitonfail $? "Unit tests"

coverage report --fail-under=80 --skip-covered --show-missing --skip-empty
exitonfail $? "Coverage check"

echo_success "Unit tests passed"
