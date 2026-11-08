"""Source-profiled Sanskrit/numeric controls, independent of musical assignments."""
from itertools import product,islice
from math import prod
from types import MappingProxyType
import unicodedata

ROWS=(('k','kh','g','gh','ṅ','c','ch','j','jh','ñ'),
      ('ṭ','ṭh','ḍ','ḍh','ṇ','t','th','d','dh','n'),
      ('p','ph','b','bh','m'),('y','r','l','v','ś','ṣ','s','h'))
DIGITS=MappingProxyType({letter:(index+1)%10 for row in ROWS for index,letter in enumerate(row)})
VOWELS=('ai','au','a','ā','i','ī','u','ū','ṛ','ṝ','ḷ','ḹ','e','o')
TOKENS=tuple(sorted(tuple(DIGITS)+VOWELS,key=lambda value:(-len(value),value)))
SOURCE_NUMERIC='https://www.numdam.org/item/10.24033/rhm.167.pdf#page=5'
SOURCE_ARTICULATION='https://sanskritdocuments.org/doc_z_misc_major_works/pANinIyashikShA.html'

def decode_katapayadi(text,vowel_policy='zero'):
    """IAST, units-first, last consonant of a vowel-bearing cluster counts.

    The zero profile follows the Sadratnamala definition quoted by Sarma2012.
    The optional ignore profile is an engineering sensitivity control; its separate
    historical textual warrant has not been retrieved in this source acquisition.
    Text normalization is a derived parsing operation; the supplied string survives.
    """
    if not isinstance(text,str) or vowel_policy not in ('zero','ignore'):raise ValueError('IAST text and documented vowel policy required')
    normalized=unicodedata.normalize('NFC',text);offset=0;pending=[];digits=[];trace=[]
    while offset<len(normalized):
        if normalized[offset].isspace() or normalized[offset]=='-':pending=[];offset+=1;continue
        token=next((value for value in TOKENS if normalized.startswith(value,offset)),None)
        if token is None:raise ValueError('Unsupported IAST sequence at derived position '+str(offset))
        if token in DIGITS:pending.append(token)
        else:
            if pending:digit=DIGITS[pending[-1]]
            elif vowel_policy=='zero':digit=0
            else:digit=None
            if digit is not None:
                digits.append(digit);trace.append({'cluster':tuple(pending),'vowel':token,'digit':digit,
                    'derived_nfc_vowel_span':(offset,offset+len(token))})
            pending=[]
        offset+=len(token)
    return {'raw':text,'normalized_for_parsing':normalized,'digits_units_first':tuple(digits),
        'number':sum(digit*10**index for index,digit in enumerate(digits)) if digits else None,
        'status':'DECODED' if digits else 'NO_NUMBER','trace':tuple(trace),'vowel_policy':vowel_policy,
        'source_ref':SOURCE_NUMERIC,'vowel_policy_authority':'SOURCE_DEFINED_ZERO' if vowel_policy=='zero' else 'ENGINEERING_SENSITIVITY_CONTROL',
        'historical_support':'Convention decoded; no historical intention inferred'}

def encode_katapayadi(number,max_candidates=4096):
    """Finite consonant+a encodings; no grammatical or historical word selection."""
    if type(number) is not int or number<0:raise ValueError('Nonnegative integer required')
    if type(max_candidates) is not int or not 1<=max_candidates<=4096:raise ValueError('Candidate cap must be 1..4096')
    digits=tuple(int(d) for d in str(number)[::-1])
    if len(digits)>32:raise ValueError('Bounded control supports at most32digits')
    domains=tuple(tuple(letter for letter,digit in DIGITS.items() if digit==value) for value in digits)
    total=prod(len(domain) for domain in domains)
    candidates=tuple(''.join(letter+'a' for letter in choice) for choice in islice(product(*domains),max_candidates))
    return {'number':number,'digits_units_first':digits,'candidates':candidates,'complete':len(candidates)==total,
        'total_candidates':total,'historical_support':'NOT_VERIFIED','source_ref':SOURCE_NUMERIC}

def sanskrit_stop_table():
    """Traditional varga distinctions; no acoustic measurements or pitch mapping."""
    places=('velar','palatal','retroflex','dental','bilabial')
    rows=(('k','kh','g','gh','ṅ'),('c','ch','j','jh','ñ'),('ṭ','ṭh','ḍ','ḍh','ṇ'),
          ('t','th','d','dh','n'),('p','ph','b','bh','m'))
    result=[]
    for place,row in zip(places,rows):
        for column,letter in enumerate(row):
            manner='nasal' if column==4 else 'stop';voice=int(column>=2);aspirated=int(column in (1,3))
            vector=tuple(int(place==p) for p in places)+(int(manner=='stop'),int(manner=='nasal'),voice,1-voice,aspirated)
            result.append({'iast':letter,'place':place,'manner':manner,'voiced':voice,'aspirated':aspirated,
                'vector':vector,'source_ref':SOURCE_ARTICULATION,'source_locator':'verses4,17–18,38–39; traditional categories',
                'acoustic_measurement':'NOT_PERFORMED','cross_orientation_assignment':None})
    return tuple(result)
