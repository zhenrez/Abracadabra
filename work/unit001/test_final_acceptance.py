import dataclasses,os,unittest
from pathlib import Path
from evidence import import_matrix,validate_graph
from sefer import SeferModel,Profile
from contracts import CrossOrientationRegistry

ROOT=Path(__file__).parent
class FinalAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.graph=import_matrix((ROOT/'frozen/source/matrix-message.txt').read_bytes(),'current-chat')
        self.model=SeferModel()
    def encoded(self):return self.model.encode(self.graph,Profile('audit:proto','Proto-Sinaitic (proxy)',self.model.baseline_hash))
    def test_native_rejects_duplicate_evidence_identity(self):
        e=self.encoded();a=[dict(x) for x in e.assignments];a[1]['record_id']=a[0]['record_id']
        with self.assertRaises(ValueError):self.model.validate_native(dataclasses.replace(e,assignments=a))
    def test_native_rejects_removed_source_binding(self):
        e=self.encoded();a=[dict(x) for x in e.assignments];a[0]['claim_refs']=()
        with self.assertRaises(ValueError):self.model.validate_native(dataclasses.replace(e,assignments=a))
    def test_cell_ordinal_must_match_source_coordinate(self):
        # A whole-cell readdressing can preserve literal spans while falsifying local ordinal.
        cell=dataclasses.replace(self.graph.cells[0],ordinal=36)
        cells=(cell,)+self.graph.cells[1:35]+(self.graph.cells[36],)+self.graph.cells[37:]
        with self.assertRaises(ValueError):validate_graph(dataclasses.replace(self.graph,cells=cells))
    def test_g7_no_environment_bypass(self):
        before=os.environ.get('G7_AUTHORIZED');os.environ['G7_AUTHORIZED']='true'
        try:
            r=CrossOrientationRegistry()
            with self.assertRaises(PermissionError):r.register({'model':'western'})
            with self.assertRaises(PermissionError):r.evaluate(None)
        finally:
            if before is None:os.environ.pop('G7_AUTHORIZED',None)
            else:os.environ['G7_AUTHORIZED']=before
    def test_complete_pair_spaces_are_not_attestations(self):
        g=self.model.possibility_graph();d=self.model.possibility_graph(True)
        self.assertEqual(g.number_of_edges(),231);self.assertEqual(d.number_of_edges(),462)
        self.assertIn('NOT_ATTESTED',g.graph['evidence_status'])
    def test_native_projection_preserves_source_differences(self):
        e=self.model.encode(self.graph,Profile('audit:hebrew','Square Hebrew',self.model.baseline_hash))
        self.assertTrue(any(a['raw_ipa']=='b/v' for a in e.assignments))
        self.assertTrue(all(a['historical_support']=='NOT_VERIFIED' for a in e.assignments))
if __name__=='__main__':unittest.main()
