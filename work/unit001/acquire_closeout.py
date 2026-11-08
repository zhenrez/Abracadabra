"""Bounded source capture; original response bytes retained, no corpus ingestion."""
from pathlib import Path
import urllib.request,json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).parent/'closeout'
def main():
    ROOT.mkdir(exist_ok=True)
    manifest=[]
    refs=['Sefer_Yetzirah.1','Sefer_Yetzirah_Gra_Version.1','Ruth.3.3','Ibn_Ezra_on_Exodus.14.18.2','Ibn_Ezra_on_Exodus.14.19.1']
    urls={ref:'https://www.sefaria.org/api/texts/'+ref+'?context=0&commentary=0' for ref in refs}
    urls['Lachish-2025']='https://jjar.huji.ac.il/sites/default/files/jjar/files/jjar08_02_lachish-ostracon.pdf'
    for key,url in urls.items():
        path=ROOT/(key+('.pdf' if key=='Lachish-2025' else '.json'))
        if path.exists():raw=path.read_bytes();context='existing pinned capture'
        else:
            raw=urllib.request.urlopen(url,timeout=30).read()
            with path.open('xb') as f:f.write(raw)
            context='live response'
        d={} if key=='Lachish-2025' else json.loads(raw)
        manifest.append(dict(id=key,path=path.name,url=url,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
          retrieved_utc=datetime.now(timezone.utc).isoformat(),capture=context,
          authority=('FAILED_HTTP_CAPTURE' if not raw.startswith(b'%PDF') else 'PRIMARY_SCHOLARLY_PUBLICATION') if key=='Lachish-2025' else 'MODERN_DIGITAL_EDITION',
          english_version=d.get('versionTitle'),hebrew_version=d.get('heVersionTitle'),
          version_source=d.get('versionSource'),hebrew_version_source=d.get('heVersionSource'),
          license=d.get('license','UNVERIFIED'),hebrew_license=d.get('heLicense','UNVERIFIED'),
          age_scope='Earliest surviving manuscript not established; source identified at edition/publication level',
          role='architecture representation control; previously exposed material, not prospective blind evidence'))
    (ROOT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
