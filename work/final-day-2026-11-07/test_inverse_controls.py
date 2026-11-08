import unittest
from inverse_controls import countermodels, relabeling_certificate


class InverseControlsTests(unittest.TestCase):
    def test_two_deterministic_models_fit_same_data_but_disagree(self):
        result = countermodels((("A", "ʔ"), ("B", "b/v")), "unseen", ("ʔ", "b/v"))
        self.assertEqual(result["observed_residual_counts"], [0, 0])
        self.assertEqual(result["unseen_predictions"], ["ʔ", "b/v"])
        self.assertFalse(result["identified_from_observations_alone"])
        self.assertEqual(result["models"][0]["transitions"][1]["output"], "b/v")

    def test_contradictions_and_false_holdouts_rejected(self):
        with self.assertRaises(ValueError):
            countermodels((("A", "a"), ("A", "b")), "unseen", ("a", "b"))
        with self.assertRaises(ValueError):
            countermodels((("A", "a"),), "A", ("a", "b"))
        with self.assertRaises(ValueError):
            countermodels((("A", "a"),), "unseen", ("a", "a"))

    def test_latent_labels_are_not_identified_by_outputs(self):
        result = relabeling_certificate({"alef": "ʔ", "bet": "b"}, {"alef": "q1", "bet": "q0"})
        self.assertEqual(result["renamed_operator"], {"q1": "ʔ", "q0": "b"})
        self.assertTrue(result["all_outputs_preserved"])
        self.assertFalse(result["historical_letter_identity_identified"])

    def test_non_bijective_or_missing_labels_rejected(self):
        for names in ({"a": "x", "b": "x"}, {"a": "x"}, {"a": "x", "b": "y", "c": "z"}):
            with self.assertRaises(ValueError):
                relabeling_certificate({"a": "p", "b": "q"}, names)


if __name__ == "__main__":
    unittest.main()
