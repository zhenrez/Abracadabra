"""Bounded contract tests. Stubbed classifications are explicitly synthetic."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('worker',ROOT/'scripts/background_reconstruction.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class BackgroundContracts(unittest.TestCase):
    def setUp(self):
        parent=ROOT/'state/background/reactivation-20261102/support-tests';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.base=Path(self.temp.name)
        self.source=self.base/'source.md';self.source.write_bytes(b'User evidence.\r\nR=2/3; L=3/4; O=1/2.\r\n')
        self.source_spec=dict(path=self.source.relative_to(ROOT).as_posix(),sha256=w.sha(self.source.read_bytes()),start_line=2,end_line=2,source_role='synthetic-test-data')
        self.job=dict(id='contract-fixture',kind='source_forensics',sources=[self.source_spec],hypotheses=[dict(id='r-law',statement='R=2/3 is stated.')])
    def tearDown(self):self.temp.cleanup()
    def test_hash_line_range_and_newlines(self):
        span=w.validate_job(self.job)[0];self.assertEqual(span['quote'],'R=2/3; L=3/4; O=1/2.\r\n');self.assertEqual(span['start_offset'],16)
        self.source.write_text('changed',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):w.validate_job(self.job)
    def test_path_traversal_and_unbounded_inputs_rejected(self):
        for p in ('../../outside.md','C:/Windows/win.ini','.git/config'):
            with self.assertRaises(ValueError):w.source_path(p)
        self.job['sources']*=9
        with self.assertRaises(ValueError):w.validate_job(self.job)
    def test_proofline_actual_projection_and_tamper(self):
        proof=w.module(w.PROOFLINE,'test_proofline');package,receipt=w.proof_package(w.read_span(self.source_spec),proof)
        self.assertTrue(receipt)
        package['payload']['citations'][0]['quote']='tampered'
        with self.assertRaises(Exception):proof.verify(package)
    def test_no_jev_no_host_substitute(self):
        def unavailable(*a,**k):return dict(status='unavailable')
        with self.assertRaisesRegex(RuntimeError,'no host classification'):w.run_job(self.job,self.base/'failed',unavailable)
        self.assertFalse((self.base/'failed/result.json').exists())
    def test_synthetic_candidate_preserves_exact_sources(self):
        def synthetic(*a,**k):return dict(status='judged',answers={'r-law':{'winner':'supports','fixture_only':True}})
        result=w.run_job(self.job,self.base/'run',synthetic)
        self.assertEqual(result['source_records'][0]['source']['quote_sha256'],w.sha(b'R=2/3; L=3/4; O=1/2.\r\n'))
        self.assertEqual(result['status'],'candidate_source_reconstruction')
    def test_declared_exact_probe_collision_and_rejection(self):
        self.job.update(kind='exact_operator_probe',probe=dict(operator_frame='TOL-R=2/3-L=3/4-O=1/2',operator_source_index=0,operator_quote='R=2/3; L=3/4; O=1/2.',words=['RL','LR','O','RR']))
        w.validate_job(self.job)
        out=w.exact_probe(self.job)
        self.assertEqual(out['scalar_collisions'],[dict(ratio='1/2',distinct_words=['LR','O','RL'])])
        self.job['probe']['words'].append('os.system("bad")')
        with self.assertRaises(ValueError):w.exact_probe(self.job)
    def test_operator_math_needs_literal_source_binding(self):
        self.job.update(kind='exact_operator_probe',probe=dict(operator_frame='TOL-R=2/3-L=3/4-O=1/2',operator_source_index=0,operator_quote='invented',words=['RL','LR']))
        with self.assertRaisesRegex(ValueError,'bind a supplied source'):w.validate_job(self.job)
    def test_exclusive_process_lock(self):
        with w.exclusive_lock(self.base/'lease'):
            with self.assertRaises(RuntimeError):
                with w.exclusive_lock(self.base/'lease'):pass
        with w.exclusive_lock(self.base/'lease'):pass
    def test_model_budget_persists_across_restart_without_live_call(self):
        budget=w.ModelBudget(self.base,maximum=2);self.assertEqual(budget.remaining,2)
        budget.state['reserved_or_completed_requests']=2;w.save(budget.path,budget.state)
        restarted=w.ModelBudget(self.base,maximum=256);self.assertEqual(restarted.remaining,0)
        with self.assertRaisesRegex(RuntimeError,'budget exhausted'):restarted.decide({})

if __name__=='__main__':unittest.main(verbosity=2)
