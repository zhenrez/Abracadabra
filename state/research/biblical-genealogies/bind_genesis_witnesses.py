"""Bind finite, inspected Genesis readings to their local source artifacts.

Values are declared interpretations of the cited tokens/images, not an OCR oracle.
This script reads only the explicit public research sources listed below.
"""
from pathlib import Path
import hashlib,json

BASE=Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    region_path=BASE/'genesis-primary-regions.json'
    regions=json.loads(region_path.read_text(encoding='utf-8'))
    mt_path=BASE/'MT-OSHB-Genesis.xml';mt_raw=mt_path.read_bytes()
    mt_commit=json.loads((BASE/'MT-OSHB-commit.json').read_text(encoding='utf-8'))
    mt_blob=hashlib.sha1(b'blob '+str(len(mt_raw)).encode()+b'\0'+mt_raw).hexdigest()
    assert mt_blob==next(f['sha'] for f in mt_commit['files'] if f['filename']=='wlc/Gen.xml')
    pdf=BASE/'Greek-Swete-original-volume1.pdf'
    pages=[(39,7),(40,8),(41,9),(49,17),(50,18)]
    bindings=[{'path':pdf.name,'sha256':digest(pdf),'bytes':pdf.stat().st_size}]
    for number,printed in pages:
        path=BASE/f'Greek-Swete-pdfpage{number}.png'
        bindings.append({'path':path.name,'sha256':digest(path),'pdfPageOneBased':number,'printedPage':printed,'visuallyInspected':True})
    detail=BASE/'Greek-Swete-pdfpage49-detail.png'
    bindings.append({'path':detail.name,'sha256':digest(detail),'pdfPageOneBased':49,'printedPage':17,'visuallyInspected':True,'purpose':'Higher-resolution apparatus reading; supersedes earlier mistaken D=400 interpretation.'})
    # ref, named parent, named descendant, MT, SP, Swete main, printed page
    table=[
      ('Gen.5.3','Adam','Seth',130,130,230,7),
      ('Gen.5.6','Seth','Enosh',105,105,205,7),
      ('Gen.5.9','Enosh','Kenan I',90,90,190,8),
      ('Gen.5.12','Kenan I','Mahalalel',70,70,170,8),
      ('Gen.5.15','Mahalalel','Jared',65,65,165,8),
      ('Gen.5.18','Jared','Enoch (son of Jared)',162,62,162,8),
      ('Gen.5.21','Enoch (son of Jared)','Methuselah',65,65,165,8),
      ('Gen.5.25','Methuselah','Lamech (father of Noah)',187,67,187,8),
      ('Gen.5.28','Lamech (father of Noah)','Noah',182,53,188,9),
      ('Gen.11.12','Arpachshad','Shelah',35,135,135,17),
      ('Gen.11.14','Shelah','Eber',30,130,130,18),
      ('Gen.11.16','Eber','Peleg',34,134,134,18),
      ('Gen.11.18','Peleg','Reu',30,130,130,18),
      ('Gen.11.20','Reu','Serug',32,132,132,18),
      ('Gen.11.22','Serug','Nahor',30,130,130,18),
      ('Gen.11.24','Nahor','Terah',29,79,79,18),
    ]
    claims=[]
    for ref,parent,child,mt,sp,gr,page in table:
        for family,value in [('MT',mt),('SP',sp),('Greek_Swete1887_main',gr)]:
            target='Cainan II' if family.startswith('Greek') and ref=='Gen.11.12' else child
            claim={'id':'bible:primary-age:'+family+':'+ref,'family':family,'reference':ref,'parentRole':parent,'descendantRole':target,'reportedAgeAtNamedBegetting':value,'unit':'reported-year','relationshipType':'textual-genealogical-begetting','biologicalImmediacyIndependentlyEstablished':False}
            if family in ['MT','SP']:
                row=next(x for x in regions[family] if x['reference']==ref)
                claim['sourceRegion']={'packet':region_path.name,'packetSha256':digest(region_path),'family':family,'reference':ref,'literalSourceText':row['text'],'wordOrNodeAddresses':[x.get('id',x.get('node')) for x in row['words']]}
                claim['sourceLayer']='digital scholarly transcription; original manuscript image not independently inspected'
            else:
                claim['sourceRegion']={'pdf':pdf.name,'pdfSha256':digest(pdf),'printedPage':page,'pdfPageOneBased':next(n for n,p in pages if p==page),'visuallyReviewedPublishedText':True}
                claim['sourceLayer']='Swete1887 printed main text; editorial publication reading, not independent ancient ink'
            if ref=='Gen.5.28':claim['qualification']='Noah is named in the following verse; declared Gen5:28–29 context.'
            claims.append(claim)
    claims.append({'id':'bible:primary-age:Greek_Swete1887_main:Gen.11.13:Cainan','family':'Greek_Swete1887_main','reference':'Gen.11.13:inserted-Cainan-clause','parentRole':'Cainan II','descendantRole':'Shelah','reportedAgeAtNamedBegetting':130,'reportedYearsAfterNamedBegetting':330,'unit':'reported-year','sourceLayer':'visually inspected printed edition; not independent ancient ink','sourceRegion':{'pdf':pdf.name,'pdfSha256':digest(pdf),'printedPage':18,'pdfPageOneBased':50},'biologicalImmediacyIndependentlyEstablished':False})
    after=[]
    for family,value in [('MT',403),('SP',303),('Greek_Swete1887_main',430)]:
        after.append({'id':'bible:primary-after-age:'+family+':Gen.11.13','family':family,'reference':'Gen.11.13','parentRole':'Arpachshad','descendantRole':'Cainan II' if family.startswith('Greek') else 'Shelah','reportedYearsAfterNamedBegetting':value,'totalByAddition':value+(135 if family!='MT' else 35),'unit':'reported-year','sourceRegion':{'packet':region_path.name,'packetSha256':digest(region_path),'reference':'Gen.11.13','literalSourceText':next(x['text'] for x in regions[family] if x['reference']=='Gen.11.13')} if family in ['MT','SP'] else {'pdf':pdf.name,'pdfSha256':digest(pdf),'printedPage':17,'pdfPageOneBased':49}})
    result={'schema':'sunny.genesis-witness-comparison.v1','status':'finite source-qualified comparison, not exhaustive collation','MTsource':{'repository':'https://github.com/openscriptures/morphhb','commit':json.loads((BASE/'MT-OSHB-commit.json').read_text(encoding='utf-8'))['sha'],'path':'MT-OSHB-Genesis.xml','sha256':digest(BASE/'MT-OSHB-Genesis.xml'),'url':'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml','scope':'WLC transcription; text public domain, OSHB linguistic annotations separately licensed CC BY4.0'},'SPsource':{'repository':'https://github.com/DT-UCPH/sp','commit':'8842267d29e37bf786b95209c76852461c389144','version':'7.3.0','manuscriptBasis':'Dublin Chester Beatty Library751 for Genesis, as declared by dataset','scope':'Pentateuch only; consonantal transliteration, not rendered ancient ink or phonetics','license':'CC BY-NC4.0 in acquired source files; conflicting Zenodo discovery label retained in regions packet','sourceBindings':regions['SPsourceBindings']},'GreekSource':{'title':'The Old Testament in Greek according to the Septuagint, vol.I, Genesis–IVKings','editor':'Henry Barclay Swete','publication':'Cambridge University Press,1887; actual PDF title page7, not aggregate Archive1905 metadata','url':'https://archive.org/download/theoldtestamenti03swetuoft_202003/oldtestamentingr01swet.pdf','sourceBindings':bindings,'OCRBoundary':'Greek OCR is unreliable; numeric readings below were inspected in rendered printed pages.','apparatusGen11_13':{'printedPage':17,'pdfPageOneBased':49,'mainYears':430,'literalApparatus':'τετρακοσια] τριακοσια E | ετη εκατον τριακοντα D','reportedVariants':[{'siglum':'E','years':330},{'siglum':'D','years':130}],'siglumDDefinition':'Codex Cottonianus Geneseos (I, Holmes), from English preface PDFpage32','DDefinitionExtraction':'D=CodexCottonianusGeneseos(I,Holmes).','earlierLowResolutionInterpretation':'D=400 was a reading error, corrected by actual higher-resolution rendering.','receivedGreek400Status':'Retained inherited chronology branch, but not corroborated by this apparatus; requires its own edition/witness source.'}},'ageAtBegettingClaims':claims,'ArpachshadAfterBegettingClaims':after,'interpretiveBoundaries':['A published text or scholarly transcription is evidence for that edition/transcription, not independent manuscript authenticity.','No fixed calendar epoch, acoustic value, musical phase, universal generation depth or historical orientation follows.','Gen5:32 and Gen11:26 list multiple sons; their collective age formula is not assigned as every son\'s exact birth year.','Greek apparatus variants are not collapsed into a single LXX chronology.'],'completeOriginalWitnessCollation':False}
    result['MTsource'].update({'gitBlobSha':mt_blob,'commitFileBindingVerified':True})
    out=BASE/'genesis-witness-comparison.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(out),'sha256':digest(out),'ageClaims':len(claims),'afterBegettingClaims':len(after),'SweteDYears':130,'receivedGreek400FreshlyCorroborated':False}))

if __name__=='__main__':main()
