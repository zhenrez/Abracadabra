"""Independent finite/exact contracts. No one model defines another's validity."""
from fractions import Fraction as Q
from itertools import combinations,product
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ariadne-inverse'))
from harmonic_verifier import HarmonicPhoneticVerifier,GROUPS

def positive(value):
    value=Q(value)
    if value<=0:raise ValueError('Positive ratio required')
    return value

class Western:
    """Exact length intervals plus a separate abstract chromatic address model."""
    length_operators={'R':Q(2,3),'L':Q(3,4),'O':Q(1,2)}
    def act(self,length,operator):return positive(length)*self.length_operators[operator]
    def octave_coordinates(self,frequency_ratio):
        x=positive(frequency_ratio);register=0
        while x>=2:x/=2;register+=1
        while x<1:x*=2;register-=1
        return x,register
    def transpose(self,address,steps):
        pc,register=address
        if type(pc) is not int or not 0<=pc<12 or type(register) is not int or type(steps) is not int:raise ValueError('Invalid chromatic address')
        register_delta,pc=divmod(pc+steps,12)
        return pc,register+register_delta
    def scale(self,classes):
        values=tuple(classes)
        if len(values)!=7 or len(set(values))!=7 or any(type(x) is not int or not 0<=x<12 for x in values):raise ValueError('Seven distinct selected classes required')
        return values
    def comma(self):return Q(3,2)**12/Q(2)**7

class Chinese:
    """Formal lü × function carrier; address rotation is not pipe tuning."""
    length_operators={'D':Q(2,3),'U':Q(4,3)}
    functions=('gong','shang','jue','zhi','yu')
    def contexts(self):return tuple(product(range(12),range(5)))
    def rotate(self,state,reference_steps=0,function_steps=0):
        if state not in self.contexts():raise ValueError('Invalid native context')
        if type(reference_steps) is not int or type(function_steps) is not int:raise ValueError('Integer steps required')
        return ((state[0]+reference_steps)%12,(state[1]+function_steps)%5)
    def act(self,length,operator):return positive(length)*self.length_operators[operator]
    def six_plus_six(self):return tuple(range(0,12,2)),tuple(range(1,12,2))

class Indian:
    """Conventional melakarta position grammar, independent of shruti tuning."""
    svaras=('Sa','Ri','Ga','Ma','Pa','Dha','Ni')
    rg=tuple(combinations(range(1,5),2));dn=tuple(combinations(range(8,12),2))
    def configurations(self):return tuple((0,r,g,m,7,d,n) for (r,g),m,(d,n) in product(self.rg,(5,6),self.dn))
    def pair_madhyama(self,scale):
        if scale not in self.configurations():raise ValueError('Not an admissible parent configuration')
        return scale[:3]+(11-scale[3],)+scale[4:]
    def intonation(self,ratios=None,source_ref=None):
        if ratios is None:return dict(status='input_gap',svara_roles=self.svaras,shruti_count=22,ratios=None)
        values=tuple(positive(x) for x in ratios)
        if not source_ref or len(values)!=22 or len(set(values))!=22 or any(not Q(1)<=v<Q(2) for v in values):raise ValueError('22 distinct octave ratios plus source required')
        return dict(status='supplied_profile',ratios=values,source_ref=source_ref,not_universal=True)

class Sefer:
    """Reuse the existing partition validator, adding typed combinatorial relations."""
    roots=tuple(x for values in GROUPS.values() for x in values)
    def validate(self,roots):return HarmonicPhoneticVerifier().validate(roots)
    def gates(self):return tuple(combinations(self.roots,2))
    def tagged_expansion(self):return tuple(HarmonicPhoneticVerifier('expanded').slots)
    def paths(self):return tuple(('sefirah',i) for i in range(10))+tuple(('letter',r) for r in self.roots)
