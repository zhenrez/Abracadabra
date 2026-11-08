import dataclasses,unittest
from kernel import *
from evidence import import_matrix,validate_graph
from pathlib import Path

class ListCompletionTests(unittest.TestCase):
    def test_derivation_provenance(self):
        s=SourceArtifact.from_bytes('s',b'original','fixture','SYNTHETIC_SCHEMA_FIXTURE')
        o=EvidenceObservation('o','s','test',1,{})
        d=DerivationRecord('d',('s',),('o',),'identity','v1',{},'fixture')
        self.assertEqual(set(KernelStore((s,o,d)).provenance('d')),{'s','o','d'})
    def test_source_lineage_provenance(self):
        a=SourceArtifact.from_bytes('a',b'old','fixture','SYNTHETIC_SCHEMA_FIXTURE')
        b=SourceArtifact.from_bytes('b',b'copy','fixture','SYNTHETIC_SCHEMA_FIXTURE',lineage=('a',))
        self.assertEqual(set(KernelStore((a,b)).provenance('b')),{'a','b'})
    def test_unknown_mutable_container_rejected(self):
        with self.assertRaises(TypeError):EvidenceObservation('o','s','test',bytearray(b'x'),{})
    def test_source_encoding(self):
        s=SourceArtifact.from_bytes('s',b'\xff\x00','fixture','SYNTHETIC_SCHEMA_FIXTURE')
        self.assertEqual(s.encoding,'binary')
    def test_serialized_source_encoding_cannot_lie(self):
        source=SourceArtifact.from_bytes('s',b'\xff\x00','fixture','SYNTHETIC_SCHEMA_FIXTURE')
        with self.assertRaises(ValueError):KernelStore((dataclasses.replace(source,encoding='utf-8'),)).validate()
    def test_T04_two_partitions_share_all_22_identities(self):
        store=schema_fixtures()['T04']
        record=next(r for r in store.records if isinstance(r,DomainRecord))
        identities=set(record.properties['letter_ids'])
        self.assertEqual(len(identities),22)
        for classification,count in (('sefer',3),('articulatory',5)):
            groups=record.properties['classifications'][classification]
            self.assertEqual(len(groups),count)
            members=[letter for group in groups.values() for letter in group]
            self.assertEqual(len(members),22);self.assertEqual(set(members),identities)
    def test_T06_alternative_has_separate_source(self):
        store=schema_fixtures()['T06']
        sources=[r for r in store.records if isinstance(r,SourceArtifact)]
        self.assertEqual(len(sources),2)
        domain=next(r for r in store.records if isinstance(r,DomainRecord))
        self.assertTrue({r.record_id for r in sources}<=set(store.provenance(domain.record_id)))
    def test_experiment_records_selection_and_candidates(self):
        receipt=ExperimentReceipt('trial','target',(),('same-artifact-family',),('already-exposed',),'frozen-v1',
            {},'unsealed',{'score':'exact'},('no advantage',),('unrelated control',),True,{'evaluated':False},(),
            'KNOWN_ORIGINALS',selection_method='source-identified engineering control',
            candidate_set_results={'status':'NOT_EVALUATED','candidates':[]})
        store=KernelStore((receipt,))
        self.assertEqual(KernelStore.from_json(store.to_json()),store)
        self.assertTrue(receipt.abstention)
        with self.assertRaises(ValueError):dataclasses.replace(receipt,evaluation_group='HISTORICAL_HOLDOUT')
    def test_unknown_evaluation_group_rejected(self):
        with self.assertRaises(ValueError):
            ExperimentReceipt('trial','target',(),(),(),'v1',{},'unsealed',{},(),(),False,{},(),'invented-group')
    def test_integer_and_reserved_mapping_keys_roundtrip(self):
        source=SourceArtifact.from_bytes('s',b'x','fixture','SYNTHETIC_SCHEMA_FIXTURE')
        observation=EvidenceObservation('o','s','test',{1:'integer','1':'string','__type__':'literal data'}, {})
        store=KernelStore((source,observation))
        self.assertEqual(KernelStore.from_json(store.to_json()),store)
    def test_absent_holdout_lock_rejected(self):
        for lock in ('','  ',None,'UNSEALED'):
            with self.subTest(lock=lock),self.assertRaises(ValueError):
                ExperimentReceipt('trial','target',(),(),(),'v1',{},lock,{},(),(),False,{},(),'HISTORICAL_HOLDOUT')
    def test_migrated_claims_are_core_links(self):
        graph=import_matrix((Path(__file__).parent/'frozen/source/matrix-message.txt').read_bytes(),'fixture')
        store=migrate_matrix(graph)
        w=graph.witnesses[0];record=next(r for r in store.records if r.record_id==w.record_id)
        self.assertEqual(record.claim_refs,w.claim_refs)
    def test_cell_ordinal_cannot_readdress_source(self):
        graph=import_matrix((Path(__file__).parent/'frozen/source/matrix-message.txt').read_bytes(),'fixture')
        # Change the label of an empty slot without changing source coordinates.
        cells=list(graph.cells);i=next(i for i,c in enumerate(cells) if not c.glyph)
        cells[i]=dataclasses.replace(cells[i],script_label='unrelated script')
        with self.assertRaises(ValueError):validate_graph(dataclasses.replace(graph,cells=tuple(cells)))
if __name__=='__main__':unittest.main()
