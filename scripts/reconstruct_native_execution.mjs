/** Source-bound register; requires npm run build first. No service or network use. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {createNativeExecutor,NATIVE_GG_SHA256} from '../dist/native-operators.js';

const root=fileURLToPath(new URL('../',import.meta.url));
const at=p=>fileURLToPath(new URL('../'+p,import.meta.url));
const hash=b=>createHash('sha256').update(b).digest('hex');
const sourcePath='data/raw/archive/SUN_Universal_Archive/Library/SUN_DEEP_RECOVERY/SUN_GG_v1_final.json';
const sourceId='9e03168cabf04e3887245d93c75f1f9d0034a53bead61e5d8b5a5e0315b259e8';
const native=createNativeExecutor(readFileSync(at(sourcePath)),sourceId);
const q=(n,d=1)=>({numerator:String(n),denominator:String(d)});
const tests=spawnSync(process.execPath,['--test','tests/native-operators.test.mjs'],{cwd:root,timeout:30000,maxBuffer:1048576,encoding:'utf8',windowsHide:true});
if(tests.status!==0)throw new Error('Focused native tests failed: '+tests.stdout+tests.stderr);
mkdirSync(at('docs/evidence/native-execution'),{recursive:true});
writeFileSync(at('docs/evidence/native-execution/focused-tests.tap'),tests.stdout,'utf8');

const scenarios=[
 ['MEC-01','source R then L gives exact O',()=>{const a=native.execute('MEC-01',{value:q(1),factor:q(2,3),carrier:'relative string length',unit:'relative length'});return native.execute('MEC-01',{value:a.output.value,factor:q(3,4),carrier:'relative string length',unit:'relative length'});} ],
 ['MEC-02','abstract T1 acting on all twelve pitch classes',()=>native.execute('MEC-02',{values:Array.from({length:12},(_,i)=>i),action:{sign:1,offset:1},realization:'Z12_affine'})],
 ['MEC-03','test sequence reversal; example values are not historical notes',()=>native.execute('MEC-03',{values:[1,2,3]})],
 ['MEC-04','no supplied historical overlap map remains unknown',()=>native.execute('MEC-04',{state:{identity:'unspecified',pitch:q(1),address:'unspecified'}})],
 ['MEC-05','test seven-index carrier; no historical pitch assignments',()=>native.execute('MEC-05',{values:[0,1,2,3,4,5,6],shift:1})],
 ['MEC-06','source E(5,13), full cyclic orbit',()=>native.execute('MEC-06',{slots:13,onsets:5})],
 ['MEC-07','test finite residue universe only',()=>native.execute('MEC-07',{universe:Array.from({length:13},(_,i)=>i-6),expression:{op:'complement',child:{op:'residue',modulus:3,residue:1}}})],
 ['MEC-08','test single-event dot; no historical event supplied',()=>native.execute('MEC-08',{events:[{id:'test:event',duration:q(1)}],unit:'beats',mode:'dot',index:0})],
 ['MEC-09','no actual joint-constitution inputs remain unknown',()=>native.execute('MEC-09',{available:[]})],
 ['MEC-10','no actual learned kernel supplied remains unknown',()=>native.execute('MEC-10',{context:[]})],
];
const observations=scenarios.map(([mechanismId,assertion,run])=>({mechanismId,assertion,result:run()}));
const requirements={
 'MEC-01':'Positive exact rational scalar and positive value, explicitly named carrier/unit. Zhu radical q=2^(1/12) is not represented by a fabricated rational.',
 'MEC-02':'Explicit abstract Z12 affine action (sign,offset). Native neo-Riemannian triad encoding/action is not supplied by abstract group equivalence.',
 'MEC-03':'Finite supplied sequence. Nonretrogradability is its reversal fixed-point predicate.',
 'MEC-04':'Actual overlap/mutation map, shared pitch/object identity, caller-declared admissibility and source references.',
 'MEC-05':'Finite nonempty cyclic sequence and integer shift. No origin or pitch tuning inferred.',
 'MEC-06':'Integers 0<=k<=n<=256,n>=1. Output is the entire distinct cyclic orbit, so phase remains open.',
 'MEC-07':'Explicit bounded finite integer universe and complete Boolean residue expression. Infinite set algebra is only evaluated on that universe.',
 'MEC-08':'Explicit event IDs, positive rational durations and unit; selected event/index and positive addition, dot, or positive inserted event. Historical shortness is not invented.',
 'MEC-09':'Source-qualified admissible rule, full distinct antecedent list, supplied antecedent witnesses, declared composite. No acoustic proof is inferred.',
 'MEC-10':'Actual source-qualified versioned finite kernel and a matching context, exact nonnegative probabilities summing to one. No training data or kernel is invented.',
};
const registry=native.registry().map(entry=>({...entry,implementationStatus:'bounded conditional interpreter',nativeInstanceRequirements:requirements[entry.id],families:entry.families.map(member=>({...member,coverage:member.system==='Zhu equal division'?'irrational generator not represented by rational subset':member.system==='neo-Riemannian PLR'?'abstract family represented; actual triad map remains required':'parameterized mechanism; native instance depends on supplied carrier/data'}))}));
const tracked=['src/native-operators.ts','tests/native-operators.test.mjs','scripts/reconstruct_native_execution.mjs',sourcePath,'docs/evidence/native-execution-math-jev-request.json','docs/evidence/native-execution-math-jev-result.json','docs/evidence/native-execution-wolfram-request.json','docs/evidence/native-execution-wolfram-result.json'];
const state={schema:'sunny.native-execution.v1',generatedAt:new Date().toISOString(),source:{sourceId,sha256:NATIVE_GG_SHA256,path:sourcePath},
 counts:{mechanisms:registry.length,sourceMemberOccurrences:registry.flatMap(x=>x.families).length,focusedTests:14,scenarioExecutions:observations.filter(x=>x.result.status==='executed').length,scenarioUnknowns:observations.filter(x=>x.result.status==='unknown').length},
 status:'All ten mechanisms have bounded interpreters; historical instances and irrational extensions are not thereby completed.',canonicalPromotion:false,
 novelty:{label:'source-conditional derived identities; exposed definitions, not blind discovery',sourcePointers:['/generative_registry/1','/generative_registry/2','/generative_registry/4'],identities:[
 {identity:'J rho_k J = rho_-k',domain:'finite nonempty sequence, integer k',argument:'(J rho_k J x)_j=x_((j-k) mod n); reversal conjugates cyclic index rotation to its inverse.',finiteCheck:'all n=1..32, k=-n..n; 1088 cases',independentCheck:'Wolfram exact finite verification'},
 {identity:'J A_(s,a) = A_(s,a) J',domain:'finite sequence of Z12 pitch classes; A_(s,a)(v)=s*v+a mod12, s=+/-1',argument:'Both compositions have entry s*x_(n-1-j)+a mod12: pitch-value action and position reversal act on distinct coordinates.',finiteCheck:'six-entry pitch sequence, both signs and all 12 offsets',independentCheck:'Wolfram exact finite verification'},
 ],nonClaims:['No unique musical orientation or phase is selected.','No native triad map, learned next-event distribution, acoustic constitution or Guido overlap is fabricated.','Finite checks support implementation; displayed index arguments supply the conditional identities.']},registry,observations,
 verification:{build:'npm run build',testArgv:[process.execPath,'--test','tests/native-operators.test.mjs'],exitCode:tests.status,signal:tests.signal,fullOutput:'docs/evidence/native-execution/focused-tests.tap',wolframReceipt:'docs/evidence/native-execution-wolfram-result.json',jevReceipt:'docs/evidence/native-execution-math-jev-result.json'},inputs:tracked.map(path=>({path,sha256:hash(readFileSync(at(path)))}))};
mkdirSync(at('state/reconstruction'),{recursive:true});writeFileSync(at('state/reconstruction/native-execution.json'),JSON.stringify(state,null,2)+'\n','utf8');
const table=registry.map(x=>`| ${x.id} | ${x.name} | ${x.families.length} | ${x.executionScope} |`).join('\n');
const markdown=`# Source-native execution register\n\nAll 10 source mechanisms and all 19 member occurrences are explicitly registered. Each has a bounded conditional interpreter. Historical carriers, maps, acoustic witnesses and learned kernels still require their actual source data. Exact rational operations reuse SUNNY's integer-string rational arithmetic. No canonical promotion occurs.\n\n| Native ID | Source mechanism | Members | Executable scope |\n|---|---|---:|---|\n${table}\n\n## Source binding and decisions\n\nEvery execution retains original source occurrence ${sourceId}, byte SHA-256 ${NATIVE_GG_SHA256}, and its exact /generative_registry index. Full literal member objects remain in the machine register. The original graph remains the authority.\n\nActual SuperJev resolved jev-1.14.0 and chose: Euclidean mechanical constructor modulo the complete cyclic orbit; missing mutation map stays unknown; two inputs cannot witness a three-input joint rule; the entire supplied conditional distribution is retained; added duration uses the positive-addition subset. Full input/output: [Jev request](../evidence/native-execution-math-jev-request.json) and [Jev result](../evidence/native-execution-math-jev-result.json). These are model decisions, not truth probabilities or proofs.\n\n## Exact interactions\n\nFor a length-n sequence with left index rotation rho_k and reversal J, J rho_k J = rho_-k. At index j both sides equal x_((j-k) mod n). This gives a precise reversal/rotation discriminator without selecting a privileged phase. All 1,088 cases n=1..32, k=-n..n pass, independently reproduced by Wolfram.\n\nAn affine pitch-class action A_(s,a) and position reversal commute: (J A x)_j = s*x_(n-1-j)+a mod12 = (A J x)_j. This is conditional on the actions occupying the stated value and position coordinates; it does not identify a particular native triad action. Both signs and all 12 offsets pass on the declared six-entry test sequence.\n\nThe abstract D12 relations s^12=e,t^2=e,tst=s^-1 also pass. E(5,13) returns 13 distinct phases, five onsets each, and cyclic gaps 2 or 3; Wolfram independently returns the same mechanical word 0010010100101 and invariants. No source-specified origin was retrieved.\n\n## Verification and limits\n\nBuild and all 14 focused tests pass. Tests also cover negative residue inputs/De Morgan, reversal involution, seven index rotations, exact R*L=1/2, source-byte tampering, undeclared/ambiguous mutation, preserving joint arity, local duration versus global scaling, missing kernel and exact sum-one validation. Test labels beginning test: are explicit constructed witnesses, not historical source evidence.\n\nThe interpreter does not represent Zhu's irrational generator as a rational, turn an abstract D12 isomorphism into a PLR triad map, infer Guidonian admissibility, reduce a joint constitution to pairs, manufacture a stochastic kernel, or select its most probable event. Unknown is a first-class result. Finite sieve complement is relative to the supplied universe.\n\nNative instances without actual inputs remain unknown in the recorded scenarios: mutation, joint constitution and next-event kernel. Other scenarios demonstrate their declared algebraic subset, not completion of every historical member.\n\nReproduce with npm run build, then node scripts/reconstruct_native_execution.mjs. This runs one bounded foreground test process and closes it. [Machine register](../../state/reconstruction/native-execution.json), [focused test output](../evidence/native-execution/focused-tests.tap), and [Wolfram receipt](../evidence/native-execution-wolfram-result.json) retain the actual results.\n`;
writeFileSync(at('docs/reconstruction/NATIVE_EXECUTION.md'),markdown,'utf8');
if(process.argv[2]){
  const target=resolve(root,process.argv[2]);
  if(!target.startsWith(root))throw new Error('Audit result must remain within the project');
  writeFileSync(target,JSON.stringify(state,null,2)+'\n',{encoding:'utf8',flag:'wx'});
}
console.log(JSON.stringify({status:'completed',...state.counts,sourceSha256:NATIVE_GG_SHA256,testExitCode:tests.status,ownedBackgroundProcesses:0}));
