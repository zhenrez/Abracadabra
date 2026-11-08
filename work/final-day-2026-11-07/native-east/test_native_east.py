"""Native assertions use primary-profile examples and independent finite counts."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util, json, unittest

ROOT=Path(__file__).resolve().parent

class NativeEastTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT/'east_models.py').exists(),'Chinese/Indian common-contract adapters are missing')
        import east_models
        self.module=east_models
    def test_chinese_generation_profile(self):
        m=self.module.ChineseModel();r=m.generation()
        self.assertEqual([x['length'] for x in r[:5]],[Q(1),Q(2,3),Q(8,9),Q(16,27),Q(64,81)])
        self.assertEqual([x['generation_index'] for x in r],list(range(12)))
        self.assertEqual([x['pitch_class'] for x in r],[0,7,2,9,4,11,6,1,8,3,10,5])
        self.assertEqual(r[7]['operator'],'U')
        self.assertEqual(r[7]['name'],'Da Lü')
    def test_length_frequency_direction(self):
        m=self.module.ChineseModel()
        self.assertEqual(m.act_length(Q(81),'D'),Q(54))
        self.assertEqual(m.act_length(Q(81),'U'),Q(108))
        self.assertEqual(m.frequency_ratio(Q(2,3)),Q(3,2))
        self.assertEqual(m.frequency_ratio(Q(4,3)),Q(3,4))
    def test_chinese_register_nonclosure(self):
        m=self.module.ChineseModel();r=m.generation(count=13)
        self.assertEqual(r[12]['pitch_class'],0)
        self.assertEqual(r[12]['frequency'],Q(531441,524288))
        self.assertNotEqual(r[12]['length'],Q(1))
        self.assertEqual(m.generation(count=2,register=2)[1]['length'],Q(8,3))
        self.assertEqual(m.generation(count=2,register=2)[1]['frequency'],Q(3,8))
    def test_chinese_role_assignment_independent(self):
        m=self.module.ChineseModel();a=m.modal_context(0,0);b=m.modal_context(0,1);c=m.modal_context(7,0)
        self.assertEqual(a['pitch_classes'],b['pitch_classes'])
        self.assertNotEqual(a['role_assignments'],b['role_assignments'])
        self.assertNotEqual(a['pitch_classes'],c['pitch_classes'])
        self.assertEqual(len(m.contexts()),60)
    def test_chinese_native_and_tamper(self):
        from dataclasses import replace
        m=self.module.ChineseModel();e=m.encode(None)
        self.assertEqual(m.validate_native(e).status,'VALID')
        self.assertEqual(m.validate_native(replace(e,assignments=e.assignments[:-1])).status,'CONTRADICTION')
        self.assertEqual(m.describe(e,None).status,'NOT_EVALUATED')
    def test_chinese_ambiguous_reconstruction(self):
        m=self.module.ChineseModel();r=m.reconstruct({0:None},{'reference_lengths':('1','2')})
        self.assertEqual(len(r.candidates.solutions),2)
        self.assertEqual(r.identifiability['status'],'MULTIPLE_DISTINGUISHABLE')
        self.assertEqual(r.historical['status'],'NOT_VERIFIED')
        r=m.reconstruct({1:'2/3'},{'reference_lengths':('1','2')})
        self.assertEqual(len(r.candidates.solutions),1)
        self.assertNotEqual(r.outcome,'DETERMINED')
    def test_chinese_wrong_value_no_solution(self):
        self.assertEqual(self.module.ChineseModel().reconstruct({0:'7/3'}).identifiability['status'],'NO_FEASIBLE_SOLUTION')
    def test_grama_allocations_primary_examples(self):
        m=self.module.GramaModel()
        self.assertEqual(m.allocations('shadja'),(4,3,2,4,4,3,2))
        self.assertEqual(m.allocations('madhyama'),(4,3,2,4,3,4,2))
        self.assertEqual(sum(m.allocations('shadja')),22)
        self.assertEqual(sum(m.allocations('madhyama')),22)
        self.assertEqual(m.frequency_profile(),None)
    def test_fourteen_named_murchanas(self):
        m=self.module.GramaModel();modes=m.murchanas()
        self.assertEqual(len(modes),14)
        self.assertEqual(len({(x['grama'],x['name']) for x in modes}),14)
        self.assertEqual(modes[1]['start_note'],'Ni')
        self.assertEqual(modes[7]['start_note'],'Ma')
        for mode in modes:
            self.assertEqual(sum(mode['interval_units']),22)
            self.assertEqual(sorted(mode['note_order']),sorted(('Sa','Ri','Ga','Ma','Pa','Dha','Ni')))
            self.assertIsNone(mode['frequency_ratios'])
    def test_grama_common_contract_and_alternatives(self):
        m=self.module.GramaModel();self.assertEqual(m.validate_native(m.encode(None)).status,'VALID')
        self.assertEqual(len(m.reconstruct({'start_note':'Sa'}).candidates.solutions),2)
        self.assertEqual(len(m.reconstruct({'start_note':'Sa','grama':'shadja'}).candidates.solutions),1)
        self.assertEqual(m.describe(None,None).bits,None)
    def test_melakarta_seventy_two_independent_enumeration(self):
        m=self.module.MelakartaModel();actual=m.configurations()
        expected={(0,r,g,ma,7,d,n) for r in range(1,4) for g in range(r+1,5)
                  for ma in (5,6) for d in range(8,11) for n in range(d+1,12)}
        self.assertEqual(set(actual),expected);self.assertEqual(len(actual),72)
        self.assertEqual(actual[28],(0,2,4,5,7,9,11))
        self.assertEqual(actual[64],(0,2,4,6,7,9,11))
    def test_madhyama_thirty_six_pairs(self):
        m=self.module.MelakartaModel();pairs=set()
        for i,scale in enumerate(m.configurations()):
            partner=m.pair_madhyama(scale);self.assertEqual(m.pair_madhyama(partner),scale)
            pairs.add(tuple(sorted((scale,partner))))
            self.assertEqual(m.configurations().index(partner),(i+36)%72)
        self.assertEqual(len(pairs),36)
    def test_melakarta_reconstruction_ambiguity(self):
        m=self.module.MelakartaModel();r=m.reconstruct((0,2,4,None,7,9,11))
        self.assertEqual(len(r.candidates.solutions),2)
        self.assertEqual(r.identifiability['status'],'MULTIPLE_DISTINGUISHABLE')
        self.assertEqual(m.validate_native(m.encode(None)).status,'VALID')
    def test_invalid_native_inputs(self):
        c=self.module.ChineseModel();g=self.module.GramaModel();i=self.module.MelakartaModel()
        for call in (lambda:c.act_length(0,'D'),lambda:c.generation(count=14),lambda:c.modal_context(12,0),
                     lambda:g.allocations('invented'),lambda:i.pair_madhyama((0,1,2,3,4,5,6))):
            with self.assertRaises(ValueError):call()
    def test_stable_serialization_and_no_mdl_fiction(self):
        from evidence import serialize
        for m in (self.module.ChineseModel(),self.module.GramaModel(),self.module.MelakartaModel()):
            self.assertEqual(serialize(m.encode(None)),serialize(m.encode(None)))
            self.assertIsNone(m.describe(None,{'unsupported':'coding'}).bits)
    def test_profiles_have_source_roles(self):
        p=json.loads((ROOT/'source-profiles.json').read_text(encoding='utf-8'))
        self.assertTrue(all(x['source_url'] and x['source_role'] and x['locator'] for x in p['sources']))
        self.assertEqual(p['grama']['frequency_ratios'],None)
        self.assertEqual(p['chinese']['generation_names'][7],'Da Lü')
    def test_source_profiles_are_immutable(self):
        with self.assertRaises(TypeError):self.module.PROFILES['grama']['shadja'][0]=99
    def test_native_numeric_types_cannot_be_forged(self):
        from dataclasses import replace
        m=self.module.ChineseModel();e=m.encode(None)
        records=[dict(r) for r in e.assignments];records[1]['generation_index']=True
        self.assertEqual(m.validate_native(replace(e,assignments=tuple(records))).status,'CONTRADICTION')
        i=self.module.MelakartaModel()
        with self.assertRaises(ValueError):i.pair_madhyama((0,True,2,5,7,8,9))
    def test_empty_inputs_not_historical_determination(self):
        for m in (self.module.ChineseModel(),self.module.GramaModel(),self.module.MelakartaModel()):
            self.assertEqual(m.reconstruct({} if not isinstance(m,self.module.MelakartaModel) else ()).execution,'NOT_EVALUATED')

if __name__=='__main__':unittest.main()
