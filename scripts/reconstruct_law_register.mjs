/** Register only source-conditioned distinctions justified by executed proofs. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {checkLawDependencies} from '../dist/law.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const raw=p=>fs.readFileSync(path.join(root,p));
const load=p=>JSON.parse(raw(p).toString('utf8').replace(/^\uFEFF/,''));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const native=load('state/reconstruction/native-derivations.json');
const orientation=load('state/reconstruction/orientation-predictions.json');
const tol=load('state/reconstruction/tol-history-math.json');
const gen=load('state/reconstruction/generational-constraints.json');
const algebraic=load('state/reconstruction/algebraic-extension.json');
const nativeRefs=native.source_bindings.sources.map(s=>s.id);
const genRefs=[...new Set(gen.sources.map(s=>s.source_id))];
const atlasRefs=[orientation.provenance.atlas_source_id];
const proof=p=>({path:p,sha256:sha(raw(p))});
const N=proof('state/reconstruction/native-derivations.json');
const O=proof('state/reconstruction/orientation-predictions.json');
const T=proof('state/reconstruction/tol-history-math.json');
const G=proof('state/reconstruction/generational-constraints.json');
const A=proof('state/reconstruction/algebraic-extension.json');
const laws=[];
function add(id,expression,assumptions,sourceRefs,dependencies,proofRefs){
  laws.push({id,revision:'1',expression,assumptions,sourceRefs,
    dependencies:dependencies.map(id=>({id,revision:'1'})),status:'conditional',proofRefs,
    authority:'Derived within stated source profile; not a universal or historical certification.'});
}
add('NATIVE-SCALAR-BASIS',{R:'2/3',L:'3/4',O:'1/2',carrier:'positive scalars in the recovered native profile'},
  ['Use the source-defined operations and source-qualified carrier.'],nativeRefs,[],[N,T]);
add('DISTINGUISH-ADDRESS-EXACT-PITCH',
  {required_distinction:['finite address','exact pitch modulo integer octaves'],'counterexample':'Address(R^12)=origin while2^7 R^12=524288/531441.'},
  ['Exact rational native scalar laws.','Finite source address action has R-order12.','Octave equivalence is multiplication by integer powers of2.'],
  atlasRefs,['NATIVE-SCALAR-BASIS'],[O]);
add('DISTINGUISH-VALUE-HISTORY',
  {required_distinction:['scalar or pitch value','ordered operation history'],
   witnesses:['RL and LR evaluate equally.','924six-R/six-L words share1/64.','Ten inverse Chinese words share the entire normalized pitch path.']},
  ['Histories mean the declared ordered words.','No extra historical equivalence identifies these words.'],
  [...new Set([...nativeRefs,...tol.source_spans.map(s=>s.source_id).filter(Boolean)])],
  ['NATIVE-SCALAR-BASIS'],[N,T]);
add('BRIDGE-DIRECTION-RESIDUAL',
  {reverse5:'256/243',forward7:'2187/2048',cycle_residual:'531441/524288',forward_bridge_for_Earth:'32768/32805'},
  ['Retained Earth target16/15 and syntonic bridge81/80.','The source-defined inverse/forward generator realizations and octave normalization.'],
  nativeRefs,['NATIVE-SCALAR-BASIS','DISTINGUISH-ADDRESS-EXACT-PITCH'],[N]);
add('CONDITIONAL-FAMILY-CONSENSUS',
  {word:'R^r L^l',common_iff:['r=l modulo6','l=0 modulo3'],shared_addresses:[[0,0],[6,0],[0,3],[6,3]]},
  ['Only the twelve source-recovered optional transitive completions.','Fixed source phase coordinates and origin.'],
  atlasRefs,[],[O]);
add('CONDITIONAL-FAMILY-PHASE-PROBES',
  {minimum_one_word_observations:2,sufficient_ordered_observations:['phase(R)','phase(O)']},
  ['Each observation is a one-word address in the declared fixed-coordinate family.','Independent source-to-phase observations remain to be recovered.'],
  atlasRefs,['CONDITIONAL-FAMILY-CONSENSUS'],[O]);
add('WITNESS-TIME-GENERATION-LATTICE',
  {lattice_basis:[[50,0],[130,1]],quotient:'Z/50',invariant:'I(t,g)=t-130g mod50',pure_time_projection:'t mod10'},
  ['The fourteen recorded shared-figure MT/SP/Greek witness shifts.','Aligned common time and generation origins.','Across-witness transformation, not conservation along genealogy.'],
  genRefs,[],[G]);
add('JOINT-OBSERVABLE-GENERATION-PERIOD',
  {conditional_minimum_generation_period:60,inputs:['fixed time modulo50','declared fifth address modulo12','joint witness character']},
  ['Generation is still retained as an integer, not replaced by this finite projection.','Only the stated fixed-time observables and source-qualified fifth assignment.','No identity with historical60pipes or other60-object populations is asserted.'],
  genRefs,['WITNESS-TIME-GENERATION-LATTICE'],[G]);
add('DISTINGUISH-GENEALOGY-INSTITUTIONAL-ADDRESS',
  {incompatible_projection:'GEN-only -> all declared camp addresses',witness:'Same biological generation, distinct Ephraim/Manasseh camp addresses.'},
  ['Use the exact expanded genealogy and camp frame retained by the sources.','The witness rejects this single-variable map; it does not elect another map.'],
  genRefs,[],[G]);
add('OVERLAP-TIMING-NULLSPACE',
  {lifespan_constraints:3,stage_durations:5,independent_timing_conditions_still_needed:2},
  ['Declared five-stage, three-voice entrance/exit experiment.','Lifetime is not audible sustain by definition; no year-to-beat conversion.'],
  genRefs,[],[G]);
add('DISTINGUISH-CLASS-ACOUSTIC-GRADE',
  {conditional_grade_relation:'acoustic grade increment=2h+epsilon',class_cycle_degrees:720,remaining_circuit_parity:'epsilon'},
  ['One native RL circuit uses the same360degree wheel and halves the scalar center.','Two circuits define the720degree class cycle.','The counters are representation-specific; parity is not silently identified with W72beta.'],
  genRefs,['NATIVE-SCALAR-BASIS'],[G]);
add('ROOT-EXTENSION-QUOTIENTS',
  {G:'<R,L>={2^a3^b:a,b in Z}',q:'2^(1/12)',H:'<G,q>',
   quotient_by_native_group:'H/G is C12',quotient_by_integer_octaves:'H/<2> is C12 x Z'},
  ['Positive finite prime monomials with rational exponents.','Recovered exact R,L and Zhu q definitions.',
   'Integer octave equivalence removes only integer prime2powers; fractional exponents survive.',
   'This is not a numerical-frequency normalization or a representation of every algebraic real.'],
  [algebraic.source.sourceId||algebraic.source.source_id||algebraic.source.id],
  ['NATIVE-SCALAR-BASIS','DISTINGUISH-ADDRESS-EXACT-PITCH'],[A]);
add('ROOT-FIFTH-COMMA',
  {delta:'q^7/(3/2)',delta_twelfth:'524288/531441',
   consequence:'A shared finite dial label cannot equate q^7 with the pure fifth3/2.'},
  ['The same exact positive-scalar definitions and integer-octave quotient.',
   'Any shared dial convention is conditional and must be independently declared; no global orientation is inferred.'],
  [algebraic.source.sourceId||algebraic.source.source_id||algebraic.source.id],
  ['ROOT-EXTENSION-QUOTIENTS'],[A,N]);
for(const law of laws)assert.ok(law.sourceRefs.length&&law.sourceRefs.every(x=>typeof x==='string'&&x.length>0));
const graph=checkLawDependencies(laws);
assert.equal(graph.verdict,'pass');assert.equal(graph.cycles.length,0);
for(const law of laws)for(const p of law.proofRefs)assert.equal(sha(raw(p.path)),p.sha256);
const output={schema:'sunny.progressive-law-register.v1',compiled_utc:new Date().toISOString(),
  selection:'docs/evidence/mandate-mathematics-superjev.json; docs/evidence/native-execution-expansion-superjev.json',
  law_proposals:laws,dependency_graph_check:graph,
  basis:'The representation distinguishes quantities only where recovered definitions and executed counterexamples require it. This is not a predefined universal ontology.',
  source_and_proof_boundary:'References and declared revision graph are mechanically bound; the linked proofs establish only their stated conditions.',
  supersession:'Keep prior versions and dependencies when refining, merging, separating or retracting a proposal.',
  unknowns:['Complete global law taxonomy','Every native carrier/instance','Independent absolute orientation selection','Full class-growth and four-dimensional realization','Complete master-score timing/instrumentation','Independent blind predictions'],
  canonicalPromotion:false,globalCompleteness:false};
const destination=path.join(root,'state/reconstruction/derived-laws.json');
if(fs.existsSync(destination)){
  const previous=fs.readFileSync(destination);
  const backup=path.join(root,'state/checkpoint-history','before-laws-'+sha(previous)+'.snapshot');
  if(!fs.existsSync(backup))fs.writeFileSync(backup,previous,{flag:'wx'});
}
fs.writeFileSync(destination,JSON.stringify(output,null,2)+'\n');
const lines=['# Progressively derived conditional law register','',
  'These distinctions follow the recovered source operations and executed proofs. They remain conditional proposals; dependency-graph validity does not prove universal musical or historical truth.','',
  ...laws.flatMap(l=>['## '+l.id,'',JSON.stringify(l.expression),'',...l.assumptions.map(a=>'- '+a),'',
    'Proofs: '+l.proofRefs.map(p=>'['+path.basename(p.path)+'](../../'+p.path+')').join(', ')+'.','']),
  '## Remaining work','',...output.unknowns.map(s=>'- '+s),''];
fs.writeFileSync(path.join(root,'docs/reconstruction/DERIVED_LAWS.md'),lines.join('\n'));
console.log(JSON.stringify({status:'passed',exit_code:0,conditional_laws:laws.length,dependency_cycles:0,canonicalPromotion:false}));
