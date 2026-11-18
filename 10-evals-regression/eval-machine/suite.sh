#!/bin/bash
# Run any evals/*.py on the eval machine (WSL distro or Linux box) with the isolated config. Usage: bash suite.sh run_suite.py --runs 1 ...
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/env.sh"
cd "$HERE/.."
exec python3 "evals/$1" "${@:2}"
