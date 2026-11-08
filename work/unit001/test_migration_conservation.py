"""Adversarial conservation tests from an independent review of the G0 adapter."""
import dataclasses
from pathlib import Path
import unittest

from evidence import (DerivedFeature, DatedAttestation, Epistemic, GenealogyEdge,
                      import_matrix, validate_graph)
from kernel import EvidenceObservation, KernelStore, migrate_matrix, restore_matrix
from evidence import serialize


class MigrationConservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = import_matrix(
            (Path(__file__).parent / 'frozen/source/matrix-message.txt').read_bytes(),
            'synthetic review of supplied matrix')

    def enriched_graph(self):
        g = self.graph
        first, second = g.witnesses[:2]
        date = DatedAttestation('review:date', first.record_id, 'manuscript_copy',
                               None, None, (g.source.artifact_id,))
        feature = DerivedFeature('review:feature', (first.record_id,), 'topology',
                                 {'observed': None}, 'synthetic review', 'v1',
                                 'unresolved', (g.source.artifact_id,))
        edge = GenealogyEdge('review:edge', first.record_id, second.record_id,
                             'PROPOSED_SIMILARITY', Epistemic.HYPOTHESIZED_ALIGNMENT,
                             (g.claims[0].claim_id,), (), {'synthetic': True})
        witness = dataclasses.replace(first, attestation_refs=(date.attestation_id,))
        claim = dataclasses.replace(g.claims[0], dating_refs=(date.attestation_id,))
        result = dataclasses.replace(g, witnesses=(witness,) + g.witnesses[1:],
                                     claims=(claim,) + g.claims[1:],
                                     attestations=(date,), genealogy=(edge,), features=(feature,))
        validate_graph(result)
        return result

    def test_migration_preserves_supplemental_record_identities(self):
        g = self.enriched_graph()
        store = migrate_matrix(g)
        ids = {r.record_id for r in store.records}
        self.assertTrue({'review:date', 'review:edge', 'review:feature'} <= ids)
        dependencies = set(store.provenance('review:edge'))
        self.assertTrue({g.witnesses[0].record_id, g.witnesses[1].record_id,
                         g.claims[0].claim_id, g.source.artifact_id} <= dependencies)

    def test_migration_preserves_claim_locator_and_dating(self):
        g = self.enriched_graph()
        store = migrate_matrix(g)
        claim = next(r for r in store.records if r.record_id == g.claims[0].claim_id)
        self.assertEqual(getattr(claim, 'source_locator', None), g.claims[0].source_locator)
        self.assertEqual(getattr(claim, 'dating_refs', None), ('review:date',))

    def test_custom_mapping_keys_cannot_mutate_immutable_record(self):
        class MutableKey:
            def __init__(self): self.label = 'original'
        key = MutableKey()
        with self.assertRaises(TypeError):
            EvidenceObservation('o', 's', 'synthetic', {key: 'value'}, {})

    def test_enriched_matrix_exact_roundtrip(self):
        graph=self.enriched_graph()
        store=KernelStore.from_json(migrate_matrix(graph).to_json())
        self.assertEqual(serialize(restore_matrix(store)),serialize(graph))


if __name__ == '__main__':
    unittest.main()
