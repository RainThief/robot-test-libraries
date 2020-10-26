#!/usr/bin/env bash
set -eu

# we do not need shellcheck to follow source
# shellcheck disable=SC1091
source "./scripts/include.sh"

echo_info "\nRunning Static Analysis"
./scripts/static_analysis.sh

echo_info "\nRunning Unit Tests"
./scripts/unit_test.sh

echo_info "\nRunning Audit"
./scripts/audit.sh

echo_success "All checks/tests successful"
