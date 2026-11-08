from collect_sources import fetch,ROOT
import concurrent.futures,json
ITEMS=[
 ('cal_A3_7','https://cal.huc.edu/get_a_chapter.php?cset=H&file=22551&sub=307','.html'),
 ('cal_A3_7_info','https://cal.huc.edu/get_file_info.php?coord=22551307&return=/showsubtexts.php?subtext%3D22','.html'),
 ('cal_A4_7','https://cal.huc.edu/get_a_chapter.php?cset=H&file=23550&sub=407','.html'),
 ('cal_A4_7_info','https://cal.huc.edu/get_file_info.php?coord=23550407&return=/showsubtexts.php?subtext%3D23','.html'),
 ('cal_A3_7_to','https://cal.huc.edu/getlex.php?coord=22551307R01&hasvariant=0&word=0','.html'),
 ('cal_A3_7_mistress','https://cal.huc.edu/getlex.php?coord=22551307R01&hasvariant=0&word=1','.html'),
 ('cal_A3_7_lord','https://cal.huc.edu/getlex.php?coord=22551307R02&hasvariant=0&word=0','.html'),
 ('cal_A4_7_to','https://cal.huc.edu/getlex.php?coord=23550407R01&hasvariant=0&word=0','.html'),
 ('cal_A4_7_god','https://cal.huc.edu/getlex.php?coord=23550407R02&hasvariant=0&word=1','.html'),
 ('cal_scope','https://cal.huc.edu/info.html','.html'),
]
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:results=list(e.map(fetch,ITEMS))
 (ROOT/'cal-fetch-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps([{k:r.get(k) for k in ['id','status','bytes','sha256','error']} for r in results],indent=2))
