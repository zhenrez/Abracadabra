import unittest
from historical_extensions import build_resh
from kernel import KernelStore,EvidenceClaim,DomainRecord

class ReshSourceControlTests(unittest.TestCase):
    def test_source_contexts_remain_distinct_and_unmapped(self):
        store=build_resh();store.validate()
        self.assertEqual(KernelStore.from_json(store.to_json()),store)
        claims=[r for r in store.records if isinstance(r,EvidenceClaim)]
        self.assertEqual(len(claims),3)
        self.assertEqual({c.value['context_example'] for c in claims},{'Micah 1:13','2 Kings 6:32','Lamentations 1:4'})
        self.assertTrue(all(c.value['sefer_state_mapping'] is None and c.value['ipa'] is None for c in claims))
        self.assertTrue(all(c.source_locator for c in claims))
        record=next(r for r in store.records if isinstance(r,DomainRecord))
        self.assertFalse(record.properties['independent_manuscripts_verified'])
        self.assertEqual(record.properties['earliest_surviving_manuscript'],'NOT ESTABLISHED')
        self.assertTrue({c.record_id for c in claims}<=set(store.provenance(record.record_id)))

if __name__=='__main__':unittest.main()
