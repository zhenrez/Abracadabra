# Chinese and Indian native delivery

This unit reuses the earlier Chinese and Indian definitions and adds common-contract adapters. It does not replace or modify the frozen SUN kernel, Unit001, Unit002 or the original four-orientations files. The checked legacy file has SHA-256 `e9085c55d560ce92a5c7afd1e9ac20a7efcbdff0506ca4cf10de4245289da217`.

`east_models.py` exposes `ChineseModel`, `GramaModel` and `MelakartaModel`. Each supports `validate_native`, `encode`, `reconstruct` and `describe` using Unit001's actual immutable result contracts. Source profiles and their source records are immutable. Encodings bind both the native profile and its declared evidence sources. Canonical typed serialization rejects a Boolean substituted for a numerical position. Description length remains a typed unavailable result until an actual coding scheme is supplied; no fictional model costs are returned.

## G3 — Chinese model

The [Lüshi Chunqiu 音律 transcript](https://www.shidianguji.com/zh/book/HY1433/chapter/1l3wfypdn3d4v) supplies the twelve-name generation order and addition/removal of one third. This is a modern transcription of an early text with editorial lineage, not an ancient manuscript image. The failed Ctext acquisition is preserved in the extraction record.

The selected mathematical length profile uses D=2/3 and U=4/3. Frequency is inverse length: D raises pitch by 3/2, while U lowers pitch by 3/4. The octave-window rule and register convention are explicit derived choices. From reference length1, the first five lengths are1,2/3,8/9,16/27,64/81. The sequence includes repeated U at the Rui Bin transition; blind D/U alternation is not used. Exact unwrapped fifth values and the chosen register are retained alongside the finite twelve-label projection.

At the thirteenth generated label the address returns to0, but frequency is531441/524288 relative to the reference. This exact nonclosure is preserved. The twelve reference labels and five functional-role reassignments form60 formal contexts. A changed role assignment can leave pitches fixed; a changed reference changes pitch labels. These are modeled contexts rather than sixty independently attested instruments. No frequency is inferred merely from a functional label.

```python
from east_models import ChineseModel

model = ChineseModel()
encoded = model.encode(None)
validation = model.validate_native(encoded)
ambiguous = model.reconstruct({0: None}, {"reference_lengths": ("1", "2")})
unique_under_profile = model.reconstruct({1: "2/3"}, {"reference_lengths": ("1", "2")})
```

The finite reference candidates are declared inputs. Both ambiguous alternatives survive. A unique mathematical reference under this profile is reported separately from historical support.

## G4 — Two separate Indian submodels

The [Ghosh translation of Nāṭyaśāstra28](https://vishvasa.github.io/kAvyam/laxaNam/kalAvisheShaH/nATyam/nATya-shAstram/manamohanAnuvAdaH/28/) supplies the grāma allocations and named mūrchanās at28.24–32. This is a digital transcription of a translation. Earliest surviving manuscript priority is not certified by access to the mirror.

`GramaModel` preserves these allocations in Sa,Ri,Ga,Ma,Pa,Dha,Ni order:

| Profile | Allocation | Total |
|---|---|---:|
| Ṣaḍja |4,3,2,4,4,3,2|22|
| Madhyama |4,3,2,4,3,4,2|22|

An allocation belongs to the interval ending at the named note. Consequently an ascending interval sequence begins with the allocation of the succeeding note. Fourteen named mūrchanās retain their source-specific starting notes and cyclic order. The construction groups22 counted units into seven intervals. It does not make seven notes surject onto22 units or invent22 frequency ratios. Missing intonation remains `None`.

`MelakartaModel` independently reuses the conventional ordered parent-scale grammar. The [official Kerala textbook](https://samagra.kite.kerala.gov.in/files/samagra-resource/uploads/tbookscmq/Class_XI/Music/Music.pdf) distinguishes later sampūrṇa and earlier asampūrṇa traditions; the [CBSE marking scheme](https://cbseacademic.nic.in/web_material/SQP/ClassX_2020_21/CarnaticMusicVocal-MS.pdf) documents72 ordered complete scales in two Madhyama groups. These are direct institutional witnesses to the modern teaching convention, not original seventeenth-century manuscript attestations.

Six ordered Ri–Ga choices, two Ma choices and six ordered Dha–Ni choices produce72 distinct configurations. The legacy iterator is reordered into the explicit modern Ma-first numbering. This makes scales29 and65 differ only at Ma. The Madhyama involution produces36 disjoint pairs and changes no other slot. Integers label svarasthānas; they impose no equal-tempered frequency tuning. The grāma unit allocations never choose mela parameters.

```python
from east_models import GramaModel, MelakartaModel

grama = GramaModel()
grama_candidates = grama.reconstruct({"start_note": "Sa"})
melakarta = MelakartaModel()
two_madhyamas = melakarta.reconstruct((0, 2, 4, None, 7, 9, 11))
```

## Execution evidence

```powershell
python -B work/final-day-2026-11-07/native-east/verify_native_east.py
```

The runner records the actual command, test totals, Python/platform, input hashes before and after, outputs and scope. `native-verification.json` is the receipt; `native-tests.log` is the complete suite output; `native-results.json` contains the computed states. Three encoded models and `native-reconstruction-receipts.json` preserve actual result contracts.

The initial17 acceptance tests failed because the adapters were absent. Additional tests reproduced mutable-profile state and Boolean-as-integer validation defects before correction. The final suite contains19 tests. These check native computations, source-profile bindings, tamper rejection, candidate ambiguity, exact arithmetic, independent finite enumeration, determinism and absent-input behavior. They do not certify historical reconstruction or exhaustive musical practice.

Legacy reuse extracts only the pinned `positive`, `Chinese` and `Indian` definitions using Python AST. The legacy module's top-level Sefer import is not executed. No model consumes another orientation's output, and no cross-orientation registry is populated or unlocked.

Research Evidence Finder's source-verification guidance, Superpowers test-driven development and Mathbox computation-audit guidance were read and applied. Actual native web retrieval and local Python checks ran. No new scholarly-model backend, manual Jev inference or remote guardrail runtime is claimed by this worker. Root's live strategy receipt remains separate from native execution evidence.
