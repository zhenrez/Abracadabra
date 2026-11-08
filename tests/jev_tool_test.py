import importlib.util,io,json,pathlib,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('jev_tool',pathlib.Path(__file__).resolve().parents[1]/'scripts'/'jev_tool.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class JevToolChecks(unittest.TestCase):
    def setUp(self): self.request={'state':{'source':'fixture, not model output'},'questions':[{'id':'next','type':'choice','question':'Which fixture label?','options':{'a':'Fixture A','b':'Fixture B'}}]}
    def test_invalid_request_cannot_reach_network(self):
        for request in ({}, {'state':{},'questions':[]}, {'state':'x'*48001,'questions':self.request['questions']}):
            with self.assertRaises(ValueError): m.validate_request(request)
    def test_duplicate_question_ids_rejected(self):
        self.request['questions']*=2
        with self.assertRaises(ValueError): m.validate_request(self.request)
    def test_invalid_distribution_and_unknown_label_rejected(self):
        for distribution in ({'a':.9,'b':.9},{'a':float('nan'),'b':.5},{'a':.5,'c':.5}):
            with self.assertRaises(ValueError): m.validate_result(self.request,{'results':[{'answers':[{'id':'next','distribution':distribution,'value':'a'}]}]})
    def test_missing_or_duplicate_answer_rejected(self):
        with self.assertRaises(ValueError): m.validate_result(self.request,{'results':[{'answers':[]}]})
    def test_native_result_fixture_keeps_full_mass(self):
        result={'results':[{'answers':[{'id':'next','type':'choice','distribution':{'a':.6,'b':.4},'value':'a'}]}]}
        self.assertEqual(m.validate_result(self.request,result)[0]['distribution'],{'a':.6,'b':.4})
    def test_wrong_winner_type_and_truncated_state_rejected(self):
        good={'id':'next','type':'choice','distribution':{'a':.6,'b':.4},'value':'a'}
        for answer,usage in (({**good,'value':'b'},{}),({**good,'type':'boolean'},{}),(good,{'truncated_inputs':1})):
            with self.assertRaises(ValueError): m.validate_result(self.request,{'results':[{'answers':[answer]}],'usage':usage})
    def test_unexpected_model_identity_rejected(self):
        with self.assertRaises(ValueError): m.validate_info({'status':'ready','checkpoint_sha256':'0'*64})
    def test_utf8_pipe_is_exact_even_when_windows_text_encoding_is_cp1252(self):
        request={**self.request,'state':'Σοφία — Śrī ???'}
        stream=io.TextIOWrapper(io.BytesIO(json.dumps(request,ensure_ascii=False).encode('utf8')),encoding='cp1252')
        with patch.object(m.sys,'stdin',stream):
            self.assertEqual(m.read_request(pathlib.Path('-')),request)

if __name__=='__main__': unittest.main()
