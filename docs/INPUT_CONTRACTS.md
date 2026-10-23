# Inputs, outputs and failure contract

The CLI accepts a **new local output path**, a mode and timeout in [1,7200] seconds. It consumes only the packaged frozen protocol/source/input tree. It is not an EEG, MRI, patient-data or natural-language input API. Altering frozen bytes fails integrity verification.

`verify` returns 0 for exact retained file hashes and 2 for invalid source/protocol. `run` returns 0 when the worker succeeds and applicable reference checks pass; 1 for a completed historical-reference mismatch or worker failure; 2 for invalid input or process-launch error; 124 for timeout. Receipts are JSON using finite numeric values; invalid caller arguments can fail before an output root is created. Existing output directories are never reused.

`RUN_RECEIPT.json` records wrapper scope, times, exit status, frozen integrity, and reference comparison. `WORKER_RECEIPT.json` records the numerical environment and Python-audit-event attempts. `REFERENCE_COMPARISON.json` lists exact categorical/structural discrepancies and floating-point comparisons (absolute tolerance 1e-10; relative tolerance 1e-8). Numeric closeness does not waive a categorical mismatch.

`compare ACTUAL EXPECTED` compares two complete JSON objects. Dictionary key sets, list lengths, integers, booleans and strings must match. Floating-point values must be finite and within the declared tolerance. It is an artifact comparison, not an inferential test, a hypothesis p-value or equivalence claim.

The worker's event guard is process-local and best-effort. It does not perform remote systemd checks, deployment budget attestations, cloud worker orchestration or third-party model calls. Historic seed commitments are not new preregistration. Original biologic arrays remain absent from this distribution.
