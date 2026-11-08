"""Recover native workbook witnesses without evaluating formulas or choosing joins."""
from pathlib import Path, PurePosixPath
import collections, hashlib, json, re, sqlite3, zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'state'/'reconstruction'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL='{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'

def canonical(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(value): return hashlib.sha256(value).hexdigest()
def txt(element): return ''.join(element.itertext()) if element is not None else ''

def workbook(path,source):
    sheets=[]
    with zipfile.ZipFile(path) as archive:
        strings=[]
        if 'xl/sharedStrings.xml' in archive.namelist():
            for item in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si',NS):
                strings.append(''.join(t.text or '' for t in item.findall('.//m:t',NS)))
        relationships={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels')).findall(REL) if r.attrib.get('TargetMode')!='External'}
        for declared in ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
            target=relationships[declared.attrib['{'+NS['r']+'}id']]
            part=target.lstrip('/') if target.startswith('/') else str(PurePosixPath('xl')/target)
            if '..' in PurePosixPath(part).parts: raise ValueError('Unexpected workbook relationship traversal')
            rows=[]
            for row in ET.fromstring(archive.read(part)).findall('m:sheetData/m:row',NS):
                cells=[]
                for cell in row.findall('m:c',NS):
                    kind=cell.attrib.get('t','n'); raw=cell.find('m:v',NS); value=raw.text if raw is not None else None
                    if kind=='s' and value is not None: decoded=strings[int(value)]
                    elif kind=='inlineStr': decoded=''.join(t.text or '' for t in cell.findall('m:is//m:t',NS))
                    else: decoded=value
                    formula=cell.find('m:f',NS)
                    if decoded is None and formula is None: continue
                    cells.append({'ref':cell.attrib.get('r'),'type':kind,'value':decoded,'raw_value':value,'formula':formula.text if formula is not None else None,'formula_attributes':dict(formula.attrib) if formula is not None else None,'style':cell.attrib.get('s')})
                if cells: rows.append({'row':int(row.attrib['r']),'cells':cells})
            content={'name':declared.attrib['name'],'part':part,'rows':rows}
            digest=sha(canonical(content).encode('utf8'))
            sheets.append({'sheet':declared.attrib['name'],'part':part,'content_sha256':digest,'rows':rows,'row_count':len(rows),'cell_count':sum(len(row['cells']) for row in rows),'source_id':source['id'],'source_sha256':source['sha256'],'source_path':str(path),'semantics':'Literal native workbook witness. Existing statuses/formulas are retained, not executed or independently validated.'})
    return sheets

def main():
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'native-tables').mkdir(exist_ok=True)
    c=sqlite3.connect((ROOT/'data'/'sunny.sqlite').as_uri()+'?mode=ro',uri=True); c.row_factory=sqlite3.Row
    selected=[dict(row) for row in c.execute("SELECT * FROM sources WHERE path LIKE '%Generative_Ontology_Stack%' AND path LIKE '%.xlsx'")]
    by_bytes=collections.defaultdict(list)
    for row in selected: by_bytes[row['sha256']].append(row)
    versions=[]; sheet_occurrences=collections.defaultdict(list); tables={}
    for digest,occurrences in sorted(by_bytes.items(),key=lambda pair:pair[1][0]['path']):
        source=occurrences[0]; path=Path(source['path'])
        if sha(path.read_bytes())!=digest: raise ValueError('Workbook source hash mismatch: '+str(path))
        recovered=workbook(path,source)
        for table in recovered:
            key=table['content_sha256']; tables.setdefault(key,table)
            sheet_occurrences[key].append({'source_id':source['id'],'source_sha256':digest,'workbook':path.name,'sheet':table['sheet'],'part':table['part'],'alias_source_ids':[o['id'] for o in occurrences]})
        versions.append({'source_id':source['id'],'source_sha256':digest,'path':str(path),'file':path.name,'aliases':occurrences,'sheet_count':len(recovered),'row_count':sum(t['row_count'] for t in recovered),'cell_count':sum(t['cell_count'] for t in recovered),'sheets':[{'name':t['sheet'],'part':t['part'],'content_sha256':t['content_sha256'],'row_count':t['row_count'],'cell_count':t['cell_count']} for t in recovered]})
    for digest,table in tables.items():
        table['occurrences']=sheet_occurrences[digest]
        (OUT/'native-tables'/(digest+'.json')).write_text(json.dumps(table,ensure_ascii=False,indent=2),encoding='utf8')
    inventory={'schema':'sunny.reconstructed-native-tables.v1','selection_receipt':'docs/evidence/reconstruction-alignment-superjev.json','source_occurrences':len(selected),'unique_workbook_bytes':len(versions),'worksheet_occurrences':sum(v['sheet_count'] for v in versions),'distinct_sheet_contents':len(tables),'literal_row_occurrences':sum(v['row_count'] for v in versions),'literal_cell_occurrences':sum(v['cell_count'] for v in versions),'distinct_sheet_rows':sum(t['row_count'] for t in tables.values()),'distinct_sheet_cells':sum(t['cell_count'] for t in tables.values()),'versions':versions,'tables':[{'sha256':k,'sheet':v['sheet'],'row_count':v['row_count'],'cell_count':v['cell_count'],'occurrences':sheet_occurrences[k],'path':str(OUT/'native-tables'/(k+'.json'))} for k,v in tables.items()],'boundary':'Counts measure literal recovered witnesses, not independent sources, approved model facts, semantic adjudication or full account completeness. No formula ran and no orientation was selected.'}
    (OUT/'tables.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in inventory.items() if k not in ('versions','tables')},ensure_ascii=True,indent=2))

if __name__=='__main__': main()
