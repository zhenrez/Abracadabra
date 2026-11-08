import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {validateHierarchyAtlas,filterHierarchy,hierarchyCensus} from '../dist/hierarchy.js';
const root=new URL('../',import.meta.url);
const atlas=JSON.parse(fs.readFileSync(new URL('state/reconstruction/musical-hierarchies.json',root),'utf8'));
const byId=new Map(atlas.entities.map(e=>[e.id,e]));
const sourceById=new Map(atlas.sources.map(s=>[s.id,s]));
const outgoing=(id,type)=>atlas.relationships.filter(e=>e.source===id&&(!type||e.type===type));
const children=(id,type)=>outgoing(id,type).map(e=>byId.get(e.target));

test('actual source hashes, typed references and pixel panels bind the supplied witness supplement',()=>{
 assert.equal(validateHierarchyAtlas(atlas).valid,true);
 for(const source of atlas.sources){
  const bytes=fs.readFileSync(new URL(source.path.replaceAll('\\','/'),root));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),source.sha256);
 }
 for(const entity of atlas.entities){
  const evidence=entity.evidence;if(!evidence?.pixelBounds)continue;
  const [x0,y0,x1,y1]=evidence.pixelBounds,[width,height]=sourceById.get(evidence.sourceId).dimensions;
  assert.ok(x0>=0&&y0>=0&&x1>x0&&y1>y0&&x1<=width&&y1<=height,entity.id);
 }
 assert.equal(atlas.inspection.length,12);assert.ok(atlas.inspection.every(i=>i.allPrintedClaimsProcessed===false));
});

test('Chinese generation, seasons and7/5versus6/6partitions retain different relation frames',()=>{
 const pipes=atlas.entities.filter(e=>e.unit==='witness-named-lu-standard');assert.equal(pipes.length,12);
 const sequence=pipes.toSorted((a,b)=>a.position.sequence-b.position.sequence);
 assert.deepEqual(sequence.slice(0,3).map(e=>e.nativeName),['黃鐘','林鐘','太蔟']);
 const generation=atlas.relationships.filter(e=>e.type==='source-generates-next-lu');assert.equal(generation.length,11);
 assert.equal(generation.some(e=>e.source===sequence.at(-1).id&&e.target===sequence[0].id),false);
 assert.notDeepEqual(sequence.map(e=>e.nativeCoordinates.generationOrderIndex),sequence.map(e=>e.nativeCoordinates.seasonalOrderIndex));
 const parts=atlas.entities.filter(e=>e.unit==='source-up-down-lu-category');
 assert.deepEqual(parts.map(p=>children(p.id,'has-up-down-member').length),[7,5]);
 const members=parts.flatMap(p=>children(p.id,'has-up-down-member').map(e=>e.id));assert.equal(new Set(members).size,12);
 const polarity=atlas.entities.filter(e=>e.unit==='source-yin-yang-lu-category');assert.deepEqual(polarity.map(p=>children(p.id,'has-yin-yang-member').length),[6,6]);
 assert.ok(polarity.every(p=>p.witnessId==='ZhouLi-ZhuShu23'));
 assert.ok(parts.every(p=>p.witnessId==='LuShiChunqiu-YinLv'));
 assert.ok(pipes.every(p=>p.exactFrequency===null));
});

test('all60Lamcontexts execute distinct native actions with inverseb/q and exact60return',()=>{
 const contexts=atlas.entities.filter(e=>e.unit==='Lam-pentatonic-note-context');assert.equal(contexts.length,60);
 const step=(id,name)=>{const edges=outgoing(id,'native-xuangong-'+name);assert.equal(edges.length,1);return byId.get(edges[0].target);};
 for(const context of contexts){
  const c=context.nativeCoordinates;
  assert.equal(step(context.id,'T1').nativeCoordinates.pos_note,c.pos_note);
  assert.equal(step(context.id,'t1').nativeCoordinates.pc_pent,c.pc_pent);
  assert.equal(step(step(context.id,'b1').id,'q1').id,context.id);
  const seen=new Set([context.id]);let current=step(context.id,'q1');
  while(current.id!==context.id){assert.equal(seen.has(current.id),false);seen.add(current.id);current=step(current.id,'q1');}
  assert.equal(seen.size,60);
 }
 const chinese=filterHierarchy(atlas,{viewIds:['music:chinese']});
 assert.equal(chinese.entities.some(e=>e.unit==='key-degree-triad-occurrence'),false);
 assert.ok(atlas.entities.find(e=>e.id==='music:chinese:lam').nativeConvention.includes('convention'));
});

test('key-degree-chord-tone ancestry is real contextual structure rather than unrelated pitch counts',()=>{
 const keys=atlas.entities.filter(e=>e.unit==='major-key-context');assert.equal(keys.length,12);
 const expected=[[0,4,7],[0,3,7],[0,3,7],[0,4,7],[0,4,7],[0,3,7],[0,3,6]];
 for(const key of keys){
  const degrees=children(key.id,'has-scale-degree-context').toSorted((a,b)=>a.position.sequence-b.position.sequence);assert.equal(degrees.length,7);
  degrees.forEach((degree,i)=>{
   const chords=children(degree.id,'stack-alternate-scale-thirds');assert.equal(chords.length,1);
   assert.deepEqual(chords[0].semitoneOffsetsFromDegree,expected[i]);
   assert.equal(children(chords[0].id,'has-chord-tone-occurrence').length,3);
   assert.equal(children(chords[0].id,'projects-to-root-quality-triad').length,1);
  });
 }
 assert.equal(atlas.entities.filter(e=>e.unit==='root-qualified-triad-occurrence').length,48);
 assert.equal(atlas.entities.some(e=>/MIDI|pitch-subset/.test(e.unit)),false);
 const census=hierarchyCensus(atlas);assert.equal(census.uniqueEntitiesAcrossWitnesses,null);
});

test('instrument types/cells and rhythmic values do not become invented physical populations',()=>{
 const rows=atlas.entities.filter(e=>e.unit==='image-native-organological-category');assert.equal(rows.length,9);
 for(const row of rows)assert.equal(children(row.id,'has-illustrated-region-cell').length,7);
 assert.ok(atlas.entities.some(e=>e.unit==='illustrated-instrument-table-cell'&&e.evidence.transcriptionStatus==='uncertain-caption-reading'));
 const materials=atlas.entities.filter(e=>e.unit==='bayin-material-category');assert.equal(materials.length,8);
 assert.equal(materials.flatMap(e=>children(e.id,'classifies-instrument-kind')).length,13);
 assert.ok(atlas.entities.filter(e=>e.unit==='source-instrument-kind').every(e=>e.physicalInstrumentOrPlayerCount===null));
 const feet=atlas.entities.filter(e=>e.unit==='source-long-short-pattern');assert.equal(new Set(feet.map(f=>f.pattern)).size,12);
 assert.equal(feet.filter(f=>f.pattern.length===2).length,4);assert.equal(feet.filter(f=>f.pattern.length===3).length,8);
 const durations=atlas.entities.filter(e=>e.unit==='relative-duration-value');assert.equal(durations.length,16);
 assert.ok(durations.every(e=>BigInt(e.durationWholeNoteRatio.numerator)>0n&&e.performedOccurrenceCount===null));
});

test('incomplete source coverage remains explicit and broken parent references fail validation',()=>{
 assert.equal(atlas.wholeMusicalSystemsComplete,false);assert.equal(atlas.missionIComplete,false);assert.equal(atlas.globalOrientationSelected,false);
 const corrupt=structuredClone(atlas);corrupt.relationships[0].target='music:nonexistent';
 assert.equal(validateHierarchyAtlas(corrupt).valid,false);
 const residual=byId.get('music:western:pythagorean-residual');assert.deepEqual(residual.exactTwelveFifthsResidual,{numerator:'531441',denominator:'524288'});
 assert.equal(residual.firstNearestLabelBoundaryCrossing,26);
});
