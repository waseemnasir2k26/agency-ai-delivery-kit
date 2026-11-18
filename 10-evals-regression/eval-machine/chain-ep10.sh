#!/bin/bash
# The Episode 10 capture chain after the candidate trials (run as the WSL user, eval policy already ON).
# CONTROLLED CHANGE chosen: client-report stage (cases 01-03, 09) Haiku -> Sonnet, everything else pinned.
E="$(cd "$(dirname "$0")/.." && pwd)"; S="$E/eval-machine/suite.sh"; C="$E/results/rerun"; mkdir -p "$C/S3" "$C/S4" "$C/S5"
STAGE="--case-model 01-report-mehr=claude-sonnet-5-5 --case-model 02-report-sufi=claude-sonnet-5-5 --case-model 03-report-noor=claude-sonnet-5-5 --case-model 09-plain-sentence=claude-sonnet-5-5"
LIM="--max-suite-usd 1.00 --timeout-min 45"
bash $S run_suite.py --runs 1 $LIM $STAGE --out evals/runs/lazy-after.json --label lazy-after > $C/S3/lazy-after.console.txt 2>&1
cp $E/evals/cases/judge-test/case.sole.json $E/evals/cases/judge-test/case.json
bash $S run_suite.py --case judge-test --runs 5 --max-suite-usd 0.25 --timeout-min 10 --out evals/runs/judge-sole.json --label judge-sole > $C/S4/judge.console.txt 2>&1
cp $E/evals/cases/judge-test/case.flag-only.json $E/evals/cases/judge-test/case.json
bash $S run_suite.py --case judge-test --runs 5 --max-suite-usd 0.25 --timeout-min 10 --out evals/runs/judge-fixed.json --label judge-fixed > $C/S4/judge-fixed.console.txt 2>&1
bash $S run_suite.py --runs 5 $LIM --out evals/baseline.json --label baseline > $C/S5/baseline.console.txt 2>&1
bash $S run_suite.py --runs 5 --max-suite-usd 1.50 --timeout-min 45 $STAGE --out evals/runs/after-change.json --label after-change > $C/S5/after-change.console.txt 2>&1
bash $S run_suite.py --case 01 --runs 1 --max-suite-usd 0.10 --timeout-min 5 --out evals/runs/shadow-old.json --label shadow-old > $C/S5/shadow-old.console.txt 2>&1
bash $S run_suite.py --case 01 --runs 1 --max-suite-usd 0.10 --timeout-min 5 --case-model 01-report-mehr=claude-sonnet-5-5 --out evals/runs/shadow-new.json --label shadow-new > $C/S5/shadow-new.console.txt 2>&1
sed -i '/systemd user session/d' $C/S3/lazy-after.console.txt $C/S4/judge*.console.txt $C/S5/*.console.txt
echo CHAIN-DONE
