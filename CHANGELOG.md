# Changelog

All notable changes to the Agency AI Delivery Kit. The kit follows the course: one module per episode.

## 1.0.0

First release, matching the finished course "Claude Code for Real Business".

- 10 episode modules plus the bonus CEO Control Room, each with a README (problem, contents, 5-step quickstart, limits, where it is shown).
- `PROMISES.md`: every item promised on screen, mapped to its file in the kit.
- `VERIFY.md`: what was run offline for this release and the result. Anything that needs a Claude login or an admin machine is marked, not guessed.
- Episode 8 native Windows policy run: still owed, marked pending in `08-team-policy/results/`.

## How releases work

- A change to a module bumps the version here and names the module.
- Before a release: rerun every offline check listed in `VERIFY.md`, plus the privacy scrub.
- After every Claude Code update: rerun `08-team-policy/policy_test.py` and the `10-evals-regression` suite before trusting old results.
