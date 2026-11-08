# Chinese native music: context, named standards, and performed sound

This bounded packet supplies two reusable constraints for SUNNY's symbol/sound inquiry. A received Chinese pitch-standard label does not determine one musical role across contexts. A pitch-class transformation does not determine its performed register. Neither result supplies an ancient frequency per written glyph or a Chinese–Hebrew/Aramaic/English phonetic correspondence.

Actual cloud Jev `jev-1.14.0` selected the role-context investigation: role 0.80, inscribed-bell investigation 0.17, historical phonology 0.03. The full request, preview and receipt are in the adjacent Chinese research directory. These are operational preferences, not proof. The local AgentJev endpoint independently returned connection refused; no service was started.

The first constraint comes from three prescriptions in [Zhou Li Zhu Shu, volume 22](https://zh.wikisource.org/w/index.php?title=周禮注疏_(四庫全書本)/卷22&oldid=544441). This is a modern transcription of the received text and its Han/Tang commentary in a Siku witness. It does not independently establish the date, original wording, performance, or claimed ritual effects.

| Context in the received prescription | 宮 | 角 | 徴 | 羽 |
|---|---|---|---|---|
| Heaven | 圜鍾 | 黄鍾 | 大蔟 | 姑洗 |
| Earth | 函鍾 | 大蔟 | 姑洗 | 南呂 |
| Ancestors | 黄鍾 | 大呂 | 大蔟 | 應鍾 |

The recorded relationship is **context + named standard + role**. Thus 黄鍾 receives 角 and 宮; 大蔟 receives 徴 and 角; 姑洗 receives 羽 and 徴. The source does not license a context-free, one-to-one assignment in either direction. This is a constraint on the selected textual assignments; physical identity in hertz is an additional question. The omitted 商 assignment remains omitted. No ordinary five-tone scale is filled into these prescriptions.

Five fresh span/relation checks passed. Proofline 2.0.2 verified the three exact normalized-text citations, package root `344bd8e01a02c7c3bf47850d4d9862289e1e10f61798462db47dcb2f5af13bc7`. Its verification establishes package and span integrity. Historical authenticity, interpretation, acoustics and empirical efficacy are outside that check.

The second constraint conditionally reuses [Nathan L. Lam's original 2024 article, §§2.1–2.7](https://mtosmt.org/issues/mto.24.30.1/mto.24.30.1.lam.html). Its model separates pentatonic context from scale position; C = huangzhong is a convention. In §2.5, a particular shawm transposition raises the resultant low D by an octave because the instrument's lowest note is E. This is a reported performance constraint, not a universal Chinese tuning rule.

Use a synthetic two-event control, E-low then F-sharp, with coordinates `[0, 2]` relative to the lower E. The down-two-semitone representative of `T10` gives `[-2, 0]`. Applying that source-qualified octave correction gives `[10, 0]`. The pitch classes agree, while the directed interval changes from `+2` to `-10` semitones. Wolfram independently evaluated the equality and both intervals. No source melody, ancient recording, absolute octave, or frequency calibration is invented.

The conditional lift is `p → p − 2 + 12k(p)`, where the correction is declared for the affected note. Its projection modulo 12 retains transposition and discards register choice. It cannot, by itself, predict melodic contour or exact acoustic realization.

The existing twelve-lü generation/seasonal-order distinction, seven/five upper/lower and six/six yin/yang partitions, five roles, eight materials, exact tuning residuals and algebraic extensions were recovered and retained. They are not new discoveries in this packet. Pitch standards, functional roles, register, timing, instrumentation, composition and realization remain separately accountable. Ritual change counts are not converted to beats or durations. Lexical speech tones are not substituted for these musical categories.

Both experiments deliberately withhold Completed Harmony, Fludd–Kepler/monochord and TOL AB/BA bridges. Their retained status is unchanged. The role experiment also withholds Lam's numerical pitch-class concordance: the received ritual role labels have not been shown to share that model's scale semantics. The register experiment uses only its declared modern context and instrument-range condition. The intended geometry remains a working premise; these results do not derive its acoustic realization.

The G16 baseline records all fourteen questions: five covered in this bounded scope, eight partial and one open. The scholarly baseline remains **OPEN**. Power/selection triage and M1–M12 have not been opened. Prior project geometry/esoteric bridges and the source outcomes were already exposed. These are source adaptations and exposed controls, with no novelty or blind-prediction claim.

At handoff, actual Jev selected critical comparison of the received ritual-role commentary before transfer into Lam's modern context model (0.76; audio reproduction 0.16, inscribed bells 0.08). This is the next investigative choice, not a historical verdict. A ready discriminating observation is an event-aligned comparison of the two source shawm versions: uniform register transposition predicts a low D at the affected event; the reported range correction predicts D one octave higher. This would reproduce an exposed source claim. Historical symbol/sound recovery additionally needs a witness-qualified notation or prescription connecting a linguistic token, musical operation, register, timing and realization. Neither shared counts nor the role table supplies that missing bridge.

Machine-readable evidence: `native-role-relation.json`, `register-transfer-control.json`, `p0a-baseline.json`, `experiment-manifests.json`, `source-and-exposure-map.json`, `plugin-use.json`, and the complete Jev, Wolfram, Proofline and Supermemory receipts under `state/research/reactivation/chinese/`. Supermemory checkpoint `iNBWwGqddKw2Y85VefRGec` was saved and read back with matching full content; document processing finished while memory extraction remained in progress. These files are a scoped research packet; all sixteen SUNNY goals and all eight mathematical outputs remain broader work in progress.

## Critical continuation: a surviving conditional bridge

The separate-mode interpretation supplies a positive candidate adapter. [Zhuzi Yulei 92, received revision 1540612](https://zh.wikisource.org/w/index.php?title=朱子語類/092&oldid=1540612) treats the ancestral prescriptions as four pieces and supplies different implicit gongs. It also tentatively distinguishes absence of a **Shang mode** from absence of the **Shang tone**. This is a later interpretation, distinct from Zheng/Jia's generation, exclusion and coarseness explanation. Both remain available.

This historical problem and the same possible tonic assignments already appear in Noa Hegesh's [“Old Music, New Times” (2025), pp. 163–164, notes 60–61](https://doi.org/10.1080/02549948.2025.2488659). The article retains uncertainty about the passage's musical system. The full article was retrieved from the [official Max Planck repository copy](https://pure.mpg.de/rest/items/item_3654306_1/component/file_3654325/content); pp. 163–164 were inspected for this question. This is prior-art reuse; the local calculation is not a new historical solution.

The conditional interpretation reads a listed standard as a piece's modal final, with a specified role within that piece's own scale context. In the declared modern pitch-class model, infer the implicit gong by `g = p − d(role) mod 12`. The four ancestral assignments become:

| Listed standard and modal role | Implicit gong from the later reading | Final address | Implicit gong address |
|---|---|---|---|
| 黃鍾 as 宮 | 黃鍾 | α | α |
| 大呂 as 角 | 南呂 | α + 1 | α + 9 |
| 太簇 as 徵 | 林鍾 | α + 2 | α + 7 |
| 應鍾 as 羽 | 太簇 | α + 11 | α + 2 |

Addresses are residues modulo 12; `α` is any common origin. The admitted role offsets are `0, 4, 7, 9`. All twelve origins satisfy the assignments. This retains named-standard identity and fixed offsets **within each modal context**. It removes the assumption that all four listed roles share the ritual row's first gong. It neither selects an absolute frequency nor establishes that the original prescription intended this interpretation.

For an explicitly conditional extension to all three rows, [Hu Yansheng's later *Yue lü biao wei*, 製調下](https://www.shidianguji.com/zh/book/SK0610/chapter/1l9w1sn66801f) states that each of the four terms denotes a separate mode. With the declared modern name concordance and scoped 圜鍾/夾鍾 and 函鍾/林鍾 identifications, the implicit-gong rows are heaven `α+[3,8,7,7]`, earth `α+[7,10,9,0]`, and ancestors `α+[0,9,7,2]`, modulo 12. All 144 row/origin combinations pass. This extends the modular candidate; it does not promote a complete exact acoustic lift or make these later commentators independent witnesses of original Zhou performance.

An optional ideal relative-frequency profile reproduces the same four assignments while retaining register. Seven literal pipe lengths were checked in the existing volume 23 witness, in its unit 寸. Under the explicitly assumed common inverse-length constant, the final ratios are `[1, 2187/2048, 9/8, 243/128]`; the inferred gong ratios are `[1, 27/16, 3/2, 9/8]`. With role ratios `[1, 81/64, 3/2, 27/16]`, the respective octave exponents are `[0, −1, −1, 0]`. Every row satisfies `final = gong × role-ratio × 2^exponent`. Multiplying all frequencies by any positive constant preserves the result. No conversion to hertz or modern metres is recovered, and real pipe corrections are not measured here.

The original one-context trial has an exact obstruction. Let `c` denote the heaven prescription's 圜鍾 gong, `h` the named 黄鍾, and `t` the named 大蔟. A context-invariant standard map with one fixed-offset scale per prescription would require:

```text
A: h − c − 4 = 0  (heaven: 黄鍾 as 角)
B: t − c − 7 = 0  (heaven: 大蔟 as 徴)
C: t − h − 7 = 0  (ancestors: 大蔟 as 徴)
```

But `B − C − A = 4 mod 12`. No assignment satisfies all three equations. Each two-equation subset has twelve solutions. Origin changes cancel; reversing the common coordinate orientation gives residue 8; integer octave changes cannot repair the residual. This excludes that joint adapter class. It does not reject the received text, either musical tradition, the intended geometry, or other context-sensitive bridges.

The commentary itself supplies a second safeguard: generation order is not use order. For earth, the accepted generated order 太蔟–南呂–姑洗 becomes role order 太蔟–姑洗–南呂. For ancestors, 太蔟–應鍾–大呂 becomes 大呂–太蔟–應鍾. Jia explicitly discusses earlier generation with later use and the reverse. Turning a generation address directly into a role, a composition sequence, or elapsed time would erase this source distinction.

The positive profile above needs none of the extra all-ritual tuning assumptions. If extending the modern modal model to every ritual row, a pure twelve-step generation profile can leave comma-sensitive tonic choices. That is an optional further test. The retrieved volume 23 transcription also prints denominator **727** in the 夷則 length, where the ideal generation-chain profile uses **729**; preserve that discrepancy rather than silently repairing it. It does not affect the four ancestral assignments checked here.

The contribution is a minimal executable incompatibility certificate plus an explicit, source-conditioned surviving family. The next discriminating evidence is a witness or performance structure identifying whether the listed terms denote separate pieces/modal finals or tones of one shared scale. Those readings make different claims about context and about a missing mode versus a missing tone. Historical dating, efficacy and linguistic intentions remain open. Completed Harmony, Fludd–Kepler/monochord and TOL AB/BA remain held aside for this comparison, with their retained project status unchanged.

Actual Jev selected the obstruction test (0.62) and conditional prior-art reuse (0.73). Actual Wolfram confirmed the obstruction, all twelve ancestral origin choices, four exact rational reconstructions, and the declared optional residual calculations. Fresh local verification passed nine groups, including the full modular extension; three new Proofline packages verify seven commentary spans, with integrity-only scope. Detailed evidence is in `conditional-adapter-obstruction.json`, `positive-modal-adapter.json`, `critical-pipe-profile.json`, `critical-verification.json` and the associated complete receipts. The P0-A14 delta is still scholarly and open; no M1–M12 stage or blind prediction is claimed.
