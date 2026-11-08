"""Render the source-backed current decision layer; does not alter source records."""
import json,re
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'state/reconstruction/decisions.json').read_text(encoding='utf8'))
lookup={r['id']:r for r in data['records']}
def ref(*names):
 return ', '.join('`DEC-'+name+'`' for name in names)
body=f'''# Reconstructed current decisions and research direction

This reconstructs the decision/correction layer through the October30 SUNNY discussion and the later-preserved Comparative Research Protocol snapshot, including the October23 orientation corrections, October24 age/year request and October29 image-extraction request. The organizing object is the **connected conductor’s master score**. The source record already contains concrete role/position constraints, conditional gains, alternative reconstructions and unresolved questions. It must not be reset to an empty72-address wheel.

The machine-readable companion is `state/reconstruction/decisions.json`. Its{len(data['records'])} individually quoted spans resolve to source messages, original/preserved paths, source hashes, within-message character offsets, literal display dates and every identical occurrence found in the selected inventory. The appendix below names each span; the JSON retains its exact full quotation. These are recovered source records, not a new scientific verdict or a claim that every account point has been interpreted.

## Current organizing mandate

The October23 user statement replaces the pizza/recipe organizing analogy with a lost symphony: recover parts, instrumentation, notes/registers, relationships, entrances, durations, sequence and the coordination of the whole. Retained wins must constrain the next passage, and losses must exclude or correct something specific. Repeated tests that return to whether a score exists do not fulfill that mandate. This preserves the governing reconstruction premise without making every particular transcription or placement immune to correction. ({ref('master_score','retained_wins','recipe_analogy')})

The exact project scopes supplied in that user turn are **SUN — Symphōnia Universālis Nūminōsa: the music for the Bible; SOL — Symphōnica Orchēstra Lūminōsa: music extending beyond the Bible to today; SOFI — Symphōniae Orchēstrae Fīnis Immūtābilis: music applied to everything else**. Historical shorthand reducing SUN to verification and SOL to interpretation must not replace these scopes. The same supplied formulation retains the existing **GEN / MEM / TIME / ADR / FUNC / TRN** register and pairs reconstructing surviving accounts with ARGO’s forward execution of recovered rules. The first-person user mandate and the polished formulation later in the same submitted turn remain separately attributable; submission alone does not establish who originally authored every later sentence. ({ref('project_scopes','six_axes','reverse_forward_roles')})

SUNNY has its own scope. It is the full connected alignment of recovered discoveries in systemic and generational wheels, the continuity mechanism, and the typed comparator for other systems. Its sibling projects keep distinct historical identities and missions. Jev’s first mission is recovering distinctions, decisions, indecisions and conditional consequences; its second mission is consequential prediction after that reconstruction, forward and backward, blind/constrained and gap aware. ({ref('sunny_full_alignment','sibling_missions','jev_mission_i','jev_mission_ii')})

## What must carry forward

- **The reference object is whole structural music, Eastern and Western.** It includes native units, addresses, ratios, transformations and the interaction between the complete Chinese pipe system and Western music. Scalar `2/3,3/4,1/2` relations are components; making a noise is insufficient to establish a lawful native musical interaction. Earlier SUN versions are formal accounts of that reference, while external bridges remain separately typed. V3 should use the hypergraph’s discoveries without being dependent on that artifact; the quarantined V4 exploration was to be compared independently against the same musical core. ({ref('music_is_core','fixed_reference','whole_native_musical_systems','independent_versions','v3_not_graph_dependency','quarantined_skeleton','compatibility_parallel_bridge')})
- **The provisional circular template is removable.** Retaining it for comparison did not authorize it to replace all native musical structure. The earlier user request to test the frozen graph with W72 and matched nulls survives as a dated request; source wins and unfinished biblical work must not disappear behind a new graph side quest. The user explicitly corrected the alleged failed Dan prediction as a personal hunch. ({ref('removable_template','freeze_and_test','biblical_continuity','dan_hunch_correction')})
- **Counting units are source-native.** The user explicitly rejected forcing every historical hierarchy to use the Valentinian Fibonacci count. Four primordial pairings, several possible roots and changes from individuals to syzygies to groups must remain in the representation. The supplied `F9=34` formulation calls that relation a constraint, not an orientation discriminator. Sri Yantra work must include native assignments, gates, petals and intersections and must retain the explicit rejection of Chiodo. ({ref('count_native_units','no_universal_fibonacci_count','primordial_pairings','f9_constraint_not_selector','reject_chiodo_reduction')})
- **The full Shem and post72 hierarchy are part of the score.** Source requests explicitly connect216letters, gates/pairings/groupings,360/364/365,Revelations and144000 with existing Sefer/positional locks, angelic/demonic hierarchies and the route to Adam. The13-to21 region was explicitly reported as populated; a remaining threshold operation is different from an empty corpus. The user asked for every lawful version consistent with locks, not a prematurely elected single version. ({ref('extend_past_seventytwo','full_shem_and_locks','shem_letter_pattern','not_empty_thirteen_twentyone','all_lawful_versions')})

## The latest connected orientation state

The October23 corrections materially advance the October18 transfer state. Preserve both with their source scopes:

1. **The Earth/aether lift is proposed at Scorpio/Ophiuchus/Sagittarius, rather than Virgo.** Thirteen does not mean adding a thirteenth angular pie slice; the user describes a Theodorus lift stacked at the boundary. The Earth sector’s apparent size must not be mistaken for a smaller elemental contribution. ({ref('lift_boundary_no_thirteenth_slice')})
2. **Sophia’s reset interpretation must not be lost.** The later correction places Sophia at the twelfth succession and a new zero/midnight; this double action can also make her13. It then compares Sophia/Yaldabaoth/Samael/Sakla with Adam/Cain/Abel/Seth. This is a source-qualified generative/role interpretation, not permission to collapse all referents or ordinal/clock meanings. ({ref('sophia_midnight_correction','new_system_reset_positions')})
3. **The Phaethon orientation remains a named candidate, with an alternative explicitly retained.** The user explores Yaldabaoth/Cronus/Phaethon, Samael/Zeus and Sakla/Saturn, while also retaining a Sophia/Gaia/Cronus/Saturn alternative and qualified language. A single flat `Yaldabaoth=Saturn` entry would erase the later discussion. ({ref('phaethon_sakla_candidate')})
4. **Chinese and Western orientations must be applied together.** The source contrasts male/female and yin/yang axes and explicitly complains that the full Chinese zodiac and monochord/Tree-of-Life bridge were omitted. The possible Western5+7 versus Chinese6+6 distinction is phrased conditionally—“I’m not saying it does”—and must not become a selected numeric law or software decision weighting. ({ref('full_chinese_polar_axes','male_female_partition_question')})
5. **Generation, element, instrumentation and timing are connected.** The user retains the early0,1,1,2,3 progression, proposes elemental instrument sections, asks about cardinal/diagonal offsets forming eight positions, and asks to retain Greek primordial→Titan→Olympian→demi→hero levels. The21–24 cluster named for further placement includes Sefer,Tree of Life,Judah,Rahu–Ketu,Chinese mountains and Shem gates. ({ref('instrumentation_layers','directions_elements_offset','greek_generational_instruments','twentyone_twentyfour_cluster','earlier_generations_retained')})

These source positions supplement, rather than disappear into, the finite twelve-completion address-family audit. A group-theoretic enumeration and a user’s current relational/orientational reconstruction are different evidence layers.

## The active human/musical passage

The current task is faithful translation between human events and musical functions, including who acts, with whom, under which conditions, what changes, what persists and how it accumulates over time. Three mathematical antecedents do not automatically mean three biological parents; genealogy, succession, a part, its performer and its address remain distinct. Known birth/sign and relationship anchors are legitimate entry points for cascading constraints; an unsuccessful cascade must still narrow the reconstruction. ({ref('human_dynamics','human_functions','birth_anchor_cascade')})

The supplied Cainan account reports the same8:9:12 harmonic configuration under competing genealogies but a different central-reference person, so the chord itself was not an election criterion. Later supplied results shifted attention from identical ordered pitches to differing proportional timing. The direct user then asked about the zoomed-out interaction between rhythms, directed a test on Eldad/Medad connected from Cainan, and requested recovery of the age/year dynamics. Those requests remain connected work, not isolated topic labels. Their reported mathematical results are retained as reports; this decision slice does not claim a fresh rerun of those historical calculations. ({ref('same_chord_different_reference','temporal_not_pitch_discrimination','zoomed_rhythm_question','eldad_medad_crosscheck','years_context_lookup')})

## October30 SUNNY constraints and remaining questions

The governing SUNNY premise is complete deterministic toroidal geometry with the Sierpinski-tetrahedral Monad at infinitum. Geometry and relations are mutually determining. Each generational class is represented with two turns/720degrees before its lift; changing displayed phase must not erase cumulative travel. Several related notions of time and several nonexhaustive interpretations of universes remain in the source. W144000 is a method-and-scale analogy: the user explicitly did not assign144000 a fixed cardinality, operator count, gematria value, rotation count or degree count. ({ref('geometry_relations','two_turns_per_class','multiple_times','universe_alternatives','w144_not_fixed_cardinality')})

The three underlying rectification goals remain zodiacal orientation/attribution, original sacred-symbol intentions and sound grammar, and date/time relationships. A discrepancy may indicate which foundational symbol, grammar or representation requires investigation; it is not automatically a reason to discard the whole accumulated model. The Intention/Will/Silence/Sophia relation remains explicitly qualified in the user’s language. The user’s last answered conceptual point favors progressively attained type law with minimal imposed constraints; no arbitrary host-designed weights or final provisional-law promotion policy was selected. The following assistant question about immediate use of unvalidated candidate laws remains unanswered in the supplied attachment. ({ref('three_goals','misalignment_localizes_changed_component','intention_will_open','progressive_type_law')})

The latest saved Comparative Research Protocol user turn, October29, requests full extraction of ten linked images. This slice preserves that request and its source references; it does not claim to have inspected those image pixels or established that no other local copy exists. ({ref('latest_image_extraction_request')})

## Coverage and verification

This slice scanned{data['coverage']['all_user_occurrences_scanned']} indexed user-message occurrences mechanically, selected{data['coverage']['selected_user_turn_occurrences']} occurrences by a declared title/local-snapshot pool, and retained{data['coverage']['unique_selected_full_texts']} exact full-text groups without deleting their occurrence provenance. Only the{len(data['records'])} curated spans received individual source-role classification here. Title screening and model classifications do not constitute exhaustive point-level interpretation or account completeness. Native exports end earlier than the later saved transcripts; later branches and inaccessible material remain separately accountable.

Actual SuperJev cloud inference selected latest-corrections-first with model mass0.96. A first classification request failed to bind each identical question instruction to its own source span; its four raw receipts remain preserved and are not adopted. Actual Jev selected explicit span linkage0.77, and corrected named-span requests/results are retained separately. Exact source-role distributions and resolved model `jev-1.14.0` remain in the JSON. They are conditional model outputs, not calibrated truth probabilities or independent historical adjudication.

Fresh verification checked{data['verification']['quote_checks']} exact quote/offset/hash records and{data['verification']['source_files_checked']} preserved source-file hashes, with zero source-hash errors and no duplicate record IDs. No source file or source database was changed by this decision-layer recovery. No service, test browser or background process was started.

## Source-span index

| Record | Literal source time | Recovered point | Source message / location |
|---|---|---|---|
'''
def order(row):
 try:return datetime.strptime(row['display_time'],'%m/%d/%Y, %I:%M:%S %p')
 except (TypeError,ValueError):return datetime.min
for row in sorted(data['records'],key=order):
 source=row['source_occurrences'][0]
 label=row['label'].replace('|','/')
 body+=f"| `{row['id']}` | {row['display_time'] or 'Source metadata only'} | {label} | `{source['id']}` · `{source['locator']}` |\n"
body+='\nExact quotations, full SHA256 values, character spans, source paths and duplicate occurrences are in `state/reconstruction/decisions.json`; all selected original user-turn text is retained in `docs/evidence/decisions-source-inventory.json`. No editorial assertion gains user authority from appearing in this index.\n'
folder=ROOT/'docs'/'reconstruction';folder.mkdir(parents=True,exist_ok=True)
(folder/'DECISIONS.md').write_text(body,encoding='utf8')
assert all('DEC-'+name in lookup for name in re.findall(r'`DEC-([^`]+)`',body))
print(json.dumps({'document':'docs/reconstruction/DECISIONS.md','records':len(data['records']),'bytes':len(body.encode('utf8'))}))
