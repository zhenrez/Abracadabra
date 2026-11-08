/* Conditional observation designs; all historical source-to-phase bridges remain explicit. */
window.SUNNY_PHASE_PROBES=function({D,h,s,panel,table,select,label,note,button,inspect}){
 const data=D.modules['orientation-predictions']?.probe_designs;if(!data)return note('Phase observation designs have not been built.');
 const target=h('div',{'data-phase-probe-results':''});let a='R1L0',b='R1L1';
 const word=id=>data.words.find(x=>x.id===id);
 function draw(){const groups=new Map();for(const c of data.candidates){const key=c.phases[a]+','+c.phases[b];if(!groups.has(key))groups.set(key,[]);groups.get(key).push(c);}
  target.dataset.distinctOutputs=String(groups.size);target.dataset.first=a;target.dataset.second=b;
  const chart=s('svg',{viewBox:'0 0 960 240',class:'chart',role:'img','aria-label':'Two hypothetical phase observations for all twelve retained candidates'});
  chart.append(s('text',{x:12,y:28,fill:'currentColor','font-size':16},'Candidate'),s('text',{x:12,y:100,fill:'currentColor','font-size':16},word(a).expression),s('text',{x:12,y:166,fill:'currentColor','font-size':16},word(b).expression));
  data.candidates.forEach((c,i)=>{const x=174+i*64;
   chart.append(s('text',{x,y:28,fill:'currentColor','font-size':13,'text-anchor':'middle'},'b'+c.b+' / s'+c.s));
   [a,b].forEach((id,j)=>{const y=94+j*66;chart.append(s('circle',{cx:x,cy:y,r:22,fill:j?'#e8d6aa':'#dce8df',stroke:'#365644'}),s('text',{x,y:y+5,fill:'#173e2e','font-size':17,'text-anchor':'middle'},String(c.phases[id])));});
  });
  const sufficient=groups.size===12;
  target.replaceChildren(h('p',{},sufficient?'These two observation functions separate all 12 candidates in this family.':groups.size+' distinct joint outputs leave collisions between candidates.'),
   h('p',{class:'mini muted'},'This shows predicted labels for competing models. It is not a set of historical observations.'),chart,
   table(['Joint phase outputs','Candidates still indistinguishable'],[...groups].map(([k,v])=>[k,v.map(c=>'b='+c.b+', s='+c.s).join(' / ')])));
 }
 const choices=data.words.map(w=>[w.id,w.expression+' · angular '+w.angular]);
 const first=select(choices,a,x=>{a=x;draw();});first.dataset.phaseProbe='first';
 const second=select(choices,b,x=>{b=x;draw();});second.dataset.phaseProbe='second';draw();
 return panel('Which observations would actually distinguish an orientation?',
  note('The older atlas already related these twelve optional phase completions by coordinate changes. Fixed source labels make a different comparison. A/B/C primordial arrangements are separate hypotheses; no correspondence is imposed here.'),
  h('p',{},'One phase observation has at most six outputs and cannot distinguish twelve candidates. Of 10,296 pairs of distinct word occurrences,4,608 separate all twelve;5,688 leave explicit collisions.'),
  h('div',{class:'controls'},label('First proposed observation',first),label('Second proposed observation',second)),target,
  h('h3',{},'Exact two-observation condition'),
  h('p',{},'For words R^r₁L^l₁ and R^r₂L^l₂: gcd(r₁−l₁,r₂−l₂,6)=1, and r₁l₂−r₂l₁ is nonzero modulo 3.'),
  h('p',{},'The missing evidence is a source-supported link into these word addresses and phase labels in the same frame. A symbol, sound, color or genealogy cannot supply that link merely because its count matches. The separate phase-preserving profile remains lawful and retained.'),
  button('Inspect every design, counterexample, proof and source condition',()=>inspect('Conditional phase observation designs',data),'link-button'));
};
