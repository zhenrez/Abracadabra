"""Regression: refreshing evidence cannot replace the user's operational inputs."""
import copy, importlib.util, pathlib, unittest
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('checkpoint_refresh',root/'scripts/refresh_reconstruction_checkpoint.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ContextPreservation(unittest.TestCase):
    def test_current_inputs_remain_exact_and_idempotent(self):
        state={'current_priority':'Current inline mandate — derive mathematics',
               'latest_user_priority_exact':'Get back to work. why do you keep deleting my inputs?!',
               'next_actions':['Preserve the full research history','Derive the global alignment'],
               'open_questions':['Question with its exact source conditions?'],
               'completion':'Current evidence, no completion claim',
               'extra_user_input':{'all_plugins_where_applicable':True}}
        before=copy.deepcopy(state)
        self.assertIs(module.preserve_user_context(state),state)
        self.assertEqual(state,before)
        module.preserve_user_context(state)
        self.assertEqual(state,before)
    def test_defaults_do_not_share_mutable_lists(self):
        a=module.preserve_user_context({});b=module.preserve_user_context({})
        a['next_actions'].append('retained input')
        self.assertEqual(b['next_actions'],[])
        self.assertEqual(a['open_questions'],[])
    def test_explicit_empty_inputs_are_preserved(self):
        state={'current_priority':'','next_actions':[],'open_questions':[],'completion':None}
        module.preserve_user_context(state)
        self.assertEqual(state['current_priority'],'')
        self.assertEqual(state['next_actions'],[])
        self.assertIsNone(state['completion'])

if __name__=='__main__':unittest.main()
