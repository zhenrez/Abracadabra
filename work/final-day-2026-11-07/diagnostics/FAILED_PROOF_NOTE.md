# Preserved failed verification checkpoint

The b49bf6e64c27483d8043707cab34ace5 verification executed twelve checks. Ten passed; the native delivery correctly rejected changed live mathematical-state versions, and the integrity check rejected the resulting partial-output/older-receipt combination. The failed proof receipt and logs remain under proof-evidence/.

failed-proof-b49 preserves the resulting outputs and dashboard before another run. These are diagnostic historical artifacts, not a successful current delivery. The original and subsequently observed mathematical-state bytes are now independently preserved in audit/mathematical-source-versions/. Exact earlier versions were recovered from the existing archive; no source content was reconstructed.
