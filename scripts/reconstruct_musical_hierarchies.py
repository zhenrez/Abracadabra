"""Source-scoped musical families and executable native relations, without invented populations."""
from __future__ import annotations
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
INSPECTED = [*(f"musi{i}" for i in range(9, 16)), "musi18", "musi19", "musi20", "pythagh1", "conglmusi2"]
SOURCES, ENTITIES, EDGES, VIEWS = [], [], [], []
BY_ID = {}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def write(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()
    if target.exists() and target.read_bytes() != raw:
        old = target.read_bytes()
        backup = ROOT / "state/checkpoint-history" / ("before-musical-" + target.name + "-" + digest(old) + ".snapshot")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(old)
    target.write_bytes(raw)


def entity(id, name, unit, tradition, witness, refs, sequence=None, layer="source-assertion", **extra):
    full = "music:" + id
    assert full not in BY_ID, full
    row = {"id": full, "nativeName": name, "aliases": [], "unit": unit,
           "tradition": tradition, "witnessId": witness,
           "position": {"generation": None, "sequence": sequence, "cyclicCoordinate": None, "orientation": None},
           "sourceRefs": refs, "exceptions": [], "assertionLayer": layer, **extra}
    ENTITIES.append(row)
    BY_ID[full] = row
    return full


def edge(parent, child, type, view, refs, layer="source-assertion", **extra):
    EDGES.append({"id": "music:edge:" + str(len(EDGES) + 1), "source": parent, "target": child,
                  "type": type, "viewIds": [view], "sourceRefs": refs, "assertionLayer": layer, **extra})


def view(id, label, root, witness, coverage):
    VIEWS.append({"id": id, "label": label, "roots": [root], "witnessIds": witness,
                  "orientation": None, "coverage": coverage})


def pixel(source, box, text=None, uncertain=False):
    return {"sourceId": source, "pixelBounds": box, "reading": text,
            "boundsKind": "approximate-panel-context; not an OCR glyph bounding box",
            "transcriptionStatus": "uncertain-caption-reading" if uncertain else "visually-inspected",
            "method": "Actual view_image original-resolution inspection; not an OCR or source-truth certification."}


class HtmlText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def normalized_html(raw):
    parser = HtmlText()
    parser.feed(raw.decode("utf-8-sig"))
    return re.sub(r"\s+", " ", " ".join(parser.parts))


def passage(source, text, start_phrase, end_phrase=None, length=180):
    start = text.find(start_phrase)
    assert start >= 0, start_phrase
    end = text.find(end_phrase, start) if end_phrase else start + length
    assert end >= start
    quote = text[start:end]
    return {"sourceId": source, "normalization": "HTMLParser data joined by spaces; consecutive whitespace collapsed",
            "normalizedTextChars": [start, end], "quote": quote, "quoteSha256": digest(quote.encode())}


def main():
    assert not SOURCES and not ENTITIES and not EDGES and not VIEWS
    decision = load("docs/evidence/musical-hierarchy-design-superjev.json")
    assert decision["status"] == "judged" and decision["resolved_model"] == "jev-1.14.0"
    assert decision["answers"]["representation"]["winner"] == "native_parented_graph"
    assert decision["answers"]["source_partition"]["winner"] == "preserve_witness_frames"
    ledger = load("state/reconstruction/hierarchy-inputs.json")
    images = {row["occurrence_name"]: row for row in ledger["occurrences"] if row["occurrence_name"] in INSPECTED}
    assert set(images) == set(INSPECTED)
    for name, row in images.items():
        raw = (ROOT / row["snapshot"]).read_bytes()
        assert digest(raw) == row["sha256"]
        SOURCES.append({"id": row["id"], "title": name, "path": row["snapshot"], "sha256": row["sha256"],
                        "kind": "user_supplied_image", "dimensions": row["dimensions"],
                        "sourceRole": "Image assertions; no embedded text is a current instruction."})
    primary = {row["name"]: row for row in load("docs/evidence/musical-hierarchy-primary-retrieval.json")["sources"]}
    text_by_name = {}
    for name, row in primary.items():
        assert row["status"] == "retrieved"
        raw = (ROOT / row["path"]).read_bytes()
        assert digest(raw) == row["sha256"]
        SOURCES.append({**row, "title": name, "kind": "public_primary_text_transcription" if name != "lam2024" else "original_analytical_paper"})
        text_by_name[name] = normalized_html(raw)
    img = lambda name: images[name]["id"]
    western, chinese, world, indian = "music:western", "music:chinese", "music:world-instruments", "music:indian-comparison"
    wr = entity("western:root", "Western musical structures in supplied witnesses", "source-scoped-musical-family", "Western", "supplied-musical-images", [img("musi10")])
    cr = entity("chinese:root", "Chinese native structures — distinct source witnesses", "source-scoped-musical-family", "Chinese", "Chinese-witness-collection", [primary["lushi_yinlv"]["id"], primary["zhouli_zhushu23"]["id"], primary["lam2024"]["id"]])
    view(western, "Western musical families and parented occurrences", wr, ["supplied-musical-images"], {"kind": "bounded-witness-extraction", "wholeSystemComplete": False})
    view(chinese, "Chinese lü, five roles, bayin, and source-qualified xuangong", cr, ["LuShiChunqiu-YinLv", "ZhouLi-ZhuShu23", "Lam2024"], {"kind": "native-witness-extraction", "wholeSystemComplete": False})

    # The table has9rows and7columns. Its63cells are illustrated classifications,
    # not63physical musicians, unique instruments or a complete world inventory.
    source = img("musi9")
    table = entity("world:table", "Illustrated instrument comparison", "illustrated-table", "Cross-cultural comparative witness", "musi9", [source], evidence=pixel(source, [0, 0, 1229, 1536]))
    view(world, "Instrument technique × region:63illustrated cells", table, ["musi9"], {"literalRows": 9, "literalColumns": 7, "cellOccurrences": 63, "wholeSystemComplete": False})
    regions = ["Africa", "Asia", "Europe", "Greece", "India", "Mid. East", "S. America"]
    rows = [
        ("STRINGS (PLUCK)", ["kora", "pipa", "guitar", "lyre", "sitar", "oud", "charango"]),
        ("STRINGS (BOW)", ["ndingidi", "erhu", "violin", "lyra", "sarangi", "rebab", "vihuela de arco"]),
        ("STRINGS (STRIKE)", ["chitradi [uncertain reading]", "yanggum", "piano", "santouri", "santur", "santur", "berimbau"]),
        ("PIPES", ["ombgwe [uncertain reading]", "shakuhachi", "flute", "syrinx", "bansuri", "nay", "quena"]),
        ("REEDS", ["algaita", "bawu", "clarinet", "aulos", "shenai", "mijwiz", "chirimía"]),
        ("TUBES", ["horn", "suona", "horn", "salpinx", "nagfani [uncertain reading]", "karnay", "trumpet"]),
        ("MEMBRANO-PHONES", ["dum-dum", "tanggu", "timpani", "daouli", "tabla", "dumbek", "conga"]),
        ("IDIO-PHONES", ["mbira", "munhayo [uncertain reading]", "triangle", "sistron", "danda", "sistrum", "guiro"]),
        ("NOISE", ["shekere", "jabara [uncertain reading]", "cymbals", "scabellum", "manjira", "zils", "maracas"]),
    ]
    for ri, (category, names) in enumerate(rows):
        y0 = 70 + 153 * ri
        parent = entity(f"world:row:{ri}", category, "image-native-organological-category", "Cross-cultural comparative witness", "musi9", [source], ri, evidence=pixel(source, [0, y0, 1229, min(1536, y0 + 165)]))
        edge(table, parent, "has-illustrated-category", world, [source])
        for ci, (region, name) in enumerate(zip(regions, names)):
            child = entity(f"world:cell:{ri}:{ci}", name, "illustrated-instrument-table-cell", "Cross-cultural comparative witness", "musi9", [source], ci,
                           regionColumn=region, categoryRow=category,
                           evidence=pixel(source, [95 + 153 * ci, y0, min(1229, 245 + 153 * ci), min(1536, y0 + 165)], name, "uncertain" in name))
            edge(parent, child, "has-illustrated-region-cell", world, [source])

    # Source triad qualities and the explicitly permitted transposition population.
    source = img("musi10")
    quality_specs = [("Major", [0, 4, 7], ["C", "E", "G"]), ("Minor", [0, 3, 7], ["C", "Eb", "G"]),
                     ("Augmented", [0, 4, 8], ["C", "E", "G#"]), ("Diminished", [0, 3, 6], ["C", "Eb", "F#"])]
    chromatic = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]
    triads = entity("western:triad-family", "Four triad qualities on the pictured12-position pitch-class dial", "triad-quality-family", "Western", "musi10", [source], evidence=pixel(source, [0, 0, 1307, 640]))
    edge(wr, triads, "has-musical-family", western, [source])
    for pc, name in enumerate(chromatic):
        root = entity(f"western:triad-root:{pc}", name + " root context", "transposition-root-context", "Western", "musi10", [source], pc,
                      layer="source-rule-derived", derivation="Pictured12-position dial plus caption permitting spelling four triad qualities on roots; finite pitch-class projection only.")
        BY_ID[root]["position"]["cyclicCoordinate"] = pc
        edge(triads, root, "has-transposition-root", western, [source], "source-rule-derived")
        for qi, (quality, offsets, c_notes) in enumerate(quality_specs):
            chord = entity(f"western:triad:{pc}:{qi}", name + " " + quality, "root-qualified-triad-occurrence", "Western", "musi10", [source], qi,
                           layer="source-assertion" if pc == 0 else "source-rule-derived", relativeSemitoneOffsets=offsets,
                           evidence=pixel(source, [qi * 320, 0, min(1307, (qi + 1) * 320), 370]))
            edge(root, chord, "has-triad-quality", western, [source], "source-rule-derived")
            for ti, offset in enumerate(offsets):
                tone_pc = (pc + offset) % 12
                tone = entity(f"western:triad-tone:{pc}:{qi}:{ti}", c_notes[ti] if pc == 0 else f"pitch class{tone_pc} (spelling unassigned)",
                              "chord-tone-membership-occurrence", "Western", "musi10", [source], ti,
                              layer="source-assertion" if pc == 0 else "source-rule-derived", pitchClass=tone_pc,
                              exactFrequency=None, absoluteRegister=None)
                edge(chord, tone, "has-chord-tone-occurrence", western, [source], "source-rule-derived")

    # Major key→scale degree→stacked-third triad→tone occurrences. Counts concern
    # separate local contexts; they are not a disjoint catalogue of unique chords.
    source = img("musi20")
    major_root = entity("western:major-keys", "Major-key circle and local scale/chord contexts", "major-key-family", "Western", "musi20", [source, img("musi11"), img("musi10")], evidence=pixel(source, [0, 0, 1274, 815]))
    edge(wr, major_root, "has-musical-family", western, [source])
    fifth_keys = [("C", 0), ("G", 7), ("D", 2), ("A", 9), ("E", 4), ("B", 11), ("F#/Gb", 6), ("Db", 1), ("Ab", 8), ("Eb", 3), ("Bb", 10), ("F", 5)]
    scale = [0, 2, 4, 5, 7, 9, 11]
    key_ids = []
    for ki, (name, pc) in enumerate(fifth_keys):
        refs = [source, img("musi11"), img("musi10")]
        key = entity(f"western:major-key:{ki}", name + " major", "major-key-context", "Western", "musi20", refs, ki,
                     evidence=pixel(source, [0, 0, 765, 790]), rootPitchClass=pc)
        key_ids.append(key)
        edge(major_root, key, "has-major-key-context", western, refs)
        for degree in range(7):
            local = entity(f"western:major-degree:{ki}:{degree}", f"{name} major degree{degree + 1}", "key-qualified-scale-degree", "Western", "musi20+musi11", refs, degree,
                           layer="source-rule-derived", pitchClass=(pc + scale[degree]) % 12,
                           derivation="Major scale read from musi11; transposition from musi20; spelling/Hz/register not selected.")
            edge(key, local, "has-scale-degree-context", western, refs, "source-rule-derived")
            offsets = [scale[(degree + step) % 7] + 12 * ((degree + step) // 7) for step in [0, 2, 4]]
            intervals = [x - offsets[0] for x in offsets]
            quality = next(q for q, o, _ in quality_specs if intervals == o)
            chord = entity(f"western:diatonic-triad:{ki}:{degree}", f"{name} degree{degree + 1} {quality} triad", "key-degree-triad-occurrence", "Western", "musi20+musi11+musi10", refs,
                           layer="source-rule-derived", semitoneOffsetsFromDegree=intervals)
            edge(local, chord, "stack-alternate-scale-thirds", western, refs, "source-rule-derived")
            class_index = [q for q, _, _ in quality_specs].index(quality)
            edge(chord, f"music:western:triad:{(pc + scale[degree]) % 12}:{class_index}", "projects-to-root-quality-triad", western, refs, "source-rule-derived",
                 boundary="Finite root/quality projection relates local occurrences; it does not identify registers, exact tunings or performed sounds.")
            for ti, offset in enumerate(offsets):
                tone = entity(f"western:diatonic-tone:{ki}:{degree}:{ti}", f"local chord tone{ti + 1}: pitch class{(pc + offset) % 12}", "key-degree-chord-tone-occurrence", "Western", "musi20+musi11+musi10", refs, ti,
                              layer="source-rule-derived", pitchClass=(pc + offset) % 12,
                              sourceScaleDegree=(degree + [0, 2, 4][ti]) % 7 + 1)
                edge(chord, tone, "has-chord-tone-occurrence", western, refs, "source-rule-derived")
    for i in range(12):
        edge(key_ids[i], key_ids[(i + 1) % 12], "next-fifth-key-label", western, [source], "source-assertion", clockwise=True,
             boundary="Finite notational key circle; exact pure-fifth acoustic residual is not erased.")
        edge(key_ids[i], f"music:western:triad:{(fifth_keys[i][1] + 9) % 12}:1", "has-relative-minor-triad", western, [source], "source-rule-derived",
             boundary="The picture places relative-minor triads inside the major-key circle. This does not reconstruct every minor-mode system.")

    # Eight actual seventh types and the four actual bass/inversion table rows.
    source = img("musi12")
    seventh_specs = [("Cmaj7", ["C", "E", "G", "B"]), ("C7", ["C", "E", "G", "Bb"]), ("C7#5", ["C", "E", "G#", "Bb"]),
                     ("Cm7", ["C", "Eb", "G", "Bb"]), ("C°7", ["C", "Eb", "Gb", "Bbb"]), ("Cm(maj7)", ["C", "Eb", "G", "B"]),
                     ("Cmaj7#5", ["C", "E", "G#", "B"]), ("Cm7b5", ["C", "Eb", "Gb", "Bb"])]
    sr = entity("western:sevenths", "Eight basic seventh chords in the suppliedC-root witness", "seventh-chord-family", "Western", "musi12", [source], evidence=pixel(source, [0, 0, 1218, 900]))
    edge(wr, sr, "has-musical-family", western, [source])
    for ci, (name, notes) in enumerate(seventh_specs):
        chord = entity(f"western:seventh:{ci}", name, "source-rooted-seventh-chord", "Western", "musi12", [source], ci,
                       evidence=pixel(source, [(ci % 4) * 300, (ci // 4) * 350, min(1218, (ci % 4 + 1) * 300), (ci // 4 + 1) * 350]))
        edge(sr, chord, "has-seventh-quality", western, [source])
        for ni, name in enumerate(notes):
            tone = entity(f"western:seventh-tone:{ci}:{ni}", name, "source-seventh-tone-membership", "Western", "musi12", [source], ni)
            edge(chord, tone, "has-chord-tone-occurrence", western, [source])
            inversion = entity(f"western:seventh-inversion:{ci}:{ni}", ["root position", "first inversion", "second inversion", "third inversion"][ni], "source-inversion-bass-context", "Western", "musi12", [source], ni,
                               bassName=name, evidence=pixel(source, [0, 900, 1218, 1380]),
                               exceptions=["Only chord content and indicated bass are fixed; complete voicing, octave spacing and doubling remain unassigned."])
            edge(chord, inversion, "has-inversion-bass-context", western, [source])
            edge(inversion, tone, "uses-chord-tone-as-bass", western, [source])

    # Solfège traditions remain distinct even though this image compares columns.
    source = img("musi11")
    solfege = entity("western:solfege", "Major scale and Curwen hand-sign comparison", "notation-role-family", "Western", "musi11", [source], evidence=pixel(source, [0, 0, 1247, 540]))
    edge(wr, solfege, "has-musical-family", western, [source])
    ir = entity("indian:solfege", "Indian syllables as compared by the supplied image", "source-comparison-family", "Indian comparison witness", "musi11", [source])
    view(indian, "Indian syllable comparison — source columns only", ir, ["musi11"], {"wholeSystemComplete": False, "ragaInventoryRecovered": False})
    syllables = ["Do", "Re", "Mi", "Fa", "So", "La", "Ti"]
    indian_names = ["Sa", "Re", "Ga", "Ma", "Pa", "Da", "Ni"]
    degrees = []
    western_qualities = [["Root", "Firm"], ["Rousing", "Hopeful"], ["Steady", "Calm"], ["Desolate", "Awe"], ["Grand", "Bright"], ["Sad", "Weeping"], ["Leading Tone", "Piercing"]]
    indian_qualities = [["Basis", "Strong"], ["Joy", "Sexuality"], ["Anger", "Wrath"], ["Cleansing", "Yin"], ["Speech", "Yang"], ["Night", "Pleasure"], ["Agitated", "Effort"]]
    for i, (syllable, name) in enumerate(zip(syllables, indian_names)):
        ws = entity(f"western:solfege:{i}", syllable, "major-scale-syllable-position", "Western", "musi11", [source], i, evidence=pixel(source, [90 + 155 * i, 0, min(1247, 250 + 155 * i), 365]))
        it = entity(f"indian:solfege:{i}", name, "image-compared-swara-syllable", "Indian comparison witness", "musi11", [source], i)
        degrees.append(ws)
        edge(solfege, ws, "has-syllable-position", western, [source])
        edge(ir, it, "has-compared-syllable-position", indian, [source])
        edge(ws, it, "image-compares-column", indian, [source], boundary="A chart comparison is not identity of Indian tuning, raga, rhythm or grammar with Western major scale.")
        for family, parent, qualities, native_view, tradition in [("western", ws, western_qualities[i], western, "Western"), ("indian", it, indian_qualities[i], indian, "Indian comparison witness")]:
            for qi, quality in enumerate(qualities):
                attribute = entity(f"{family}:syllable-quality:{i}:{qi}", quality, "image-attributed-syllable-quality", tradition, "musi11", [source], qi,
                                   evidence=pixel(source, [75 + 155 * i, 230, min(1247, 255 + 155 * i), 475]),
                                   exceptions=["Image-associated meaning/quality is a source assertion, not an independently established acoustic or psychological law."])
                edge(parent, attribute, "image-attributes-quality", native_view, [source])
    for family, parent, name, native_view, tradition in [("western", solfege, "Do", western, "Western"), ("indian", ir, "Sa", indian, "Indian comparison witness")]:
        endpoint = entity(f"{family}:syllable-octave-return", name + " (pictured octave return)", "octave-return-syllable-occurrence", tradition, "musi11", [source], 7,
                          evidence=pixel(source, [1090, 0, 1247, 470]), nominalSyllable=name, uniqueNewSyllable=False)
        edge(parent, endpoint, "has-octave-return-occurrence", native_view, [source])
    for degree, alterations in [(1, ["lowered", "natural", "raised"]), (3, ["natural", "raised"]), (5, ["lowered", "natural", "raised"]), (6, ["lowered", "natural"])]:
        for ai, alteration in enumerate(alterations):
            node = entity(f"western:solfege-variant:{degree}:{ai}", f"degree{degree + 1} {alteration}", "source-intermediary-tone-variant", "Western", "musi11", [source], ai, evidence=pixel(source, [0, 1000, 1247, 1536]))
            edge(degrees[degree], node, "has-intermediary-tone-variant", western, [source])

    # Forms contain repeated occurrences, not duplicate theme identities.
    forms = entity("western:forms", "Source structural-form families", "musical-form-family", "Western", "musi13+musi19", [img("musi13"), img("musi19")])
    edge(wr, forms, "has-musical-family", western, [img("musi13"), img("musi19")])
    form_specs = [("Sonata", ["Intro", "X tonic", "Y dominant", "Development(XY) modulate", "X tonic", "Y tonic", "Coda"], "musi13", [0, 0, 1041, 375]),
                  ("Through-composed", list("QRSTUVW"), "musi13", [0, 400, 1041, 650]),
                  ("Rondo", list("XPXQXRX"), "musi13", [0, 690, 1041, 940]),
                  ("Arch", list("XYZYX"), "musi13", [0, 975, 1041, 1220]),
                  ("Theme and variations", ["X", "Xa", "Xb", "Xc", "Xd", "Xe"], "musi13", [0, 1240, 1041, 1536]),
                  ("Binary", ["A", "B"], "musi19", [70, 130, 460, 630]),
                  ("Rounded binary", ["A", "B", "A'"], "musi19", [470, 130, 830, 650]),
                  ("Ternary", ["A", "B", "A"], "musi19", [850, 130, 1220, 630])]
    for fi, (name, sections, image_name, box) in enumerate(form_specs):
        ref = img(image_name)
        f = entity(f"western:form:{fi}", name, "source-musical-form", "Western", image_name, [ref], fi, evidence=pixel(ref, box))
        edge(forms, f, "has-form", western, [ref])
        previous = None
        for si, name in enumerate(sections):
            section = entity(f"western:form-section:{fi}:{si}", name, "form-section-occurrence", "Western", image_name, [ref], si,
                             evidence=pixel(ref, box), metricDuration=None)
            edge(f, section, "contains-section-occurrence", western, [ref])
            if previous:
                edge(previous, section, "precedes-in-source-form", western, [ref])
            previous = section

    # Rest duration remains positive potential temporal space, not a zero or a
    # universal disappearance operator. Only8value levels are populated.
    source = img("musi18")
    rhythm = entity("western:rhythm", "Note/rest subdivisions, meter and long/short feet", "source-rhythmic-family", "Western", "musi18", [source])
    edge(wr, rhythm, "has-musical-family", western, [source])
    duration_names = ["whole", "half", "quarter", "eighth", "sixteenth", "thirty-second", "sixty-fourth", "one-hundred-twenty-eighth"]
    for kind in ["note", "rest"]:
        branch = entity("western:duration:" + kind, kind + " duration values", "duration-value-family", "Western", "musi18", [source])
        edge(rhythm, branch, "has-duration-family", western, [source])
        last = None
        for k, name in enumerate(duration_names):
            item = entity(f"western:duration:{kind}:{k}", name + " " + kind, "relative-duration-value", "Western", "musi18", [source], k,
                          layer="source-assertion" if k <= 4 else "source-rule-derived",
                          durationWholeNoteRatio={"numerator": "1", "denominator": str(2**k)},
                          evidence=pixel(source, [0, 0, 1137, 510]), performedOccurrenceCount=None)
            edge(branch, item, "has-duration-value", western, [source])
            if last:
                edge(last, item, "halves-duration-value", western, [source], "source-rule-derived", multiplicity=2, unit="equal-subdivision-value", physicalOrPerformedCount=None)
            last = item
    feet = [("Iamb", "SL"), ("Trochee", "LS"), ("Spondee", "LL"), ("Dibrach", "SS"),
            ("Tribrach", "SSS"), ("Dactyl", "LSS"), ("Amphibrach", "SLS"), ("Anapest", "SSL"),
            ("Bacchius", "SLL"), ("Antibacchius", "LLS"), ("Amphimacer", "LSL"), ("Molossus", "LLL")]
    feet_parent = entity("western:poetic-feet", "Twelve duple/triple long-short feet in the source", "source-pattern-family", "Western", "musi18", [source])
    edge(rhythm, feet_parent, "has-long-short-pattern-family", western, [source])
    for i, (name, pattern) in enumerate(feet):
        node = entity(f"western:poetic-foot:{i}", name, "source-long-short-pattern", "Western", "musi18", [source], i, pattern=pattern,
                      evidence=pixel(source, [575, 960, 1137, 1536]), longShortDurationRatio=None)
        edge(feet_parent, node, "has-duple-foot" if len(pattern) == 2 else "has-triple-foot", western, [source])
    assert len({p for _, p in feet if len(p) == 2}) == 4
    assert len({p for _, p in feet if len(p) == 3}) == 8
    for i, signature in enumerate(["2/4", "2/8", "2/16", "3/4", "3/8", "3/16"]):
        node = entity(f"western:meter:{i}", signature, "source-meter-example", "Western", "musi18", [source], i, evidence=pixel(source, [0, 960, 585, 1480]))
        edge(rhythm, node, "has-meter-example", western, [source])

    # The comparative page carries separate4- and5-element representations.
    # No causal/musical equivalence is inferred from its circular presentation.
    source = img("musi19")
    elements = entity("western:humoral-elements", "Four-element humoral comparison in supplied image", "source-correspondence-family", "Western comparison witness", "musi19", [source],
                      evidence=pixel(source, [50, 755, 665, 1420]))
    edge(wr, elements, "has-source-correspondence-family", western, [source])
    for i, (name, attributes) in enumerate([("Fire", ["Hot", "Dry", "Yellow bile", "Choleric", "Summer"]),
                                           ("Air", ["Hot", "Wet", "Blood", "Sanguine", "Spring"]),
                                           ("Water", ["Cold", "Wet", "Phlegm", "Phlegmatic", "Winter"]),
                                           ("Earth", ["Cold", "Dry", "Black bile", "Melancholic", "Autumn"]) ]):
        node = entity(f"western:humoral-element:{i}", name, "image-element-category", "Western comparison witness", "musi19", [source], i,
                      evidence=pixel(source, [50, 755, 665, 1420]), attributedQualities=attributes,
                      exceptions=["Humoral and seasonal correspondences are the image's assertions; no independent physical/medical law is claimed."])
        edge(elements, node, "has-image-element-category", western, [source])
    five_elements = entity("chinese:image-five-elements", "Far-Eastern five-element diagram in supplied image", "source-correspondence-family", "Chinese comparison witness", "musi19", [source],
                           evidence=pixel(source, [645, 750, 1225, 1420]))
    edge(cr, five_elements, "has-source-correspondence-family", chinese, [source])
    for i, name in enumerate(["Fire", "Earth", "Metal", "Water", "Wood"]):
        node = entity(f"chinese:image-element:{i}", name, "image-five-element-category", "Chinese comparison witness", "musi19", [source], i,
                      evidence=pixel(source, [645, 750, 1225, 1420]),
                      exceptions=["Creates/destroys labels are visible; complete directed-arrow transcription is pending, so none is fabricated here."])
        edge(five_elements, node, "has-image-five-element-category", chinese, [source])

    # Native Chinese12pitch generation and seasonal orders are kept separately.
    ls = primary["lushi_yinlv"]["id"]
    text = text_by_name["lushi_yinlv"]
    lushi_passage = passage(ls, text, "黃鐘生林鐘", "天地之風氣正")
    lushi = entity("chinese:lushi", "呂氏春秋 音律 witness", "native-text-musical-system", "Chinese", "LuShiChunqiu-YinLv", [ls], evidence=lushi_passage)
    edge(cr, lushi, "has-native-witness", chinese, [ls])
    generation = ["黃鐘", "林鐘", "太蔟", "南呂", "姑洗", "應鐘", "蕤賓", "大呂", "夷則", "夾鐘", "無射", "仲呂"]
    seasons = [("仲冬", "黃鐘"), ("季冬", "大呂"), ("孟春", "太蔟"), ("仲春", "夾鐘"), ("季春", "姑洗"), ("孟夏", "仲呂"),
               ("仲夏", "蕤賓"), ("季夏", "林鐘"), ("孟秋", "夷則"), ("仲秋", "南呂"), ("季秋", "無射"), ("孟冬", "應鐘")]
    assert len(set(generation)) == 12 and {p for _, p in seasons} == set(generation)
    for a, b in zip(generation, generation[1:]):
        assert a + "生" + b in text
    pipes = {}
    for i, name in enumerate(generation):
        pipes[name] = entity(f"chinese:lushi:pipe:{i}", name, "witness-named-lu-standard", "Chinese", "LuShiChunqiu-YinLv", [ls], i,
                             evidence=lushi_passage, nativeCoordinates={"generationOrderIndex": i, "seasonalOrderIndex": [p for _, p in seasons].index(name)}, exactFrequency=None)
        edge(lushi, pipes[name], "has-named-lu-standard", chinese, [ls])
        if i:
            edge(pipes[generation[i-1]], pipes[name], "source-generates-next-lu", chinese, [ls], exactAcousticClosureAsserted=False)
    upper = ["黃鐘", "大呂", "太蔟", "夾鐘", "姑洗", "仲呂", "蕤賓"]
    lower = ["林鐘", "夷則", "南呂", "無射", "應鐘"]
    upper_literal = re.search(r"黃鐘、(.+?)為上", text).group(0)
    lower_literal = re.search(r"林鐘、夷則、南呂、無射、應鐘為下", text).group(0)
    assert len(upper_literal.removesuffix("為上").split("、")) == 7
    assert len(lower_literal.removesuffix("為下").split("、")) == 5
    partition_nodes = []
    for name, members in [("上", upper), ("下", lower)]:
        part = entity("chinese:lushi:partition:" + name, name, "source-up-down-lu-category", "Chinese", "LuShiChunqiu-YinLv", [ls],
                      evidence=lushi_passage, statedExtent={"value": len(members), "unit": "witness-named-lu-standard"},
                      literalPartitionText=upper_literal if name == "上" else lower_literal,
                      exceptions=["Native上/下 classification is not silently equated with male/female, sixyang/sixyin or Western keyboardcolor."])
        partition_nodes.append(part)
        edge(lushi, part, "has-native-up-down-partition", chinese, [ls])
        for name in members:
            edge(part, pipes[name], "has-up-down-member", chinese, [ls])
    for i, (season, name) in enumerate(seasons):
        node = entity(f"chinese:lushi:season:{i}", season, "native-seasonal-period-position", "Chinese", "LuShiChunqiu-YinLv", [ls], i, evidence=lushi_passage)
        edge(lushi, node, "has-seasonal-position", chinese, [ls])
        edge(node, pipes[name], "season-associates-lu", chinese, [ls])

    # The6/6categories belong to another exact witness; lexical variants remain
    # visible rather than silently identified with the preceding twelve names.
    zs = primary["zhouli_zhushu23"]["id"]
    text = text_by_name["zhouli_zhushu23"]
    zhou_passage = passage(zs, text, "陽聲黄鍾", "注以合陰陽之聲")
    material_passage = passage(zs, text, "金鍾鎛也", "音義")
    zhou = entity("chinese:zhouli", "周禮注疏 卷23 witness", "native-text-musical-system", "Chinese", "ZhouLi-ZhuShu23", [zs], evidence=zhou_passage)
    edge(cr, zhou, "has-native-witness", chinese, [zs])
    for category, names in [("陽聲", ["黄鍾", "大蔟", "姑洗", "蕤賓", "夷則", "無射"]), ("陰聲", ["大呂", "應鍾", "南呂", "函鍾", "小呂", "夾鍾"])]:
        parent = entity("chinese:zhouli:category:" + category, category, "source-yin-yang-lu-category", "Chinese", "ZhouLi-ZhuShu23", [zs],
                        statedExtent={"value": 6, "unit": "witness-named-lu-category-member"}, evidence=zhou_passage)
        edge(zhou, parent, "has-native-yin-yang-category", chinese, [zs])
        for i, name in enumerate(names):
            node = entity(f"chinese:zhouli:pitch:{category}:{i}", name, "witness-named-lu-category-member", "Chinese", "ZhouLi-ZhuShu23", [zs], i, evidence=zhou_passage,
                          exceptions=["Native witness spelling retained. Cross-witness alias/concordance is a separate relation, not inferred by count."])
            edge(parent, node, "has-yin-yang-member", chinese, [zs])
    five = entity("chinese:zhouli:five", "五聲", "native-tone-function-family", "Chinese", "ZhouLi-ZhuShu23", [zs], evidence=zhou_passage)
    edge(zhou, five, "has-tone-function-family", chinese, [zs])
    for i, name in enumerate(["宮", "商", "角", "徴", "羽"]):
        node = entity(f"chinese:zhouli:function:{i}", name, "native-tone-function", "Chinese", "ZhouLi-ZhuShu23", [zs], i, evidence=zhou_passage)
        edge(five, node, "has-tone-function", chinese, [zs])
    bayin = entity("chinese:zhouli:bayin", "八音", "native-material-classification", "Chinese", "ZhouLi-ZhuShu23", [zs], evidence=material_passage)
    edge(zhou, bayin, "has-organological-classification", chinese, [zs])
    materials = [("金", ["鍾", "鎛"]), ("石", ["磬"]), ("土", ["塤"]), ("革", ["鼓", "鼗"]),
                 ("絲", ["琴", "瑟"]), ("木", ["柷", "敔"]), ("匏", ["笙"]), ("竹", ["管", "簫"])]
    for i, (name, instruments) in enumerate(materials):
        parent = entity(f"chinese:zhouli:material:{i}", name, "bayin-material-category", "Chinese", "ZhouLi-ZhuShu23", [zs], i, evidence=material_passage)
        edge(bayin, parent, "has-material-category", chinese, [zs])
        for j, name in enumerate(instruments):
            child = entity(f"chinese:zhouli:instrument:{i}:{j}", name, "source-instrument-kind", "Chinese", "ZhouLi-ZhuShu23", [zs], j,
                           evidence=material_passage, physicalInstrumentOrPlayerCount=None,
                           exceptions=["A named instrument kind is not a physical performer or strict material-disjointness claim."])
            edge(parent, child, "classifies-instrument-kind", chinese, [zs])

    # Lam's own2024formal model, not an undated universal Chinese ontology.
    ls = primary["lam2024"]["id"]
    text = text_by_name["lam2024"]
    lam_evidence = passage(ls, text, "Index numbers 0", length=88)
    lam = entity("chinese:lam", "Lam2024 xuangong model", "dated-native-analytical-model", "Chinese", "Lam2024", [ls], evidence=lam_evidence,
                 citation={"author": "Nathan L. Lam", "title": "Pentatonic Xuangong 旋宮 Transformations in Chinese Music", "year": 2024, "doi": "10.30535/mto.30.1.5"},
                 nativeConvention="Huangzhong=C is the paper's chosen labeling convention, not independently recovered absolute historical orientation.")
    edge(cr, lam, "has-dated-formal-model", chinese, [ls])
    names = ["gong 宮", "shang 商", "jue 角", "zhi 徵", "yu 羽"]
    offsets = [0, 2, 4, 7, 9]
    contexts = {}
    for key in range(12):
        parent = entity(f"chinese:lam:set:{key}", f"gong-set index{key}", "Lam-pentatonic-set-context", "Chinese", "Lam2024", [ls], key,
                        layer="source-rule-derived", nativeCoordinates={"pc_pent": key}, evidence=lam_evidence)
        edge(lam, parent, "has-gong-set-context", chinese, [ls], "source-rule-derived")
        for role in range(5):
            node = entity(f"chinese:lam:context:{key}:{role}", f"({key}, {names[role]})", "Lam-pentatonic-note-context", "Chinese", "Lam2024", [ls], role,
                          layer="source-rule-derived", nativeCoordinates={"pc_pent": key, "pos_note": role, "pc_note": (key + offsets[role]) % 12},
                          evidence=lam_evidence, exceptions=["A formal set-position context is not an extra physicalpipe, attestedmode, historicalperformer or exactfrequency."])
            contexts[key, role] = node
            edge(parent, node, "has-pentatonic-position-context", chinese, [ls], "source-rule-derived")
    actions = {"T1": (1, 0), "t1": (0, 1), "b1": (7, 2), "q1": (5, 3)}
    for (key, role), source_node in contexts.items():
        for name, (a, b) in actions.items():
            target = ((key + a) % 12, (role + b) % 5)
            edge(source_node, contexts[target], "native-xuangong-" + name, chinese, [ls], "source-rule-derived",
                 sourceSections="Lam2024 §§2.2,2.5,2.6,3.5,3.10", formula=f"(k,p)->(k+{a} mod12,p+{b} mod5)")
        assert ((key + 7 + 5) % 12, (role + 2 + 3) % 5) == (key, role)
    assert next(n for n in range(1, 61) if (5*n) % 12 == 0 and (3*n) % 5 == 0) == 60
    assert (5*5) % 12 == 1 and (3*5) % 5 == 0
    assert (5*12) % 12 == 0 and (3*12) % 5 == 1

    # All remaining assigned images receive accountable, bounded semantic status.
    # These named concepts are source claims; no tiny notation is guessed.
    supplementary = [
        ("musi14", "Notation witnesses", [("Bhatkhande — Indian", ["rag", "tal", "tempo", "melody", "lyrics"]),
         ("Song of Seikilos — Greek", ["lyrics", "basic melodic outline"]), ("Jianpu — Chinese", ["scale pitch numbers", "duration/rest dots and lines", "lyrics"]),
         ("Medieval Europe", ["staff", "square/line pitch and rhythm", "lyrics"])]),
        ("musi15", "Chord extension and resolution families", [("Extensions", ["Cmaj9", "Cmaj7#11", "C13(#11,b9)"]),
         ("Diminished-seventh resolution examples", ["D#°7 -> E", "F#°7 -> G", "A°7 -> Bb", "C°7 -> Db"]),
         ("Altered-sixth labels", ["Italian Aug6th", "German Aug6th", "French Aug6th", "Neapolitan6th"])]),
        ("musi20", "Modulation and cadences", [("Cadences", ["authentic", "plagal", "deceptive", "half"]),
         ("Source progression", ["I", "IV", "V7", "I"]), ("Pivot modulation", ["one click: vi in X = ii in Y", "one click: iii in X = vi in Y", "two clicks: iii in X = ii in Y"]) ]),
        ("conglmusi2", "Provisional contact-sheet headings", [("Visible source headings", ["Dotted notes and rests", "Form and structure", "Further melodic elements", "Around the world", "Complex chord progressions", "Acoustics and overtones", "Enharmonic circular spellings"]) ]),
    ]
    for image_name, family, branches in supplementary:
        source = img(image_name)
        parent = entity("supplement:" + image_name, family, "bounded-source-concept-family", "Cross-cultural notation witness" if image_name == "musi14" else "Western", image_name, [source],
                        evidence=pixel(source, [0, 0, *images[image_name]["dimensions"]]),
                        exceptions=["Full printed notation, source dating and every prose assertion are not exhaustively transcribed in this unit."])
        local_view = western
        if image_name == "musi14":
            local_view = "music:notation-witnesses"
            view(local_view, "Distinct Indian, Greek, Chinese and European notation witnesses", parent, ["musi14"],
                 {"wholeSystemComplete": False, "claim": "Only source-caption encoding channels recovered; historical dating and full score transcription unverified."})
        else:
            edge(wr, parent, "has-source-concept-family", western, [source])
        for bi, (name, children) in enumerate(branches):
            native_tradition = ["Indian", "Ancient Greek", "Chinese", "Western"][bi] if image_name == "musi14" else "Western"
            group = entity(f"supplement:{image_name}:{bi}", name, "source-concept-subfamily", native_tradition, image_name, [source], bi)
            edge(parent, group, "has-source-subfamily", local_view, [source])
            if image_name == "musi14" and bi == 2:
                edge(cr, group, "has-source-notation-witness", chinese, [source])
            for ci, name in enumerate(children):
                node = entity(f"supplement:{image_name}:{bi}:{ci}", name, "printed-concept-or-example-occurrence", native_tradition, image_name, [source], ci)
                edge(group, node, "has-source-example", local_view, [source])
                if image_name == "musi14" and bi == 2:
                    edge(group, node, "has-source-example", chinese, [source])
    source = img("pythagh1")
    with localcontext() as ctx:
        ctx.prec = 50
        delta = Decimal(1200) * (Decimal(3) / 2).ln() / Decimal(2).ln() - Decimal(700)
        first_change = next(k for k in range(1, 100) if k * delta > 50)
        assert first_change == 26
    residual = entity("western:pythagorean-residual", "Pure-fifth residual survives the12-step label wheel", "source-plotted-mathematical-relation", "SUN/Western comparison", "pythagh1", [source],
                      evidence=pixel(source, [0, 0, 1770, 870]), exactTwelveFifthsResidual={"numerator": "531441", "denominator": "524288"},
                      binaryDecimalCentsAtTwelve=str(12 * delta), firstNearestLabelBoundaryCrossing=26,
                      exceptions=["Graph already depicts the result; reproducing it is not a blind prediction. nearest-label threshold50cents is the plot's convention."])
    edge(wr, residual, "retains-exact-frequency-residual", western, [source])

    inspected = [{"occurrenceName": name, "sourceId": row["id"], "sha256": row["sha256"],
                  "semanticStatus": "bounded-visual-extraction", "allPrintedClaimsProcessed": False,
                  "scope": "Graph members and relationships with pixel/source citations; contact sheet headings only where original subimage is unavailable."}
                 for name, row in images.items()]
    counts = Counter(e["unit"] for e in ENTITIES)
    assertions = {
        "instrumentTableCells": 63, "transposedTriadOccurrences": 48, "transposedTriadToneOccurrences": 144,
        "majorKeyContexts": 12, "majorScaleDegreeContexts": 84, "localDiatonicTriadOccurrences": 84, "localDiatonicChordToneOccurrences": 252,
        "literalSeventhQualities": 8, "literalInversionBassContexts": 32,
        "longShortFeet": 12, "ChineseLuShiNamedStandards": 12, "ChineseLuShiUpperLower": [7, 5],
        "ChineseZhouLiYangYin": [6, 6], "ChineseBayinMaterials": 8, "ChineseNamedInstrumentKinds": 13,
        "LamContextOccurrences": 60, "LamNativeActionEdges": 240,
    }
    assert counts["illustrated-instrument-table-cell"] == 63
    assert counts["root-qualified-triad-occurrence"] == 48
    assert counts["chord-tone-membership-occurrence"] == 144
    assert counts["key-degree-triad-occurrence"] == 84
    assert counts["key-degree-chord-tone-occurrence"] == 252
    assert counts["source-inversion-bass-context"] == 32
    assert counts["source-instrument-kind"] == 13
    assert counts["Lam-pentatonic-note-context"] == 60
    all_source_ids = {s["id"] for s in SOURCES}
    assert len(all_source_ids) == len(SOURCES)
    assert all(set(e["sourceRefs"]) <= all_source_ids for e in ENTITIES)
    assert all(e["source"] in BY_ID and e["target"] in BY_ID and set(e["sourceRefs"]) <= all_source_ids for e in EDGES)
    output = {"schema": "sunny.musical-hierarchy-supplement.v1", "sources": SOURCES, "entities": ENTITIES, "relationships": EDGES, "views": VIEWS,
              "inspection": inspected, "counts": {"sources": len(SOURCES), "entities": len(ENTITIES), "relationships": len(EDGES), "views": len(VIEWS), "byUnit": dict(counts)},
              "executedAssertions": assertions, "decisionReceipt": "docs/evidence/musical-hierarchy-design-superjev.json",
              "sourceCoverage": "Only12assigned images visually inspected here; other supplied image occurrences and root-reviewed pages are outside this worker's claimed processing.",
              "newSourceConsequence": {"id": "CHINESE-PARTITIONS-DISTINCT", "claim": "The primary Chinese witnesses themselves contain7/5上/下 and6/6陽/陰 classifications under different native relations.",
                                      "premises": ["Exact LuShi音律 upper/lower named lists", "Exact ZhouLi注疏23 yin/yang named lists"],
                                      "consequence": "A Chinese6/6 versus Western7/5 comparison cannot be treated as a unique tradition-level partition law. Recover relation/witness and actual members before aligning the partitions.",
                                      "notClaimed": "No biological-sex mapping, global orientation, exact cross-witness alias resolution or historical alteration is proved."},
              "boundaries": ["Parentage means source-family membership unless a different typed edge explicitly states generation or succession.",
                             "Derived roots, key contexts and chord memberships remain separate occurrence units; sums are not unique musical objects.",
                             "No128MIDI catalogue or4096pitchsubset catalogue is called complete musical law.",
                             "Lü generation is an open source chain here; finite label recurrence does not erase exact tuning residuals.",
                             "Lam's12×5 model is explicitly dated and source qualified; it is not imposed on every Chinese or Western system.",
                             "Physical sound sources, instrumental categories, functional tone positions, notes, time and symbolic associations remain separate dimensions.",
                             "Image concept/date/quality claims remain witness assertions, including unresolved captions and notation not yet transcribed."],
              "wholeMusicalSystemsComplete": False, "missionIComplete": False, "globalOrientationSelected": False}
    write("state/reconstruction/musical-hierarchies.json", output)
    write("docs/evidence/musical-hierarchy-image-processing.json", {"schema": "sunny.image-semantic-processing.v1", "inspected": inspected, "inputLedgerModified": False,
                                                                   "graphPath": "state/reconstruction/musical-hierarchies.json", "graphSha256": digest((ROOT / "state/reconstruction/musical-hierarchies.json").read_bytes()),
                                                                   "notProcessed": "Full image prose, every score note, all source systems, and other workers' pages."})
    lines = ["# Musical hierarchy supplement", "", f"The graph contains{len(ENTITIES)}source-scoped entity/context records and{len(EDGES)}typed relationships across{len(VIEWS)}views. Counts distinguish literal source objects, classifications and conditional generated occurrences; they are not a claim to a complete musical universe.", "",
             "## Native Chinese distinction recovered", "",
             "吕氏春秋《音律》 names12pitch standards in a generation chain and a different seasonal order. It also names7上standards and5下standards. 周礼注疏卷23 separately names6陽聲and6陰聲. These are different source relations; upper/lower does not become biological sex or keyboard color. The exact lists, witnesses and source hashes are in the graph.", "",
             "Chinese branches retain12namedlü,5tone functions,8material classes and13instrument kinds, with no invented physical players. A separate Lam2024view of60set-position contexts executesT/t/b/q; b1andq1are inverse, each has order60, q5=T1andq12=t1. These are properties of that original modern analytical model.", "",
             "## Western and comparative branches", "",
             "The pictured12-position root frame supports48four-quality triad occurrences and144tone memberships. The major-key frame has12keys,84local scale-degree contexts,84local stacked-third triads and252tone memberships. They are parented, source-qualified occurrences; duplicated names and contexts are not counted as independently distinct chords. Complete enharmonic spelling, register and exact tuning remain separate.", "",
             "The literalC-root table supplies8seventh qualities,32tone memberships and32bass/inversion contexts. Other branches preserve8composition-form patterns,12duple/triple long-short feet,8duration levels each for notes/rests, meter examples, solfege variants, notation examples, cadence and modulation labels. The comparative instrument chart has63cells under its9rows and7region columns, with uncertain caption readings explicitly marked.", "",
             "The pure-fifth plot is reproduced as an already-exposed relation: twelve steps retain531441/524288, and its50-cent nearest-label convention first changes class at26steps. This is not a blind prediction.", "",
             "## Coverage and reproduction", "",
             "This worker visually inspectedmusi9–15,musi18–20,pythagh1andconglmusi2 at original resolution. Every image hash is bound; concept-level and contact-sheet extraction do not mean every printed symbol/prose claim is reconstructed. The source input ledger is unchanged.", "",
             "Reproduce with `python -X utf8 scripts/reconstruct_musical_hierarchies.py`, then validate the atlas with the existing hierarchy engine. The whole Western/Chinese traditions and MissionI remain incomplete.", "",
             "Primary source editions: [吕氏春秋卷六](https://zh.wikisource.org/zh/呂氏春秋/卷六), [周礼注疏卷23](https://zh.wikisource.org/wiki/周禮注疏_(四庫全書本)/卷23). The original analytical model is [Nathan L. Lam2024](https://mtosmt.org/issues/mto.24.30.1/mto.24.30.1.lam.html). Original HTML bytes and exact normalized-text/source-image locators are retained.", ""]
    (ROOT / "docs/reconstruction/MUSICAL_HIERARCHIES.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "passed", "exit_code": 0, "counts": output["counts"], "executedAssertions": assertions, "missionIComplete": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
