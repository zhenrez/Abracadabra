import unittest,copy
from fractions import Fraction as Q
from itertools import product
from evidence import preserve,restore,compress,decompress,validate
from native_models import Western,Chinese,Indian,Sefer
from comparison import Map,preservation,reconstruct

class EvidenceTests(unittest.TestCase):
    def bundle(self):return dict(schema='sun.orientation-evidence.v1',sources=[preserve('s',b'\xef\xbb\xbfraw\r\n','fixture','source')],observations=[],relations=[])
    def test_exact_bytes(self):
        b=self.bundle();self.assertEqual(decompress(compress(b)),b)
        self.assertEqual(restore(b['sources'][0]),b'\xef\xbb\xbfraw\r\n')
    def test_tamper(self):
        b=self.bundle();b['sources'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):validate(b)
    def test_untyped_relation(self):
        b=self.bundle();b['relations']=[dict(kind='same count',source_refs=['s'],**{'from':'x','to':'y'})]
        from jsonschema import ValidationError
        with self.assertRaises((ValueError,ValidationError)):validate(b)

class WesternTests(unittest.TestCase):
    def test_exact_sun(self):
        w=Western()
        for x in (Q(1),Q(7,11),Q(81,80)):
            self.assertEqual(w.act(w.act(x,'R'),'L'),x/2)
            self.assertEqual(w.act(w.act(x,'L'),'R'),x/2)
    def test_register(self):
        w=Western();self.assertEqual(w.transpose((11,0),1),(0,1))
        self.assertEqual(w.transpose((0,0),-1),(11,-1))
        for x in (Q(1,8),Q(3,2),Q(9,2)):
            pc,r=w.octave_coordinates(x);self.assertEqual(pc*Q(2)**r,x);self.assertTrue(1<=pc<2)
    def test_nonclosure_and_scale(self):
        w=Western();self.assertEqual(w.comma(),Q(531441,524288));self.assertNotEqual(w.comma(),1)
        with self.assertRaises(ValueError):w.scale([0]*7)
        self.assertEqual(w.scale((0,2,4,5,7,9,11)),(0,2,4,5,7,9,11))

class ChineseTests(unittest.TestCase):
    def test_context_operations(self):
        c=Chinese();self.assertEqual(len(set(c.contexts())),60)
        for x in c.contexts():self.assertEqual(c.rotate(c.rotate(x,7,3),-7,-3),x)
        a,b=c.six_plus_six();self.assertEqual(len(a),6);self.assertEqual(set(a)|set(b),set(range(12)));self.assertFalse(set(a)&set(b))
    def test_composition(self):
        c=Chinese();self.assertEqual(c.act(c.act(1,'D'),'U'),Q(8,9));self.assertNotEqual(Q(8,9),Q(1,2))

class IndianTests(unittest.TestCase):
    def test_independent_enumeration(self):
        expected={(0,r,g,m,7,d,n) for r,g,m,d,n in product(range(1,5),range(1,5),(5,6),range(8,12),range(8,12)) if r<g and d<n}
        actual=set(Indian().configurations());self.assertEqual(actual,expected);self.assertEqual(len(actual),72)
        self.assertTrue(all(tuple(sorted(s))==s and len(set(s))==7 for s in actual))
    def test_pairing(self):
        i=Indian();pairs=set()
        for s in i.configurations():
            t=i.pair_madhyama(s);self.assertEqual(i.pair_madhyama(t),s)
            self.assertEqual(sum(a!=b for a,b in zip(s,t)),1);pairs.add(tuple(sorted((s,t))))
        self.assertEqual(len(pairs),36)
    def test_no_invented_tuning(self):
        self.assertEqual(Indian().intonation()['status'],'input_gap')
        with self.assertRaises(ValueError):Indian().intonation([Q(1)]*22,'fixture')

class SeferTests(unittest.TestCase):
    def test_native_relations(self):
        s=Sefer();self.assertEqual(s.validate(s.roots)['status'],'Valid')
        self.assertEqual(len(set(s.gates())),231)
        self.assertEqual(len(s.tagged_expansion()),29)
        self.assertEqual(len(set(s.paths())),32)
    def test_duplicate(self):
        s=Sefer();self.assertEqual(s.validate(s.roots[:-1]+(s.roots[0],))['status'],'Invalid')

class ComparisonTests(unittest.TestCase):
    def test_operator_preservation_and_counterexample(self):
        identity=Map('identity','length','length','identity',lambda x:x)
        source=Map('SUN R','length','length','generation',lambda x:Q(2,3)*x)
        target=Map('Chinese D','length','length','generation',lambda x:Q(2,3)*x)
        self.assertEqual(preservation([Q(1)],source,target,identity,identity)['status'],'preserved_on_test_domain')
        sun=Map('SUN RL','length','length','generation',lambda x:x/2)
        china=Map('Chinese DU','length','length','generation',lambda x:Q(8,9)*x)
        self.assertEqual(preservation([Q(1)],sun,china,identity,identity)['status'],'falsified_on_test_domain')
    def test_wrong_types_rejected(self):
        a=Map('x','letter','letter','order',lambda x:x);b=Map('y','pitch','pitch','order',lambda x:x)
        with self.assertRaises(ValueError):preservation([0],a,b,a,a)
    def test_ambiguity(self):
        self.assertEqual(reconstruct(['A','B'],True,True)['status'],'ambiguous')
        self.assertEqual(reconstruct(['A'],True,False)['status'],'ambiguous')
        self.assertEqual(reconstruct([],True,True)['status'],'falsified')
        self.assertEqual(reconstruct(['A'],True,True)['status'],'determined')

if __name__=='__main__':unittest.main()
