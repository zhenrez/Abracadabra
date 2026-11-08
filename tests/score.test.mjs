import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createNativeExecutor} from '../dist/native-operators.js';
import {executeMasterScore,executeScoreView,executeScoreTransition,sameScoreFrame} from '../dist/score.js';
const root=new URL('../',import.meta.url),load=p=>JSON.parse(fs.readFileSync(new URL(p,root),'utf8').replace(/^\uFEFF/,''));
const fixture=load('state/reconstruction/master-score.json');
const nativeSource=fixture.provenance.native_source;
const native=createNativeExecutor(fs.readFileSync(new URL(nativeSource.path,root)),nativeSource.sourceId);
const clone=x=>structuredClone(x);
const cn=fixture.program.views.find(v=>v.id==='chinese-native-construction');
const sol=fixture.program.views.find(v=>v.id==='sophia-working-lock');
const q=(n,d=1)=>({numerator:String(n),denominator:String(d)});

test('source Chinese construction preserves81→54→72 /8→12→9 and unassigned timing',()=>{
  const out=executeScoreView(cn,native);
  assert.deepEqual(cn.participants.map(p=>p.note.value.relativeFrequency.value.value),[q(8),q(12),q(9)]);
  assert.deepEqual(fixture.sourceMathChecks.chineseNativeOrder.products,[q(648),q(648),q(648)]);
  assert.equal(out.checks.filter(c=>c.id.startsWith('cn:length:')||c.id.startsWith('cn:frequency:')).every(c=>c.verdict==='pass'),true);
  assert.equal(out.overlapWindows.length,0);
  assert.ok(out.checks.some(c=>c.id==='cn:order:0'&&c.verdict==='unknown'));
  assert.ok(cn.participants.every(p=>p.duration.status==='unknown'&&p.onset.status==='unknown'));
});
test('all five source witness chronologies reproduce their five overlap stages without claiming audio sustain',()=>{
  const expected={MT:[35,30,373,30,61],SP:[135,130,173,130,101],Greek_430:[135,130,300,30,130],Greek_400:[135,130,270,60,130],Clementine_Latin:[35,30,273,130,61]};
  for(const [name,durations] of Object.entries(expected)){
    const view=fixture.program.views.find(v=>v.id==='chronology:'+name),out=executeScoreView(view,native);
    assert.deepEqual(out.overlapWindows.map(w=>w.duration.value),durations.map(n=>q(n)));
    assert.deepEqual(out.overlapWindows.map(w=>w.activeParticipantIds.length),[1,2,3,2,1]);
    assert.ok(out.overlapWindows.every(w=>w.onset.carrier==='chronological-lifetime'&&w.duration.unit==='reported-year'));
    assert.match(view.condition,/not audible sustain/);
    assert.equal(out.checks.some(c=>c.verdict==='fail'),false);
  }
});
test('clock, dimension, unit, reference and genealogy/succession carrier conflations fail explicitly',()=>{
  const base=clone(fixture.program.views.find(v=>v.id==='chronology:MT'));
  for(const patch of [{unit:'beat'},{reference:'another birth origin'},{carrier:'audible-performance'},{dimension:'count',carrier:'biological-descent-depth'}]){
    const view=clone(base);Object.assign(view.participants[0].duration.value,patch);
    assert.ok(executeScoreView(view,native).checks.some(c=>c.id.endsWith(':interval')&&c.verdict==='fail'));
  }
  const t=clone(cn.transitions[0]);t.expected.value.carrier='succession';assert.equal(executeScoreTransition(t,native).verdict,'fail');
  const a={...base.participants[0].onset.value,dimension:'count',carrier:'biological-descent-depth',unit:'generation-step'};
  const b={...a,carrier:'institutional-succession'};assert.equal(sameScoreFrame(a,b),false);
  const countClock=clone(base);for(const event of countClock.events)event.at.value.dimension='count';
  assert.ok(executeScoreView(countClock,native).checks.some(c=>c.id===countClock.order[0].id&&c.verdict==='fail'));
});
test('cyclic source order and a known reversed chronological order are rejected',()=>{
  const c=clone(cn);c.order.push({...c.order[0],id:'adverse:cycle',before:'cn:event:2',after:'cn:event:0'});
  assert.ok(executeScoreView(c,native).checks.some(x=>x.id.endsWith(':partial-order')&&x.verdict==='fail'));
  const v=clone(fixture.program.views.find(v=>v.id==='chronology:MT'));
  [v.order[0].before,v.order[0].after]=[v.order[0].after,v.order[0].before];
  assert.ok(executeScoreView(v,native).checks.some(x=>x.id===v.order[0].id&&x.verdict==='fail'));
});
test('Sophia working labels execute relative octave/fifth with no inventedHz, time or instrument',()=>{
  assert.deepEqual(sol.participants.map(p=>[p.label,p.note.value.label,p.register.value]),[['Sophia','F','upper'],['Yaldabaoth','F','lower'],['Sabaoth','C','lower']]);
  assert.deepEqual(sol.participants.map(p=>p.note.value.relativeFrequency.value.value),[q(1),q(1,2),q(3,4)]);
  assert.ok(sol.participants.every(p=>p.note.value.absoluteHz.status==='unknown'&&p.onset.status==='unknown'&&p.instrument.status==='unknown'));
  const out=executeScoreView(sol,native);assert.ok(sol.transitions.every(t=>out.checks.find(c=>c.id===t.id)?.verdict==='pass'));
});
test('explicit cross-system links preserve ordered ratios and reject reordered or invalid quantities',()=>{
  const output=executeMasterScore(fixture.program,native);assert.ok(output.links.every(c=>c.verdict==='pass'));
  const changed=clone(fixture.program);[changed.links[0].toParticipants[1],changed.links[0].toParticipants[2]]=[changed.links[0].toParticipants[2],changed.links[0].toParticipants[1]];
  assert.equal(executeMasterScore(changed,native).links[0].verdict,'fail');
  const malformed=clone(fixture.program);malformed.views[0].participants[0].note.value.relativeFrequency.value.value.denominator='0';
  assert.doesNotThrow(()=>executeMasterScore(malformed,native));assert.equal(executeMasterScore(malformed,native).links[0].verdict,'fail');
});
test('known negative/zero/wrong-dimension pitches fail, while unknown evidence cannot become a completed score',()=>{
  for(const value of [q(-1),q(0)]){
    const view=clone(cn);view.participants[0].note.value.relativeFrequency.value.value=value;
    assert.ok(executeScoreView(view,native).checks.some(c=>c.id==='cn:0:relativeFrequency:domain'&&c.verdict==='fail'));
  }
  const wrong=clone(cn);wrong.participants[0].note.value.relativeFrequency.value.dimension='time';
  assert.ok(executeScoreView(wrong,native).checks.some(c=>c.id==='cn:0:relativeFrequency:domain'&&c.verdict==='fail'));
  const unbound=clone(cn.transitions[0]);unbound.factor.sourceRefs=[];assert.equal(executeScoreTransition(unbound,native).verdict,'unknown');
  const result=executeMasterScore(fixture.program,native);assert.equal(result.status,'partial-source-backed-instantiation');assert.equal(result.universalCompletion,false);assert.equal(result.missionIComplete,false);assert.ok(result.missingVariables.length>0);
});
