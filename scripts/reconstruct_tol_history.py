"""Execute the recovered TOL scalar/history boundary without inventing A/B maps."""
from pathlib import Path
from fractions import Fraction
from collections import Counter, defaultdict
from itertools import product
from math import comb
from datetime import datetime, timezone
import hashlib, json, sqlite3

ROOT = Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def main():
    db = sqlite3.connect("file:" + (ROOT / "data/sunny.sqlite").as_posix() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    row = db.execute("select d.id document_id,d.text,s.* from documents d join sources s on s.id=d.source_id where s.id=?", ("6d0e6405bba76f693e8810327a39c0a663813316222c64fc4cc179a54f377fe9",)).fetchone()
    source = Path(row["path"]); raw = source.read_bytes()
    if sha(raw) != row["sha256"]: raise ValueError("TOL source digest mismatch")
    text = row["text"]
    spans = []
    for label, first, last in [("primitive_scalar_operations",198,252), ("history_and_observable_projection",258,323),
            ("prime_coordinates_and_evaluation",638,742), ("faithfulness_protected_distinctions",888,927),
            ("registered_partial_adapter",1238,1321), ("unfinished_domains_and_type_system",1455,1509)]:
        quote = "\n".join(text.splitlines()[first-1:last])
        start = text.index(quote)
        spans.append({"id": label, "document_id": row["document_id"], "source_id": row["id"],
            "source_path": str(source), "source_sha256": row["sha256"], "source_role": "historical_recovered_research_archive",
            "extracted_document_lines": [first,last], "document_char_start": start, "document_char_end": start+len(quote),
            "exact_quote": quote, "quote_sha256": sha(quote.encode()),
            "locator_boundary": "Lines and offsets address the stored extracted document; source file bytes are separately hash-verified."})
    factors = {"R":Fraction(2,3), "L":Fraction(3,4), "O":Fraction(1,2)}
    exact_cases = []
    for n in range(9):
        fibers = defaultdict(set)
        for letters in product("RLO", repeat=n):
            word = "".join(letters); counts=Counter(word); r,l,o = (counts[x] for x in "RLO")
            value = Fraction(1)
            for letter in word: value *= factors[letter]
            a,b = r-2*l-o, l-r
            predicted = Fraction(2)**a * Fraction(3)**b
            if value != predicted: raise AssertionError("Prime evaluation failed")
            effective_counts = (r+o,l+o)
            fibers[value].add(effective_counts)
            if (r+o,l+o) != (-a-2*b,-a-b): raise AssertionError("Count inversion failed")
        if any(len(v) != 1 for v in fibers.values()): raise AssertionError("Fiber count theorem failed")
        exact_cases.append({"word_length": n, "words_executed": 3**n, "distinct_scalar_outputs":len(fibers),
                            "all_evaluations_and_effective_count_inversions_match":True})
    binary_fibers = []
    for n in range(1,7):
        count = comb(2*n,n)
        if n<=5:
            enumerated=sum(1 for w in product("RL",repeat=2*n) if w.count("R")==n)
            if count != enumerated: raise AssertionError("Binary fiber count failed")
        binary_fibers.append({"R_count":n,"L_count":n,"common_ratio":str(Fraction(1,2)**n),
            "distinct_ordered_word_records":count,"minimum_additional_binary_labels_for_exact_path":(count-1).bit_length(),
            "condition":"The retained history records the full ordered R/L word; scalar observation alone is retained."})
    result = {"schema":"sunny.tol-history-mathematical-reconstruction.v1", "created_utc":datetime.now(timezone.utc).isoformat(),
        "selection_receipt":"docs/evidence/mandate-tol-unit-superjev.json", "solver_receipt":"docs/evidence/mandate-tol-wolfram.json",
        "unit_status":"bounded_conditional_derivation_executed; not a complete TOL type system or global orientation",
        "source_spans":spans,
        "recovered": {"scalar_operations":{"R":"C -> 2C/3","L":"C -> 3C/4","O":"C -> C/2"},
            "history_boundary":"Distinct ordered histories may have the same scalar evaluation. The source explicitly preserves RL versus LR internally.",
            "adapter":"A_v:X_v ⇀ X_SUN; A_v∘T_v = T_SUN∘A_v where established; TOL does not generate the SUN native law."},
        "derivation": {"domain":"Finite ordered words in the recovered R,L,O scalar factors, with positive reference C. The statement concerns evaluation and separately retained histories, not a new physical sound-generation model.",
            "evaluation":"q(w)/C = (2/3)^r (3/4)^l (1/2)^o = 2^(r-2l-o) 3^(l-r)",
            "effective_counts":"N_R=r+o; N_L=l+o. If q(w)/C=2^a3^b, then N_R=-a-2b and N_L=-a-b.",
            "proof":"Substitute a=r-2l-o and b=l-r. Then -a-2b=r+o and -a-b=l+o. Unique prime factorization makes (a,b) unique for a positive rational in the 3-limit group. Therefore two words have equal scalar evaluation exactly when their effective count pairs coincide.",
            "normal_form_boundary":"R^N_R L^N_L represents the same scalar evaluation, not the same protected history. Replacing O by RL and commuting R/L is permissible only after evaluation.",
            "consequence":"Scalar output cannot recover RL versus LR, or any exact ordered path in a fiber with multiple protected histories. A bridge claiming to preserve history must carry independent path information or a richer observable.",
            "no_scalar_history_left_inverse":"If protected histories u=RL and v=LR are distinct but q(u)=q(v), no function s from scalar outputs back to histories can satisfy s∘q=id on a domain containing both: s(q(u))=s(q(v)) would force u=v. This follows from the recovered two-path example without assuming that every longer word is distinct.",
            "path_information_example":"With six R and six L operations, 924 ordered word records share ratio 1/64. Distinguishing all requires at least 10 binary labels (ceil(log2(924))); this is an encoding lower bound under the stated full-word-history condition, not a source-supplied ontology or frequency measurement precision claim.",
            "novelty_boundary":"The quotient/history distinction is recovered prior work. The explicit inverse-count formula and quantified fiber-information consequence were derived and executed in this unit. No corpus-wide novelty or blind prediction is certified."},
        "execution":{"exact_word_cases":exact_cases,"total_words_executed":sum(x['words_executed'] for x in exact_cases),
            "binary_fiber_counts":binary_fibers,"arithmetic":"Python fractions.Fraction; independent Wolfram symbolic/count calculations retained"},
        "partial_adapter_obligations":[
            {"condition":"For x in the declared comparison domain, A_v(x) and A_v(T_v(x)) must both be defined; state T_v(x) domain membership explicitly.","reason":"An undefined partial-map composition is not a failed equality or permission to invent an output."},
            {"condition":"For n-step forward deductions, every required native iterate must remain in the adapter domain, or the deduction stops at the first undefined iterate.","reason":"A one-step diagram does not itself supply total domain invariance."},
            {"condition":"Backward deduction needs native/target predecessor or invertibility conditions, plus the relevant image/domain bounds.","reason":"Forward semiconjugacy alone does not determine a unique past or recover protected histories lost by q."}],
        "unretrieved_literal_AB_BA": {"status":"Operational A/B definitions and domains not retrieved in the inspected TOL archive or cited Sept11 source transcript.",
            "positive_evidence":"Oct30 user message c6ed8ef0a10eb9e6df30f5f78876a0c1271a0c4a53cae792fb30057da7c2712a, source 7c5cd4c51ad9da8020d497ab449770e5dd38b3d334bf8ad612e1c9f8e747f125, lines1019-1041 mentions TOL AB/BA and possible bridges as an investigation.",
            "search_boundary":"This is bounded source retrieval, not an account-wide nonexistence claim. Named A/B is not silently identified with R/L or with arbitrary matrices."},
        "source_fidelity_checks":{"source_hash_matches":True,"exact_quote_spans":len(spans)},
        "continuation":"Recover the literal A/B native operators, types, domains and protected distinctions; test an explicit registered adapter against these obligations. Continue other native musical reconstruction in parallel.",
        "database_mutation":False}
    write(ROOT/"state/reconstruction/tol-history-math.json", result)
    (ROOT/"docs/reconstruction/TOL_HISTORY_MATH.md").write_text("""# TOL history and musical evaluation

The recovered TOL algebra preserves ordered histories even when their scalar musical outputs agree. This unit executes that boundary and derives an exact restriction on any proposed bridge.

For an ordered word containing r copies of R=2/3, l copies of L=3/4 and o copies of O=1/2, its evaluated ratio is

`2^(r−2l−o) 3^(l−r)`.

If the result is `2^a3^b`, it determines the effective counts `r+o=−a−2b` and `l+o=−a−b`. It does not determine order. Thus RL and LR both evaluate to 1/2 while their retained construction records differ. A scalar normal form preserves the observed value; it cannot replace the original history.

This becomes substantial at greater depth: six R and six L steps have 924 ordered word records with the same ratio, 1/64. If all those histories are protected, a bridge needs at least 10 extra binary labels to distinguish the paths. This is a conditional information bound derived here, not a newly imposed cosmological class.

The execution checked all 9,841 words of lengths zero through eight over R/L/O using exact rational arithmetic. Every prime-coordinate evaluation and inverse-count result agreed. Independent Wolfram results confirm the inverse formulas and binomial fiber counts.

The source's registered adapter is partial: A_v:X_v⇀X_SUN, with A_v∘T_v=T_SUN∘A_v where established. Forward repetition requires the intervening native states to remain in its domain. A unique backward deduction additionally needs predecessor/invertibility conditions. Neither a scalar equality nor a one-step diagram recovers a lost history.

The literal native A/B operators referred to as TOL AB/BA have not been retrieved in the inspected TOL archive and its cited September 11 transcript. The user's later reference remains an open source-linked investigation. This unit does not substitute R/L labels or invented matrices for that missing definition.

Source: TOL_COMPLETE_WORK_ARCHIVE_2026-09-29 (1).md, SHA-256 1e471374598497383adaf7d6ab21af2dfb2a6999a0a41ae1f253072ddaf4f065, sections 5–6, 13–14, 17, 22 and 26. The JSON companion preserves exact source spans, dependencies, execution results, actual Jev selection and independent Wolfram receipts.

This is one executed mathematical reconstruction unit. Mission I, the full type system and the global orientation remain incomplete.
""",encoding="utf-8")
    db.close()
    print(json.dumps({"source_hash":row['sha256'],"source_spans":len(spans),"exact_words_executed":result['execution']['total_words_executed'],"binary_depth6_paths":binary_fibers[-1]}))
if __name__=="__main__": main()
