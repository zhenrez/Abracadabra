"""Exact conditional topology control; no historical genealogy is inferred."""
from pathlib import Path
from functools import lru_cache
from itertools import combinations, product
from fractions import Fraction
from math import comb, factorial
import hashlib
import json
import datetime

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/reconstruction/symbol-sound-census"
INPUTS = [BASE / "phyla-waves-assessment.json", BASE / "reading-tradition-edge-assessment.json"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


before = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in INPUTS}
source = json.loads(INPUTS[0].read_text(encoding="utf-8"))
character = next(c for c in source["concreteCharacters"] if c["id"] == "PW-C1")
ones = frozenset(character["authorReportedDerivedTraditions"])
zeros = frozenset(character["authorReportedUnroundedComparanda"])
assert ones == {"Tiberian", "Babylonian"}
assert zeros == {"Secunda", "Jerome", "Palestinian"}
assert not ones & zeros
labels = tuple(sorted(ones | zeros))
checks = []


def check(value, name):
    assert value, name
    checks.append({"name": name, "status": "passed"})


def newick(tree):
    return tree if isinstance(tree, str) else "(" + newick(tree[0]) + "," + newick(tree[1]) + ")"


def node(left, right):
    return tuple(sorted((left, right), key=newick))


# Enumerator A: root bipartitions. Requiring the least label in the left
# partition visits each unordered root split exactly once.
@lru_cache(None)
def split_trees(names):
    if len(names) == 1:
        return frozenset([names[0]])
    pivot, rest = names[0], names[1:]
    result = set()
    for size in range(len(rest) + 1):
        for chosen in combinations(rest, size):
            left = tuple(sorted((pivot,) + chosen))
            right = tuple(name for name in names if name not in left)
            if not right:
                continue
            for a in split_trees(left):
                for b in split_trees(right):
                    result.add(node(a, b))
    return frozenset(result)


def paths(tree):
    yield ()
    if not isinstance(tree, str):
        for side, child in enumerate(tree):
            for path in paths(child):
                yield (side,) + path


def insert(tree, path, label):
    if not path:
        return node(tree, label)
    side = path[0]
    children = list(tree)
    children[side] = insert(children[side], path[1:], label)
    return node(*children)


# Enumerator B: insert each new fixed label above every existing node,
# including the root/stem case. Deleting that label is a unique inverse.
def insertion_trees(names):
    result = {names[0]}
    stages = [{"leaves": 1, "count": 1}]
    for label in names[1:]:
        result = {insert(tree, path, label) for tree in result for path in paths(tree)}
        stages.append({"leaves": len(stages) + 1, "count": len(result)})
    return result, stages


def leaves(tree):
    return frozenset([tree]) if isinstance(tree, str) else leaves(tree[0]) | leaves(tree[1])


def clades(tree):
    if isinstance(tree, str):
        return {frozenset([tree])}
    return {leaves(tree)} | clades(tree[0]) | clades(tree[1])


def internal_paths(tree, path=()):
    if not isinstance(tree, str):
        yield path
        for side, child in enumerate(tree):
            yield from internal_paths(child, path + (side,))


def state_assignments(tree, derived, max_gains=1):
    internal = list(internal_paths(tree))
    nonroot = [p for p in internal if p]
    successes = []
    for values in product((0, 1), repeat=len(nonroot)):
        states = {(): 0, **dict(zip(nonroot, values))}
        transitions = []

        def visit(current, path=()):
            parent_state = states[path]
            for side, child in enumerate(current):
                child_path = path + (side,)
                child_state = int(child in derived) if isinstance(child, str) else states[child_path]
                transitions.append((parent_state, child_state))
                if not isinstance(child, str):
                    visit(child, child_path)

        visit(tree)
        gains = transitions.count((0, 1))
        losses = transitions.count((1, 0))
        if 1 <= gains <= max_gains and losses == 0:
            successes.append({"gains": gains, "losses": losses})
    return successes


def rooted_count(n):
    value = 1
    for k in range(2, n + 1):
        value *= 2*k - 3
    return value


all_trees = set(split_trees(labels))
inserted, insertion_stages = insertion_trees(labels)
check(all_trees == inserted, "Complete topology sets from two independent enumerators agree")
check(len(all_trees) == rooted_count(5) == 105, "Five-leaf count equals insertion-recurrence105")
check(comb(8, 4)//5 * factorial(5)//2**4 == 105, "Independent labelled-planar Catalan quotient gives105")
compatible = {t for t in all_trees if ones in clades(t)}
state_compatible = {t for t in all_trees if state_assignments(t, ones)}
check(compatible == state_compatible, "All105 topologies: exact internal-state test equals two-leaf-clade criterion")
check(len(compatible) == 15, "Exactly15 topologies remain under one gain/no loss")

# Collapse the two-leaf clade to X; expansion is a bijection, not a score.
collapsed_labels = tuple(sorted(zeros | {"X"}))
collapsed = split_trees(collapsed_labels)


def expand(tree):
    if isinstance(tree, str):
        return node(*sorted(ones)) if tree == "X" else tree
    return node(expand(tree[0]), expand(tree[1]))


expanded = {expand(t) for t in collapsed}
check(expanded == compatible and len(collapsed) == rooted_count(4) == 15,
      "Full clade-collapse/expansion bijection independently gives15")
check(len(all_trees - compatible) == 90, "Ninety of105 topologies are excluded conditionally")
common = set.intersection(*(clades(t) for t in compatible))
proper_common = {c for c in common if 1 < len(c) < len(labels)}
check(proper_common == {ones}, "Only nontrivial consensus clade is Tiberian+Babylonian")

# A negative ancestral state is not a second positive synapomorphy.
zeros_are_clade = {t for t in all_trees if zeros in clades(t)}
both_groups = compatible & zeros_are_clade
check(len(both_groups) == 3 and len(compatible - both_groups) == 12,
      "Forcing unrounded trio to be a clade would wrongly discard12 of15")
relaxed_two_origins = {t for t in all_trees if state_assignments(t, ones, max_gains=2)}
check(relaxed_two_origins == all_trees, "Allowing up to two origins/no loss admits all105")
unknown_polarity = compatible | zeros_are_clade
check(len(zeros_are_clade) == rooted_count(3)*rooted_count(3) == 9 and len(unknown_polarity) == 21,
      "Optional unknown-polarity one-change control admits21, not the primary15")
check(before == {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in INPUTS},
      "Original source assessments unchanged throughout calculation")
decision = json.loads((BASE / "rounded-qames-tree-superjev.json").read_text())
check(decision["status"] == "judged" and decision["resolved_model"] == "jev-1.14.0"
      and decision["answers"]["verification_route"]["winner"] == "two_enumerators_state_assignment_and_bijection",
      "Executed method follows actual Jev decision")

result = {
    "schema": "sunny.rounded-qames-conditional-tree-control.v1",
    "createdUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "passed", "exitCode": 0, "checksPassed": len(checks), "checks": checks,
    "verdict": "proved as written for the stated mathematical model; linguistic application remains conditional on the source-qualified character states and evolutionary assumptions",
    "labels": list(labels), "states": {"derived1": sorted(ones), "ancestral0": sorted(zeros)},
    "sourceFeature": {"id": "PW-C1", "sourceLocator": character["sourceLocator"], "sourceClaimStatus": character["sourceClaimStatus"]},
    "sourceBindings": before,
    "treeConvention": "Fully resolved rooted non-plane binary trees; five distinct leaf labels; unlabelled internal nodes; no branch lengths, internal rankings, dates, contact edges or sampled ancestors.",
    "primaryAssumptions": ["Root/ancestral state0", "Exactly one0-to1 innovation", "No1-to0 loss", "No contact, parallel origin or scribal mixing in this character", "The five leaf states are treated as specified for this calculation, not independently proven historical observations"],
    "counts": {"unconstrained": 105, "compatible": 15, "excluded": 90},
    "compatibleFractionOfSuppliedFamily": str(Fraction(len(compatible), len(all_trees))),
    "fractionBoundary": "A combinatorial fraction, not a prior, posterior, calibrated confidence or probability of actual genealogy.",
    "enumerators": {"rootBipartitions": len(all_trees), "independentFixedLabelInsertion": len(inserted), "insertionStages": insertion_stages, "stateSolver": "All binary internal-node assignments with root0 tested for each topology; no-loss exactly-one-gain condition compared to explicit clade membership.", "cladeCollapse": len(collapsed)},
    "proof": {
        "unconstrained": "A rooted binary tree on n-1 leaves has2n-4 edges plus one root-stem insertion position. Insert labelled leaf n at one of2n-3 positions. Deletion of that leaf and suppression of its parent is the unique inverse, so T1=1 and Tn=(2n-3)T(n-1). Therefore T5=1*3*5*7=105.",
        "oneFeature": "With root0, one0-to1 gain and no loss, exactly the descendants below the gain are1. Hence the two1leaves must form a clade. Conversely any tree with that clade admits the gain on its entering edge, with all other states0.",
        "compatible": "Collapse the fixed two-leaf clade to one label X. This bijects compatible five-leaf trees with arbitrary rooted binary trees on X and the other three labels. T4=1*3*5=15; the two-leaf expansion is unique.",
        "independentFormula": "Fully labelled planar trees count C(n-1)*n!; exchanging the two children of each of n-1 internal nodes acts freely with distinct leaf labels. Quotient by2^(n-1). For n=5 this is14*120/16=105."
    },
    "onlyNontrivialCommonClade": sorted(ones),
    "allCompatibleTreesNewick": sorted(newick(t)+";" for t in compatible),
    "allUnconstrainedTreesNewick": sorted(newick(t)+";" for t in all_trees),
    "negativeAndSensitivityControls": {
        "unroundedTrioAlsoMonophyletic": {"compatibleWithBothGroups": len(both_groups), "otherwiseCompatibleWronglyExcluded": len(compatible-both_groups), "boundary": "The three ancestral-state leaves need not form a clade."},
        "upToTwoOriginsNoLoss": {"compatible": len(relaxed_two_origins), "boundary": "Every topology can assign an independent gain to each1leaf; this relaxes the primary single-innovation assumption."},
        "unknownPolaritySingleChange": {"compatible": len(unknown_polarity), "zeroTrioCladeCount": len(zeros_are_clade), "intersectionBothClades": len(both_groups), "boundary": "If which state is ancestral is not fixed, either state block can be the derived clade. This optional control is not the primary rooted0 model."}
    },
    "limitations": [
        "The feature leaves15 topologies and identifies no unique actual genealogy, historical ancestor, branch time or direction of community contact.",
        "Rounded/unrounded coding and its historical polarity come from the existing conditional linguistic assessment; original witness phonetics/chronology were not newly verified.",
        "Reticulate contact, multiple origins, reversals, uncertain states, polytomies and non-binary trees are outside the primary105-tree family.",
        "No hierarchy edge, musical/geometric adapter or central ontology is changed by this control."
    ],
    "guardrails": {"actualJev": "docs/reconstruction/symbol-sound-census/rounded-qames-tree-superjev.json", "methodsApplied": ["Mathbox proof-audit: exact objects, hypotheses, boundary cases, exhaustive enumerator and independent criterion check", "SuperJev actual operational choice; probabilities do not prove the count"], "runtimeBoundary": "Local exact Python enumeration/state solving is executed. A specialist skill is not itself a separate external solver result."},
    "programSha256": digest(Path(__file__)), "persistentProcessesStarted": 0, "centralInputsChanged": False,
}
(BASE / "rounded-qames-tree-control.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "passed", "exitCode": 0, "checksPassed": len(checks), "unconstrained": 105, "compatible": 15, "excluded": 90, "output": "docs/reconstruction/symbol-sound-census/rounded-qames-tree-control.json"}))
