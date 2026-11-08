/** Combine source-scoped views without electing identities or pairing independent axes. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {validateHierarchyAtlas,hierarchyCensus,reconcileLegionCatalogue} from '../dist/hierarchy.js';
const root=fileURLToPath(new URL('../',import.meta.url));
const at=p=>path.join(root,p),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const names=['hierarchy-atlas','musical-hierarchies','angelic-hierarchy-supplement'];
const inputs=names.map(name=>{const p='state/reconstruction/'+name+'.json',b=fs.readFileSync(at(p));return {name,path:p,sha256:sha(b),value:JSON.parse(b.toString('utf8'))};});
const combined={schema:'sunny.hierarchy-atlas-combined.v1',generatedAt:new Date().toISOString(),
  sources:[],entities:[],relationships:[],views:[],componentSnapshots:inputs.map(({value,...rest})=>rest),
  independence:inputs[0].value.independence,
  unresolved:inputs.flatMap(x=>(x.value.unresolved??x.value.boundaries??[]).map(v=>({component:x.name,record:v}))),
  sourceComponents:inputs.map(x=>({name:x.name,coverage:x.value.coverage??x.value.sourceCoverage,
    counts:x.value.counts,inspection:x.value.inspection,discrepancies:x.value.discrepancies})),
  wholeHierarchyComplete:false,globalOrientationSelected:false,
  boundary:'Combined witness/context records and explicitly generated memberships. Independent A/B/C and catalogue axes; source projections, classifications, partnerships, production and command remain typed. No unique global population or complete universal hierarchy is inferred.'};
for(const key of ['sources','entities','relationships','views']){
  const seen=new Map();
  for(const input of inputs)for(const row of input.value[key]){
    const old=seen.get(row.id);
    if(old){
      if(JSON.stringify(old)===JSON.stringify(row))continue;
      if(key!=='sources'||old.sha256!==row.sha256)throw new Error('Conflicting '+key+' identifier: '+row.id);
      old.recordVariants??=[];old.recordVariants.push({component:input.name,record:row});
      continue;
    }
    const copy=structuredClone(row);seen.set(row.id,copy);combined[key].push(copy);
  }
}
const joins=inputs.flatMap(x=>x.value.externalJoinCandidates??[]);
combined.proposedExternalJoins=joins;
const ids=new Set(combined.entities.map(e=>e.id));
if(joins.length){
  const viewId='comparison:Irenaeus-passage-continuation';
  const roots=[...new Set(joins.flatMap(j=>[j.sourceEntityId,j.targetEntityId]))];
  combined.views.push({id:viewId,label:'Proposed Irenaeus passage continuation — explicit interpretation',
    roots,witnessIds:[...new Set(combined.entities.filter(e=>roots.includes(e.id)).map(e=>e.witnessId))],
    coverage:{status:'hypothesis-only-source-role-comparison',universalComplete:false,
      boundary:'A proposed relation between source contexts, not automatic identity or a proven musical mapping.'}});
  for(const [i,j] of joins.entries()){
    assert.ok(ids.has(j.sourceEntityId)&&ids.has(j.targetEntityId),'External join endpoints must exist');
    combined.relationships.push({id:'combined:proposed-continuation:'+i,source:j.sourceEntityId,target:j.targetEntityId,
      type:j.type,viewIds:[viewId],sourceRefs:j.sourceRefs,assertionLayer:j.assertionLayer,boundary:j.boundary});
  }
}
const valid=validateHierarchyAtlas(combined);assert.equal(valid.valid,true,JSON.stringify(valid.errors));
combined.census=hierarchyCensus(combined);
combined.catalogueReconciliation=['uploaded-repository','de-laurence-1916','peterson-sloane3825'].map(witnessId=>({witnessId,...reconcileLegionCatalogue(combined,witnessId)}));
assert.equal(combined.census.generatedMembershipSlots,7911);
assert.ok(combined.catalogueReconciliation.every(x=>x.valid??x.status==='reconciled'),JSON.stringify(combined.catalogueReconciliation));
for(const input of inputs)assert.equal(sha(fs.readFileSync(at(input.path))),input.sha256,'Input changed during merge');
const target=at('state/reconstruction/hierarchy-atlas-combined.json');
if(fs.existsSync(target)){
  const old=fs.readFileSync(target),backup=at('state/checkpoint-history/before-combined-hierarchy-'+sha(old)+'.json');
  if(!fs.existsSync(backup))fs.writeFileSync(backup,old,{flag:'wx'});
}
fs.writeFileSync(target,JSON.stringify(combined,null,2)+'\n');
const report={schema:'sunny.hierarchy-merge-verification.v1',status:'passed',exit_code:0,
  artifact:'state/reconstruction/hierarchy-atlas-combined.json',sha256:sha(fs.readFileSync(target)),
  sources:combined.sources.length,entities:combined.entities.length,relationships:combined.relationships.length,views:combined.views.length,
  census:combined.census,inputs:combined.componentSnapshots,validation:valid,
  boundary:combined.boundary};
fs.writeFileSync(at('docs/evidence/hierarchy-merge-verification.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:'passed',exit_code:0,sha256:report.sha256,entities:report.entities,views:report.views,
  entityRecords:combined.census.entityRecords,generatedMembershipSlots:combined.census.generatedMembershipSlots}));
