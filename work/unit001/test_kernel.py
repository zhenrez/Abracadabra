import unittest
from kernel import *
from evidence import import_matrix
from pathlib import Path

class KernelTests(unittest.TestCase):
    def test_T01_matrix(self):
        graph=import_matrix((Path(__file__).parent/'frozen/source/matrix-message.txt').read_bytes(),'current-chat')
        store=migrate_matrix(graph)
        self.assertEqual(sum(isinstance(x,EvidenceObservation) for x in store.records),540)
        witness=graph.witnesses[0]
        self.assertEqual(set(store.provenance(witness.record_id)),
                         {witness.record_id,witness.raw_cell_id,graph.source.artifact_id,*witness.claim_refs})
    def test_T02_to_T12_representability(self):
        for name,store in schema_fixtures().items():
            with self.subTest(fixture=name):
                store.validate();self.assertEqual(store.to_json(),KernelStore.from_json(store.to_json()).to_json())
                self.assertTrue(all(s.authority=='SYNTHETIC_SCHEMA_FIXTURE' for s in store.records if isinstance(s,SourceArtifact)))
        self.assertEqual(len(schema_fixtures()),11)
    def test_append_only_and_refs(self):
        store=next(iter(schema_fixtures().values()))
        with self.assertRaises(ValueError):store.append(store.records[0])
        with self.assertRaises(ValueError):store.append(EvidenceClaim('bad','missing','p',1,'INFERRED',('missing',)))
    def test_nested_immutable(self):
        source={'x':[{'y':1}]};o=EvidenceObservation('o','s','test',source,{})
        source['x'][0]['y']=2;self.assertEqual(o.value['x'][0]['y'],1)
        with self.assertRaises(TypeError):o.value['x'][0]['y']=3
    def test_missing_states(self):self.assertEqual(len(set(DataState)),12)
    def test_operator_and_claim_separate(self):
        op=OperatorSpecification('op','letter','letter','C22','C22',{},(), 'identity',False,True,True,('identity',),'exact','v1',())
        registry=OperatorRegistry();registry=registry.register(op)
        self.assertEqual(registry.definitions,(op,))
        with self.assertRaises(PermissionError):registry.execute('op',None)
    def test_exposure_cannot_be_blind(self):
        with self.assertRaises(ValueError):ExperimentReceipt('trial','target',(),(),('already_seen',),'v1',{},'unsealed',{},(),(),False,{},(), 'HISTORICAL_HOLDOUT')
if __name__=='__main__':unittest.main()
