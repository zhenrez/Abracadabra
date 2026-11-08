"""Independent symbolic-library verification of the new source-conditioned result."""
from pathlib import Path
from itertools import combinations
import importlib.util,json,sys,unittest
import sympy as S
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from derive_score_anchors import solve,identifiable,unit,minimal_conflicts

class IndependentScoreAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=json.loads((ROOT/'state/delivery-2026-11-07/mathematics/score-anchors.json').read_text(encoding='utf8'))
        cls.A=S.Matrix(cls.output['matrix'])
        native=json.loads((ROOT/'state/reconstruction/generational-constraints.json').read_text(encoding='utf8'))
        cls.witnesses=next(x for x in native['constraints'] if x['id']=='GT-TIME-OVERLAP')['witness_executions']
    def test_symbolic_projection_and_all_anchor_minors(self):
        self.assertEqual(self.A.rank(),3)
        d1,d2,lA,lB,lC=S.symbols('d1 d2 lA lB lC')
        answer=S.linsolve((self.A.col_join(S.Matrix([unit(0),unit(1)])),S.Matrix([lA,lB,lC,d1,d2])))
        self.assertEqual(next(iter(answer)),(d1,d2,lA-d1-d2,lB-lA+d1,lC-lB+d2))
        for p in self.output['anchorPairs']:
            augmented=self.A.col_join(S.Matrix([unit(i-1) for i in p['stageIndices']]))
            self.assertEqual(augmented.rank()==5,p['sufficient'])
        self.assertEqual([p['stageIndices'] for p in self.output['anchorPairs'] if not p['sufficient']],[[1,4],[2,5]])
    def test_all_fifty_reconstructions_with_independent_solver(self):
        for w in self.witnesses:
            for pair in combinations(range(5),2):
                matrix=self.A.col_join(S.Matrix([unit(i) for i in pair]))
                rhs=S.Matrix(w['lifespans']+[w['durations'][i] for i in pair])
                independent=matrix.gauss_jordan_solve(rhs)[0]
                actual=solve(matrix.tolist(),list(rhs))
                self.assertTrue(actual['consistent'])
                if matrix.rank()==5:self.assertEqual(list(independent),[S.Rational(x) for x in actual['particular']])
                else:self.assertEqual(actual['dimension'],1)
    def test_inconsistent_subset_is_minimal_and_not_full_source_failure(self):
        matrix=self.A.col_join(S.Matrix([unit(0),unit(3)]));rhs=S.Matrix([438,433,464,35,31])
        bad=[0,1,3,4]
        self.assertGreater(matrix[bad,:].row_join(rhs[bad,:]).rank(),matrix[bad,:].rank())
        for removed in bad:
            keep=[i for i in bad if i!=removed]
            self.assertEqual(matrix[keep,:].row_join(rhs[keep,:]).rank(),matrix[keep,:].rank())
        self.assertNotIn('lifespan_C',self.output['contradictionControl']['minimalConflicts'][0])
    def test_unique_algebra_does_not_imply_positive_ordered_score(self):
        answer=self.A.col_join(S.Matrix([unit(0),unit(1)])).inv()*S.Matrix([438,433,464,1,30])
        self.assertEqual(answer[3],-4)
        self.assertFalse(self.output['orderControl']['positiveOrderedStageModelAdmissible'])
    def test_library_agrees_on_free_partial_predictions(self):
        answer=solve(self.A.tolist()+[unit(0)],[438,433,464,35])
        self.assertEqual(identifiable(answer,unit(3)),{'status':'determined','value':30})
        self.assertEqual(identifiable(answer,unit(1)),{'status':'underdetermined'})
        self.assertEqual(identifiable(answer,[0,1,0,0,-1]),{'status':'determined','value':-31})

if __name__=='__main__':unittest.main()
