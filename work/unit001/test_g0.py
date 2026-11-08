import dataclasses,json,unittest
from pathlib import Path
from evidence import *
from contracts import CrossOrientationRegistry

ROOT=Path(__file__).parent
class G0Tests(unittest.TestCase):
    def setUp(self):self.graph=import_matrix((ROOT/'frozen/source/matrix-message.txt').read_bytes(),'conversation:current:matrix')
    def test_01_groups_and_order(self):
        self.assertEqual(len(self.graph.grid.script_labels),15)
        self.assertEqual(self.graph.grid.script_labels[0],'Proto-Sinaitic (proxy)')
        self.assertEqual(self.graph.grid.script_labels[-1],'English')
    def test_02_all_fields_and_source_roundtrip(self):
        self.assertEqual(roundtrip_source(self.graph), (ROOT/'frozen/source/matrix-message.txt').read_bytes())
        self.assertEqual(len(self.graph.cells),540)
        for c in self.graph.cells:
            for name in ('glyph','ipa','english'):
                coordinate=c.coordinates[name]
                self.assertEqual(self.graph.source.raw_text[coordinate['start']:coordinate['end']],getattr(c,name))
    def test_03_counts_and_unique_coordinates(self):
        self.assertEqual(len(self.graph.witnesses),381)
        self.assertEqual(sum(c.glyph=='' for c in self.graph.cells),159)
        self.assertEqual(len({(c.script_id,c.ordinal) for c in self.graph.cells}),540)
    def test_04_unknown_is_not_silence(self):
        unknown=[w for w in self.graph.witnesses if w.raw_supplied_ipa=='?']
        self.assertEqual([w.local_ordinal for w in unknown],[2,4,18,26])
        self.assertTrue(all(w.phonetic_type==PhoneticType.UNKNOWN_VALUE for w in unknown))
    def test_05_proxies_and_scalars(self):
        first=self.graph.witnesses[0]
        self.assertEqual(first.glyph_type,GlyphType.UNICODE_PROXY_FOR_UNENCODED)
        self.assertEqual(first.unicode_scalars,tuple(map(ord,first.raw_supplied_glyph)))
    def test_06_local_ordinal_is_not_alignment(self):
        self.assertEqual(self.graph.genealogy,())
        self.assertEqual(self.graph.alignments,())
    def test_07_heterogeneous_persian(self):
        values=[w.phonetic_type for w in self.graph.witnesses if w.script_label=='Old Persian']
        self.assertEqual(values.count(PhoneticType.VOWEL_SIGN),3)
        self.assertEqual(values.count(PhoneticType.SYLLABOGRAM),33)
    def test_08_english_names(self):
        self.assertTrue(all(w.phonetic_type==PhoneticType.LETTER_NAME for w in self.graph.witnesses if w.script_label=='English'))
    def test_09_alternatives_and_glosses(self):
        w=next(w for w in self.graph.witnesses if w.script_label=='Square Hebrew' and w.local_ordinal==2)
        self.assertEqual(w.raw_supplied_ipa,'b/v');self.assertEqual(w.raw_supplied_english_approx,'b/v')
    def test_10_claims_and_dating(self):
        self.assertEqual(self.graph.attestations,())
        self.assertTrue(all(c.epistemic_status in (Epistemic.USER_SUPPLIED_DATA,Epistemic.INFERRED) for c in self.graph.claims))
        with self.assertRaises(ValueError):DatedAttestation('d','s','inscription',10,-10)
        self.assertIsNone(DatedAttestation('d','s','inscription',None,None).earliest)
    def test_11_nested_immutability(self):
        with self.assertRaises(TypeError):self.graph.cells[0].coordinates['glyph']['start']=7
        raw={'nested':[{'x':1}]};claim=Claim('c','s','p',raw,Epistemic.INFERRED,(),None,'test')
        raw['nested'][0]['x']=8;self.assertEqual(claim.value['nested'][0]['x'],1)
    def test_12_deterministic_serialization(self):
        serialized=serialize(self.graph)
        self.assertEqual(serialize(deserialize(serialized)),serialized)
        self.assertEqual(serialize(import_matrix(roundtrip_source(self.graph),'conversation:current:matrix')),serialized)
    def test_13_bad_foreign_key(self):
        bad=dataclasses.replace(self.graph.witnesses[0],raw_cell_id='not-real')
        with self.assertRaises(ValueError):validate_graph(dataclasses.replace(self.graph,witnesses=(bad,)+self.graph.witnesses[1:]))
    def test_14_duplicate_occupancy(self):
        with self.assertRaises(ValueError):validate_graph(dataclasses.replace(self.graph,witnesses=self.graph.witnesses+(self.graph.witnesses[0],)))
    def test_15_tamper_and_bad_source(self):
        with self.assertRaises(ValueError):validate_graph(dataclasses.replace(self.graph,source=dataclasses.replace(self.graph.source,raw_text=self.graph.source.raw_text+'x')))
        with self.assertRaises(ValueError):import_matrix(b'Alphabet\t1\n','bad')
    def test_16_g0_full_validation(self):
        result=verify_g0_conservation(self.graph)
        self.assertEqual(result['status'],'PASSED');self.assertEqual(len(result['invariants']),20)
    def test_17_registry_lock(self):
        registry=CrossOrientationRegistry();self.assertEqual(registry.adapters,())
        with self.assertRaises(PermissionError):registry.register({'source':'sefer','target':'western'})
        with self.assertRaises(PermissionError):registry.evaluate(None)
        with self.assertRaises(PermissionError):CrossOrientationRegistry.from_json('{"g7":true,"adapters":[{}]}')
    def test_18_genealogy_and_feature_refs(self):
        edge=GenealogyEdge('edge','missing','missing','PROPOSED_SIMILARITY',Epistemic.HYPOTHESIZED_ALIGNMENT,(),(),{})
        with self.assertRaises(ValueError):validate_graph(dataclasses.replace(self.graph,genealogy=(edge,)))
    def test_19_blank_flags(self):
        for c in self.graph.cells:
            self.assertEqual(c.blank_fields,tuple(n for n in ('glyph','ipa','english') if getattr(c,n)==''))
    def test_20_no_implicit_alignment_or_dates(self):
        self.assertTrue(all(not w.attestation_refs for w in self.graph.witnesses))
        self.assertTrue(all(c['status']=='PASS' for c in verify_g0_conservation(self.graph)['invariants']))
if __name__=='__main__':unittest.main()
