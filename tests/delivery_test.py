"""Focused data-preservation and loopback decision-scope checks."""
import importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from delivery_server import asset_path,decision_payload

class DeliveryTests(unittest.TestCase):
    def test_data_preserves_declared_graph_and_goals(self):
        data=json.loads((ROOT/'web/delivery-2026-11-07/data.json').read_text(encoding='utf8'))
        native=json.loads((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_text(encoding='utf8'))
        self.assertEqual(data['graph']['entities'],native['entities'])
        self.assertEqual(data['graph']['relationships'],native['relationships'])
        self.assertEqual(len(data['goals']),16);self.assertEqual(len(data['registers']),8)
        self.assertFalse(data['evidenceStatus']['globalOrientationSelected'])
        anchors=json.loads((ROOT/'state/reconstruction/score-anchor-constraints.json').read_text(encoding='utf8'))
        self.assertEqual(data['modules']['score-anchor-constraints'],anchors)
        for output in data['registers']:
            self.assertIn('score-anchor-constraints',output['units'])
            self.assertTrue(all(unit in data['modules'] for unit in output['units']))
    def test_assets_cannot_escape_delivery(self):
        for value in ['/../state/task.json','/%2e%2e/%2e%2e/AGENTS.md','/C:/secret.json','/..\\secret.json','/x.py']:
            with self.assertRaises(ValueError):asset_path(value)
        self.assertEqual(asset_path('/').name,'index.html')
    def test_api_cannot_select_external_provider_or_run_commands(self):
        valid={'state':'Finite supplied source comparison','questions':[{'id':'x','type':'choice','question':'Which value is supplied?','options':['a','b']}]}
        self.assertEqual(decision_payload(valid),valid)
        for patch in [{'provider':'typesafe'},{'endpoint':'https://example.com'},{'command':'arbitrary'}]:
            with self.assertRaises(ValueError):decision_payload({**valid,**patch})
        with self.assertRaises(ValueError):decision_payload({'state':'x','questions':[]})
        with self.assertRaises(ValueError):decision_payload({**valid,'state':{'bad':float('inf')}})

if __name__=='__main__':unittest.main()
