# Invariant OMEGA Portable 0.2.0

A private, path-independent distribution of the preserved RARI OMEGA numerical kernels. This is a **replay interface**, not a new independent experiment, a recreation of the remote E2B/Kimi infrastructure, or biological validation.

## Install and run

The accompanying dependency bundle supports **Linux x86-64 / CPython 3.13** only. Its NumPy and SciPy wheels are locally reconstructed from the installed distributions; read `offline_wheels/LOCAL_REPACK_PROVENANCE.json`. They are not represented as downloaded vendor wheels. Do not rename their platform tags for another platform.

From the root of the combined CP06 delivery (with the separately delivered `offline_wheels` directory placed next to `github`):

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install --no-index --find-links offline_wheels github/invariant-omega-portable/dist/invariant_omega_portable-0.2.0-py3-none-any.whl
.venv/bin/python -m invariant_omega verify
mkdir runs
.venv/bin/python -m invariant_omega run --mode fixture --output runs/fixture
.venv/bin/python -m invariant_omega run --mode gop-controls --output runs/gop
.venv/bin/python -m invariant_omega run --mode synthetic --output runs/synthetic --timeout-seconds 1200
```

Every output leaf must be new. Existing directories, including empty directories, are rejected to protect historical outputs. The parent directory must exist. The last command intentionally exits **1** in the tested environment: computation completes, but the historical selected-representation label does not match. Inspect the JSON receipts rather than treating any nonzero exit as a missing output.

For Windows, macOS or another Python version, install the matching official NumPy 2.3.5 and SciPy 1.17.0 distributions through a trusted package source and then this pure-Python wheel. Those platforms were **not tested** in CP06.

## Three modes and their boundaries

|Mode|What actually runs|What it does not establish|
|---|---|---|
|`fixture`|A small affine numerical fixture and event guard checks|Full scientific reproduction|
|`gop-controls`|The seven preserved G1–G7 numerical control functions|Cloud preflight, the full foundation suite, a universal physics result|
|`synthetic`|Preserved development, validation, calibration and two confirmation-bank numerical pipeline, including refitting|Fresh independent confirmation or replay of the original distributed subject|

All 22 frozen manifest members and the original manifest file are byte-verified before invocation. The wrapper supplies relocated ROOT/PKG paths **before** importing the historical kernels; it does not modify their source bytes, criteria or seed settings. Historical deployment preflight is not invoked and is explicitly marked `NOT_EXECUTED_NOT_CLAIMED`.

## Observed reference mismatch—do not hide it

The source record selected `pca/11`. Two isolated CP06 refits selected `pca/20`. Across 2,283 numeric result leaves, the largest absolute difference from the historical summary was about 3.6832e-12; numeric tolerances were met and the ten card-status decisions did not change. The literal selected label still differs, so strict reference comparison remains `FAILED` and the run is `COMPLETED_REFERENCE_MISMATCH`. The two CP06 result files are byte-identical. This is within-environment repeatability, not byte-identical reproduction of the historical run. See `docs/NUMERICAL_REPLAY_BOUNDARY.md` and the verification directory.

## Tests

```sh
# Run from this repository after installation into the venv:
/path/to/.venv/bin/python -m unittest discover -s tests -v
# Frozen source tests are a distinct, smaller layer:
/path/to/.venv/bin/python -m unittest discover -s src/invariant_omega/_frozen/tests -v
```

29 wrapper tests and 14 preserved tests were run separately. Repeated executions of the same tests do not add independent tests or experiments. The seven-case GOP comparison passed numeric tolerances; its negative and unestablished case decisions remain unchanged.

## Safety and privacy

The numerical worker uses Python audit events to reject socket connections/binds, subprocess creation and process-execution events. This is **not an operating-system security sandbox** and cannot warrant arbitrary untrusted native-code execution. Do not run unreviewed replacement code or attacker-controlled dependencies. No public publication, license grant, external submission, clinical deployment, or provider service call is made by this package.

Original source wording is retained verbatim. In particular, historical result metadata describing a 'fresh' confirmation refers to the original protocol; the CP06 wrapper receipt always marks this invocation as replay and `new_independent_experiment=false`. New output files must not replace frozen source results.

Read `SOURCE_PROVENANCE.json`, `RIGHTS_AND_RELEASE.md`, and `docs/INPUT_CONTRACTS.md` before redistributing. Copyright and third-party notices are retained; project-level publication permission is still required.
## Verified packaging revision — 2026-10-20

Wheel built and installed; 28/29 checks passed. Isolated replay worker lacks pinned SciPy in its environment; no tolerance relaxation.

Runtime state: `PASS`. Rights and release approval are separate. See `RELEASE_VERIFICATION.json`. No paper or conference submission is included as a new software result.

## Runtime revision — 2026-10-21

29 original tests including installed-package isolation and fresh fixture.

Install into a dedicated environment before isolated tests: `python -m pip install .`. Then `python -m unittest discover -s tests -v`. The 29 interface tests passed; the preserved full synthetic PCA rank discrepancy is NOT repaired or hidden.

Evidence: `RELEASE_VERIFICATION.json`. Rights and hosted/server/Windows checks are separate.

## Software-only nested inputs
Historical manuscript files were excluded from nested input ZIPs. Scientific core members are byte-identical to their original hashes. `SOFTWARE_ONLY_INPUTS.json` records the old/new container hashes and exact exclusions; historical input manifests remain historical, not current distribution manifests. No paper or conference submission is released here.
