from collect_sources import fetch,ROOT
import concurrent.futures,json
ITEMS=[
 ('berlin2024_exhibition','https://www.smb.museum/fileadmin/website/Presse/Pressematerial/2024/04/03_AEMP_240424_Elephantine_Exponate.pdf','.pdf'),
 ('hanson_A4_7','https://kchanson.com/ANCDOCS/westsem/templeauth.html','.html'),
 ('praat_pitch','https://praat.org/manual/Pitch.html','.html'),
 ('praat_formant','https://praat.org/manual/Sound__To_Formant__burg____.html','.html'),
 ('khan2020_metadata','https://www.openbookpublishers.com/books/10.11647/obp.0163','.html'),
 ('cmudict_readme','https://raw.githubusercontent.com/cmusphinx/cmudict/master/README','.txt'),
 ('cal_guide','https://cal.huc.edu/cal_new_user_guide.html','.html'),
]
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:results=list(e.map(fetch,ITEMS))
 (ROOT/'source-fetch-extra-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(results,ensure_ascii=False,indent=2))
