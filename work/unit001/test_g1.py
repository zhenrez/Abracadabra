import json,unittest
from pathlib import Path
from evidence import import_matrix,serialize
from sefer import SeferModel,Profile,SLOT_ALIASES
from contracts import CrossOrientationRegistry

ROOT=Path(__file__).parent
class G1Tests(unittest.TestCase):
    def setUp(self):self.model=SeferModel()
    def test_A_complete(self):
        result=self.model.reconstruct(list(SLOT_ALIASES.values()))
        self.assertEqual(result.structural['status'],'VALID')
        self.assertEqual(self.model.pair_counts(),{'base':22,'expanded':29,'undirected':231,'directed_distinct':462,'ordered_with_self':484})
    def test_B_missing_mem_legacy(self):
        symbols=[v for v in SLOT_ALIASES.values() if v!='m']
        legacy=self.model.legacy(symbols)
        self.assertEqual(legacy['status'],'Invalid');self.assertEqual(legacy['reconstruction_suggestion'],'m');self.assertIsNone(legacy['harmonic_distance'])
        r=self.model.reconstruct(symbols)
        self.assertEqual(r.structural['status'],'INCOMPLETE');self.assertEqual(r.identifiability['status'],'UNIQUE_UNDER_MODEL')
        self.assertEqual(r.historical['status'],'NOT_VERIFIED');self.assertNotEqual(r.outcome,'DETERMINED')
    def test_C_original_ambiguity(self):
        symbols=[v for v in SLOT_ALIASES.values() if v not in ('s','ʃ')]+['s']
        r=self.model.reconstruct(symbols)
        self.assertEqual(len(r.candidates.solutions),2)
        self.assertEqual(r.identifiability['status'],'MULTIPLE_DISTINGUISHABLE')
    def test_D_resh(self):
        states=self.model.state_inventory('expanded')
        self.assertIn('sefer:letter:resh:state:1',states)
        self.assertIsNone(states['sefer:letter:resh:state:1']['phonetic_realization'])
    def test_E_duplicate(self):
        r=self.model.reconstruct(list(SLOT_ALIASES.values())[:-1]+['b'])
        self.assertEqual(r.structural['status'],'CONTRADICTION')
    def test_F_overflow(self):
        r=self.model.reconstruct(list(self.model.state_inventory('expanded'))+['b'],mode='expanded')
        self.assertEqual(r.structural['status'],'CONTRADICTION')
    def test_G_no_profile(self):
        self.assertEqual(self.model.validate_native(None).status,'NOT_EVALUATED')
        self.assertEqual(self.model.reconstruct([]).execution,'NOT_EVALUATED')
    def test_H_candidate_exhaustion(self):
        r=self.model.reconstruct(['b'],constraints={0:('sefer:letter:mem',)})
        self.assertEqual(r.identifiability['status'],'NO_FEASIBLE_SOLUTION')
    def test_I_multiple(self):
        r=self.model.reconstruct(['b/g'])
        self.assertEqual(len(r.candidates.solutions),2)
    def test_J_stability(self):
        self.assertEqual(serialize(self.model.reconstruct(['b/g'])),serialize(self.model.reconstruct(['b/g'])))
    def test_profile_encoding(self):
        graph=import_matrix((ROOT/'frozen/source/matrix-message.txt').read_bytes(),'conversation:current:matrix')
        profile=Profile('baseline:proto','Proto-Sinaitic (proxy)',self.model.baseline_hash)
        encoded=self.model.encode(graph,profile)
        self.assertEqual(len(encoded.assignments),22)
        self.assertTrue(all(a['record_id'] and a['claim_refs'] for a in encoded.assignments))
        self.assertEqual(self.model.validate_native(encoded).status,'VALID')
        with self.assertRaises(ValueError):self.model.encode(graph,Profile('bad','absent',self.model.baseline_hash))
    def test_no_fake_mdl(self):
        r=self.model.describe(None,None)
        self.assertEqual(r.status,'NOT_EVALUATED');self.assertIsNone(r.bits)
    def test_class_constraint(self):
        r=self.model.reconstruct(['b'],class_constraints={0:'Mothers'})
        self.assertEqual(r.structural['status'],'CONTRADICTION')
    def test_original_demonstration(self):
        saved=json.loads((ROOT/'frozen/sefer/harmonic-demo.json').read_bytes())
        base=list(self.model.legacy_module.GROUPS.values());base=[x for xs in base for x in xs]
        self.assertEqual(self.model.legacy(base),saved['complete'])
        self.assertEqual(self.model.legacy([x for x in base if x!='m']),saved['missing_m'])
        self.assertEqual(self.model.legacy(base[:-1]+['b']),saved['duplicate'])
if __name__=='__main__':unittest.main()
