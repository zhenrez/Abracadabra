/* Source-bound observability explorer. Numeric examples retain witness-year units. */
window.SUNNY_SCORE_ANCHORS=function({D,h,panel,table,select,label,badge,note,button,inspect}){
 const data=D.scoreAnchors;if(!data)return note('Score-anchor derivation is not built.');
 let selected='1,2',witness='MT';const result=h('div'),checks=h('div',{class:'anchor-checks'});
 const native=D.modules['generational-constraints'].constraints.find(c=>c.id==='GT-TIME-OVERLAP').witness_executions;
 function draw(){
  const pair=data.anchorPairs.find(p=>p.stageIndices.join(',')===selected),w=native.find(x=>x.witness===witness);
  result.replaceChildren(badge(pair.sufficient?'Two independent anchors — all five stages determined':'Redundant pair — one timing freedom remains',pair.sufficient?'source':'unknown'),
   h('p',{},pair.labels.join(' + ')),
   note('Already-exposed source-conditioned examples. These are not blind predictions or a conversion from reported years into audible sustain.'),
   table(['Stage','Source duration','What follows from this pair'],Array.from({length:5},(_,i)=>{
    const fixed=pair.sufficient||pair.stageIndices.some(j=>(j===1||j===4)&&(i===0||i===3))||pair.stageIndices.some(j=>(j===2||j===5)&&(i===1||i===4));
    return ['d'+(i+1)+' · '+['solo A','A+B','A+B+C','B+C','solo C'][i],w.durations[i]+' reported years',fixed?w.durations[i]+' determined':'Remaining alternatives'];
   })),h('p',{class:'mini muted'},'Lifespans A/B/C: '+w.lifespans.join(' / ')+'. Positive-order constraints remain required.'),
   button('Inspect exact derivation and source binding',()=>inspect('Score-anchor observability',data),'link-button'));
  checks.replaceChildren(...data.anchorPairs.map(p=>{const b=button(p.stageIndices.map(i=>'d'+i).join(' + '),()=>{selected=p.stageIndices.join(',');picker.value=selected;draw();},p.sufficient?'anchor-pair':'anchor-pair redundant');b.title=p.sufficient?'Independent on both timing freedoms':'Dependent: the second observation repeats a constrained difference';b.setAttribute('aria-pressed',String(p.stageIndices.join(',')===selected));return b;}));
 }
 const picker=select(data.anchorPairs.map(p=>[p.stageIndices.join(','),p.stageIndices.map(i=>'Stage '+i).join(' + ')]),selected,v=>{selected=v;draw();});
 const frame=select(native.map(w=>[w.witness,w.witness]),witness,v=>{witness=v;draw();});draw();
 return panel('Which observations resolve the score?',h('div',{class:'controls'},label('Two measured stage durations',picker),label('Retained witness example',frame)),
  h('p',{},'Eight pairs resolve both timing freedoms. Measuring stages 1 and 4, or stages 2 and 5, repeats the same information and leaves alternatives.'),checks,result);
};
