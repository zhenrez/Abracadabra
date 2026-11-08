"""Extract the declared MT XML and SP Text-Fabric Gen5/11 source regions."""
from pathlib import Path
import bisect,hashlib,json,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def tf_feature(path):
    result={};started=False;last=0
    for line in path.read_text(encoding='utf-8').splitlines():
        if not started:
            if line=='':started=True
            continue
        if '\t' in line:
            spec,value=line.split('\t',1)
            if '-' in spec:lo,hi=map(int,spec.split('-',1));nodes=range(lo,hi+1)
            else:nodes=[int(spec)]
        else:nodes=[last+1];value=line
        for node in nodes:result[node]=value;last=node
    return result

def interval(spec):
    points=[]
    for part in spec.split(','):
        points.extend(map(int,part.split('-')))
    return min(points),max(points)

def main():
    xml=BASE/'MT-OSHB-Genesis.xml';root=ET.fromstring(xml.read_bytes());mt=[]
    for node in root.iter():
        if node.tag.split('}')[-1]!='verse':continue
        ref=node.attrib.get('osisID','')
        if not ref.startswith(('Gen.5.','Gen.11.')):continue
        words=[{'text':''.join(w.itertext()),'id':w.attrib.get('id'),'lemma':w.attrib.get('lemma'),'morph':w.attrib.get('morph')} for w in node.iter() if w.tag.split('}')[-1]=='w']
        mt.append({'reference':ref,'words':words,'text':' '.join(w['text'] for w in words),'sourcePath':xml.name,'sourceSha256':sha(xml),'layer':'OSHB WLC XML transcription; not independently collated manuscript image'})
    folder=BASE/'SP-7.3.0';books=tf_feature(folder/'book.tf');chapters=tf_feature(folder/'chapter.tf');verses=tf_feature(folder/'verse.tf');cons=tf_feature(folder/'g_cons.tf');trail=tf_feature(folder/'trailer.tf');slots={n:interval(v) for n,v in tf_feature(folder/'oslots.tf').items()}
    book_intervals=sorted((slots[n][0],slots[n][1],title) for n,title in books.items())
    chapter_intervals=sorted((slots[n][0],slots[n][1],int(number)) for n,number in chapters.items())
    word_intervals=sorted((slots[n][0],slots[n][1],n) for n in cons)
    chapter_starts=[x[0] for x in chapter_intervals];word_starts=[x[0] for x in word_intervals]
    sp=[]
    for node,number in verses.items():
        start,end=slots[node]
        book=next(title for lo,hi,title in book_intervals if lo<=start<=hi)
        chapter=chapter_intervals[bisect.bisect_right(chapter_starts,start)-1]
        if book!='Genesis' or chapter[2] not in [5,11]:continue
        selected=[]
        i=bisect.bisect_left(word_starts,start)
        while i<len(word_intervals) and word_intervals[i][0]<=end:
            lo,hi,word=word_intervals[i]
            assert start<=lo<=hi<=end
            selected.append({'node':word,'signSlotRangeInclusive':[lo,hi],'consonantalTransliteration':cons[word],'trailerRaw':trail.get(word,'')});i+=1
        text=''.join(w['consonantalTransliteration']+w['trailerRaw'].replace('\\n','\n').replace('\\t','\t') for w in selected)
        sp.append({'reference':'Gen.'+str(chapter[2])+'.'+number,'verseNode':node,'signSlotRangeInclusive':[start,end],'words':selected,'text':text,'representation':'Source g_cons transliteration plus trailer; not Samaritan glyphs or a phonetic reading','manuscriptBasis':'Dublin Chester Beatty751 for Genesis; dataset source declaration','sourceCommit':'8842267d29e37bf786b95209c76852461c389144','datasetVersion':'7.3.0'})
    sp_tree=json.loads((BASE/'SP-tree.json').read_text(encoding='utf-8'));tree_index={x['path']:x for x in sp_tree['tree']};bindings=[]
    for p in sorted(folder.glob('*.tf')):
        raw=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==tree_index['tf/7.3.0/'+p.name]['sha']
        bindings.append({'path':'SP-7.3.0/'+p.name,'sha256':sha(p),'gitBlobSha':blob,'bytes':len(raw)})
    result={'schema':'sunny.primary-genesis-text-regions.v1','MT':mt,'SP':sp,'SPsourceBindings':bindings,'SPlicense':'Source files declare CC BY-NC4.0; a Zenodo search result showed CC BY4.0. Preserve discrepancy and use the captured file declaration.','interpretiveBoundary':'Text and token boundaries extracted mechanically. Numeric age interpretation and biological/genealogical meaning require separately declared claims.'}
    (BASE/'genesis-primary-regions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for family,rows in [('MT',mt),('SP',sp)]:
        print(family,len(rows))
        for row in rows:
            if row['reference'] in ['Gen.5.3','Gen.5.18','Gen.5.25','Gen.5.28','Gen.11.12','Gen.11.13','Gen.11.14','Gen.11.15','Gen.11.16','Gen.11.17']:print(row['reference'],row['text'])

if __name__=='__main__':main()
