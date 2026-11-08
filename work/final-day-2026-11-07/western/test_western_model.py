import importlib.util
from fractions import Fraction as F
import json
from pathlib import Path
import unittest


class WesternContractTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('western_model'), 'native orientation adapter is absent')
        import western_model
        return western_model

    def fixture(self, mode='ionian'):
        api=self.api();model=api.WesternOrientation()
        return {'profile_id':model.namespace,'kind':'scale','mode':mode,'source_ref':'engineering:exact-mode',
                'observations':[{'record_id':'degree:'+str(i),'ratio':str(r),'onset':str(i),'duration':'1',
                                 'voice':'v1'} for i,r in enumerate(model.core.mode(mode)['ratios'])]}

    def test_four_contract_methods_and_empty_input(self):
        m=self.api().WesternOrientation()
        self.assertEqual(m.validate_native(None).status,'NOT_EVALUATED')
        self.assertEqual(m.describe().status,'NOT_EVALUATED')
        self.assertIsNone(m.describe().bits)

    def test_all_seven_actual_scale_profiles_validate(self):
        m=self.api().WesternOrientation()
        for name in m.core.MODE_NAMES:
            self.assertEqual(m.validate_native(m.encode(self.fixture(name))).status,'VALID')

    def test_actual_scale_error_is_rejected(self):
        m=self.api().WesternOrientation();data=self.fixture();data['observations'][3]['ratio']='5/4'
        self.assertEqual(m.validate_native(data).status,'INVALID')

    def test_evidence_binding_and_identity_tamper(self):
        from dataclasses import replace
        api=self.api();m=api.WesternOrientation();encoded=m.encode(self.fixture())
        self.assertEqual(m.validate_native(replace(encoded,evidence_sha256='tampered')).status,'INVALID')
        data=self.fixture();data['observations'][1]['record_id']=data['observations'][0]['record_id']
        self.assertEqual(m.validate_native(data).status,'INVALID')

    def test_register_is_not_projected_away(self):
        api=self.api();m=api.WesternOrientation()
        e=m.encode({'kind':'performance','source_ref':'engineering:event','observations':[{'record_id':'a','ratio':'3'}]})
        self.assertEqual(e.observations[0].register,1)
        self.assertEqual(e.observations[0].pitch_class,F(3,2))
        self.assertEqual(e.observations[0].ratio,F(3))

    def test_exact_composition_and_nonclosure(self):
        api=self.api();m=api.WesternOrientation()
        fifth=api.Interval(4,7,F(3,2));fourth=api.Interval(3,5,F(4,3))
        self.assertEqual(fifth.compose(fourth).ratio,2)
        self.assertEqual(m.core.fifth_cycle()['comma'],F(531441,524288))
        self.assertFalse(m.core.fifth_cycle()['exact_return'])

    def test_rhythm_and_polyphony_preserve_voices(self):
        api=self.api();m=api.WesternOrientation()
        e=m.encode({'kind':'performance','source_ref':'engineering:polyphony','observations':[
            {'record_id':'a','ratio':'1','onset':'0','duration':'1/2','voice':'upper'},
            {'record_id':'b','ratio':'1/2','onset':'0','duration':'1','voice':'lower'}]})
        result=m.transform_events(e,api.Interval(7,12,F(2)),F(3,2))
        self.assertEqual(tuple(o.voice for o in result),('upper','lower'))
        self.assertEqual(tuple(o.ratio for o in result),(F(2),F(1)))
        self.assertEqual(tuple(o.duration for o in result),(F(3,4),F(3,2)))

    def test_unique_missing_pitch_under_configured_mode(self):
        m=self.api().WesternOrientation();values=['1','9/8',None,'4/3','3/2','27/16','243/128']
        receipt=m.reconstruct({'ratios':values,'tonic':'1'}, {'mode':'ionian'})
        self.assertEqual(receipt.identifiability['status'],'UNIQUE_UNDER_MODEL')
        self.assertEqual(receipt.candidates.solutions[0]['ratios'][2],'81/64')
        self.assertEqual(receipt.historical['status'],'NOT_VERIFIED')

    def test_ambiguous_and_contradictory_reconstruction(self):
        m=self.api().WesternOrientation()
        ambiguous=m.reconstruct({'ratios':['1']+[None]*6,'tonic':'1'})
        self.assertEqual(len(ambiguous.candidates.solutions),7)
        bad=m.reconstruct({'ratios':['1','7/5']+[None]*5,'tonic':'1'})
        self.assertEqual(bad.identifiability['status'],'NO_FEASIBLE_SOLUTION')

    def test_float_inputs_and_unknown_profile_rejected(self):
        m=self.api().WesternOrientation()
        for ratio in (1.5,0,-1):
            with self.assertRaises(ValueError):m.encode({'source_ref':'fixture','observations':[{'record_id':'x','ratio':ratio}]})
        data=self.fixture();data['profile_id']='ancient:all-tunings'
        with self.assertRaises(ValueError):m.encode(data)

    def test_serialization_and_source_profiles(self):
        api=self.api();m=api.WesternOrientation();a=m.encode(self.fixture())
        self.assertEqual(api.canonical_json(a),api.canonical_json(m.encode(self.fixture())))
        profiles=api.source_profiles()
        self.assertTrue({'greek_tetrachord','fludd_monochord','kepler_harmony','completed_harmony'}<=set(profiles))
        self.assertTrue(all('status' in p and 'source_ref' in p for p in profiles.values()))
        self.assertFalse(any(p.get('equal_temperament_imposed') for p in profiles.values()))

    def test_tetrachord_residual_and_length_frequency_dual(self):
        m=self.api().WesternOrientation()
        t=m.tetrachord()
        self.assertEqual(t['steps'],(F(9,8),F(9,8),F(256,243)))
        self.assertEqual(t['span'],F(4,3))
        self.assertEqual(m.length_action(F(1),'fifth'),F(2,3))
        self.assertEqual(1/m.length_action(F(1),'fifth'),F(3,2))

    def test_no_foreign_native_model_import(self):
        api=self.api();text=Path(api.__file__).read_text(encoding='utf-8')
        self.assertNotIn('from native_models',text)
        self.assertNotIn('import sefer',text)
        self.assertNotIn('harmonic_verifier',text)

    def test_exact_fraction_input_survives_binding_and_receipt_serialization(self):
        api=self.api();m=api.WesternOrientation()
        evidence={'source_ref':'engineering:fraction','observations':[{'record_id':'r','ratio':F(3,2)}]}
        self.assertEqual(m.validate_native(m.encode(evidence)).status,'VALID')
        receipt=m.reconstruct({'ratios':['1']+[None]*6,'tonic':'1'})
        self.assertIsInstance(json.loads(api.canonical_json(receipt)),dict)


if __name__=='__main__':unittest.main()
