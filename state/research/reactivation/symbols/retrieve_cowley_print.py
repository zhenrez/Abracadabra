from pathlib import Path
import urllib.request,struct,json,zlib,hashlib,datetime
from PIL import Image
ROOT=Path(__file__).resolve().parent
locator=json.loads((ROOT/'cowley39-page-locator.json').read_text(encoding='utf-8'))
ident='aramaicpapyrioff00ahikuoft';zipname=locator['zip']['name'];total=locator['zip']['size']
url='https://archive.org/download/'+ident+'/'+zipname
target_name=locator['pages'][0]['page_file'].replace('.djvu','.jp2');calls=[]
def read_range(start,end):
 req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
 with urllib.request.urlopen(req,timeout=15) as r:
  if r.status!=206:raise ValueError('Expected206; refusing full archive')
  data=r.read(end-start+2)
  if len(data)!=end-start+1:raise ValueError('Unexpected byte count')
  calls.append({'range':f'{start}-{end}','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'final_url':r.url});return data
tail=read_range(total-66000,total-1);e=tail.rfind(b'PK\x05\x06');assert e>=0
end=struct.unpack('<4s4H2LH',tail[e:e+22]);size,offset=end[5],end[6]
directory=read_range(offset,offset+size-1);pos=0;entry=None
while pos<len(directory):
 h=struct.unpack('<4s6H3L5H2L',directory[pos:pos+46]);assert h[0]==b'PK\x01\x02'
 name=directory[pos+46:pos+46+h[10]].decode('utf-8')
 if name.endswith('/'+target_name):entry={'name':name,'compression':h[4],'crc32':h[7],'compressed_size':h[8],'uncompressed_size':h[9],'local_offset':h[16]}
 pos+=46+h[10]+h[11]+h[12]
assert entry is not None
off=entry['local_offset'];head=read_range(off,off+29);lh=struct.unpack('<4s5H3L2H',head);start=off+30+lh[9]+lh[10]
body=read_range(start,start+entry['compressed_size']-1)
if entry['compression']==8:body=zlib.decompress(body,-15)
else:assert entry['compression']==0
assert len(body)==entry['uncompressed_size'];assert zlib.crc32(body)==entry['crc32']
p=ROOT/'sources/cowley1923-printed138.jp2';p.write_bytes(body);im=Image.open(p);im.save(ROOT/'sources/cowley1923-printed138.png')
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'source_locator':'cowley39-page-locator.json, OCRpage0174; verify printedpage138 visually','entry':entry,'member_sha256':hashlib.sha256(body).hexdigest(),'crc_matches':True,'original_local_path':str(p.relative_to(ROOT)),'reading_rendition':'sources/cowley1923-printed138.png','dimensions':im.size,'range_calls':calls,'scope':'Original printed edition page retrieved, not a new papyrus photograph or phonetic recording.'}
(ROOT/'cowley39-printed-page-receipt.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
