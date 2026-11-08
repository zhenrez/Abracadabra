"""NumPy adapter: aligned [P(15) | G(5)], masks and lossless alternatives.

Optional raster geometry requires an explicit font. It measures that font only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from features import parse_ipa

G_NAMES=['endpoints','junction_regions','stroke_segments','holes','reflection_axes']

def phoneme_vector(ipa):
    """15-vector for one phoneme; null/empty -> zeros; sequences reject."""
    if ipa is None or ipa=='': return np.zeros(15,dtype=float)
    parsed=parse_ipa(ipa)
    if parsed['kind']!='segment': raise ValueError('A single supported segment is required')
    return np.asarray(parsed['alternatives'][0]['segments'][0]['vector'],dtype=float)

def raw_table_to_data(text):
    """Read the user's TSV layout: script row, IPA row, optional gloss row."""
    import csv
    from io import StringIO
    from build_dataset import ROWS
    metadata={name:(role,block) for name,_,_,role,block in ROWS}
    rows=list(csv.reader(StringIO(text),delimiter='\t'))
    if not rows or rows[0]!=['Alphabet']+[str(i) for i in range(1,37)]:
        raise ValueError('Expected Alphabet plus columns 1..36')
    cells=[]; current=None; glyphs=None; used=set()
    for row in rows[1:]:
        if not row or not any(row): continue
        if row[0]=='English sound': continue
        if len(row)>37 and any(row[37:]): raise ValueError('Values outside 36 columns')
        values=(row[1:37]+['']*36)[:36]
        if row[0]=='IPA':
            if current is None: raise ValueError('IPA row without script')
            role,block=metadata.get(current,('unvalidated','unclassified'))
            for col,(glyph,ipa) in enumerate(zip(glyphs,values),1):
                if bool(glyph)!=bool(ipa): raise ValueError('Unpaired glyph/IPA at '+current+':'+str(col))
                cells.append(dict(script=current,column=col,glyph=glyph or None,ipa=ipa or None,
                                  role=role,block=block,graph=None,historical_validation='not_independently_validated'))
            current=None
        else:
            if current is not None or row[0] in used: raise ValueError('Missing IPA or repeated script')
            current=row[0]; used.add(current); glyphs=values
    if current is not None: raise ValueError('Missing final IPA row')
    return dict(schema='ariadne.user-table.v1',cells=cells)

def record_distance(left,right):
    """Euclidean distance after per-block normalization on shared valid features.

    Returns NaN when no jointly observed informative block exists. Missing data
    never become evidence of similarity. Unit-norm raw output is a separate view.
    """
    parts=[]
    for block in [slice(0,15),slice(15,20)]:
        common=left['mask'][block]&right['mask'][block]
        a=left['vector'][block][common]; b=right['vector'][block][common]
        if not len(a) or not np.linalg.norm(a) or not np.linalg.norm(b): continue
        parts.append(float(np.sum((normalize_vectors(a)-normalize_vectors(b))**2)))
    return float(np.sqrt(np.mean(parts))) if parts else float('nan')

def normalize_vectors(values):
    values=np.asarray(values,dtype=np.float64)
    if not np.isfinite(values).all(): raise ValueError('Nonfinite feature')
    norms=np.linalg.norm(values,axis=-1,keepdims=True)
    return np.divide(values,norms,out=np.zeros_like(values),where=norms>0)

def validate_normalized(values,atol=1e-10):
    values=np.asarray(values,dtype=float)
    if not np.isfinite(values).all(): return False
    norms=np.linalg.norm(values,axis=-1)
    return bool(np.all(np.isclose(norms,1,atol=atol,rtol=0)|np.isclose(norms,0,atol=atol,rtol=0)))

def thin_bitmap(bitmap):
    """Zhang-Suen thinning; 8-connected foreground, deterministic boolean pixels."""
    image=np.pad(np.asarray(bitmap,dtype=bool),1)
    if image.ndim!=2: raise ValueError('Expected 2D bitmap')
    changed=True
    while changed:
        changed=False
        for phase in (0,1):
            p=[image[:-2,1:-1],image[:-2,2:],image[1:-1,2:],image[2:,2:],
               image[2:,1:-1],image[2:,:-2],image[1:-1,:-2],image[:-2,:-2]]
            neighbors=sum(x.astype(np.uint8) for x in p)
            transitions=sum((~p[i]&p[(i+1)%8]).astype(np.uint8) for i in range(8))
            cond=(~(p[0]&p[2]&p[4])&~(p[2]&p[4]&p[6])) if phase==0 else (~(p[0]&p[2]&p[6])&~(p[0]&p[4]&p[6]))
            remove=image[1:-1,1:-1]&(neighbors>=2)&(neighbors<=6)&(transitions==1)&cond
            if remove.any():
                image[1:-1,1:-1][remove]=False; changed=True
    return image[1:-1,1:-1]

def bitmap_geometry(bitmap):
    image=np.asarray(bitmap,dtype=bool)
    if image.ndim!=2 or not image.any(): raise ValueError('Nonempty 2D ink bitmap required')
    ys,xs=np.nonzero(image); image=image[ys.min():ys.max()+1,xs.min():xs.max()+1]
    # Hole count: padded background components with four-connectivity, minus exterior.
    _,background_components=ndimage.label(~np.pad(image,1),ndimage.generate_binary_structure(2,1))
    holes=background_components-1
    skeleton=thin_bitmap(image)
    coordinates=set(map(tuple,np.argwhere(skeleton)))
    adjacent={p:{(p[0]+dy,p[1]+dx) for dy in (-1,0,1) for dx in (-1,0,1)
                 if (dy or dx) and (p[0]+dy,p[1]+dx) in coordinates} for p in coordinates}
    endpoints={p for p in coordinates if len(adjacent[p])==1}
    junctions={p for p in coordinates if len(adjacent[p])>=3}
    regions=[]; remaining=set(junctions)
    while remaining:
        stack=[min(remaining)]; group=set()
        while stack:
            p=stack.pop()
            if p in group: continue
            group.add(p); stack.extend(adjacent[p]&remaining-group)
        remaining-=group; regions.append(group)
    node_groups=regions+[{p} for p in sorted(endpoints)]
    node_of={p:i for i,g in enumerate(node_groups) for p in g}
    visited=set(); edges=0
    def edge(a,b): return tuple(sorted((a,b)))
    for group in node_groups:
        for p in sorted(group):
            for q in sorted(adjacent[p]):
                if q in group or edge(p,q) in visited: continue
                edges+=1; previous,current=p,q; visited.add(edge(p,q))
                while current not in node_of:
                    choices=adjacent[current]-{previous}
                    if len(choices)!=1: break
                    nxt=next(iter(choices)); visited.add(edge(current,nxt)); previous,current=current,nxt
    # Components with no endpoints/junctions are closed degree-two paths.
    remaining=coordinates-set(node_of)
    while remaining:
        stack=[min(remaining)]; group=set()
        while stack:
            p=stack.pop()
            if p in group: continue
            group.add(p); stack.extend(adjacent[p]&remaining-group)
        remaining-=group
        if all(len(adjacent[p])==2 for p in group) and not any(adjacent[p]&set(node_of) for p in group): edges+=1
    # Four exact reflection tests about bounding-box-centered square canvas.
    h,w=image.shape
    axes=int(np.array_equal(image,image[:,::-1]))+int(np.array_equal(image,image[::-1,:]))
    if h==w:
        axes+=int(np.array_equal(image,image.T))+int(np.array_equal(image,image[::-1,::-1].T))
    else:
        # An exact diagonal reflection requires equal bounding-box extents.
        axes+=0
    return np.array([len(endpoints),len(regions),edges,holes,axes],dtype=float),dict(
        skeleton_pixels=len(coordinates),isolated_pixels=sum(not adjacent[p] for p in coordinates),
        convention='Zhang-Suen; 8-connected skeleton; junction pixels contracted; 4-connected background holes; four exact reflections')

class FontGeometry:
    def __init__(self,font_path,size=96):
        from PIL import ImageFont
        from fontTools.ttLib import TTFont
        self.path=Path(font_path); self.sha256=hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.font=ImageFont.truetype(str(self.path),size=size)
        with TTFont(str(self.path)) as f: self.cmap=f.getBestCmap()
        self.size=size
    def __call__(self,glyph):
        from PIL import Image, ImageDraw
        if any(ord(c) not in self.cmap for c in glyph): return None
        bbox=self.font.getbbox(glyph)
        if bbox is None: return None
        x0,y0,x1,y1=bbox
        if x1<=x0 or y1<=y0: return None
        image=Image.new('L',(x1-x0+16,y1-y0+16),0)
        ImageDraw.Draw(image).text((8-x0,8-y0),glyph,font=self.font,fill=255)
        vector,meta=bitmap_geometry(np.asarray(image)>=128)
        return vector,dict(meta,font_sha256=self.sha256,font_size=self.size,threshold=128,
                           source='modern font proxy; not historical tracing')

def table_to_numpy(data,geometry=None):
    scripts=list(dict.fromkeys(c['script'] for c in data['cells']))
    dtype=np.dtype([('vector','f8',(20,)),('mask','?',(20,)),('normalized','f8',(20,)),
                    ('kind','U20'),('ipa',object),('glyph',object),('details',object)])
    output=np.zeros((len(scripts),36),dtype=dtype)
    seen=set()
    for c in data['cells']:
        key=(scripts.index(c['script']),c['column']-1)
        if not 0<=key[1]<36 or key in seen: raise ValueError('Duplicate or invalid matrix address')
        seen.add(key); p=parse_ipa(c['ipa']); record=output[key]
        record['ipa']=c['ipa']; record['glyph']=c['glyph']; record['kind']=p['kind']
        g=geometry(c['glyph']) if geometry and c['glyph'] else None
        gv=np.zeros(5) if g is None else np.asarray(g[0],dtype=float)
        if gv.shape!=(5,) or not np.isfinite(gv).all() or np.any(gv<0): raise ValueError('Invalid geometry')
        record['vector'][15:]=gv
        record['mask'][15:]=g is not None
        if p['kind']=='segment':
            s=p['alternatives'][0]['segments'][0]
            record['vector'][:15]=s['vector']; record['mask'][:15]=s['mask']
        # Sequence/alternative data remain ordered rather than averaged into a fake phoneme.
        expanded=[]
        for a in p['alternatives']:
            expanded.append(np.array([np.concatenate((s['vector'],gv)) for s in a['segments']]))
        record['details']=dict(parsed=p,segment_vectors=expanded,geometry=None if g is None else g[1],
                               atomic_vector_available=p['kind']=='segment')
    output['normalized']=normalize_vectors(output['vector'])
    if not validate_normalized(output['normalized']): raise ValueError('Normalization failed')
    return scripts,output

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--font',type=Path); parser.add_argument('--table-tsv',type=Path); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): raise SystemExit('Use a new output directory')
    data=raw_table_to_data(args.table_tsv.read_text(encoding='utf-8')) if args.table_tsv else json.loads((Path(__file__).parent/'table.json').read_text(encoding='utf-8'))
    geometry=FontGeometry(args.font) if args.font else None
    scripts,array=table_to_numpy(data,geometry)
    args.output.mkdir(parents=True)
    # Numeric arrays only: safe to load without pickle. Rich typed data are in vectors.json.
    np.savez_compressed(args.output/'matrix.npz',vector=array['vector'],mask=array['mask'],normalized=array['normalized'],
                        scripts=np.array(scripts),columns=np.arange(1,37),kind=array['kind'])
    report=dict(shape=list(array.shape),vector_dimension=20,geometry_features=G_NAMES,
                normalized=validate_normalized(array['normalized']),
                atomic_cells=int(sum(array['details'][i,j]['atomic_vector_available'] for i in range(len(scripts)) for j in range(36))),
                glyph_geometry_cells=int(array['mask'][:,:,15].sum()),
                font=None if geometry is None else dict(path=str(geometry.path),sha256=geometry.sha256,size=geometry.size),
                missing_policy='zero vector plus false mask; cosine undefined for all-zero vectors; restrict distance to jointly available blocks',
                geometry_scope='modern font proxy only' if geometry else 'No geometry supplied; zero geometry block, false mask')
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
