"""Literal-label entropy and conditional code-length audit; no historical recoding."""
import json
from pathlib import Path
from collections import Counter
import numpy as np
from features import parse_ipa

NAMES=['Proto-Sinaitic (proxy)','Phoenician','Paleo-Hebrew','Imperial Aramaic','Square Hebrew','Syriac']
ROOT=Path(__file__).resolve().parent

def extract(matrix):
    x=np.asarray(matrix,dtype=str)
    if x.ndim!=2 or x.shape[1]!=22: raise ValueError('Expected n x 22, including 14 x 22 when actually supplied')
    entropy=[]
    for col in x.T:
        p=np.array(list(Counter(col).values()))/len(col)
        entropy.append(float(-np.sum(p*np.log2(p))))
    # Candidate means are explicitly an analysis projection, not observed phonemes.
    vectors=np.array([[np.mean([np.mean([s['vector'] for s in a['segments']],axis=0)
                        for a in parse_ipa(raw)['alternatives']],axis=0) for raw in row] for row in x])
    samples=vectors.reshape(-1,15)
    try:
        from sklearn.decomposition import PCA
        ratios=PCA().fit(samples).explained_variance_ratio_
        backend='scikit-learn'
    except ImportError:
        singular=np.linalg.svd(samples-samples.mean(axis=0),compute_uv=False)
        ratios=singular**2/np.sum(singular**2)
        backend='NumPy centered SVD (scikit-learn unavailable)'
    correlations=[]
    for row in vectors:
        correlations.append([float(np.corrcoef(np.arange(1,23),row[:,j])[0,1])
                             if np.std(row[:,j]) else None for j in range(15)])
    residual=np.argwhere(x!=x[0])
    # Exact two-part prefix-decodable candidates; dictionary supplied externally.
    # k exceptions: 9-bit k, enumerative positions, 5-bit literal labels.
    import math
    labels=len(set(x.ravel())); width=math.ceil(math.log2(labels)); n=x.size; k=len(residual)
    flat=n*width
    shared=22*width+math.ceil(math.log2(n+1))+math.ceil(math.log2(math.comb(n,k)))+k*width
    return dict(shape=list(x.shape),entropy=entropy,zero_entropy_columns=[i+1 for i,h in enumerate(entropy) if h==0],
                literal_residual_cells=k,residual_addresses=(residual+1).tolist(),labels=labels,label_width=width,
                conditional_code_bits=dict(flat=flat,base_plus_exceptions=shared,model_selector_bits=1),
                pca_variance_ratio=ratios.tolist(),pca_backend=backend,pearson_index_by_feature=correlations,
                projection='Equal weighting of listed alternatives and sequence segments; sensitivity model, not historical probabilities')

if __name__=='__main__':
    data=json.loads((ROOT/'table.json').read_text(encoding='utf-8'))['cells']
    matrix=[[c['ipa'] for c in data if c['script']==name and c['column']<=22] for name in NAMES]
    result=extract(matrix)
    (ROOT/'carrier-statistics.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
