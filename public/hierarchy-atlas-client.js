const payload=JSON.parse(document.getElementById('atlas-data').textContent);
const hierarchy=await import(payload.moduleUrl);
const {atlas,sourceBodies,sourceImages={}}=payload;
const $=s=>document.querySelector(s),byId=new Map(atlas.entities.map(e=>[e.id,e])),sourceMap=new Map(atlas.sources.map(s=>[s.id,s]));
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const bdi=text=>{const n=el('bdi',text);n.dir='auto';return n;};
const fmt=n=>new Intl.NumberFormat('en').format(n),value=v=>v===null||v===undefined?'Unknown / unassigned':typeof v==='object'?JSON.stringify(v):String(v);
const state={origin:'A',witness:'de-laurence-1916',domain:'comparison',query:'',selected:null,traceMode:'upstream'};
const productionTypes=['production-input','production-output','qualified-nonexternal-production-input','qualified-nonexternal-production-output','source-generates-next-lu'];
let selectedGraph,scope,outgoing=new Map(),treeRows=new Map();
const origins=atlas.views.filter(v=>v.id.startsWith('origin:'));
for(const v of origins){const o=el('option',v.label);o.value=v.id.split(':')[1];$('#origin').append(o);}
const catalogues=atlas.views.filter(v=>v.id.startsWith('catalogue:'));
for(const v of catalogues){const o=el('option',v.label);o.value=v.witnessIds[0];$('#witness').append(o);}
$('#origin').value=state.origin;$('#witness').value=state.witness;
const sourceViewOptions=el('optgroup');sourceViewOptions.label='Source-specific views';
for(const v of atlas.views.filter(v=>!v.id.startsWith('origin:')&&!v.id.startsWith('catalogue:'))){const o=el('option',v.label);o.value='view:'+v.id;sourceViewOptions.append(o);}$('#domain').append(sourceViewOptions);
function viewIds(){
  if(state.domain.startsWith('view:'))return [state.domain.slice(5)];
  const upper=['origin:'+state.origin,...atlas.views.filter(v=>/^(upper|angelic|archonic):/.test(v.id)).map(v=>v.id)];
  const musical=kind=>atlas.views.filter(v=>!v.id.startsWith('catalogue:')&&new RegExp(kind,'i').test(v.id+' '+v.label)).map(v=>v.id);
  if(state.domain==='upper')return upper;
  if(state.domain==='legions')return ['catalogue:'+state.witness];
  if(state.domain==='western')return musical('western|music-native|western musical');
  if(state.domain==='chinese')return musical('chinese|china');
  return [...upper,'catalogue:'+state.witness];
}
function linkEntity(id){const e=byId.get(id),button=el('button',undefined,'entity-link');button.type='button';button.append(bdi(e?.nativeName??id));button.dataset.entityId=id;button.addEventListener('click',()=>selectEntity(id));return button;}
function relationList(edges,direction){
  const list=el('ul',undefined,'relation-list');
  for(const r of edges){const li=el('li');li.append(el('span',r.type,'relation-label'),linkEntity(direction==='in'?r.source:r.target));list.append(li);}return list;
}
function renderDetail(id){
  const e=byId.get(id),panel=$('#entity-detail');panel.replaceChildren();if(!e){panel.append(el('h2','Select a record'));return;}
  const heading=el('h2',undefined,'detail-title');heading.id='detail-heading';heading.append(bdi(e.nativeName));panel.append(heading,el('div',e.id,'record-id'));
  panel.append(el('span',e.assertionLayer??'status unassigned','badge '+(e.assertionLayer==='generated'?'generated':'')),el('span',e.unit,'badge'));
  if(!selectedGraph.entities.some(x=>x.id===id))panel.append(el('p','This record is outside the current tree filters. Your origin and witness choices have not changed.','detail-note'));
  const ins=atlas.relationships.filter(r=>r.target===id),outs=atlas.relationships.filter(r=>r.source===id),anc=hierarchy.ancestorsOf(atlas,id,state.traceMode==='production'?{relationTypes:productionTypes}:{});
  const facts=el('dl',undefined,'facts');
  for(const [key,v] of [['Tradition',e.tradition],['Witness',e.witnessId],['Aliases',e.aliases?.join(' · ')||'None recorded'],['GEN',e.position.generation],['Sequence',e.position.sequence],['Cyclic position',e.position.cyclicCoordinate],['Orientation',e.position.orientation],['Stated extent',e.statedExtent],['Direct targets',new Set(outs.map(r=>r.target)).size+' distinct records'],['Typed occurrences',outs.length],['Incoming affiliations',ins.length],...(e.tradition==='Solomonic Goetia'?[['Unique legions','Unknown'],['Personnel','Unknown']]:[['Cross-system identity','Unassigned; no join inferred']])]){facts.append(el('dt',key),el('dd',value(v)));}panel.append(facts);
  if(e.unit===hierarchy.LEGION_SLOT_UNIT)panel.append(el('p','GENERATED anonymous command-membership slot. This address is not a named legion, a person, or proof that commands are disjoint.','detail-note'));
  const exceptions=el('ul',undefined,'detail-list');for(const x of e.exceptions??[])exceptions.append(el('li',x));if(exceptions.childNodes.length)panel.append(exceptions);
  panel.append(el('h3','Direct children / relations'),relationList(outs,'out'),el('h3','Incoming relationships / affiliations'),relationList(ins,'in'));
  panel.append(el('h3',state.traceMode==='production'?'Declared production paths':'Upstream relationships'));
  const traceLabel=el('label','Trace relationships'),traceSelect=el('select');traceSelect.id='trace-mode';
  for(const [v,label] of [['upstream','All typed upstream relationships'],['production','Production inputs / outputs only']]){const o=el('option',label);o.value=v;traceSelect.append(o);}traceSelect.value=state.traceMode;traceSelect.addEventListener('change',()=>{state.traceMode=traceSelect.value;renderDetail(id);});traceLabel.append(traceSelect);panel.append(traceLabel);
  panel.append(el('p',state.traceMode==='production'?'Only declared production/generation edges are followed. Pitch generation is not biological descent; hypotheses, partnership and membership are excluded.':'Upstream traversal includes partnership, membership and command. It is not genealogical ancestry and does not imply parenthood.','hint'));
  const traced=new Set([id,...(anc.ancestorIds??[])]),types=[...new Set(atlas.relationships.filter(r=>traced.has(r.source)&&traced.has(r.target)&&(state.traceMode!=='production'||productionTypes.includes(r.type))).map(r=>r.type))];
  const typeDetails=el('details');typeDetails.append(el('summary','Included relation types ('+types.length+')'));const typeList=el('ul',undefined,'detail-list');for(const type of types){const li=el('li',type);li.dataset.relationType=type;typeList.append(li);}typeDetails.append(typeList);panel.append(typeDetails);
  const ancestors=el('ul',undefined,'detail-list');ancestors.id='upstream-list';for(const aid of anc.ancestorIds??[]){const li=el('li');li.append(linkEntity(aid),el('span',' · '+byId.get(aid)?.witnessId,'entity-meta'));ancestors.append(li);}panel.append(ancestors);
  if(!ancestors.childNodes.length)panel.append(el('p','No upstream record is present. This does not establish an ultimate origin.','hint'));
  if(anc.cycles?.length)panel.append(el('p','Cycle retained: '+JSON.stringify(anc.cycles),'detail-note'));
  panel.append(el('h3','Source evidence'));
  const inherited=e.assertionLayer==='generated'?ins.map(r=>byId.get(r.source)).find(Boolean):null;
  for(const sid of e.sourceRefs??[]){
    const s=sourceMap.get(sid),section=el('section',undefined,'source');section.append(el('div',s?.title??sid,'source-title'),el('div',sid,'record-id'));
    if(s?.sourceRole)section.append(el('p',s.sourceRole));
    if(s?.sha256)section.append(el('div','SHA-256 '+s.sha256,'record-id'));
    if(s?.locator||e.sourceLocator)section.append(el('div','Locator: '+value(e.sourceLocator??s.locator),'record-id'));
    const body=sourceBodies[sid];const evidence=Array.isArray(e.evidence)?e.evidence.find(x=>[x.sourceId,x.source_id].includes(sid)):e.evidence;
    let excerpt=evidence?.quote??e.sourceQuote??e.quote??null,location=evidence?.normalization?'Recorded source excerpt; '+evidence.normalization:null;
    if(!excerpt&&body){const labels=[inherited?.comparisonName,inherited?.nativeName,...(inherited?.aliases??[]),e.comparisonName,e.nativeName,...(e.aliases??[])].filter(Boolean);const label=labels.find(name=>body.text.includes(name));const at=label?body.text.indexOf(label):-1;if(at>=0){const start=Math.max(0,at-180),end=Math.min(body.text.length,at+1200);excerpt=body.text.slice(start,end);location='Literal name occurrence, source text offsets '+start+'–'+end+' (UTF-16).';}}
    if(excerpt){section.append(el('p',inherited?'Commander source context; the generated slot has no individual source quotation.':location??'Recorded source quotation.','hint'));if(location)section.append(el('div',location,'record-id'));const pre=el('pre',typeof excerpt==='string'?excerpt:JSON.stringify(excerpt,null,2));pre.dir='auto';section.append(pre);section.append(el('p','A literal occurrence supplies context; it does not by itself prove the imported relationship. Markup, where present, is shown as inert source text.','hint'));}
    else section.append(el('p','No entity-specific literal passage is embedded. The source identifier, declared locator and uncertainty remain available.','hint'));
    if(sourceImages[sid]){const preview=el('details');preview.append(el('summary','View the supplied source image'));const img=el('img');img.src=sourceImages[sid].dataUrl;img.alt='Supplied source image: '+(s?.title??sid);img.loading='lazy';img.className='source-image';preview.append(img);section.append(preview);if(!sourceImages[sid].matchesDeclared)section.append(el('p','Embedded image differs from its declared digest.','detail-note'));}
    if(body&&!body.matchesDeclared)section.append(el('p','Current file digest differs from the declared source digest.','detail-note'));
    if(s?.url&&/^https?:\/\//.test(s.url)){const a=el('a','Open cited source');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';section.append(a);}panel.append(section);
  }
  panel.append(el('h3','Unknown joins and boundaries'));
  const gaps=el('ul',undefined,'detail-list');for(const x of atlas.unresolved??[])gaps.append(el('li',typeof x==='string'?x:x.detail??JSON.stringify(x)));panel.append(gaps);
  const raw=el('details');raw.append(el('summary','Complete recorded fields'));raw.append(el('pre',JSON.stringify(e,null,2),'raw-fields'));panel.append(raw);
}
function selectEntity(id){state.selected=id;for(const nodes of treeRows.values())for(const n of nodes)n.classList.remove('selected');for(const n of treeRows.get(id)??[])n.classList.add('selected');renderDetail(id);}
function nodeRow(id,relation,path=[]){
  const e=byId.get(id),li=el('li');if(!e)return li;
  const row=el('div',undefined,'tree-row '+(e.assertionLayer==='generated'?'generated':''));row.dataset.entityId=id;if(state.selected===id)row.classList.add('selected');
  const rows=treeRows.get(id)??[];rows.push(row);treeRows.set(id,rows);
  const edges=outgoing.get(id)??[],cycle=path.includes(id);const expand=el('button',edges.length&&!cycle?'›':'·','expand');expand.type='button';expand.setAttribute('aria-label',(edges.length?'Expand ':'Leaf ')+e.nativeName);expand.setAttribute('aria-expanded','false');expand.disabled=!edges.length||cycle;
  const name=el('button',undefined,'entity-name');name.type='button';name.dataset.entityId=id;name.append(bdi(e.nativeName),el('span',e.unit+(edges.length?' · '+fmt(edges.length)+' relation occurrences':''),'entity-meta'));if(relation)name.append(el('span',relation,'relation'));if(cycle)name.append(el('span','Cycle: retained without recursive expansion','relation'));name.addEventListener('click',()=>selectEntity(id));
  row.append(expand,name);li.append(row);let opened=false,children=null;
  expand.addEventListener('click',()=>{opened=!opened;expand.textContent=opened?'⌄':'›';expand.setAttribute('aria-expanded',String(opened));expand.setAttribute('aria-label',(opened?'Collapse ':'Expand ')+e.nativeName);if(!opened){children?.remove();children=null;return;}children=el('ul',undefined,'branches');let count=0;const more=el('button',undefined,'more');more.type='button';function page(){more.remove();const end=Math.min(count+100,edges.length);for(;count<end;count++){const r=edges[count];children.append(nodeRow(r.target,r.type,[...path,id]));}if(count<edges.length){more.textContent='Show next '+Math.min(100,edges.length-count)+' · '+count+' of '+edges.length;children.append(more);}}more.addEventListener('click',page);page();li.append(children);});return li;
}
function renderTree(){
  scope={viewIds:viewIds()};selectedGraph=hierarchy.filterHierarchy(atlas,scope);outgoing=new Map();treeRows=new Map();
  for(const r of (state.query?atlas.relationships:selectedGraph.relationships)){const list=outgoing.get(r.source)??[];list.push(r);outgoing.set(r.source,list);}
  const tree=$('#atlas-tree');tree.replaceChildren();
  const census=hierarchy.hierarchyCensus(atlas,scope),catalogue=hierarchy.reconcileLegionCatalogue(atlas,state.witness),catalogueCensus=hierarchy.hierarchyCensus(atlas,{viewIds:['catalogue:'+state.witness]});
  $('#census').textContent=fmt(census.entityRecords)+' entity records · '+fmt(census.generatedMembershipSlots)+' GENERATED catalogue slots in this view · selected catalogue '+catalogue.chiefCount+' chiefs / '+(catalogueCensus.rankMembershipOccurrences?catalogueCensus.rankMembershipOccurrences+' native rank memberships / ':'native rank census unassigned / ')+fmt(catalogue.primaryCommandCountSum)+' command occurrences · unique legions and personnel unknown';
  if(state.query){const query=state.query.toLocaleLowerCase(),found=byId.has(state.query)?[byId.get(state.query)]:atlas.entities.filter(e=>[e.id,e.nativeName,...e.aliases].some(v=>String(v).toLocaleLowerCase().includes(query)));tree.append(el('p',fmt(found.length)+' matching records across the whole atlas; selectors are unchanged.','search-count'));const list=el('ul',undefined,'branches');tree.append(list);let count=0;const more=el('button',undefined,'more');more.type='button';function page(){more.remove();const end=Math.min(count+100,found.length);for(;count<end;count++)list.append(nodeRow(found[count].id,'Search result: '+found[count].witnessId));if(count<found.length){more.textContent='Show next '+Math.min(100,found.length-count)+' search results';list.append(more);}}more.addEventListener('click',page);page();}
  else if(!selectedGraph.views.length)tree.append(el('p','This musical source view has not yet been integrated into this atlas file.','empty'));
  else for(const v of selectedGraph.views){const section=el('section');section.dataset.viewId=v.id;section.append(el('h3',v.label));const list=el('ul',undefined,'branches');for(const id of v.roots)list.append(nodeRow(id,null));section.append(list);tree.append(section);}
  if(state.selected)renderDetail(state.selected);
}
for(const name of ['origin','witness','domain'])$('#'+name).addEventListener('change',()=>{state[name]=$('#'+name).value;renderTree();});
$('#filters').addEventListener('submit',e=>e.preventDefault());let searchTimer;
$('#entity-search').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.query=$('#entity-search').value.trim();renderTree();},100);});
$('#collapse-all').addEventListener('click',renderTree);
const coverage=$('#coverage'),full=hierarchy.hierarchyCensus(atlas);coverage.append(el('p',fmt(full.generatedMembershipSlots)+' generated anonymous catalogue slots across all readings. Entity records and command-membership occurrences are separate counting units.'));
coverage.append(el('p','The de Laurence source retains 72 chiefs and 79 rank memberships; multiple ranks do not create additional chiefs. Unique legions, personnel and cross-witness identity remain unknown.'));
coverage.append(el('p',atlas.coverage?.scope??'Only supplied source records and declared views are represented. Universal completion is not claimed.'));
coverage.append(el('p','Source graph '+payload.provenance.input+' · SHA-256 '+payload.provenance.inputSha256,'record-id'));
renderTree();const initial=selectedGraph.views[0]?.roots[0];if(initial)selectEntity(initial);
window.__SUNNY_ATLAS__={ready:true,selection:()=>({...state}),counts:()=>hierarchy.hierarchyCensus(atlas,scope),selectEntity,atlas};
