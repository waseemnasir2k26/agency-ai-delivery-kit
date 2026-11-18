#!/bin/sh
# Site Watch nightly (Linux / macOS server): same two steps as nightly.cmd.
# The fixture sites must already be served (python3 serve.py). Needs ANTHROPIC_API_KEY in the environment.
cd "$(dirname "$0")" || exit 1
python3 site_watch.py --run nightly --mode hardened --scenario clean --model sonnet --max-turns 40 --budget 1.00
python3 verify.py runs/nightly
