from pathlib import Path
import urllib.request,struct,json,zlib,hashlib,datetime
from PIL import Image
ROOT=Path(__file__).resolve().parent
URL='https://archive.org/download/aramischepapyr02sachuoft/aramischepapyr02sachuoft_jp2.zip'
TOTAL=76827403
calls=[]
def read_range(start,end):
 req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}'})
 with urllib.request.urlopen(req,timeout=20) as r:
  if r.status!=206:raise ValueError('Expected206 range response; refusing full archive download')
  b=r.read(end-start+2)
  if len(b)!=end-start+1:raise ValueError('Unexpected range byte count')
  calls.append({'request_range':f'{start}-{end}','final_url':r.url,'content_range':r.headers.get('Content-Range'),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
  return b
tail=read_range(TOTAL-66000,TOTAL-1)
i=tail.rfind(b'PK\x05\x06')
if i<0:raise ValueError('ZIP end directory missing')
end=struct.unpack('<4s4H2LH',tail[i:i+22]);size,offset=end[5],end[6]
directory=read_range(offset,offset+size-1);pos=0;selected=None
while pos<len(directory):
 h=struct.unpack('<4s6H3L5H2L',directory[pos:pos+46])
 if h[0]!=b'PK\x01\x02':raise ValueError('Bad central directory entry')
 name=directory[pos+46:pos+46+h[10]].decode('utf-8')
 if name.endswith('_0039.jp2'):selected={'name':name,'compression':h[4],'crc32':h[7],'compressed_size':h[8],'uncompressed_size':h[9],'local_offset':h[16]}
 pos+=46+h[10]+h[11]+h[12]
if selected is None:raise ValueError('Exact observed PAGE0039 member not found')
off=selected['local_offset'];head=read_range(off,off+29);lh=struct.unpack('<4s5H3L2H',head)
start=off+30+lh[9]+lh[10];body=read_range(start,start+selected['compressed_size']-1)
if selected['compression']==8:body=zlib.decompress(body,-15)
elif selected['compression']!=0:raise ValueError('Unsupported compression')
assert len(body)==selected['uncompressed_size']
assert zlib.crc32(body)==selected['crc32']
target=ROOT/'sources/sachau1911-plate13.jp2';target.write_bytes(body)
im=Image.open(target);im.save(ROOT/'sources/sachau1911-plate13.png')
record={'schema':'sunny.original-facsimile-retrieval.v1','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':URL,'selection':'Sachau1911 volume2, OCR PAGE0039, expected plate13; verify caption visually','member':selected,'member_sha256':hashlib.sha256(body).hexdigest(),'crc_matches':True,'range_calls':calls,'original_local_path':'sources/sachau1911-plate13.jp2','reading_rendition':'sources/sachau1911-plate13.png','dimensions':im.size,'scope':'Exact archive member extracted; only format conversion for document reading, no correction of original sign.'}
(ROOT/'sachau-facsimile-receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
