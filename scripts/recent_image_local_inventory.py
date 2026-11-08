"""Metadata-only local image inventory in explicitly scoped research locations."""
from pathlib import Path
import os,json,hashlib,collections
from datetime import datetime,timezone,timedelta
BASE=Path(r'C:\Users\Brend')
OUT=BASE/'Documents'/'ChatGPT'/'SUN'/'docs'/'evidence'/'recent-image-local-inventory.json'
PHOENIX=timezone(timedelta(hours=-7))
START=datetime(2026,10,28,tzinfo=PHOENIX).timestamp()
END=datetime(2026,11,1,tzinfo=PHOENIX).timestamp()
EXT={'.jpg','.jpeg','.png','.webp','.gif','.tif','.tiff','.bmp','.heic','.heif','.avif','.svg'}
ROOTS=[('downloads',BASE/'Downloads'),('codex_attachments',BASE/'.codex'/'attachments'),('chatgpt_projects',BASE/'Documents'/'ChatGPT'),('known_sacred_timeline_export',BASE/'Documents'/'Codex'/'2026-10-28'/'sacred-timeline-research-plugin-sacred-timeline'/'outputs'/'sacred-timeline'),('codex_artifacts',BASE/'.codex'/'artifacts'),('codex_app_artifact_sessions',BASE/'AppData'/'Roaming'/'Codex'/'web'/'Codex'/'artifact-sessions')]
SKIP={'node_modules','.git','.venv','__pycache__','runtime','Cache','Code Cache','GPUCache','Cookies','Sessions','Session Storage','Local Storage','IndexedDB','Network','Service Worker'}
def iso(t):return datetime.fromtimestamp(t,timezone.utc).isoformat()
def local(t):return datetime.fromtimestamp(t,PHOENIX).isoformat()
def classification(path):
 s=str(path).lower().replace('\\','/');n=path.name.lower()
 if n.startswith('codex-clipboard-'):return 'clipboard_capture_not_confirmed_original'
 if '/sun/docs/evidence/' in s or '/.codex/artifacts/' in s or '/artifact-sessions/' in s:return 'generated_or_app_artifact_not_upload_proof'
 if '/data/raw/' in s or '/outputs/sacred-timeline/' in s:return 'recovered_export_or_extracted_archive_not_recent_upload_proof'
 if 'generated' in n or n.startswith('image-gen'):return 'generation_named_file_not_confirmed_original_upload'
 if n.startswith('screenshot') or 'screenshot' in n:return 'screenshot_named_file_not_confirmed_original_upload'
 if 'sun_' in n or n.startswith('fb_img_'):return 'research_named_candidate_pending_content_match'
 return 'unclassified_local_image_candidate'
def main():
 records=[];errors=[];stats=[];seen=set()
 for label,root in ROOTS:
  count=0;recent=0
  if not root.is_dir():stats.append({'label':label,'path':str(root),'exists':False});continue
  for folder,dirs,names in os.walk(root,followlinks=False):
   dirs[:]=[name for name in dirs if name not in SKIP and not (Path(folder)/name).is_symlink()]
   for name in names:
    path=Path(folder)/name
    if path.suffix.lower() not in EXT or str(path).lower() in seen:continue
    try:
     if path.is_symlink():continue
     st=path.stat();count+=1;seen.add(str(path).lower())
     created=getattr(st,'st_birthtime',st.st_ctime);is_recent=START<=st.st_mtime<END or START<=created<END
     if is_recent:recent+=1
     records.append({'path':str(path),'filename':name,'root':label,'extension':path.suffix.lower(),'bytes':st.st_size,'created_utc':iso(created),'modified_utc':iso(st.st_mtime),'created_phoenix':local(created),'modified_phoenix':local(st.st_mtime),'recent_by_created_or_modified':is_recent,'classification':classification(path),'latest_metadata_epoch':max(created,st.st_mtime)})
    except OSError as exc:errors.append({'path':str(path),'error_type':type(exc).__name__})
  stats.append({'label':label,'path':str(root),'exists':True,'image_file_occurrences':count,'recent_metadata_occurrences':recent})
 records.sort(key=lambda row:row['latest_metadata_epoch'],reverse=True)
 recent=[row for row in records if row['recent_by_created_or_modified']]
 original_candidates=[row for row in recent if row['classification'] in ['research_named_candidate_pending_content_match','unclassified_local_image_candidate'] and row['root'] in ['downloads','codex_attachments','chatgpt_projects']]
 # SHA checks identify byte duplicates only. Repeated path occurrences remain rows.
 hash_targets={row['path'] for row in recent[:500]}|{row['path'] for row in original_candidates}
 hash_groups=collections.defaultdict(list)
 for row in records:
  if row['path'] in hash_targets and row['bytes']<=60_000_000:
   try:
    with Path(row['path']).open('rb') as stream:row['sha256']=hashlib.file_digest(stream,'sha256').hexdigest()
    hash_groups[row['sha256']].append(row['path'])
   except OSError as exc:errors.append({'path':row['path'],'operation':'sha256','error_type':type(exc).__name__})
 report={'generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'Metadata-only discovery in authorized local roots; no browser, cookies, credentials, session tokens or image content inspected.','time_window_phoenix':['2026-10-28T00:00:00-07:00','2026-11-01T00:00:00-07:00'],'timestamp_semantics':'Filesystem creation/modification only. Copy, extraction, download and sync can change them; they do not prove account upload time.','roots':stats,'total_image_file_occurrences':len(records),'recent_metadata_occurrences':len(recent),'recent_by_classification':dict(collections.Counter(row['classification'] for row in recent)),'original_candidate_occurrences_pending_content_or_account_match':len(original_candidates),'hashes_computed':sum('sha256' in row for row in records),'duplicate_sha256_groups':[{ 'sha256':digest,'paths':paths,'occurrences':len(paths)} for digest,paths in hash_groups.items() if len(paths)>1],'newest100_local_metadata_occurrences':recent[:100],'newest100_original_candidates_pending_match':original_candidates[:100],'records':records,'errors':errors,'unsearched':['Browser profile storage/caches/cookies/databases','Unrelated personal folders','Remote ChatGPT account originals; root agent handles browser/account retrieval'],'limits':['Not an account-upload inventory and not proof the newest80–100account uploads are local.','Filename classification is a search cue, not a content judgment or an exclusion based on name.','Previously supplied clipboard-list screenshots are context, not assumed to be the sought original research images.','Archive-derived files remain listed but are not treated as recent uploads.','No byte duplicate path is collapsed or substituted for another upload occurrence.']}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:report[k] for k in ['generated_utc','total_image_file_occurrences','recent_metadata_occurrences','recent_by_classification','original_candidate_occurrences_pending_content_or_account_match','hashes_computed','roots']},indent=2))
 print(json.dumps({'original_candidates':original_candidates[:25]},ensure_ascii=True,indent=2))
if __name__=='__main__':main()
