from pathlib import Path
from dataclasses import replace
from fractions import Fraction
import json,sys,unittest

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
for path in (ROOT,BASE/'western',BASE/'native-east',BASE,BASE.parents[1]/'unit001'):
    if str(path) not in sys.path:sys.path.insert(0,str(path))

class CommonModelTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT/'common_models.py').exists(),'Common native contract wrapper is absent')
        import common_models,east_models,western_model
        self.common=common_models;self.east=east_models;self.west=western_model
    def western_fixture(self):
        native=self.west.WesternOrientation()
        return {'profile_id':native.namespace,'source_ref':'engineering:integration-control','kind':'performance',
            'observations':[{'record_id':'a','ratio':Fraction(3,2),'onset':'0','duration':'1/2','voice':'upper'},
                            {'record_id':'b','ratio':'1/2','onset':'0','duration':'1','voice':'lower'}]}
    def test_all_orientations_return_common_encoding(self):
        from contracts import EncodedModel
        for native in (self.east.ChineseModel(),self.east.GramaModel(),self.east.MelakartaModel()):
            wrapper=self.common.CommonOrientation(native)
            encoded=wrapper.encode(None,wrapper.default_profile_id)
            self.assertIsInstance(encoded,EncodedModel)
            self.assertEqual(wrapper.validate_native(encoded).status,'VALID')
        wrapper=self.common.CommonOrientation(self.west.WesternOrientation())
        encoded=wrapper.encode(self.western_fixture(),wrapper.default_profile_id)
        self.assertIsInstance(encoded,EncodedModel)
        self.assertEqual(wrapper.validate_native(encoded).status,'VALID')
    def test_unknown_profile_cannot_be_admitted(self):
        wrapper=self.common.CommonOrientation(self.east.GramaModel())
        with self.assertRaises(ValueError):wrapper.encode(None,'invented:universal-profile')
        with self.assertRaises(ValueError):self.common.CommonOrientation(self.east.GramaModel(),'invented')
    def test_western_exact_evidence_roundtrip(self):
        wrapper=self.common.CommonOrientation(self.west.WesternOrientation())
        encoded=wrapper.encode(self.western_fixture())
        self.assertEqual(encoded.assignments[0]['ratio'],{'numerator':3,'denominator':2})
        self.assertEqual(encoded.assignments[0]['duration'],{'numerator':1,'denominator':2})
        self.assertEqual(encoded.assignments[1]['voice'],'lower')
        text=wrapper.to_json(encoded);self.assertEqual(wrapper.to_json(wrapper.from_json(text)),text)
    def test_full_binding_rejects_unused_and_altered_records(self):
        for native,evidence in ((self.east.ChineseModel(),None),(self.west.WesternOrientation(),self.western_fixture())):
            wrapper=self.common.CommonOrientation(native);encoded=wrapper.encode(evidence)
            self.assertNotEqual(wrapper.validate_native(replace(encoded,unassigned_records=('invented',))).status,'VALID')
            self.assertNotEqual(wrapper.validate_native(replace(encoded,unmatched_values=('invented',))).status,'VALID')
            self.assertNotEqual(wrapper.validate_native(replace(encoded,assignments=encoded.assignments[:-1])).status,'VALID')
    def test_coding_is_explicit_measured_and_roundtrips(self):
        wrapper=self.common.CommonOrientation(self.east.ChineseModel());encoded=wrapper.encode(None)
        self.assertIsNone(wrapper.describe(encoded,None).bits)
        result=wrapper.describe(encoded,'lossless-typed-v1');details=wrapper.description_measurement(encoded)
        self.assertIsInstance(result.bits,int);self.assertGreater(result.bits,0)
        self.assertEqual(result.bits,details['conditional_total_bits'])
        self.assertEqual(details['roundtrip'],'EXACT')
        self.assertEqual(details['adapter_program_bytes'],(ROOT/'common_models.py').stat().st_size)
        self.assertEqual(details['historical_comparison'],'NOT_EVALUATED')
    def test_reconstruction_keeps_historical_axis(self):
        wrapper=self.common.CommonOrientation(self.east.MelakartaModel())
        result=wrapper.reconstruct((0,2,4,None,7,9,11))
        self.assertEqual(len(result.candidates.solutions),2)
        self.assertEqual(result.historical['status'],'NOT_VERIFIED')
    def test_forged_serialization_and_unknown_coding_rejected(self):
        wrapper=self.common.CommonOrientation(self.east.ChineseModel());encoded=wrapper.encode(None)
        data=json.loads(wrapper.to_json(encoded));data['profile_id']='invented'
        with self.assertRaises(ValueError):wrapper.from_json(json.dumps(data))
        self.assertIsNone(wrapper.describe(encoded,'imaginary-coding').bits)

if __name__=='__main__':unittest.main()
