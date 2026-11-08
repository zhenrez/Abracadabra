import copy
import unittest
from build_dataset import dataset
from features import vectorize_phoneme as v, parse_ipa, masked_distance, graph_features
from run import analyze, blocked_error
from inverse import reconstruct, apply_operator

class PipelineTests(unittest.TestCase):
    def test_vector_contract(self):
        for s in 'bpmstzʃqʔae':
            x=v(s); self.assertEqual(len(x['vector']),15)
            self.assertEqual(sum(x['vector'][7:12]),1)
            self.assertEqual(sum(x['vector'][12:14]),1)
            self.assertTrue(all(n in (0,1) for n in x['vector']))
    def test_voicing_and_emphasis(self):
        self.assertEqual([i for i,(a,b) in enumerate(zip(v('b')['vector'],v('p')['vector'])) if a!=b],[12,13])
        self.assertEqual([i for i,(a,b) in enumerate(zip(v('s')['vector'],v('sˤ')['vector'])) if a!=b],[14])
    def test_vowel_place_inapplicable(self):
        self.assertEqual(v('a')['mask'][:7],[0]*7)
        self.assertEqual(v('a')['vector'],v('i')['vector'])  # documented information loss
        self.assertEqual(masked_distance(v('a'),v('i')),0)
        self.assertNotEqual(v('a')['extended'],v('i')['extended'])
        self.assertEqual(v('kʰ')['extended']['aspirated'],1)
    def test_operator_reconstruction(self):
        observations=[v(s) for s in ['b','p','bˤ','pˤ','m','a']]
        model=reconstruct(observations)
        self.assertEqual(len(model['basis']),3)
        for original,a in zip(observations,model['assignments']):
            self.assertEqual(apply_operator(model['basis'][a['root']]['vector'],*a['operator']),original['vector'])
            self.assertEqual(a['coarse_feature_edits'],[])
        for s in ['b','p','a']:
            for op in [(0,0),(0,1),(1,0),(1,1)]:
                self.assertEqual(apply_operator(apply_operator(v(s)['vector'],*op),*op),v(s)['vector'])
    def test_types_preserved(self):
        for raw,kind in [(None,'missing'),('?','unknown'),('s³','unresolved_label'),('b/v','alternatives'),('ka','sequence'),('kʷ','segment')]:
            self.assertEqual(parse_ipa(raw)['kind'],kind)
        self.assertEqual(len(parse_ipa('ʔa')['alternatives'][0]['segments']),2)
        self.assertEqual(parse_ipa('ˈdʌbəljuː')['alternatives'][0]['stress'][0]['before_segment'],0)
    def test_fail_closed(self):
        for raw in ['','b/','@','ʰb']:
            with self.assertRaises(ValueError): parse_ipa(raw)
        for raw in ['ks','b/v','?','a˞']:
            with self.assertRaises(ValueError): v(raw)
    def test_full_table(self):
        data=dataset(); self.assertEqual(len(data['cells']),540)
        cells,result=analyze(data,3)
        self.assertEqual(result['scripts'],15)
        self.assertEqual(result['topology_available'],0)
        self.assertEqual(result['kinds']['unknown'],4)
        self.assertEqual(result['kinds']['unresolved_label'],1)
        self.assertEqual(len(cells),540)
    def test_reproducibility(self):
        self.assertEqual(analyze(dataset(),4),analyze(dataset(),4))
    def test_graph_invariants(self):
        square=dict(source='synthetic square fixture',annotation_convention='four corners, four straight edges',
                    vertices=[[0,0],[1,0],[1,1],[0,1]],edges=[[0,1],[1,2],[2,3],[3,0]])
        a=graph_features(square)['vector']; self.assertEqual(a[:6],[4,4,1,1,0,0])
        self.assertEqual(a[-3:],[1,1,1])
        translated=copy.deepcopy(square); translated['vertices']=[[2*x+8,2*y-3] for x,y in square['vertices']]
        self.assertEqual(a,graph_features(translated)['vector'])
        reversed_edges=copy.deepcopy(square); reversed_edges['edges']=[e[::-1] for e in square['edges']]
        self.assertEqual(a,graph_features(reversed_edges)['vector'])
        self.assertIsNone(graph_features(None))
    def test_invalid_graph(self):
        for graph in [{},dict(source='fixture',annotation_convention='test',vertices=[[0,0]],edges=[[0,2]])]:
            with self.assertRaises((ValueError,KeyError)): graph_features(graph)
    def test_no_test_label_leakage(self):
        rows=[dict(block='a',column=1,ipa='b'),dict(block='b',column=1,ipa='p')]
        self.assertEqual(blocked_error(rows)['rates']['column'],1)

if __name__=='__main__': unittest.main()
