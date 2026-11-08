from pathlib import Path
import hashlib,json,tempfile,unittest

ROOT=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()

class SnapshotCopyTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT/'snapshot_copy.py').exists(),'Source-preserving snapshot copier is absent')
        import snapshot_copy
        self.api=snapshot_copy
        self.temporary=tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.workspace=Path(self.temporary.name)/'workspace';self.workspace.mkdir()
        self.destination=self.workspace/'work/github-delivery-fixture/checkout'
        self.control=self.workspace/'work/github-delivery-fixture/control';self.control.mkdir(parents=True)
    def source(self,path,raw=b'authored work\n'):
        target=self.workspace/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);return target
    def document(self,name,value):
        target=self.control/name;target.write_text(json.dumps(value),encoding='utf-8');return target
    def inputs(self,paths):
        candidates=self.control/'include.jsonl';candidates.write_text(''.join(json.dumps({'path':p,'category':'PROJECT_AUTHORED_PRODUCT'})+'\n' for p in paths),encoding='utf-8')
        preflight=self.document('preflight.json',{'files':[{'path':p,'sha256':sha((self.workspace/p).read_bytes()),'status':'APPROVED'} for p in paths]})
        return candidates,preflight
    def copy(self,paths,**options):
        candidates,preflight=self.inputs(paths)
        return self.api.snapshot_copy(self.workspace,self.destination,candidates,preflight,**options)
    def test_approved_bytes_and_portable_manifest(self):
        original=self.source('src/main.txt',b'Exact \xe2\x84\x8f bytes\r\n')
        result=self.copy(['src/main.txt'])
        self.assertEqual((self.destination/'src/main.txt').read_bytes(),original.read_bytes())
        self.assertEqual(result['files'][0]['source_sha256'],sha(original.read_bytes()))
        self.assertNotIn(str(self.workspace),json.dumps(result))
        self.assertEqual(result['status'],'COMPLETE')
    def test_manifest_cannot_be_overwritten(self):
        self.source('src/main.txt');self.copy(['src/main.txt'])
        manifest=self.destination/'PUBLICATION_MANIFEST.json';before=manifest.read_bytes()
        with self.assertRaises(ValueError):self.copy(['src/main.txt'])
        self.assertEqual(manifest.read_bytes(),before)
    def test_unapproved_and_changed_source_rejected(self):
        self.source('src/main.txt');c,p=self.inputs(['src/main.txt'])
        approval=json.loads(p.read_text());approval['files'][0]['status']='UNREVIEWED';p.write_text(json.dumps(approval))
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p)
        c,p=self.inputs(['src/main.txt']);(self.workspace/'src/main.txt').write_bytes(b'changed after review')
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p)
        self.assertFalse((self.destination/'src/main.txt').exists())
    def test_unsafe_candidate_paths_rejected(self):
        for value in ('../outside.txt','/absolute.txt','C:/outside.txt','a\\b.txt','.git/config','src/.git/config',
                      'work/github-delivery-any/loop.txt','work/publication/parts.txt','src//a.txt','src/./a.txt'):
            with self.subTest(value=value),self.assertRaises(ValueError):self.api.safe_relative(value)
    def test_destination_root_and_outside_workspace_rejected(self):
        self.source('src/main.txt');c,p=self.inputs(['src/main.txt'])
        for destination in (self.workspace,self.workspace.parent/'outside'):
            with self.subTest(destination=str(destination)),self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,destination,c,p)
    def test_existing_file_collision_even_if_identical(self):
        source=self.source('src/main.txt');target=self.destination/'src/main.txt';target.parent.mkdir(parents=True);target.write_bytes(source.read_bytes())
        with self.assertRaises(ValueError):self.copy(['src/main.txt'])
        self.assertEqual(target.read_bytes(),source.read_bytes())
    def test_explicit_exclusion_reason_is_local_only(self):
        self.source('reviewed/a.txt');self.source('reviewed/private.txt')
        exclusion=self.document('exclusions.json',{'files':[{'path':'reviewed/private.txt','reason':'Hold for privacy review'}]})
        result=self.copy(['reviewed/a.txt','reviewed/private.txt'],exclusions=exclusion)
        self.assertEqual(len(result['files']),1)
        self.assertNotIn('reviewed/private.txt',json.dumps(result))
        self.assertFalse((self.destination/'reviewed/private.txt').exists())
        updates=list(self.control.glob('exclusion-updates.*.LOCAL-ONLY.json'))
        self.assertEqual(len(updates),1);self.assertEqual(json.loads(updates[0].read_text())['excluded'][0]['reason'],'Hold for privacy review')
    def test_source_fixture_promotion_still_needs_approval(self):
        self.source('src/main.txt');self.source('data/reviewed-source.txt',b'licensed fixture')
        c,p=self.inputs(['src/main.txt'])
        promoted=self.document('promotions.json',{'files':[{'path':'data/reviewed-source.txt','category':'SOURCE_FIXTURE_PROMOTION','reason':'Explicitly reviewed source fixture'}]})
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p,promotions=promoted)
        approval=json.loads(p.read_text());approval['files'].append({'path':'data/reviewed-source.txt','sha256':sha(b'licensed fixture'),'status':'APPROVED'});p.write_text(json.dumps(approval))
        result=self.api.snapshot_copy(self.workspace,self.destination,c,p,promotions=promoted)
        self.assertEqual(len(result['files']),2)
    def test_keep_approved_destination_preserves_original_source_bytes(self):
        original=self.source('README.md',b'original project readme')
        target=self.destination/'README.md';target.parent.mkdir(parents=True);target.write_bytes(b'public reviewed overview')
        adaptation=self.document('adaptations.json',{'files':[{'path':'README.md','mode':'KEEP_APPROVED_DESTINATION',
            'destination_sha256':sha(target.read_bytes()),'reason':'Explicit destination-only public overview'}]})
        result=self.copy(['README.md'],adaptations=adaptation)
        record=result['files'][0]
        self.assertEqual(target.read_bytes(),b'public reviewed overview')
        self.assertEqual((self.destination/record['source_snapshot_path']).read_bytes(),original.read_bytes())
        self.assertEqual(original.read_bytes(),b'original project readme')
    def test_only_root_readme_gitignore_may_be_adapted(self):
        self.source('src/main.txt')
        adaptation=self.document('adaptations.json',{'files':[{'path':'src/main.txt','mode':'KEEP_APPROVED_DESTINATION','destination_sha256':'0'*64,'reason':'Not permitted'}]})
        with self.assertRaises(ValueError):self.copy(['src/main.txt'],adaptations=adaptation)
    def test_duplicate_candidate_identity_rejected(self):
        self.source('src/main.txt');c,p=self.inputs(['src/main.txt','src/main.txt'])
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p)
    def test_empty_exclusion_reason_rejected(self):
        self.source('src/main.txt');exclusion=self.document('exclusions.json',{'files':[{'path':'src/main.txt','reason':''}]})
        with self.assertRaises(ValueError):self.copy(['src/main.txt'],exclusions=exclusion)
    def test_reparse_guard_is_checked(self):
        from unittest.mock import patch
        self.source('src/main.txt');c,p=self.inputs(['src/main.txt'])
        original=self.api.is_reparse
        def flagged(path):return Path(path).name=='src' or original(path)
        with patch.object(self.api,'is_reparse',side_effect=flagged),self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p)
    def test_manifest_cannot_target_git_metadata(self):
        self.source('src/main.txt');c,p=self.inputs(['src/main.txt'])
        with self.assertRaises(ValueError):
            self.api.snapshot_copy(self.workspace,self.destination,c,p,manifest=self.destination/'.git/config')
        self.assertFalse((self.destination/'src/main.txt').exists())
    def test_exclusion_log_must_stay_local_before_any_copy(self):
        self.source('src/main.txt');self.source('src/held.txt')
        c,p=self.inputs(['src/main.txt','src/held.txt'])
        self.destination.mkdir(parents=True)
        inside=self.destination/'preflight.json';inside.write_bytes(p.read_bytes())
        exclusion=self.document('exclusions.json',{'files':[{'path':'src/held.txt','reason':'Hold local'}]})
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,inside,exclusions=exclusion)
        self.assertFalse((self.destination/'src/main.txt').exists())
    def test_destination_parent_file_conflict_precedes_any_copy(self):
        self.source('src/main.txt');self.source('blocked/child.txt');c,p=self.inputs(['src/main.txt','blocked/child.txt'])
        self.destination.mkdir(parents=True);(self.destination/'blocked').write_bytes(b'existing file')
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p)
        self.assertFalse((self.destination/'src/main.txt').exists())
    def test_planned_prefix_collision_with_intervening_name_rejected(self):
        self.source('a');self.source('a-b');c,p=self.inputs(['a','a-b'])
        with self.assertRaises(ValueError):self.api.snapshot_copy(self.workspace,self.destination,c,p,manifest=self.destination/'a/receipt.json')
        self.assertFalse((self.destination/'a').exists())

if __name__=='__main__':unittest.main()
