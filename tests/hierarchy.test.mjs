import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateHierarchyAtlas,filterHierarchy,hierarchyCensus,ancestorsOf,reconcileLegionCatalogue,LEGION_SLOT_UNIT,LEGION_COMMAND_RELATION} from '../dist/hierarchy.js';
const atlas=JSON.parse(readFileSync(new URL('../state/reconstruction/hierarchy-atlas.json',import.meta.url),'utf8'));
const witnesses=['uploaded-repository','de-laurence-1916','peterson-sloane3825'];

test('source-bound atlas has resolving references and preserves universal gaps',()=>{
 const r=validateHierarchyAtlas(atlas);assert.equal(r.valid,true,r.errors.join('\n'));
 assert.equal(atlas.coverage.completeUniversalHierarchy,false);
 assert.equal(atlas.coverage.semanticCorpusComplete,false);
 assert.equal(atlas.unresolved.find(x=>x.id==='GAP-FULL-ARCHON-GRAPH').detail.includes('recovered, not invented'),true);
 assert.equal(atlas.independence.paired,false);
});

test('all three complete chief vectors reconcile their own declared primary extents',()=>{
 const results=witnesses.map(w=>reconcileLegionCatalogue(atlas,w));
 assert.ok(results.every(r=>r.valid));assert.deepEqual(results.map(r=>r.chiefCount),[72,72,72]);
 assert.deepEqual(results.map(r=>r.primaryCommandCountSum),[2648,2645,2618]);
 assert.deepEqual(results.map(r=>r.generatedMembershipSlotCount),[2648,2645,2618]);
 for(const r of results){assert.equal(r.uniqueLegions,null);assert.equal(r.uniquePersonnel,null);assert.equal(r.membershipDisjointness,'unknown');}
 assert.equal(reconcileLegionCatalogue(atlas,'not-a-witness').valid,false);
});

test('native Peterson names come from catalogue paragraphs, separately from URL anchor spellings',()=>{
 const expected=['Bael','Agares','Vassago','Gamigin','Marbas','Valefar'];
 for(const [i,name] of expected.entries())assert.equal(atlas.entities.find(e=>e.id==='peterson-sloane3825:chief:'+(i+1)).nativeName,name);
 assert.equal(atlas.entities.find(e=>e.id==='peterson-sloane3825:chief:1').sourceLocator.paragraph_id,'baal');
});

test('addressable slots remain generated membership occurrences with exact commander/source binding',()=>{
 const slots=atlas.entities.filter(x=>x.unit===LEGION_SLOT_UNIT);assert.equal(slots.length,7911);
 const byId=new Map(atlas.entities.map(e=>[e.id,e]));
 const edges=atlas.relationships.filter(e=>e.type===LEGION_COMMAND_RELATION);assert.equal(edges.length,7911);
 for(const e of edges){const child=byId.get(e.target),parent=byId.get(e.source);assert.equal(child.assertionLayer,'generated');assert.equal(child.witnessId,parent.witnessId);assert.ok(parent.sourceRefs.some(ref=>child.sourceRefs.includes(ref)&&e.sourceRefs.includes(ref)));assert.match(child.nativeName,/^Catalogue-attributed legion slot [1-9][0-9]* of /);}
 const c=hierarchyCensus(atlas);assert.equal(c.generatedMembershipSlots,7911);assert.equal(c.entityRecords,atlas.entities.length-7911);assert.equal(c.uniqueEntitiesAcrossWitnesses,null);
});

test('native multiple ranks count79 memberships of72 chiefs, separately from imported primary ranks',()=>{
 const native=hierarchyCensus(atlas,{viewIds:['catalogue:de-laurence-1916']});
 const imported=hierarchyCensus(atlas,{viewIds:['catalogue:uploaded-repository']});
 assert.equal(native.chiefRecords,72);assert.equal(native.rankMembershipOccurrences,79);
 assert.equal(imported.chiefRecords,72);assert.equal(imported.rankMembershipOccurrences,72);
 const count=new Map();for(const e of filterHierarchy(atlas,{viewIds:['catalogue:de-laurence-1916']}).relationships.filter(e=>e.type==='has-rank-member'))count.set(e.target,(count.get(e.target)??0)+1);
 assert.equal([...count.values()].filter(n=>n===2).length,7);
});

test('all nine origin and witness combinations remain selectable without forced pairing',()=>{
 for(const letter of ['A','B','C'])for(const w of witnesses){
  const selected=filterHierarchy(atlas,{viewIds:['origin:'+letter,'catalogue:'+w]});
  assert.ok(selected.entities.some(e=>e.id==='origin:'+letter+':condition'));
  assert.equal(selected.entities.filter(e=>e.unit==='catalogue-chief').length,72);
  assert.ok(selected.entities.filter(e=>e.unit==='catalogue-chief').every(e=>e.witnessId===w));
  assert.ok(selected.entities.filter(e=>e.position.orientation!==null).every(e=>e.position.orientation===letter));
 }
 const stages=filterHierarchy(atlas,{viewIds:['origin:B'],units:['proposed-functional-boundary']}).entities;
 assert.deepEqual(stages.map(x=>x.statedExtent.value),[0,1,1,2]);assert.ok(stages.every(x=>x.position.generation===null));
});

test('native production events preserve source-specific joint arity and contextual aeon identities',()=>{
 const upper=filterHierarchy(atlas,{viewIds:['upper:I1']});assert.equal(upper.entities.filter(e=>e.unit==='aeon-member-position').length,30);
 const incoming=upper.relationships.filter(e=>e.target==='i1:event:first'&&e.type==='production-input');
 assert.equal(incoming.length,2);assert.equal(upper.relationships.filter(e=>e.source==='i1:event:first'&&e.type==='production-output').length,2);
 const later=upper.entities.find(e=>e.nativeName==='Monogenes'&&e.id.includes('Decad'));
 const first=upper.entities.find(e=>e.nativeName==='Nous');assert.ok(later&&first);assert.notEqual(later.id,first.id);
 const c=filterHierarchy(atlas,{viewIds:['origin:C']});assert.equal(c.relationships.filter(e=>e.target==='origin:C:event:joint'&&e.type==='hypothesized-joint-condition-input').length,4);
 assert.ok(c.relationships.filter(e=>e.type.startsWith('hypothesized')).every(e=>e.assertionLayer==='research-hypothesis'));
});

test('Chinese functions and imported angel names retain their distinct source roles',()=>{
 const chinese=filterHierarchy(atlas,{viewIds:['native:Chinese-early-source-register']});
 assert.equal(chinese.entities.filter(e=>e.unit.endsWith('operator')).length,2);
 assert.ok(chinese.relationships.some(e=>e.type==='contains-embodied-regulator'));
 assert.ok(chinese.entities.every(e=>e.position.generation===null));
 const imported=filterHierarchy(atlas,{viewIds:['imported:angel-table-order']});
 assert.equal(imported.entities.filter(e=>e.unit==='imported-angel-name-at-gate').length,72);
 assert.ok(imported.relationships.every(e=>e.assertionLayer==='editorial'));
 assert.equal(imported.views[0].coverage.nativeAngelicHierarchy,false);
});

test('typed ancestry follows a slot commander without inventing rank or generation equivalence',()=>{
 const id='de-laurence-1916:chief:9:attributed-slot:200';
 const r=ancestorsOf(atlas,id,{viewIds:['catalogue:de-laurence-1916'],relationTypes:[LEGION_COMMAND_RELATION]});
 assert.equal(r.status,'traced');assert.deepEqual(r.ancestorIds,['de-laurence-1916:chief:9']);
 assert.equal(ancestorsOf(atlas,id,{viewIds:['catalogue:peterson-sloane3825']}).status,'unavailable');
});

function small(){
 const e=(id,unit='catalogue-chief')=>({id,nativeName:id,aliases:[],unit,tradition:'test',witnessId:'w',position:{generation:null,sequence:1,cyclicCoordinate:null,orientation:null},sourceRefs:['s'],exceptions:[],assertionLayer:unit===LEGION_SLOT_UNIT?'generated':'source-assertion',...(unit==='catalogue-chief'?{statedExtent:{value:1,unit:'primary-legion-command-count'}}:{})});
 return {sources:[{id:'s'}],entities:[e('parent'),e('child',LEGION_SLOT_UNIT)],relationships:[{id:'edge',source:'parent',target:'child',type:LEGION_COMMAND_RELATION,viewIds:['v'],sourceRefs:['s'],assertionLayer:'generated'}],views:[{id:'v',label:'test scope',roots:['parent'],witnessIds:['w'],coverage:'finite adverse test fixture, not inference'}]};
}

test('cycles terminate and remain visible instead of silently flattening relation paths',()=>{
 const a=small();a.relationships.push({...a.relationships[0],id:'back',source:'child',target:'parent',type:'hypothesized-return'});
 const r=ancestorsOf(a,'child');assert.equal(r.status,'cycle-detected');assert.ok(r.cycles.some(c=>c.length===3));assert.deepEqual(r.ancestorIds,['parent']);
});

test('negative controls reject dangling provenance, duplicate identities and unmarked generated slots',()=>{
 const a=small();assert.equal(validateHierarchyAtlas(a).valid,true);
 a.entities[1].sourceRefs=['missing'];assert.equal(validateHierarchyAtlas(a).valid,false);
 const b=small();b.entities.push({...b.entities[0]});assert.equal(validateHierarchyAtlas(b).valid,false);
 const c=small();c.entities[1].assertionLayer='source-assertion';assert.equal(validateHierarchyAtlas(c).valid,false);
 const d=small();d.relationships[0].target='absent';assert.equal(validateHierarchyAtlas(d).valid,false);
});

test('count reconciliation fails on lost slots, duplicate command and source/witness changes',()=>{
 assert.equal(reconcileLegionCatalogue(small(),'w').valid,true);
 const lost=small();lost.relationships=[];assert.equal(reconcileLegionCatalogue(lost,'w').valid,false);
 const duplicate=small();duplicate.relationships.push({...duplicate.relationships[0],id:'twice'});assert.equal(reconcileLegionCatalogue(duplicate,'w').valid,false);
 const source=small();source.entities[1].sourceRefs=['other'];assert.equal(reconcileLegionCatalogue(source,'w').valid,false);
 const wrong=small();wrong.entities[1].witnessId='other';assert.equal(reconcileLegionCatalogue(wrong,'w').valid,false);
 const sequence=small();sequence.entities[1].position.sequence=2;assert.equal(reconcileLegionCatalogue(sequence,'w').valid,false);
 const extent=small();extent.entities[0].statedExtent.value=2;assert.equal(reconcileLegionCatalogue(extent,'w').valid,false);
});
