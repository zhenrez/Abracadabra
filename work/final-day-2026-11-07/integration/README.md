# Common native model contract

`CommonOrientation(native, default_profile_id=None)` adapts the actual Western and east-native implementations to Unit001's `EncodedModel`, `NativeValidation`, `CandidateSet`, `ReconstructionReceipt` and `DescriptionLength` contracts. It preserves each model's independent validation rules and never sends one orientation's output to another.

Use `encode(evidence=None, profile=None)`. The profile must match the profile already configured by the native model; invented memberships are rejected. Western requires an actual evidence mapping with a source reference. Its exact ratios, rhythm, voices, original canonical evidence and implementation/source bindings survive the wrapper. East-native models use their bound source profiles with `evidence=None`.

`validate_native(encoded)` rebuilds the entire common representation from the native input and rejects altered assignments, profile identity, evidence binding, unassigned records or unmatched values. `to_json` and `from_json` provide checked, deterministic common-record round trips. Reconstruction delegates to the same native model and retains its structural, model-preference, identifiability and historical axes.

Without a coding scheme, `describe` returns typed `NOT_EVALUATED`. Explicit `lossless-typed-v1` measures a reversible prefix code over every native assignment field and its sequence order. It also charges the actual native-program/profile bytes and this adapter's program bytes. The source evidence graph, common contracts and shared codec are explicitly given side information; their byte counts are disclosed separately. This conditional representation cost does not demonstrate an optimal generative model or historical compression advantage. `description_measurement(encoded)` returns the detailed method, measured costs and hashes; `describe(encoded, 'lossless-typed-v1')` returns the common result with the same total and details in its reason field.

```powershell
python -B -m unittest discover -s work/final-day-2026-11-07/integration -p test_common_models.py -v
```

Seven acceptance tests first failed because the wrapper was absent, then passed with exit0. They verify all four native adapters, exact Western source binding, profile rejection, complete-field tamper rejection, serialization, conditional-code round trips and unchanged historical uncertainty. `test-receipt.json` records the actual command and hashes; `common-tests.log` records test names and outcomes. The separate integration-review manifest records native examples, source roles and broader historical-profile limits.
