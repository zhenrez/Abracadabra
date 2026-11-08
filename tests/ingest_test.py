import importlib.util, json, pathlib, sqlite3, tempfile, unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('ingest', pathlib.Path(__file__).resolve().parents[1]/'scripts'/'ingest.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ImportChecks(unittest.TestCase):
    def test_archive_paths(self):
        for name in ('../escape','/absolute','C:/escape','ok/../../escape','..\\escape'):
            with self.assertRaises(ValueError): m.safe_zip_name(name)
        self.assertEqual(str(m.safe_zip_name('folder/Title: Sound.docx')),'folder/Title%3A Sound.docx')
        self.assertNotEqual(str(m.safe_zip_name('Title%3A Sound')),str(m.safe_zip_name('Title: Sound')))

    def test_branches_and_provenance(self):
        db=sqlite3.connect(':memory:'); db.executescript(m.SCHEMA)
        db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)',('s','p','p','a'*64,1,'application/json','test','preserved',None))
        i=m.Importer(db)
        def node(parent,text,role): return {'parent':parent,'message':{'author':{'role':role},'content':{'parts':[text]}}}
        i.export('s',[{'id':'c','title':'test','current_node':'b','mapping':{'a':node(None,'must preserve','user'),'b':node('a','current','assistant'),'c':node('a','alternate','assistant'),'empty':{'parent':'b','message':None}}}])
        self.assertEqual(db.execute('SELECT branch_status,text FROM messages ORDER BY text').fetchall(),[('alternate','alternate'),('current','current'),('current','must preserve')])
        self.assertEqual(db.execute('SELECT count(*) FROM nodes').fetchone()[0],4)
        self.assertEqual(db.execute('SELECT status FROM decisions').fetchone()[0],'extracted_unreviewed')
        self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_actual_codex_import_preserves_unicode_separators_and_exact_byte_positions(self):
        records=[{'type':'session_meta','payload':{'id':'fixture-native','cwd':'fixture'}},{'type':'response_item','payload':{'role':'user','content':[{'text':'Σοφία\u2028retained'}]}},{'type':'response_item','payload':{'role':'assistant','content':[{'text':'Śrī\u2029unchanged'}]}}]
        raw=('\n'.join(json.dumps(r,ensure_ascii=False) for r in records)+'\n').encode('utf8')
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder); source=root/'sessions'; source.mkdir(); (source/'fixture.jsonl').write_bytes(raw)
            db=sqlite3.connect(':memory:'); db.executescript(m.SCHEMA)
            with patch.object(m,'ROOT',root): m.Importer(db).codex(source,'')
            self.assertEqual(db.execute('SELECT count(*) FROM messages').fetchone()[0],3)
            self.assertIn('Σοφία\u2028retained',[r[0] for r in db.execute('SELECT text FROM messages')])
            positions=db.execute('SELECT physical_lf_line,utf8_byte_start,utf8_byte_end FROM source_positions ORDER BY physical_lf_line').fetchall()
            self.assertEqual(len(positions),3)
            for line,start,end in positions: self.assertEqual(json.loads(raw[start:end]),records[line-1])
            self.assertTrue(all(r[0].startswith('physicalLF:') for r in db.execute('SELECT native_id FROM messages')))
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])

if __name__=='__main__': unittest.main()
