"""Byte-preservation and hostile-path tests using small temporary fixtures only."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,tempfile,unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
def module(name,filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/filename);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
pack=module('source_packer','package-large-sources.py');restore=module('source_restorer','restore-large-sources.py')

class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.owned=ROOT/'work/publication/large';self.owned.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='fixture-',dir=self.owned);self.root=Path(self.temp.name).resolve()
        assert self.root.is_relative_to(self.owned.resolve())
        self.payload=self.root/'payload';self.manifest_path=self.root/'manifest.json';self.output=self.root/'restored';self.output.mkdir()
        self.bytes=os.urandom(90000)+b'\x00literal\xff\n'*1000
        self.source=self.root/'sources/original.bin';self.source.parent.mkdir();self.source.write_bytes(self.bytes)
    def tearDown(self):
        assert self.root.is_relative_to(self.owned.resolve());self.temp.cleanup()
    def packaged(self,paths=None):return pack.package_files(self.root,paths or ['sources/original.bin'],self.payload,self.manifest_path,part_bytes=4096)
    def restore(self,m,**kwargs):return restore.restore(m,self.root,self.output,self.payload,**kwargs)
    def test_streaming_cross_part_roundtrip_preserves_original(self):
        before=self.source.stat().st_mtime_ns;m=self.packaged();row=m['files'][0]
        self.assertGreater(row['partCount'],2);self.assertTrue(all(p['bytes']<=4096 for p in row['parts']))
        result=self.restore(m);self.assertEqual(result['status'],'verified');self.assertEqual((self.output/'sources/original.bin').read_bytes(),self.bytes)
        self.assertEqual(self.source.read_bytes(),self.bytes);self.assertEqual(self.source.stat().st_mtime_ns,before)
    def test_existing_matching_file_is_not_replaced(self):
        m=self.packaged();self.restore(m);path=self.output/'sources/original.bin';before=(path.stat().st_ino,path.stat().st_mtime_ns)
        result=self.restore(m);self.assertEqual(result['files'][0]['status'],'already-present-and-verified');self.assertEqual((path.stat().st_ino,path.stat().st_mtime_ns),before)
    def test_repeated_pack_preserves_completed_manifest(self):
        self.packaged();before=self.manifest_path.read_bytes()
        with self.assertRaises(FileExistsError):self.packaged()
        self.assertEqual(self.manifest_path.read_bytes(),before)
    def test_existing_mismatching_user_bytes_are_preserved(self):
        m=self.packaged();path=self.output/'sources/original.bin';path.parent.mkdir();path.write_bytes(b'USER BYTES')
        with self.assertRaises(FileExistsError):self.restore(m)
        self.assertEqual(path.read_bytes(),b'USER BYTES')
    def test_corrupted_part_rejects_without_target_or_partial_file(self):
        m=self.packaged();row=m['files'][0];path=self.payload/row['originalSha256']/'part-0002.gzpart';b=bytearray(path.read_bytes());b[20]^=1;path.write_bytes(b)
        with self.assertRaises((ValueError,OSError,EOFError)):self.restore(m)
        self.assertFalse((self.output/'sources/original.bin').exists());self.assertFalse(list(self.output.rglob('*.partial')))
    def test_gzip_and_decompressed_lengths_are_independently_checked(self):
        m=self.packaged();bad=copy.deepcopy(m);bad['files'][0]['gzipSha256']='0'*64
        with self.assertRaises(restore.IntegrityError):self.restore(bad)
        bad=copy.deepcopy(m);bad['files'][0]['originalBytes']-=1
        with self.assertRaises(restore.IntegrityError):self.restore(bad)
    def test_output_and_payload_path_traversal_are_rejected(self):
        m=self.packaged()
        for path in ['../escape.bin','/escape.bin','C:/escape.bin','a\\escape.bin','a//b','a/../b','a/NUL.bin','a/file.','a/file:stream']:
            bad=copy.deepcopy(m);bad['files'][0]['sourcePath']=path
            with self.subTest(path=path),self.assertRaises(ValueError):self.restore(bad)
        bad=copy.deepcopy(m);bad['files'][0]['parts'][0]['repositoryPath']='../outside.gzpart'
        with self.assertRaises(ValueError):self.restore(bad)
    def test_identical_content_aliases_keep_both_paths_and_one_payload(self):
        second=self.root/'sources/alias.bin';second.write_bytes(self.bytes);m=self.packaged(['sources/original.bin','sources/alias.bin'])
        self.assertEqual(m['files'][1]['samePayloadAs'],'sources/original.bin');self.assertEqual(m['uniquePartCount'],m['files'][0]['partCount'])
        self.restore(m);self.assertEqual((self.output/'sources/alias.bin').read_bytes(),self.bytes)
        a=self.output/'sources/original.bin';b=self.output/'sources/alias.bin';self.assertNotEqual(a.stat().st_ino,b.stat().st_ino)
    def test_case_alias_output_is_rejected(self):
        m=self.packaged();row=copy.deepcopy(m['files'][0]);row['sourcePath']='SOURCES/ORIGINAL.BIN';m['files'].append(row);m['fileCount']=2
        with self.assertRaises(ValueError):self.restore(m)
    def test_existing_file_appearing_mid_restore_is_never_replaced(self):
        m=self.packaged();target=self.output/'sources/original.bin'
        def appeared(source,destination,**kwargs):Path(destination).write_bytes(b'CONCURRENT USER FILE');raise FileExistsError()
        with mock.patch.object(restore.os,'link',side_effect=appeared),self.assertRaises(FileExistsError):self.restore(m)
        self.assertEqual(target.read_bytes(),b'CONCURRENT USER FILE');self.assertFalse(list(self.output.rglob('*.partial')))
    def test_smaller_parts_retain_exact_gzip_stream_and_original(self):
        m=self.packaged();before=m['files'][0]['gzipSha256'];m=pack.rechunk_manifest(self.manifest_path,self.payload,2048)
        self.assertEqual(m['files'][0]['gzipSha256'],before);self.assertTrue(all(p['bytes']<=2048 for p in m['files'][0]['parts']))
        self.restore(m);self.assertEqual((self.output/'sources/original.bin').read_bytes(),self.bytes)
    def test_sqlite_wal_is_reported_without_opening_or_mutation(self):
        path=self.root/'sources/raw.sqlite';path.write_bytes(self.bytes);wal=Path(str(path)+'-wal');wal.write_bytes(b'fixtureWAL')
        m=self.packaged(['sources/raw.sqlite']);note=m['files'][0]['sqlite'];self.assertTrue(note['sidecarsBefore']['-wal']['exists']);self.assertIn('NOT established',note['assessment'])
        self.assertFalse(note['databaseOpenedBySQLite']);self.assertEqual(wal.read_bytes(),b'fixtureWAL')
    def test_symlink_parent_cannot_escape_output_root(self):
        m=self.packaged();outside=self.root/'outside';outside.mkdir()
        try:(self.output/'sources').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('Symlink creation unavailable for this account')
        with self.assertRaises(ValueError):self.restore(m)
        self.assertFalse((outside/'original.bin').exists())

if __name__=='__main__':unittest.main(verbosity=2)
