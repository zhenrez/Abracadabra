"""Reversible prefix-code baseline. No music, genealogy or historical inference."""
from collections import Counter

def _values(values):
    result=tuple(tuple(value) for value in values)
    if len(result)>10000 or any(len(v)!=2 or any(type(x) is not str for x in v) for v in result):
        raise ValueError('At most10000 pairs of literal strings required')
    return result

def _gamma(number):
    if type(number) is not int or number<1:raise ValueError('Positive gamma integer required')
    digits=bin(number)[2:];return '0'*(len(digits)-1)+digits

def _text(value):
    raw=value.encode('utf-8')
    if len(raw)>65536:raise ValueError('String exceeds bounded codec')
    return _gamma(len(raw)+1)+''.join(format(byte,'08b') for byte in raw)

def _pair(value):return _text(value[0])+_text(value[1])

def _text_size(value):
    count=len(value.encode('utf-8'))
    if count>65536:raise ValueError('String exceeds bounded codec')
    return 2*(count+1).bit_length()-1+8*count

def _pair_size(value):return sum(_text_size(part) for part in value)

def _budget(total):
    if total>8000000:raise ValueError('Encoded bitstream exceeds decoder budget')

def encode_literal(values):
    values=_values(values);size=1+len(_gamma(len(values)+1))
    for value in values:size+=_pair_size(value);_budget(size)
    data=_gamma(len(values)+1)+''.join(_pair(v) for v in values)
    bits='0'+data
    return {'bits':bits,'model_bits':1,'data_bits':len(data),'total_bits':len(bits),'escaped_values':len(values),
            'scheme':'literal-typed-utf8-gamma-v1'}

def fit_dictionary(values):return tuple(sorted(set(_values(values))))

def encode_dictionary(values,vocabulary):
    values=_values(values);vocabulary=_values(vocabulary)
    if len(set(vocabulary))!=len(vocabulary):raise ValueError('Duplicate dictionary entry')
    index={value:i for i,value in enumerate(vocabulary)};width=max(0,(len(vocabulary)-1).bit_length())
    size=1+len(_gamma(len(vocabulary)+1))+len(_gamma(len(values)+1))
    for value in vocabulary:size+=_pair_size(value);_budget(size)
    for value in values:size+=1+width if value in index else 1+_pair_size(value);_budget(size)
    model='1'+_gamma(len(vocabulary)+1)+''.join(_pair(v) for v in vocabulary)
    body=[];escaped=0
    for value in values:
        if value in index:body.append('0'+(format(index[value],'0'+str(width)+'b') if width else ''))
        else:body.append('1'+_pair(value));escaped+=1
    data=_gamma(len(values)+1)+''.join(body);bits=model+data
    return {'bits':bits,'model_bits':len(model),'data_bits':len(data),'total_bits':len(bits),
            'escaped_values':escaped,'dictionary_entries':len(vocabulary),'scheme':'dictionary-typed-utf8-gamma-v1'}

class _Reader:
    def __init__(self,bits):
        if type(bits) is not str or not bits or len(bits)>8000000 or set(bits)-{'0','1'}:raise ValueError('Invalid bounded bitstream')
        self.bits=bits;self.offset=0
    def take(self,count):
        if self.offset+count>len(self.bits):raise ValueError('Truncated code')
        value=self.bits[self.offset:self.offset+count];self.offset+=count;return value
    def gamma(self):
        zeros=0
        while self.take(1)=='0':
            zeros+=1
            if zeros>31:raise ValueError('Gamma integer exceeds bound')
        return int('1'+self.take(zeros),2)
    def count(self):
        value=self.gamma()-1
        if value>10000:raise ValueError('Record count exceeds bound')
        return value
    def text(self):
        count=self.gamma()-1
        if count>65536:raise ValueError('String length exceeds bound')
        data=self.take(count*8)
        return bytes(int(data[i:i+8],2) for i in range(0,len(data),8)).decode('utf-8')
    def pair(self):return self.text(),self.text()

def decode(bits):
    reader=_Reader(bits);mode=reader.take(1)
    if mode=='0':values=tuple(reader.pair() for _ in range(reader.count()))
    else:
        vocabulary=tuple(reader.pair() for _ in range(reader.count()))
        if len(set(vocabulary))!=len(vocabulary):raise ValueError('Duplicate dictionary entry')
        width=max(0,(len(vocabulary)-1).bit_length());result=[]
        for _ in range(reader.count()):
            if reader.take(1)=='1':result.append(reader.pair())
            else:
                index=int(reader.take(width),2) if width else 0
                if index>=len(vocabulary):raise ValueError('Invalid dictionary address')
                result.append(vocabulary[index])
        values=tuple(result)
    if reader.offset!=len(bits):raise ValueError('Trailing bits')
    return values

def grouped_folds(records):
    records=tuple(records);ids=[r['record_id'] for r in records]
    if len(ids)!=len(set(ids)) or any(not isinstance(r['cluster'],str) or not r['cluster'] for r in records):
        raise ValueError('Unique records and explicit cluster assignments required')
    clusters=sorted({r['cluster'] for r in records});folds=[]
    for cluster in clusters:
        train=tuple(r for r in records if r['cluster']!=cluster);test=tuple(r for r in records if r['cluster']==cluster)
        folds.append({'held_out_cluster':cluster,'train_ids':tuple(r['record_id'] for r in train),
            'test_ids':tuple(r['record_id'] for r in test),'train_clusters':tuple(sorted({r['cluster'] for r in train})),
            'test_clusters':(cluster,),'prospective_blind':False,
            'independence_status':'Declared dependence-control partition; independent historical source ancestry NOT_VERIFIED'})
    return tuple(folds)

def infer_basis(values):
    """Exact code-length search over a declared finite frequency-threshold family.

    This learns a codec dictionary, not a historically necessary alphabet. Literal
    escapes guarantee losslessness and must not be counted as successful predictions.
    """
    values=_values(values)
    if not values:return {'status':'NOT_EVALUATED','selected_model':None,'basis':(),'selected_bits':None,
        'candidates':(),'global_optimality_claim':False,'historical_support':'NOT_VERIFIED'}
    counts=Counter(values);candidates=[];rejected=[]
    def evaluate(model,vocabulary):
        try:encoded=encode_literal(values) if model=='literal' else encode_dictionary(values,vocabulary)
        except ValueError as error:
            rejected.append({'model':model,'basis':vocabulary,'reason':str(error)});return
        candidates.append({'model':model,'basis':vocabulary,'model_bits':encoded['model_bits'],
            'data_bits':encoded['data_bits'],'total_bits':encoded['total_bits'],'literal_escapes':encoded['escaped_values']})
    evaluate('literal',())
    vocabularies=[()]
    for threshold in sorted(set(counts.values())):
        vocabulary=tuple(sorted(value for value,count in counts.items() if count>=threshold))
        if vocabulary not in vocabularies:vocabularies.append(vocabulary)
    for vocabulary in vocabularies:
        evaluate('dictionary',vocabulary)
    if not candidates:raise ValueError('No candidate coding model fits the declared resource bounds')
    minimum=min(c['total_bits'] for c in candidates);minima=tuple(c for c in candidates if c['total_bits']==minimum)
    selected=minima[0]
    return {'status':'EVALUATED','selected_model':selected['model'],'basis':selected['basis'],'selected_bits':minimum,
        'selected':selected,'candidates':tuple(candidates),'rejected_candidates':tuple(rejected),'minimizers':minima,
        'identifiability':'UNIQUE_WITHIN_REGISTERED_CODING_FAMILY' if len(minima)==1 else 'MULTIPLE_DISTINGUISHABLE',
        'family':'literal plus empty dictionary plus dictionaries defined by observed-frequency thresholds',
        'tie_break':'first registered model is a display representative; all minima retained',
        'global_optimality_claim':False,'historical_support':'NOT_VERIFIED','sequence_order_modelled':False,
        'operators':('DICTIONARY_LOOKUP','LITERAL_ESCAPE'),'prediction_success_claim':False}
