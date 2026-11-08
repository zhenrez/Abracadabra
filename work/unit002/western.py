"""Independent bounded Western model: exact rational tuning, modes and register.

The chosen tuning is explicitly Pythagorean major. It does not represent all
Western tunings, ancient Greek genera, Fludd or Kepler. No Sefer/W72 mapping.
Chromatic coordinates are interval labels, not equal-tempered frequencies.
"""
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class Interval:
    diatonic_steps:int
    chromatic_steps:int
    ratio:Fraction
    def __post_init__(self):
        if type(self.diatonic_steps) is not int or type(self.chromatic_steps) is not int:raise ValueError('Integer interval coordinates required')
        object.__setattr__(self,'ratio',Fraction(self.ratio))
        if self.ratio<=0:raise ValueError('Positive interval ratio required')
    def compose(self,other):return Interval(self.diatonic_steps+other.diatonic_steps,self.chromatic_steps+other.chromatic_steps,self.ratio*other.ratio)
    def inverse(self):return Interval(-self.diatonic_steps,-self.chromatic_steps,1/self.ratio)
    @property
    def chromatic_mod12(self):return self.chromatic_steps%12

@dataclass(frozen=True)
class Pitch:
    ratio:Fraction
    def __post_init__(self):
        object.__setattr__(self,'ratio',Fraction(self.ratio))
        if self.ratio<=0:raise ValueError('Positive relative frequency required')
    @property
    def register(self):
        # Exact comparisons avoid logarithm rounding at octave boundaries.
        value=self.ratio;register=0
        while value>=2:value/=2;register+=1
        while value<1:value*=2;register-=1
        return register
    @property
    def pitch_class(self):return self.ratio/(Fraction(2)**self.register)
    def transpose(self,interval):return Pitch(self.ratio*interval.ratio)
    def invert(self):return Pitch(1/self.ratio)

class WesternModel:
    namespace='western:pythagorean-major:v1'
    MODE_NAMES=('ionian','dorian','phrygian','lydian','mixolydian','aeolian','locrian')
    MAJOR_STEPS=(0,2,4,5,7,9,11)
    MAJOR_RATIOS=tuple(Fraction(n,d) for n,d in [(1,1),(9,8),(81,64),(4,3),(3,2),(27,16),(243,128)])
    def mode(self,name):
        if name not in self.MODE_NAMES:raise ValueError('Unknown mode')
        index=self.MODE_NAMES.index(name);p=self.MAJOR_RATIOS;s=self.MAJOR_STEPS
        ratios=p[index:]+tuple(x*2 for x in p[:index])
        steps=s[index:]+tuple(x+12 for x in s[:index])
        return {'name':name,'ratios':tuple(x/p[index] for x in ratios),
                'chromatic_steps':tuple(x-s[index] for x in steps),'tuning':'Pythagorean, explicitly selected'}
    def fifth_cycle(self):
        exact=Fraction(3,2)**12;octaves=Fraction(2)**7
        return {'twelve_fifths':exact,'seven_octaves':octaves,'comma':exact/octaves,
                'chromatic_return':(12*7)%12,'exact_return':exact==octaves}
    def describe(self,*args):
        return {'status':'NOT_EVALUATED','bits':None,'reason':'G6 remains locked; no historical coding-scheme comparison'}
