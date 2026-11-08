/* The selected source conditions are inspectable; this is not an original-sound claim. */
window.SUNNY_SYMBOL_CONTEXT=function({D,h,s,panel,table,select,label,note,button,inspect}){
 const data=D.modules['phonological-context-constraints'];if(!data)return note('Source-context extension not built.');
 const body=h('div');let selected=0;
 function draw(){const branch=data.conditionalExecutions[selected];body.replaceChildren(
  table(['Passage','Published Greek form','Theme-letter grade','Condition'],data.sourceCases.map((row,i)=>[row.locus,i===2&&selected===1?'θεσαδηνι':i===2&&selected===2?'Theme vowel unread':row.publishedGreekForm,branch.transcriptionGrades[i]??'Unresolved',row.pronominalSuffix?'With pronominal suffix':'Without pronominal suffix'])),
  h('p',{class:'mini muted'},branch.checkedContexts+' reported contexts checked; '+branch.simpleSuffixConditionConflicts.length+' conflict with this explicit conditional transcription rule. Phonological and morphological explanations remain separate alternatives.'),
  button('Inspect source, variants and exact calculation',()=>inspect('Phonological context constraints',data),'link-button'));
 }
 draw();
 const diagram=s('svg',{class:'chart',viewBox:'0 0 800 250',role:'img','aria-label':'Local rounding precedes two distinct changes; no order between those changes follows'});
 for(const y of [65,185])diagram.append(s('line',{x1:260,y1:125,x2:485,y2:y,stroke:'#a57b3d','stroke-width':2}));
 for(const [x,y,lines]of [[140,125,['L · Local rounding','before waw']],[630,65,['V · w → v','consonantal change']],[630,185,['G · Broader shift','syllabic distribution']]]){diagram.append(s('rect',{x:x-115,y:y-31,width:230,height:62,rx:4,fill:'#e7eddf',stroke:'#b6c5b2'}));lines.forEach((t,i)=>diagram.append(s('text',{x,y:y-4+i*19,'text-anchor':'middle',fill:'#26392f','font-size':13},t)));}
 return panel('Source conditions change the admissible reading',note('Howard’s published argument is conditional. These are edition reports, not independently recovered manuscript ink or measured ancient phones.'),
  label('Disputed Ps18:36 theme vowel — preserve each reading',select(data.conditionalExecutions.map((c,i)=>[String(i),c.reading.editionReport]),'0',v=>{selected=Number(v);draw();})),body,
  h('h3',{},'A date bound needs a justified bridge'),diagram,
  h('p',{},'L before V, and L before G, allows both L → V → G and L → G → V. Dating V therefore cannot alone date G. The two processes must retain separate identities.'),
  h('a',{href:data.source.url,target:'_blank',rel:'noopener noreferrer'},'Original publication and source conditions'));
};
