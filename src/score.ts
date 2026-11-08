/** Executable, source-qualified score views. These contracts are not a cosmological ontology. */
import {rational, type Rational, type Json, type Verdict} from './law.js';
import type {createNativeExecutor} from './native-operators.js';

export type ScoreField<T> = {status:'known'; value:T; sourceRefs:string[]}
  | {status:'unknown'; missing:string; sourceRefs:string[]};
export interface ScoreQuantity {value:Rational; dimension:string; carrier:string; unit:string; reference:string}
export interface ScoreNote {label:string; relativeFrequency:ScoreField<ScoreQuantity>; absoluteHz:ScoreField<ScoreQuantity>}
export interface ScoreParticipant {
  id:string; label:string; sourceRefs:string[];
  role:ScoreField<string>; instrument:ScoreField<string>; note:ScoreField<ScoreNote>; register:ScoreField<string>;
  onset:ScoreField<ScoreQuantity>; duration:ScoreField<ScoreQuantity>;
  coordinates:Record<string,ScoreField<Json>>;
}
export interface ScoreEvent {id:string; participantId:string; kind:string; at:ScoreField<ScoreQuantity>; sourceRefs:string[]}
export interface ScoreOrder {id:string; before:string; after:string; relation:string; sourceRefs:string[]}
export interface ScoreTransition {
  id:string; relation:string; input:ScoreField<ScoreQuantity>; factor:ScoreField<Rational>;
  expected:ScoreField<ScoreQuantity>; sourceRefs:string[];
}
export interface ScoreView {
  id:string; system:string; condition:string; sourceRefs:string[];
  participants:ScoreParticipant[]; events:ScoreEvent[]; order:ScoreOrder[]; transitions:ScoreTransition[];
}
export interface ScorePatternLink {
  id:string; fromView:string; toView:string; fromParticipants:string[]; toParticipants:string[];
  normalization:'divide-by-first-within-each-declared-frame'; preserves:string[];
  missingRelations:string[]; sourceRefs:string[]; condition:string;
}
export interface ScoreProgram {id:string; views:ScoreView[]; links:ScorePatternLink[]; sourceRefs:string[]}
export interface ScoreCheck {id:string; verdict:Verdict; reason:string; missingVariables:string[]; sourceRefs:string[]; output?:Json}
type NativeExecutor=ReturnType<typeof createNativeExecutor>;
const refs=(v:string[])=>Array.isArray(v)&&v.length>0&&v.every(s=>typeof s==='string'&&s.trim().length>0);
const text=(s:string)=>typeof s==='string'&&s.trim().length>0;
function rat(q:Rational):Rational {
  if (!q || typeof q.numerator!=='string'||typeof q.denominator!=='string'||q.numerator.length>128||q.denominator.length>128) throw new TypeError('bounded exact rational required');
  return rational(q.numerator,q.denominator);
}
const add=(a:Rational,b:Rational)=>rational(BigInt(a.numerator)*BigInt(b.denominator)+BigInt(b.numerator)*BigInt(a.denominator),BigInt(a.denominator)*BigInt(b.denominator));
const sub=(a:Rational,b:Rational)=>add(a,{numerator:String(-BigInt(b.numerator)),denominator:b.denominator});
const divide=(a:Rational,b:Rational)=>rational(BigInt(a.numerator)*BigInt(b.denominator),BigInt(a.denominator)*BigInt(b.numerator));
const cmp=(a:Rational,b:Rational)=>{const d=BigInt(a.numerator)*BigInt(b.denominator)-BigInt(b.numerator)*BigInt(a.denominator);return d<0n?-1:d>0n?1:0;};
function quantity(q:ScoreQuantity):ScoreQuantity {
  if(!q||!text(q.dimension)||!text(q.carrier)||!text(q.unit)||!text(q.reference))throw new TypeError('quantity requires dimension, carrier, unit and reference frame');
  return {...q,value:rat(q.value)};
}
export function sameScoreFrame(a:ScoreQuantity,b:ScoreQuantity):boolean {
  quantity(a);quantity(b);return a.dimension===b.dimension&&a.carrier===b.carrier&&a.unit===b.unit&&a.reference===b.reference;
}
function check(id:string,verdict:Verdict,reason:string,sourceRefs:string[],missingVariables:string[]=[],output?:Json):ScoreCheck {
  return {id,verdict,reason,sourceRefs,missingVariables,...(output===undefined?{}:{output})};
}
function known<T>(field:ScoreField<T>,id:string,sourceRefs:string[],checks:ScoreCheck[]):T|undefined {
  if(field.status==='unknown'){checks.push(check(id,'unknown',field.missing,sourceRefs,[id]));return undefined;}
  if(!refs(field.sourceRefs)){checks.push(check(id,'unknown','Known value has no source binding.',sourceRefs,[id+':sourceRefs']));return undefined;}
  return field.value;
}
function unique(values:{id:string}[],name:string):void {
  if(values.some(x=>!text(x.id))||new Set(values.map(x=>x.id)).size!==values.length)throw new TypeError(name+' IDs must be nonempty and unique');
}

/** Scalar action dispatches to the existing source-bound native executor after frame checks. */
export function executeScoreTransition(t:ScoreTransition,native:NativeExecutor):ScoreCheck {
  const checks:ScoreCheck[]=[];
  if(!refs(t.sourceRefs))return check(t.id,'unknown','Transition source is unresolved.',[],[t.id+':sourceRefs']);
  const input=known(t.input,t.id+':input',t.sourceRefs,checks),factor=known(t.factor,t.id+':factor',t.sourceRefs,checks),expected=known(t.expected,t.id+':expected',t.sourceRefs,checks);
  if(input===undefined||factor===undefined||expected===undefined)return check(t.id,'unknown','Transition has localized missing inputs.',t.sourceRefs,checks.flatMap(x=>x.missingVariables));
  try {
    const a=quantity(input),b=quantity(expected);
    if(!sameScoreFrame(a,b))return check(t.id,'fail','Scalar action cannot change carrier, unit or reference frame without an explicit adapter.',t.sourceRefs);
    const result=native.execute('MEC-01',{value:a.value,factor:rat(factor),carrier:a.carrier,unit:a.unit});
    if(result.status!=='executed')return check(t.id,result.status==='invalid'?'fail':'unknown',result.reason??'Native scalar result unavailable.',t.sourceRefs,[t.id+':nativeAction']);
    const value=rat((result.output as unknown as {value:Rational}).value);
    return check(t.id,cmp(value,b.value)===0?'pass':'fail','Exact source-native scalar action in the unchanged declared frame.',t.sourceRefs,[],{actual:value as unknown as Json,expected:b.value as unknown as Json,nativeSource:result.source as unknown as Json});
  } catch(error) {return check(t.id,'fail',error instanceof Error?error.message:String(error),t.sourceRefs);}
}

export function executeScoreView(view:ScoreView,native:NativeExecutor) {
  unique(view.participants,'participant');unique(view.events,'event');unique(view.order,'order');unique(view.transitions,'transition');
  if(view.participants.length>256||view.events.length>1024||view.order.length>2048)throw new RangeError('bounded score view exceeded');
  const checks:ScoreCheck[]=[];
  const intervals:{id:string;onset:ScoreQuantity;end:ScoreQuantity}[]=[];
  for(const p of view.participants){
    for(const [key,field] of Object.entries({role:p.role,instrument:p.instrument,register:p.register,...p.coordinates}))known(field,p.id+':'+key,p.sourceRefs,checks);
    const note=known(p.note,p.id+':note',p.sourceRefs,checks);
    if(note){
      for(const [key,field] of Object.entries({relativeFrequency:note.relativeFrequency,absoluteHz:note.absoluteHz})){
        const value=known(field,p.id+':'+key,p.sourceRefs,checks);
        if(value!==undefined){
          try{const q=quantity(value);
            if(q.dimension!=='frequency'||BigInt(q.value.numerator)<=0n||(key==='absoluteHz'&&q.unit!=='Hz'))throw new TypeError('Pitch needs a positive frequency quantity; absoluteHz additionally requires Hz units.');
            checks.push(check(p.id+':'+key+':domain','pass','Positive frequency in its declared reference.',p.sourceRefs));
          }catch(error){checks.push(check(p.id+':'+key+':domain','fail',error instanceof Error?error.message:String(error),p.sourceRefs));}
        }
      }
    }
    const onset=known(p.onset,p.id+':onset',p.sourceRefs,checks),duration=known(p.duration,p.id+':duration',p.sourceRefs,checks);
    if(onset&&duration){
      try{
        const a=quantity(onset),d=quantity(duration);
        if(a.dimension!=='time'||d.dimension!=='time'){checks.push(check(p.id+':interval','fail','Intervals require time quantities; generation and address counts cannot substitute.',p.sourceRefs));continue;}
        if(!sameScoreFrame(a,d)){checks.push(check(p.id+':interval','fail','Onset and duration use different carriers, units or clock references.',p.sourceRefs));continue;}
        if(cmp(d.value,rational(0,1))<=0){checks.push(check(p.id+':interval','fail','Duration must be strictly positive.',p.sourceRefs));continue;}
        intervals.push({id:p.id,onset:a,end:{...a,value:add(a.value,d.value)}});
        checks.push(check(p.id+':interval','pass','Positive half-open interval in its declared carrier and clock.',p.sourceRefs));
      }catch(error){checks.push(check(p.id+':interval','fail',error instanceof Error?error.message:String(error),p.sourceRefs));}
    }
  }
  const eventMap=new Map(view.events.map(e=>[e.id,e]));
  const graph=new Map(view.events.map(e=>[e.id,[] as string[]]));
  for(const e of view.events){
    if(!view.participants.some(p=>p.id===e.participantId))checks.push(check(e.id,'fail','Event participant is absent.',e.sourceRefs));
  }
  for(const relation of view.order){
    const a=eventMap.get(relation.before),b=eventMap.get(relation.after);
    if(!a||!b){checks.push(check(relation.id,'fail','Partial-order endpoint is absent.',relation.sourceRefs));continue;}
    graph.get(a.id)!.push(b.id);
    if(!refs(relation.sourceRefs)){checks.push(check(relation.id,'unknown','Partial-order relation has no source binding.',[],[relation.id+':sourceRefs']));continue;}
    const ac:ScoreCheck[]=[];const av=known(a.at,a.id+':time',a.sourceRefs,ac),bv=known(b.at,b.id+':time',b.sourceRefs,ac);
    if(av===undefined||bv===undefined){checks.push(check(relation.id,'unknown','Order is declared, but metric timing is not assigned.',relation.sourceRefs,ac.flatMap(x=>x.missingVariables)));continue;}
    try{
      if(av.dimension!=='time'||bv.dimension!=='time'){checks.push(check(relation.id,'fail','Metric event order requires time quantities; generation/address order must remain a separate declared relation.',relation.sourceRefs));continue;}
      checks.push(check(relation.id,!sameScoreFrame(av,bv)||cmp(rat(av.value),rat(bv.value))>=0?'fail':'pass',
        !sameScoreFrame(av,bv)?'Order cannot compare different carriers, units or references.':'Strict source-event order checked in the declared clock.',relation.sourceRefs));
    }catch(error){checks.push(check(relation.id,'fail',error instanceof Error?error.message:String(error),relation.sourceRefs));}
  }
  const visiting=new Set<string>(),visited=new Set<string>();let cycle=false;
  function visit(id:string){if(visiting.has(id)){cycle=true;return;}if(visited.has(id))return;visiting.add(id);for(const next of graph.get(id)??[])visit(next);visiting.delete(id);visited.add(id);}
  for(const id of graph.keys())visit(id);
  checks.push(check(view.id+':partial-order',cycle?'fail':'pass',cycle?'Declared partial order contains a cycle.':'Declared order is acyclic; no metric duration follows from construction order alone.',view.sourceRefs));
  const windows:{onset:ScoreQuantity;duration:ScoreQuantity;activeParticipantIds:string[]}[]=[];
  if(intervals.length===view.participants.length&&intervals.length){
    const frame=intervals[0]!.onset;
    if(!intervals.every(x=>sameScoreFrame(frame,x.onset)))checks.push(check(view.id+':overlap','fail','Overlap requires one declared carrier, unit and clock reference.',view.sourceRefs));
    else{
      const endpoints=[...intervals.flatMap(x=>[x.onset.value,x.end.value])].sort(cmp).filter((x,i,a)=>i===0||cmp(x,a[i-1]!)!==0);
      for(let i=0;i<endpoints.length-1;i++){
        const start=endpoints[i]!,end=endpoints[i+1]!;
        const active=intervals.filter(x=>cmp(x.onset.value,start)<=0&&cmp(x.end.value,start)>0).map(x=>x.id);
        if(active.length)windows.push({onset:{...frame,value:start},duration:{...frame,value:sub(end,start)},activeParticipantIds:active});
      }
      checks.push(check(view.id+':overlap','pass','Half-open overlap windows computed only in the declared carrier; no audio sustain inferred.',view.sourceRefs,[],{windows:windows.length}));
    }
  }else checks.push(check(view.id+':overlap','unknown','Some intervals are unavailable; no complete overlap pattern is inferred.',view.sourceRefs,view.participants.filter(p=>!intervals.some(i=>i.id===p.id)).map(p=>p.id+':interval')));
  for(const t of view.transitions)checks.push(executeScoreTransition(t,native));
  return {viewId:view.id,status:checks.some(x=>x.verdict==='fail')?'inconsistent':checks.some(x=>x.verdict==='unknown')?'partial':'executed-within-supplied-view',
    checks,overlapWindows:windows,missingVariables:[...new Set(checks.flatMap(x=>x.missingVariables))],universalCompletion:false};
}

function executePatternLink(link:ScorePatternLink,program:ScoreProgram):ScoreCheck {
  if(link.normalization!=='divide-by-first-within-each-declared-frame')return check(link.id,'fail','Unsupported cross-system normalization.',link.sourceRefs);
  if(!refs(link.sourceRefs))return check(link.id,'unknown','Cross-system link source is unresolved.',[],[link.id+':sourceRefs']);
  const from=program.views.find(v=>v.id===link.fromView),to=program.views.find(v=>v.id===link.toView);
  if(!from||!to)return check(link.id,'fail','Cross-system view is absent.',link.sourceRefs);
  if(link.fromParticipants.length!==link.toParticipants.length||link.fromParticipants.length===0)return check(link.id,'fail','Pattern endpoints must have equal nonzero arity.',link.sourceRefs);
  const sequences:ScoreQuantity[][]=[];
  for(const [view,ids] of [[from,link.fromParticipants],[to,link.toParticipants]] as const){
    const values:ScoreQuantity[]=[];
    for(const id of ids){const p=view.participants.find(p=>p.id===id);
      if(!p)return check(link.id,'fail','Pattern participant is absent.',link.sourceRefs);
      if(p.note.status!=='known'||p.note.value.relativeFrequency.status!=='known')return check(link.id,'unknown','Relative pitch pattern is incomplete.',link.sourceRefs,[id+':relativeFrequency']);
      const field=p.note.value.relativeFrequency;if(!refs(p.note.sourceRefs)||!refs(field.sourceRefs))return check(link.id,'unknown','Pattern pitch lacks source binding.',link.sourceRefs,[id+':pitchSource']);
      values.push(quantity(field.value));
    }sequences.push(values);
  }
  const [a,b]=sequences as [ScoreQuantity[],ScoreQuantity[]];
  if(!a.every(v=>sameScoreFrame(v,a[0]!))||!b.every(v=>sameScoreFrame(v,b[0]!))||a[0]!.carrier!==b[0]!.carrier||a[0]!.unit!==b[0]!.unit)return check(link.id,'fail','Pattern normalization cannot mix carriers or units.',link.sourceRefs);
  if(a.some(x=>BigInt(x.value.numerator)<=0n)||b.some(x=>BigInt(x.value.numerator)<=0n))return check(link.id,'fail','Relative pitch normalization needs positive values.',link.sourceRefs);
  const norm=(values:ScoreQuantity[])=>values.map(x=>divide(x.value,values[0]!.value));
  const x=norm(a),y=norm(b);return check(link.id,x.every((v,i)=>cmp(v,y[i]!)===0)?'pass':'fail',
    'Explicit source-qualified comparison of ordered relative ratios; timing, ancestry and identity are not identified.',link.sourceRefs,[],{from:x as unknown as Json,to:y as unknown as Json});
}

export function executeMasterScore(program:ScoreProgram,native:NativeExecutor){
  unique(program.views,'view');unique(program.links,'link');
  const views=program.views.map(v=>executeScoreView(v,native));
  const links=program.links.map(l=>{try{return executePatternLink(l,program);}catch(error){return check(l.id,'fail',error instanceof Error?error.message:String(error),l.sourceRefs);}});
  const failed=views.some(v=>v.status==='inconsistent')||links.some(l=>l.verdict==='fail');
  return {schema:'sunny.master-score-execution.v1',programId:program.id,status:failed?'inconsistent':'partial-source-backed-instantiation',
    views,links,missingVariables:views.flatMap(v=>v.missingVariables.map(variable=>({viewId:v.viewId,variable}))),
    scope:'Only supplied source views and declared adapters; unknown fields remain unassigned.',universalCompletion:false,missionIComplete:false,canonicalPromotion:false};
}
