/** Reuse recovered source definitions; enumerate complete finite classes, not an invented music ontology. */
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
import {compositionCount,compositions,mathematicalPredecessors,pentagonalEndpoint,rotatePentagonalAddress,balancedInheritance,binomial} from '../dist/generational-classes.js';
const root=process.cwd(),read=p=>fs.readFileSync(path.join(root,p)),load=p=>JSON.parse(read(p)),sha=x=>createHash('sha256').update(x).digest('hex');
const recordPath='state/research/native-class/source-records.json',record=load(recordPath);
assert.equal(sha(read(record.sourcePath)),record.sourceSha256);
for(const line of [209,348,384])assert.ok(record.records.some(r=>r.line===line));
const sourceId='source:recovered-five-direction-definition';
const sources=[{id:sourceId,title:'Recovered five-direction definitions and adopted comparison, Oct23',path:recordPath,sha256:sha(read(recordPath)),kind:'role-preserving-research-source',
 boundary:'Assistant definition at line209 and user-supplied/adopted discussion at348/384. Original Padgett experiment reports remain unretrieved.'}];
const entities=[],relationships=[],views=[],classes=[];const refs=[sourceId],viewId='native:five-direction-classes';
function entity(id,name,unit,generation,extra={}){entities.push({id,nativeName:name,aliases:[],unit,tradition:'Recovered five-direction mathematical construction',witnessId:'Oct23-five-direction-definition',position:{generation,sequence:null,cyclicCoordinate:null,orientation:null},
 generationFrame:'Five-direction commutative construction depth; not biological generation, octave, or universal SUNNY class',sourceRefs:refs,exceptions:[],assertionLayer:'source-conditional-mathematical-derivation',...extra});}
function edge(source,target,type,extra={}){relationships.push({id:'class-edge:'+relationships.length,source,target,type,viewIds:[viewId],sourceRefs:refs,assertionLayer:'source-conditional-mathematical-derivation',...extra});}
entity('native-class:root','Five-direction construction classes','source-qualified-constructor-family',null);
const id=m=>'native-class:state:'+m.join(',');
for(let n=0;n<=14;n++){
 const rows=compositions(5,n),classId='native-class:depth:'+n,visited=new Set(),orbits=[];
 entity(classId,'G'+n+' · '+rows.length+' complete count-vector states','native-construction-class',n,{nativeAddress:{frame:'five-direction-construction',depth:n},statedExtent:{value:rows.length,unit:'count-vector states',source:'derived stars-and-bars count'}});
 edge('native-class:root',classId,'has-native-construction-class');
 for(const m of rows){const p=pentagonalEndpoint(m);entity(id(m),'('+m.join(',')+')','five-direction-count-vector',n,{nativeAddress:{frame:'five-direction-construction',depth:n,counts:m},nativeCoordinates:p,globalSunnyAddress:null});edge(classId,id(m),'has-count-vector-state');
  if(n)for(const previous of mathematicalPredecessors(m))edge(id(previous.counts),id(m),'alternative-last-step-construction',{generatorIndex:previous.generatorIndex,biologicalParentage:false});
  if(!visited.has(id(m))){let next=m;const members=[];do{visited.add(id(next));members.push(id(next));next=rotatePentagonalAddress(next);}while(id(next)!==id(m));assert.ok([1,5].includes(members.length));orbits.push(members);}
 }
 assert.equal(BigInt(rows.length),compositionCount(5,n));
 const fixed=n%5===0?1:0;assert.equal(orbits.length,(rows.length+4*fixed)/5);
 classes.push({depth:n,count:rows.length,cumulativeCount:String(binomial(BigInt(n+5),5)),fixedRotationStates:fixed,rotationOrbits:orbits,
  predecessorIncidences:rows.reduce((s,m)=>s+mathematicalPredecessors(m).length,0),sourceGlobalEmbedding:null});
}
assert.equal(classes[3].count,35);assert.equal(classes[4].count,70);assert.equal(classes[4].predecessorIncidences,175);
const c4=compositions(5,4),support=[1,2,3,4].map(k=>c4.filter(m=>m.filter(Boolean).length===k).length);assert.deepEqual(support,[5,30,30,5]);
const comparisons=[{id:'G3-versus-Indian-35',cardinality:35,
 families:['five-direction degree3count vectors','seven svaras × five textbook registers','seven tala types × five jatis'],
 identityEstablished:false,reason:'Different units and actions. Register shift changes octave and is not a five-state identity; equality of cardinality supplies no operator-preserving bridge.'}];
const report={schema:'sunny.native-class-constructors.v1',jevReceipt:'state/jev-receipts/000064-fc22fe7cfcff.json',sources,entities,relationships,
 views:[{id:viewId,label:'Recovered native construction classes G0–G14 and exact four-coordinate endpoints',roots:['native-class:root'],witnessIds:['Oct23-five-direction-definition'],coverage:{kind:'complete-finite-constructor-slice',minimumDepth:0,maximumDisplayDepth:14,mathematicalDepthUnbounded:true,wholeSystemComplete:false}}],
 formula:{classCount:'|G_n|=C(n+4,4)',prefixCount:'sum(k=0..n)|G_k|=C(n+5,5)',sourceDomain:'m inN_0^5, sum(m)=n',predecessors:'m-e_j whenm_j>0; alternative histories, not simultaneous biological parents'},classes,
 exactR4:{field:'Q(zeta5)',basis:['1','zeta5','zeta5^2','zeta5^3'],rank:4,rotationMatrix:[[0,0,0,-1],[1,0,0,-1],[0,1,0,-1],[0,0,1,-1]],
  universalTorusProved:false,meaning:'Exact algebraic endpoint coordinates and two conjugate-plane display embeddings; not a derived metric/radius/oscillation law for the whole SUNNY geometry.'},
 targetReconciliation:{requestedRange:[2500,2700],singleCompleteClassInRange:false,bracketingClasses:[{depth:13,count:2380},{depth:14,count:3060}],
  completePrefixInRange:false,bracketingPrefixes:[{maximumDepth:9,count:2002},{maximumDepth:10,count:3003}],
  implication:'This particular recovered count-vector family cannot supply2500–2700as one complete class or complete initial prefix. Native musical products have different counting units and need their own source-defined operators.'},
 rotationObstruction:{claim:'No single class contains a rotation-closed72-state selection.',proof:'C5orbits have length5, with at most one fixed state (the all-equal vector). Any closed selection has cardinality0or1mod5.72is2mod5.',scope:'One fixed-depth five-direction class; cross-depth unions or other operations remain different hypotheses.'},
 inheritedRecurrence:balancedInheritance([10,0,0,0,0]),comparisons,
 counts:{classNodes:classes.length,countVectorStates:classes.reduce((s,c)=>s+c.count,0),entities:entities.length,relationships:relationships.length},
 sourceHistory:{originalRecordPath:record.sourcePath,originalRecordSha256:record.sourceSha256,recoveredRoles:[{line:209,role:'assistant'},{line:348,role:'user-supplied text'},{line:384,role:'user-supplied text'}],originalExperimentReportsRecovered:false},
 globalSunnyMapping:{selected:false,remaining:['Music-to-generator/source-class bridge','Which angular variable measures the720degree class condition','Radius/rebound/temporal metric and universal four-dimensional realization']},
 codeBindings:['src/generational-classes.ts','dist/generational-classes.js','scripts/derive_native_classes.mjs'].map(p=>({path:p,sha256:sha(read(p))})),
 inputBindings:[{path:recordPath,sha256:sha(read(recordPath))},{path:record.sourcePath,sha256:record.sourceSha256}],canonicalPromotion:false,missionIComplete:false};
fs.writeFileSync(path.join(root,'state/reconstruction/native-class-constructors.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:'passed',exit_code:0,...report.counts,knownCountsReused:[35,70,175],newScope:'completeG0–G14,exactR4basis,all-classrotationobstruction,targetcountreconciliation',universalClassLawEstablished:false}));
