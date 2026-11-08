from pathlib import Path
import importlib.util,json,tempfile,unittest

ROOT=Path(__file__).resolve().parent

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT/'build_dashboard.py').exists(),'Source-preserving dashboard builder is absent')
        import build_dashboard
        self.builder=build_dashboard
    def fixture(self):
        return {'counts':{'positions':2,'populated':1,'empty':1},'matrix':[
            {'script':'Test','ordinal':1,'glyph':'<script>alert(1)</script>','ipa':'?','english':'unknown',
             'phonetic_type':'UNKNOWN_VALUE','proxy':True,'record_id':'a'},
            {'script':'Test','ordinal':2,'glyph':'','ipa':'','english':'','phonetic_type':'UNKNOWN_VALUE','proxy':False,'record_id':'b'}],
            'native':{},'coding':{},'comparisons':[],'gates':{'G7':'LOCKED'},'requirements':[],
            'source_links':[],'limitations':['Historical reconstruction not verified']}
    def test_exact_payload_roundtrip_and_script_escaping(self):
        value=self.fixture();text=self.builder.render(value,{'status':'READY','sha256':'test'})
        embedded=text.split('<script id="evidence-data" type="application/json">',1)[1].split('</script>',1)[0]
        self.assertEqual(json.loads(embedded),value)
        self.assertNotIn('<script>alert(1)</script>',text)
        self.assertIn('\\u003cscript',text)
    def test_builder_preserves_original_source_bytes(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            path=Path(temporary);source=path/'input.json';raw=json.dumps(self.fixture(),ensure_ascii=False,indent=3).encode('utf-8')
            source.write_bytes(raw)
            receipt=self.builder.build(source,path/'workbench.html')
            self.assertEqual(receipt['status'],'READY')
            self.assertEqual((path/'dashboard-data.snapshot.json').read_bytes(),raw)
            self.assertTrue((path/'workbench.html').exists())
    def test_missing_data_is_explicit_without_invented_counts(self):
        text=self.builder.render(None,{'status':'WAITING_FOR_SOURCE','message':'Source not available'})
        self.assertIn('Waiting for the evidence file',text)
        self.assertNotIn('381 observations',text)
    def test_count_mismatch_is_rejected(self):
        value=self.fixture();value['counts']['positions']=3
        with self.assertRaises(ValueError):self.builder.validate(value)
    def test_every_requested_surface_is_available(self):
        text=self.builder.render(self.fixture(),{'status':'READY'})
        for key in ('evidence','models','compression','relationships','delivery'):
            self.assertIn('id="panel-'+key+'"',text)
        self.assertIn('download-data',text)
        self.assertIn('aria-live',text)
        self.assertIn('Historical reconstruction',text)
    def test_current_assessment_is_separate_from_original_audit(self):
        value=self.fixture();value['requirements']=[{'id':'EG5','status':'NOT_IMPLEMENTED_AT_AUDIT','requirement':'Controls'}]
        current={'requirements':[{'original':value['requirements'][0],
                                 'engineering_assessment':{'status':'PASSED_SOURCE_DEFINED_CONTROLS'}}]}
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            folder=Path(temporary);source=folder/'input.json';source.write_text(json.dumps(value),encoding='utf-8')
            assessment=folder/'current-deliverables.json';assessment.write_text(json.dumps(current),encoding='utf-8')
            receipt=self.builder.build(source,folder/'workbench.html',assessment_source=assessment)
            text=(folder/'workbench.html').read_text(encoding='utf-8')
            embedded=json.loads(text.split('<script id="evidence-data" type="application/json">',1)[1].split('</script>',1)[0])
            self.assertEqual(embedded['requirements'],value['requirements'])
            self.assertEqual(embedded['current_delivery']['requirements'][0]['engineering_assessment']['status'],'PASSED_SOURCE_DEFINED_CONTROLS')
            self.assertIn('current_delivery_sha256',receipt)
            self.assertEqual(json.loads((folder/'dashboard-data.snapshot.json').read_bytes()),value)
            self.assertEqual((folder/'current-deliverables.snapshot.json').read_bytes(),assessment.read_bytes())
    def test_source_bound_sefer_view_is_available(self):
        text=self.builder.render(self.fixture(),{'status':'READY'})
        self.assertIn('data-model="sefer"',text)
        self.assertIn('Sefer',text)

if __name__=='__main__':unittest.main()
