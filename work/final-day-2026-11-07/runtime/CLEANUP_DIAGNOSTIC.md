# Worker cleanup failure: bounded diagnostic handoff

The durable default npm acceptance receipt records99tests,98passed and1failed, exit1. The remaining failure is output overflow returning cleanup_error instead of output_limit. HTTP capacity recovery now passes, supporting the earlier timer-race correction within that tested case.

The overflowing fixture reached its marker, which requires successful ownership capture and input dispatch. The failure is therefore in stop/verification or subsequent handle closure. It differs from the earlier restricted-runtime AuthorizationManager denial at capture.

The15-second helper deadline and repeated Windows CIM queries make variable host load a plausible explanation. The22.19-second total case duration is consistent with that explanation, but the assertion output omits result.error. Identity mismatch and delayed handle closure remain unexcluded. Other test files have no direct ownership-helper calls; cross-file contention has not been established.

## Smallest next check

Use cleanup-diagnostic-plan.json for exact argument arrays. One command runs the original13-file/99-test population with --test-concurrency=1. The other substitutes worker-lifecycle-diagnostic.test.mjs for the original lifecycle file exactly once. Its only behavioral diagnostic change prints the synthetic result, fixture path and owned fixture PIDs before the overflow assertion. Imports and project-root references are relocated; identity checks and timeouts are unchanged.

The copy passed node --check, exit0. No lifecycle run, new escalation, original-file edit or process termination was performed by this audit. Serial success must remain a distinct configuration result and cannot erase the default failure. Capture result.error before proposing another implementation change or timeout increase.
