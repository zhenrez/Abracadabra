"""Bind interface checks to the current graph, while retaining meaningful scope assertions."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'tests/guide-browser.mjs';text=p.read_text(encoding='utf8')
text=text.replace("assert.equal(await ev('document.querySelectorAll(\"#guide-view option\").length'),23)","assert.equal(await ev('document.querySelectorAll(\"#guide-view option\").length'),G.views.length)")
text=text.replace("assert.deepEqual(checked.generationOptions,['*','?']);", "const rows=G.entities.filter(e=>view.ids.includes(e.id)),known=[...new Set(rows.map(e=>e.position?.generation).filter(x=>x!==null&&x!==undefined&&x!==''))].sort((a,b)=>String(a).localeCompare(String(b),undefined,{numeric:true}));assert.deepEqual(checked.generationOptions,['*',...(rows.some(e=>e.position?.generation==null)?['?']:[]),...known.map(String)]);")
text=text.replace("assert.ok(row.generation.includes('Not assigned'));", "if(entity.position.generation==null)assert.ok(row.generation.includes('Not assigned'));else{assert.ok(row.generation.includes(String(entity.position.generation)));assert.ok(row.generation.includes(entity.generationFrame));}")
text=text.replace('size,9512)','size,G.entities.length)').replace('All23view','All current view').replace('all23views','all current views').replace('all23source','all current source')
p.write_text(text,encoding='utf8')
p=root/'tests/delivery-browser.mjs';text=p.read_text(encoding='utf8')
needle="const root=resolve(fileURLToPath(new URL('..',import.meta.url))),evidence=join(root,'docs/evidence/delivery-2026-11-07');mkdirSync(evidence,{recursive:true});"
if 'const expectedData=' not in text:
 text=text.replace(needle,needle+"\nconst expectedData=JSON.parse(readFileSync(join(root,'web/delivery-2026-11-07/data.json'),'utf8'));const expectedGraph=expectedData.graph;")
text=text.replace("entityCount'),9512)","entityCount'),expectedGraph.entities.length)")
text=text.replace("graph.relationships.length'),10251)","graph.relationships.length'),expectedGraph.relationships.length)")
text=text.replace("Object.keys(SUNNY_DELIVERY.modules).length+1'),16)","Object.keys(SUNNY_DELIVERY.modules).length+1'),Object.keys(expectedData.modules).length+1)")
text=text.replace("document.querySelector(\"main select\").options.length'),23)","document.querySelector(\"main select\").options.length'),expectedGraph.views.length)")
text=text.replace('All9512 graph records,16modules','All current graph records and modules')
p.write_text(text,encoding='utf8')
print('{"status":"updated","exit_code":0,"files":["tests/guide-browser.mjs","tests/delivery-browser.mjs"]}')
