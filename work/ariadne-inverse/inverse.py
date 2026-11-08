"""Exact orbit factoring under a declared finite operator family.

This is an empirical articulation codec, not a recovered historical mechanism.
Operators act only on 15-feature vectors; raw symbols and extensions are residuals.
"""
def apply_operator(vector,voicing,emphasis):
    out=list(vector)
    if voicing: out[12],out[13]=out[13],out[12]
    if emphasis: out[14]=1-out[14]
    return out

def reconstruct(segments):
    roots={}; assignments=[]
    for segment in segments:
        v=segment['vector']; mask=segment['mask']
        # Canonical gauge: choose unvoiced, non-pharyngealized orbit representative.
        root=list(v); root[12:]=[0,1,0]
        key=tuple(root)+tuple(mask)
        if key not in roots: roots[key]=len(roots)
        op=[v[12],v[14]]
        predicted=apply_operator(root,*op)
        edits=[dict(feature=i,expected=a,observed=b) for i,(a,b) in enumerate(zip(predicted,v)) if a!=b]
        assignments.append(dict(root=roots[key],operator=op,coarse_feature_edits=edits,
                                residual=dict(ipa=segment['ipa'],extended=segment['extended'],
                                              modifiers=segment['modifiers'],secondary_place=segment['secondary_place'])))
    basis=[None]*len(roots)
    for key,index in roots.items(): basis[index]=dict(vector=list(key[:15]),mask=list(key[15:]))
    return dict(basis=basis,assignments=assignments,
                operators=['toggle voiced/unvoiced flags','toggle pharyngealized flag'],
                minimality='One root per observed orbit is necessary and sufficient under these fixed operators. This is not minimality among all possible machines.',
                gauge='unvoiced non-pharyngealized representative; may be unattested or physiologically inappropriate',
                interpretation='Declared four-element abstract action, not learned sound laws. Zero coarse residual is guaranteed by construction; historical transitions unidentified.')
