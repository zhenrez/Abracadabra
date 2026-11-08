"""Finite, explicit identifiability controls; no historical reconstruction claim.

For any finite single-symbol observations and one unobserved input, two
deterministic one-state Mealy machines can reproduce every observation exactly
and disagree on the new input. A prior restricting admissible machines could
exclude these lookup constructions; the observations alone cannot do so.
Latent-state bijective renaming is a separate gauge ambiguity.
"""
import hashlib
import json


def _text(value):
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 65536:
        raise ValueError("Expected a nonempty bounded Unicode string")
    return value


def countermodels(observations, unseen_input, possible_outputs):
    observations = tuple(observations)
    outputs = tuple(possible_outputs)
    if not observations or len(observations) > 1000:
        raise ValueError("Require 1–1000 finite observations")
    unseen_input = _text(unseen_input)
    if len(outputs) != 2 or len({_text(value) for value in outputs}) != 2:
        raise ValueError("Exactly two distinguishable possible outputs required")
    table = {}
    for input_symbol, output in observations:
        input_symbol, output = _text(input_symbol), _text(output)
        if input_symbol in table and table[input_symbol] != output:
            raise ValueError("Conflicting observations for deterministic input")
        table[input_symbol] = output
    if unseen_input in table:
        raise ValueError("The proposed unseen input is already observed")
    ordered = sorted(table.items())
    models = []
    residuals = []
    for prediction in outputs:
        transitions = [{"state": "q0", "input": key, "next_state": "q0", "output": value}
                       for key, value in ordered + [(unseen_input, prediction)]]
        model_table = {row["input"]: row["output"] for row in transitions}
        residuals.append(sum(model_table[key] != value for key, value in ordered))
        models.append({"kind": "finite_one_state_Mealy_machine", "states": ["q0"],
                       "initial_state": "q0", "transitions": transitions})
    payload = json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {"observed_inputs": len(ordered), "observations_sha256": hashlib.sha256(payload).hexdigest(),
            "models": models, "observed_residual_counts": residuals,
            "unseen_input": unseen_input, "unseen_predictions": list(outputs),
            "identified_from_observations_alone": False,
            "logical_scope": "Constructive counterexample within unrestricted finite deterministic transducers",
            "non_claims": ["No minimal historically admissible machine is inferred",
                           "The differing outputs are logical possibilities, not historical candidate probabilities",
                           "A more restrictive independently justified model family may resolve this ambiguity"]}


def relabeling_certificate(operator, renaming):
    operator, renaming = dict(operator), dict(renaming)
    if not operator or set(operator) != set(renaming):
        raise ValueError("Renaming must cover exactly the original state domain")
    for key, value in operator.items():
        _text(key)
        _text(value)
    for value in renaming.values():
        _text(value)
    if len(set(renaming.values())) != len(renaming):
        raise ValueError("State renaming must be bijective")
    renamed = {renaming[key]: value for key, value in operator.items()}
    return {"original_operator": operator, "renaming": renaming, "renamed_operator": renamed,
            "all_outputs_preserved": all(renamed[renaming[key]] == value for key, value in operator.items()),
            "identity": "T_prime(phi(b)) = T(b); T_prime = T composed with phi_inverse",
            "historical_letter_identity_identified": False,
            "boundary": "Latent labels require independent anchors; this is not a proposed historical alignment"}
