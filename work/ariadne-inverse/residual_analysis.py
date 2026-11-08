"""Source-qualified categorical residuals. Unavailable predictions are not zero errors."""
from collections import Counter,defaultdict
from pathlib import Path
import json,math,hashlib
import numpy as np
from features import parse_ipa
from vowel_drift import CARRIER,GREEK,LATIN,VowelDriftOperator
from drift_engine import FRICATIVES

ROOT=Path(__file__).resolve().parent
ALIGNED=['Proto-Sinaitic (proxy)','Phoenician','Paleo-Hebrew','Imperial Aramaic','Square Hebrew','Syriac']
SIBILANTS=(7,15,18,21)

def entropy(values):
    counts=Counter(values);n=sum(counts.values())
    return -sum((v/n)*math.log2(v/n) for v in counts.values()) if n else None

def mutual_information(pairs):
    if not pairs:return None
    joint=Counter(pairs);left=Counter(x for x,y in pairs);right=Counter(y for x,y in pairs);n=len(pairs)
    return sum(c/n*math.log2(c*n/(left[x]*right[y])) for (x,y),c in joint.items())

def prediction(script,column):
    if script in ALIGNED and column<=22:
        values={CARRIER[column]}
        if script in ('Square Hebrew','Syriac') and column in FRICATIVES:values.add(FRICATIVES[column])
        return column,values,'identity plus declared parity states'
    target={'Ancient Greek (Ionic)':GREEK,'Old Latin (21-character convention)':LATIN}.get(script)
    if target:
        for i,mapping in target.mappings.items():
            if mapping.target_index==column:
                return i,{VowelDriftOperator().apply_vowel_drift(i,target.name,include_glide=True)},'declared vowel/glide correspondence'
    return None

def analyze(cells):
    scripts=list(dict.fromkeys(c['script'] for c in cells));records=[];ghosts=[]
    for c in cells:
        p=prediction(c['script'],c['column']);raw=c['ipa'];kind=parse_ipa(raw)['kind']
        record=dict(script=c['script'],target_column=c['column'],glyph=c['glyph'],observed=raw,
                    canonical_column=p[0] if p else None,predicted=sorted(p[1]) if p else None,
                    operator=p[2] if p else None,residual=None)
        if kind in ('missing','unknown','unresolved_label'):record['status']=kind
        elif p:
            readings=set(raw.split('/'));outside=readings-p[1]
            record.update(status='unpredicted_reading' if outside else 'compatible',
                          residual=int(bool(outside)),unpredicted_readings=sorted(outside),
                          omitted_allowed_readings=sorted(p[1]-readings))
        else:record['status']='unmapped'
        records.append(record)
        if kind=='unknown' and c['glyph'] is not None:
            ghosts.append(dict(script=c['script'],target_column=c['column'],glyph=c['glyph'],raw_value=raw,
              structural_position_preserved=True,phonetic_status='unknown',silent=False,
              silence_status='not established',sacred_template='sequence preservation stipulated; sacred intent untested'))
    canonical=[]
    for col in range(1,23):
        rows=[r for r in records if r['canonical_column']==col and r['residual'] is not None]
        canonical.append(dict(column=col,carrier=CARRIER[col],n=len(rows),
             observed_label_entropy=entropy([r['observed'] for r in rows]),
             binary_residual_entropy=entropy([r['residual'] for r in rows]),
             mismatches=sum(r['residual'] for r in rows)))
    raw_entropy=[]
    for col in range(1,37):
        values=[c['ipa'] for c in cells if c['column']==col and c['script']!='English'
                and parse_ipa(c['ipa'])['kind'] not in ('missing','unknown','unresolved_label')]
        raw_entropy.append(dict(column=col,n=len(values),entropy=entropy(values)))
    comparison=[]
    for label,names in [('Other 13 historical/proxy rows',[s for s in scripts if s not in ('English','Old Persian')]),('Old Persian',['Old Persian'])]:
        subset=[c for c in cells if c['script'] in names and c['ipa'] is not None]
        counts=Counter(parse_ipa(c['ipa'])['kind'] for c in subset)
        scored=[r for r in records if r['script'] in names and r['residual'] is not None]
        comparison.append(dict(group=label,populated=len(subset),kinds=dict(counts),
          scored_cells=len(scored),mismatches=sum(r['residual'] for r in scored),
          historical_topological_MI=None,origin_classification='not inferred'))
    persian=defaultdict(set)
    for c in cells:
        if c['script']=='Old Persian' and c['ipa'] and c['ipa'][-1:] in ('a','i','u') and len(c['ipa'])>1:
            persian[c['ipa'][:-1]].add(c['ipa'][-1])
    return dict(records=records,unknown_glyph_nodes=ghosts,canonical_entropy=canonical,
        raw_ordinal_entropy=raw_entropy,comparison=comparison,
        persian_vowel_families={k:sorted(v) for k,v in persian.items()},
        historical_TMI=dict(value=None,status='unidentifiable',reason='No paired historical graphs or independent cross-script alignment; modern-font features do not establish historical topology'),
        scope='Canonical scoring covers six aligned rows and ten declared vowel/glide correspondences. Emission-matched permutations are descriptive and excluded from predictive scoring. Alternatives use conservative set coverage, not a calibrated likelihood.')

def plot(result,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    scripts=list(dict.fromkeys(r['script'] for r in result['records']))
    values=np.full((len(scripts),36),np.nan)
    for r in result['records']:
        if r['residual'] is not None:values[scripts.index(r['script']),r['target_column']-1]=r['residual']
    fig,(ax,bx)=plt.subplots(2,1,figsize=(15,10),gridspec_kw={'height_ratios':[3,1]},layout='constrained')
    cmap=matplotlib.colors.ListedColormap(['#cee9df','#c33d4a']);cmap.set_bad('#dedede')
    ax.imshow(np.ma.masked_invalid(values),vmin=0,vmax=1,cmap=cmap,aspect='auto')
    ax.set_yticks(range(len(scripts)),scripts,fontsize=8);ax.set_xticks(range(36),range(1,37),fontsize=8)
    ax.set_xlabel('Original target column (canonical correspondence stored in JSON)')
    ax.set_title('Operator residuals: green = compatible; red = unpredicted reading; gray = unscored')
    for r in result['unknown_glyph_nodes']:
        ax.text(r['target_column']-1,scripts.index(r['script']),'?',ha='center',va='center',fontsize=9)
    rows=result['canonical_entropy'];x=np.arange(1,23)
    bx.bar(x,[r['observed_label_entropy'] for r in rows],color=['#b44975' if i in SIBILANTS else '#527c9c' for i in x])
    bx.set_xticks(x);bx.set_ylabel('Shannon entropy (bits)');bx.set_xlabel('Canonical carrier column; unequal coverage by column')
    bx.set_title('Observed-label entropy within supported correspondence subset; pink = requested sibilants')
    fig.savefig(path,dpi=160);plt.close(fig)

def main():
    raw=(ROOT/'table.json').read_bytes();result=analyze(json.loads(raw)['cells'])
    result['input_sha256']=hashlib.sha256(raw).hexdigest()
    (ROOT/'residual-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'dead-nodes.json').write_text(json.dumps(result['unknown_glyph_nodes'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    plot(result,ROOT/'residual-heatmap.png')
    print(json.dumps(dict(status_counts=dict(Counter(r['status'] for r in result['records'])),
         sibilants=[r for r in result['canonical_entropy'] if r['column'] in SIBILANTS],
         comparison=result['comparison'],persian_vowel_families=result['persian_vowel_families']),ensure_ascii=True,indent=2))

if __name__=='__main__':main()
