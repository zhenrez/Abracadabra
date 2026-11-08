"""Synthetic historical-corpus contract; no live model or production DB writes."""
import hashlib,importlib.util,json,sqlite3,tempfile,unittest
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('intake',PROJECT/'scripts/build_background_source_queue.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class IntakeContracts(unittest.TestCase):
    def setUp(self):
        parent=PROJECT/'state/background/reactivation-20261102/support-tests';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);root=Path(self.temp.name)
        self.old=(b.ROOT,b.BASE,b.RAW);b.ROOT=root;b.BASE=root/'state/background';b.RAW=root/'data/raw/background-projections'
        (root/'data').mkdir();(root/'state/reconstruction').mkdir(parents=True)
        (root/'state/reconstruction/coverage.json').write_text('{"reconstruction_module_references":{}}')
        source=root/'data/history.md';source.write_text('Original historical fixture bytes.',encoding='utf-8')
        digest=hashlib.sha256(source.read_bytes()).hexdigest();c=sqlite3.connect(root/'data/sunny.sqlite')
        c.executescript('CREATE TABLE sources(id,path,original_path,sha256,kind);CREATE TABLE conversations(id,title);CREATE TABLE messages(id,native_id,conversation_id,role,text,content_sha256,source_id,locator,create_time,branch_status);CREATE VIRTUAL TABLE search_index USING fts5(id UNINDEXED,title,text);')
        c.execute('INSERT INTO sources VALUES(?,?,?,?,?)',('historic',str(source),str(source),digest,'supplied_archive_member'))
        c.execute('INSERT INTO sources VALUES(?,?,?,?,?)',('generated',str(source),str(source),digest,'local_codex_session'))
        c.execute('INSERT INTO conversations VALUES(?,?)',('c','Music and Calendars'))
        texts=[('user1','user','Completed Harmony TOL adapter compares Western and Chinese music.','historic'),('userduplicate','user','Completed Harmony TOL adapter compares Western and Chinese music.','generated'),('assistant1','assistant','Completed Harmony TOL adapter compares Western and Chinese music.','historic'),('oversized','assistant','calendar '+('long '*4000),'historic'),('generated','assistant','Aramaic phonetics generated tool log.','generated')]
        for mid,role,text,sid in texts:
            sha=hashlib.sha256(text.encode()).hexdigest();c.execute('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?,?)',(mid,mid,'c',role,text,sha,sid,'lines:1-2','2026-10-01','fixture'))
            c.execute('INSERT INTO search_index VALUES(?,?,?)',(mid,'Music and Calendars',text))
        c.commit();c.close()
    def tearDown(self):b.ROOT,b.BASE,b.RAW=self.old;self.temp.cleanup()
    def test_duplicate_roles_original_refs_and_oversized_preserved(self):
        x=b.build(1,quiet=True)
        self.assertEqual(x['unique_text_role_groups'],3);self.assertEqual(x['message_occurrences'],4)
        self.assertEqual(x['eligible_bounded_groups'],2)
        self.assertEqual(len(x['queued_jobs']),1)
        users=next(r for r in x['records'] if r['source_role']=='user')
        self.assertEqual(users['occurrence_count'],2)
        manifest=json.loads((b.ROOT/users['occurrence_manifest']).read_text())
        self.assertEqual({o['source_kind'] for o in manifest['occurrences']},{'local_codex_session','supplied_archive_member'})
        oversized=next(r for r in x['records'] if r['characters']>16000)
        self.assertIn('pending_oversized',oversized['status']);self.assertEqual(len((b.ROOT/oversized['projection_path']).read_text()),oversized['characters'])
    def test_next_packet_never_requeues_existing_source_role(self):
        a=b.build(1,quiet=True);second=b.build(1,quiet=True);third=b.build(1,quiet=True)
        self.assertEqual(len(second['queued_jobs']),1);self.assertEqual(third['queued_jobs'],[])
        self.assertNotEqual(a['queued_jobs'][0]['id'],second['queued_jobs'][0]['id'])
    def test_immutable_projection_rejects_changed_bytes(self):
        x=b.build(0,quiet=True);path=b.ROOT/x['records'][0]['projection_path'];path.write_bytes(b'tamper')
        with self.assertRaisesRegex(ValueError,'immutable projection collision'):b.build(0,quiet=True)

if __name__=='__main__':unittest.main(verbosity=2)
