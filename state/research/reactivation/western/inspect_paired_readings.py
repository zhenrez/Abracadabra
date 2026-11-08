"""Inspect publisher-linked reconstructed-reading metadata without installing a decoder."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, shutil, sys, urllib.request
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parent
TARGETS=[
 ("OBP.0163.06","https://doi.org/10.11647/OBP.0163.06","https://cdn.openbookpublishers.com/resources/10.11647/obp.0163/OBP.0163.06_Gen_1-13_forte_lene.mp3","without melody"),
 ("OBP.0163.07","https://doi.org/10.11647/OBP.0163.07","https://cdn.openbookpublishers.com/resources/10.11647/obp.0163/OBP.0163.07_Gen_1-13_forte_lene_melodic.mp3","with Sefardi melody"),
]
def head(item):
 ident,doi,url,condition=item
 rec={"id":ident,"doi":doi,"url":url,"condition":condition,"method":"HTTP HEAD only;12-second socket timeout; no audio body requested","utc":datetime.now(timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,method="HEAD",headers={"User-Agent":"Mozilla/5.0 SUNNY-source-research"}),timeout=12) as response:
   rec.update(status="metadata_retrieved",http_status=response.status,final_url=response.url,content_type=response.headers.get("Content-Type"),content_length=response.headers.get("Content-Length"),last_modified=response.headers.get("Last-Modified"))
 except Exception as e: rec.update(status="unavailable",error=f"{type(e).__name__}: {e}")
 return rec
if __name__=="__main__":
 with ThreadPoolExecutor(max_workers=2) as pool: recs=list(pool.map(head,TARGETS))
 availability={"ffmpeg_on_path":shutil.which("ffmpeg"),"ffprobe_on_path":shutil.which("ffprobe"),"python_modules":{k:importlib.util.find_spec(k) is not None for k in ["soundfile","audioread","av","pydub","imageio_ffmpeg"]}}
 packet={"schema":"sunny.western-paired-reading-access.v1","created_utc":datetime.now(timezone.utc).isoformat(),"sources":recs,"decoder_probe":availability,"scope":"Publisher labels and HEAD metadata only. No audio decode, listening, segmentation, phonetic measurement, waveform reconstruction or ancient attestation is claimed.","next_dependency":"Use an existing approved decoder and token-alignment procedure for modern reconstructed performance comparison; otherwise retain observation contract as prospective."}
 (ROOT/"paired-reading-access.json").write_text(json.dumps(packet,indent=2),encoding="utf8")
 print(json.dumps(packet,indent=2))
