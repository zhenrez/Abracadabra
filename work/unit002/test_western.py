import unittest
from fractions import Fraction as F
from western import Interval,Pitch,WesternModel

class WesternTests(unittest.TestCase):
    def test_interval_composition(self):
        fifth=Interval(4,7,F(3,2));fourth=Interval(3,5,F(4,3));octave=fifth.compose(fourth)
        self.assertEqual(octave,Interval(7,12,F(2)))
        self.assertEqual(fourth.compose(fifth),octave)
        self.assertEqual(fifth.compose(fifth.inverse()),Interval(0,0,F(1)))
    def test_register_is_retained(self):
        p=Pitch(F(3));self.assertEqual(p.pitch_class,F(3,2));self.assertEqual(p.register,1)
        self.assertNotEqual(p,Pitch(F(3,2)))
        self.assertEqual(Pitch(F(1,4)).register,-2)
    def test_modes(self):
        m=WesternModel();self.assertEqual(m.mode('dorian')['chromatic_steps'],(0,2,3,5,7,9,10))
        for name in m.MODE_NAMES:
            values=m.mode(name)['ratios'];self.assertEqual(values[0],F(1));self.assertEqual(len(values),7)
            self.assertTrue(all(a<b for a,b in zip(values,values[1:])));self.assertLess(values[-1],2)
    def test_transposition_and_inversion(self):
        p=Pitch(F(9,8));i=Interval(4,7,F(3,2))
        self.assertEqual(p.transpose(i).transpose(i.inverse()),p)
        self.assertEqual(p.invert().invert(),p)
    def test_nonclosure(self):
        m=WesternModel();r=m.fifth_cycle()
        self.assertEqual(r['comma'],F(531441,524288));self.assertNotEqual(r['comma'],1)
        self.assertEqual(r['chromatic_return'],0)
    def test_projection_is_not_exact_tuning(self):
        self.assertEqual(Interval(4,7,F(3,2)).compose(Interval(4,7,F(3,2))).chromatic_mod12,2)
        self.assertEqual(Pitch(F(81,64)).pitch_class,F(81,64))
        with self.assertRaises(ValueError):Pitch(F(0))
    def test_no_foreign_model(self):
        import ast,pathlib
        tree=ast.parse(pathlib.Path(__file__).with_name('western.py').read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(set(imports)&{'sefer','harmonic_verifier','kernel','contextual_alignment'})
if __name__=='__main__':unittest.main()
