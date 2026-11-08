/* Render the exact executed source conditions and controls, without inventing historical bounds. */
window.SUNNY_PHONOLOGICAL_HISTORY=function({D,h,s,panel,table,select,label,note,button,inspect}){
 const data=D.modules['phonological-history-constraints'];if(!data)return note('History discriminator not yet built.');
 const body=h('div',{'data-history-result':''});
 const number=x=>x===null?'Unbounded':x.denominator==='1'?x.numerator:x.numerator+'/'+x.denominator;
 const interval=x=>(x.lowerClosed?'[':'(')+number(x.lower)+', '+number(x.upper)+(x.upperClosed?']':')');
 function draw(id){const c=data.conditionalControls.find(x=>x.id===id);body.dataset.feasible=String(c.result.feasible);
  body.replaceChildren(table(['Event','Permitted interval'],c.inputs.map((v,i)=>[['Donor onset','Contact','Recipient acquisition'][i],interval(v)])),
   h('p',{class:'history-verdict'},c.result.feasible?'A contact timing remains possible under these assumptions.':'This proposed contact timing conflicts with these bounds.'),
   h('p',{class:'mini muted'},c.scope),
   c.result.witness?table(['Exact timing witness','Value'],Object.entries(c.result.witness).map(([k,v])=>[k,number(v)])):h('p',{class:'mini muted'},'Removing either member of the contradictory additional-bound pair restores a possible timing.'),
   button('Inspect inputs, assumptions and result',()=>inspect('Conditional contact timing',c),'link-button'));
 }
 const choice=select(data.conditionalControls.map(c=>[c.id,c.id.replaceAll('_',' ')]),data.conditionalControls[0].id,draw);
 choice.dataset.historyCase='';draw(data.conditionalControls[0].id);
 const diagram=s('svg',{class:'chart',viewBox:'0 0 940 340',role:'img','aria-label':'Contact and independent change have identical sound-state trajectories, with a transmission edge only in the contact model'});
 for(const [base,title,edge] of [[45,'Contact candidate',true],[205,'Independent-change candidate',false]]){
  diagram.append(s('text',{x:15,y:base,fill:'#26392f','font-size':14},title));
  for(const [dy,name,onset]of [[35,'Donor',2],[80,'Recipient',4]]){
   const y=base+dy;diagram.append(s('text',{x:20,y:y+4,fill:'#26392f','font-size':13},name),
    s('line',{x1:210,x2:900,y1:y,y2:y,stroke:'#bdcbb9','stroke-width':2}),
    s('line',{x1:210+onset*130,x2:900,y1:y,y2:y,stroke:'#41694f','stroke-width':9}),
    s('circle',{cx:210+onset*130,cy:y,r:5,fill:'#a57b3d'}));
  }
  if(edge){const x=210+3*130;diagram.append(s('line',{x1:x,y1:base+35,x2:x,y2:base+75,stroke:'#a57b3d','stroke-width':2}),
    s('path',{d:`M${x-5},${base+69} L${x},${base+77} L${x+5},${base+69}`,fill:'none',stroke:'#a57b3d','stroke-width':2}),
    s('text',{x:x+12,y:base+62,fill:'#805f30','font-size':12},'Proposed transmission'));}
 }
 for(let i=0;i<=5;i++)diagram.append(s('text',{x:210+i*130,y:325,'text-anchor':'middle',fill:'#65725f','font-size':12},String(i)));
 return panel('Which evidence can distinguish a sound history?',
  note('No historical date bounds are admitted here. The numerical examples use arbitrary order coordinates. Source acquisition and phonetic licensing remain explicit dependencies.'),
  h('h3',{},'Earlier writing does not establish earlier innovation'),
  label('Executed timing control',choice),body,
  h('h3',{},'Identical sounds can leave different causal histories'),diagram,
  h('p',{},'These two declared histories share their complete sound-state paths. A transmission edge appears in one candidate. More samples of those same states cannot identify the edge; an independent relationship or a justified additional constraint is needed.'),
  table(['Needed source observation','What it could discriminate'],data.queryRegister.map(q=>[q.need,q.consequence])),
  button('Inspect source bindings, independent checks and remaining alternatives',()=>inspect('Phonological history discriminator',data),'link-button'));
};
