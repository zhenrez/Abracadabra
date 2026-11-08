"""Coarse articulatory features and annotated graph descriptors. No font inference."""
import math
import unicodedata

FEATURES = ['bilabial','labiodental','dental_alveolar','postalveolar_palatal','velar',
            'uvular_pharyngeal','glottal','stop','fricative','nasal','approximant_liquid',
            'vowel_resonant','voiced','unvoiced','pharyngealized']
INVENTORY = {}
for place, manner, voiceless, voiced in [
    (0,0,'p','b'),(2,0,'t','d'),(3,0,'c','ɟ'),(4,0,'k','gɡ'),(5,0,'q','ɢ'),(6,0,'ʔ',''),
    (0,1,'ɸ','β'),(1,1,'f','v'),(2,1,'θsɬ','ðzɮ'),(3,1,'ʃç','ʒʝ'),(4,1,'x','ɣ'),
    (5,1,'χħ','ʁʕ'),(6,1,'h','ɦ'),(0,2,'','m'),(2,2,'','n'),(3,2,'','ɲ'),(4,2,'','ŋ'),
    (2,3,'','lrɹɾ'),(3,3,'','j'),(4,3,'','wɰ')]:
    for symbols, voice in [(voiceless,0),(voiced,1)]:
        for symbol in symbols:
            INVENTORY[symbol]=(place,manner,voice)
for symbol in 'aeiouyɛɔɑæœɪʊəʌɒɐɜɞɨʉɯɤøɶ':
    INVENTORY[symbol]=(None,4,1)
MODIFIERS={'ˤ':'pharyngealized','ʰ':'aspirated','ʷ':'labialized','ː':'long','ˑ':'half_long'}
# IPA vowel coordinates: height 1=close..7=open; backness 1=front..3=back.
VOWELS={}
for symbols,height,backness,rounded in [
    ('i',1,1,0),('y',1,1,1),('ɨ',1,2,0),('ʉ',1,2,1),('ɯ',1,3,0),('u',1,3,1),
    ('ɪ',2,1,0),('ʊ',2,3,1),('e',3,1,0),('ø',3,1,1),('ɤ',3,3,0),('o',3,3,1),
    ('ə',4,2,0),('ɛ',5,1,0),('œ',5,1,1),('ɜ',5,2,0),('ɞ',5,2,1),('ʌ',5,3,0),('ɔ',5,3,1),
    ('æ',6,1,0),('ɐ',6,2,0),('a',7,1,0),('ɶ',7,1,1),('ɑ',7,3,0),('ɒ',7,3,1)]:
    for s in symbols: VOWELS[s]=(height,backness,rounded)

def vectorize_phoneme(ipa):
    """One base IPA symbol plus supported modifiers; rejects sequences/alternatives."""
    value=unicodedata.normalize('NFC',ipa)
    if not value or value[0] not in INVENTORY or any(c not in MODIFIERS for c in value[1:]):
        raise ValueError('Expected one supported IPA segment: '+repr(ipa))
    place,manner,voice=INVENTORY[value[0]]
    vector=[0]*15
    mask=[1]*15
    if place is None:
        mask[:7]=[0]*7  # consonantal place is inapplicable, not glottal
    else:
        vector[place]=1
    vector[7+manner]=1
    vector[12:]=[voice,1-voice,int('ˤ' in value)]
    return dict(ipa=value, vector=vector, mask=mask,
                extended=dict(vowel_height=VOWELS[value[0]][0] if place is None else None,
                              vowel_backness=VOWELS[value[0]][1] if place is None else None,
                              vowel_rounded=VOWELS[value[0]][2] if place is None else None,
                              aspirated=int('ʰ' in value),labialized=int('ʷ' in value),
                              length=2 if 'ː' in value else 1 if 'ˑ' in value else 0,
                              affrication=None),
                modifiers=[MODIFIERS[c] for c in value[1:]],
                secondary_place=['bilabial'] if value[0]=='w' else [],
                losses=['vowel_quality'] if place is None else
                       ['trill_tap_lateral_merged'] if value[0] in 'lrɹɾ' else [])

def parse_ipa(raw):
    if raw is None: return dict(kind='missing',alternatives=[])
    if raw=='?': return dict(kind='unknown',alternatives=[])
    if '³' in raw: return dict(kind='unresolved_label',raw=raw,alternatives=[])
    alternatives=[]
    for candidate in raw.split('/'):
        segments=[]; stress=[]
        for char in unicodedata.normalize('NFC',candidate):
            if char in 'ˈˌ':
                stress.append(dict(before_segment=len(segments),mark=char)); continue
            if char in MODIFIERS:
                if not segments: raise ValueError('Orphan modifier')
                segments[-1]+=char
            elif char in INVENTORY:
                segments.append(char)
            else: raise ValueError('Unsupported IPA symbol '+repr(char))
        if not segments: raise ValueError('Empty IPA candidate')
        alternatives.append(dict(segments=[vectorize_phoneme(s) for s in segments],stress=stress))
    return dict(kind='alternatives' if len(alternatives)>1 else
                'segment' if len(alternatives[0]['segments'])==1 else 'sequence',
                alternatives=alternatives,
                segmentation='literal IPA symbols; untied affricate/diphthong boundaries unasserted')

def masked_distance(a,b):
    indices=[i for i in range(15) if a['mask'][i] and b['mask'][i]]
    return sum(a['vector'][i]!=b['vector'][i] for i in indices)/len(indices) if indices else None

def graph_features(graph):
    """Undirected embedded skeleton; vertices explicitly include all junctions/bends.

    Crossing connectivity and tracing are annotation decisions. Multiedges and loops
    are allowed. Symmetry is geometric about the vertex centroid, not topological.
    """
    if graph is None: return None
    if not graph.get('source') or not graph.get('annotation_convention'):
        raise ValueError('Graph requires source and annotation convention')
    points=graph['vertices']; edges=graph['edges']; n=len(points)
    if not n: raise ValueError('Empty graph')
    if any(len(p)!=2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in p) for p in points):
        raise ValueError('Invalid coordinates')
    if len({tuple(p) for p in points})!=n: raise ValueError('Duplicate coordinates')
    adjacent=[set() for _ in points]; degree=[0]*n; histogram=[0]*8
    for edge in edges:
        if len(edge)!=2 or any(type(v) is not int or v<0 or v>=n for v in edge):
            raise ValueError('Invalid edge')
        a,b=edge; adjacent[a].add(b); adjacent[b].add(a); degree[a]+=1; degree[b]+=1
        dx=points[b][0]-points[a][0]; dy=points[b][1]-points[a][1]
        if dx or dy: histogram[int((math.atan2(dy,dx)%math.pi)/math.pi*8)%8]+=1
    visited=set(); components=0
    for v in range(n):
        if v in visited: continue
        components+=1; stack=[v]
        while stack:
            k=stack.pop()
            if k in visited: continue
            visited.add(k); stack.extend(adjacent[k]-visited)
    cx=sum(p[0] for p in points)/n; cy=sum(p[1] for p in points)/n
    scale=max(max(abs(p[0]-cx),abs(p[1]-cy)) for p in points) or 1
    canonical_edges=sorted(tuple(sorted(e)) for e in edges)
    def symmetry(transform):
        mapping=[]
        for x,y in points:
            tx,ty=transform(x-cx,y-cy); target=(tx+cx,ty+cy)
            matches=[i for i,p in enumerate(points) if math.dist(p,target)<=scale*1e-8]
            if len(matches)!=1: return 0
            mapping.append(matches[0])
        if len(set(mapping))!=n: return 0
        return int(sorted(tuple(sorted((mapping[a],mapping[b]))) for a,b in edges)==canonical_edges)
    summary=[n,len(edges),components,len(edges)-n+components,
             sum(d==1 for d in degree),sum(d>=3 for d in degree)]
    axes=[symmetry(lambda x,y:(-x,y)),symmetry(lambda x,y:(x,-y)),symmetry(lambda x,y:(-x,-y))]
    return dict(names=['vertices','edges','components','cycle_rank','endpoints','junctions']+
                ['angle_bin_'+str(i) for i in range(8)]+['vertical_reflection','horizontal_reflection','rotation_180'],
                vector=summary+histogram+axes,
                note='Cycle rank counts independent cycles, not every visual enclosed region. Edges are skeleton segments, not pen strokes.')
