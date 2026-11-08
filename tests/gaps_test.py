import importlib.util, json, pathlib, sqlite3, tempfile, unittest, sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('gap_ingest_original',ROOT/'scripts'/'ingest.py')
ingest=importlib.util.module_from_spec(spec); spec.loader.exec_module(ingest)
try:
    repair_spec=importlib.util.spec_from_file_location('gap_repair',ROOT/'scripts'/'repair_extraction_gaps.py')
    repair=importlib.util.module_from_spec(repair_spec); repair_spec.loader.exec_module(repair)
except FileNotFoundError:
    repair=None

class GapRegression(unittest.TestCase):
    def fixture(self,folder):
        source=folder/'sessions'; source.mkdir()
        records=[{'type':'session_meta','payload':{'id':'fixture','cwd':'fixture'}},
                 {'type':'response_item','payload':{'role':'assistant','content':[{'text':'before\u2028after'}]}},
                 {'type':'response_item','payload':{'role':'user','content':[{'text':'last'}]}}]
        path=source/'fixture.jsonl'; path.write_bytes(('\n'.join(json.dumps(r,ensure_ascii=False) for r in records)+'\n').encode())
        db=sqlite3.connect(':memory:'); db.executescript(ingest.SCHEMA)
        sid=ingest.stable(str(path),ingest.digest(path.read_bytes()))
        db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)',(sid,str(path),str(path),ingest.digest(path.read_bytes()),len(path.read_bytes()),'application/jsonl','local_codex_session','native_codex_imported',None))
        cid=ingest.stable(sid,'fixture')
        db.execute('INSERT INTO conversations VALUES(?,?,?,?,?,?,?,?,?)',(cid,'fixture','fixture',sid,'lines:1-',None,None,None,'{}'))
        importer=ingest.Importer(db)
        # Freeze the observed legacy failure: middle record lost, later record
        # numbered4 because str.splitlines split its predecessor at U+2028.
        importer.message(cid,'1',None,'session_meta',ingest.canonical(records[0]['payload']),sid,'line:1',None,'recorded_sequence',records[0])
        importer.message(cid,'4','1','user','last',sid,'line:4',None,'recorded_sequence',records[2])
        return db,sid,records,path

    def test_unicode_separator_record_and_locator_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            db,sid,records,original=self.fixture(pathlib.Path(tmp))
            before={r[0]:r[1:] for r in db.execute('SELECT id,text,raw_json,content_sha256,locator FROM messages')}
            self.assertEqual(len(before),2) # Actual original splitter symptom.
            if repair is not None: repair.repair_jsonl_source(db,sid,'synthetic:receipt','revise_with_history')
            self.assertEqual(db.execute('SELECT count(*) FROM messages').fetchone()[0],3)
            self.assertEqual(db.execute("SELECT count(*) FROM messages WHERE native_id LIKE 'physicalLF:%'").fetchone()[0],1)
            for mid,(text,raw,sha,old_locator) in before.items():
                current=db.execute('SELECT text,raw_json,content_sha256 FROM messages WHERE id=?',(mid,)).fetchone()
                self.assertEqual(current,(text,raw,sha))
                self.assertEqual(db.execute('SELECT previous_locator FROM source_locator_history WHERE message_id=?',(mid,)).fetchone()[0],old_locator)
            positions=db.execute('SELECT physical_lf_line,utf8_byte_start,utf8_byte_end,raw_record_sha256 FROM source_positions ORDER BY physical_lf_line').fetchall()
            self.assertEqual([p[0] for p in positions],[1,2,3])
            raw=original.read_bytes()
            for line,start,end,sha in positions:
                self.assertEqual(json.loads(raw[start:end]),records[line-1])
            first_count=db.execute('SELECT count(*) FROM source_locator_history').fetchone()[0]
            repair.repair_jsonl_source(db,sid,'synthetic:receipt','revise_with_history')
            self.assertEqual(db.execute('SELECT count(*) FROM messages').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT count(*) FROM source_locator_history').fetchone()[0],first_count)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])

    @unittest.skipIf(repair is None,'repair module not implemented yet')
    def test_duplicate_json_occurrences_keep_source_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=pathlib.Path(tmp); db,sid,_,_=self.fixture(folder)
            # Dedicated physical-LF scanner preserves identical occurrences.
            payload=b'{"x":1}\n{"x":1}\n'
            rows=list(repair.physical_records(payload))
            self.assertEqual([(x['line'],x['start'],x['end']) for x in rows],[(1,0,7),(2,8,15)])
            self.assertEqual(rows[0]['record'],rows[1]['record'])

    @unittest.skipIf(repair is None,'repair module not implemented yet')
    def test_archive_path_guard_and_array_pickle_rejection(self):
        import numpy as np
        for name in ('../escape','/root','C:/absolute','ok/../../outside','..\\escape'):
            with self.assertRaises(ValueError): repair.safe_member_name(name)
        self.assertEqual(str(repair.safe_member_name('folder/Name: File.txt')),'folder/Name%3A File.txt')
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'object.npz'; np.savez(p,unsafe=np.array([{'x':1}],dtype=object))
            with self.assertRaises(ValueError): repair.npz_metadata(p)

    @unittest.skipIf(repair is None,'repair module not implemented yet')
    def test_exact_search_sets_detect_missing_duplicate_and_orphan(self):
        with tempfile.TemporaryDirectory() as tmp:
            db,_,_,_=self.fixture(pathlib.Path(tmp))
            ids=[r[0] for r in db.execute('SELECT id FROM messages ORDER BY id')]
            db.execute('DELETE FROM search_index WHERE id=?',(ids[1],))
            db.execute('INSERT INTO search_index VALUES(?,?,?,?)',(ids[0],'message','duplicate','duplicate'))
            db.execute('INSERT INTO search_index VALUES(?,?,?,?)',('orphan','message','orphan','orphan'))
            self.assertEqual(repair.search_integrity(db),{'search_duplicate_ids':1,'messages_missing_search':1,'documents_missing_search':0,'orphan_search_ids':1})

if __name__=='__main__': unittest.main()
