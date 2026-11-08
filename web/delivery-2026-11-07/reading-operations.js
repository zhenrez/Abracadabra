/* Source-qualified partial reading relations and the same units used in atlas/score views. */
window.SUNNY_READING_OPERATIONS=function({D,h,panel,table,select,label,note,button,inspect}){
 const data=D.modules['reading-operations'];if(!data)return note('Reading operations not built.');
 const result=h('div',{'data-reading-result':''});
 function draw(value){const q=data.queries[Number(value)];result.dataset.outputs=q.result.outputs.join('|');
  result.replaceChildren(h('p',{},'Admitted output alternatives: '+q.result.outputs.join(' / ')),
   h('p',{class:'mini muted'},q.result.scope),button('Inspect exact query and dependencies',()=>inspect('Conditional reading query',q),'link-button'));
 }
 const chooser=select(data.queries.map((q,i)=>[String(i),i===0?'Surface[a] + pausal':JSON.stringify(q.input)]),'0',draw);
 chooser.dataset.readingQuery='';draw('0');
 const trees=data.operationRows.map(row=>{const forms=data.forms.filter(f=>f.parent===row.id);
  return h('details',{class:'reading-tree'},h('summary',{},row.values.lexeme+' · '+forms.length+' comparative readings'),
   ...forms.map(form=>h('details',{},h('summary',{},form.role+' · '+form.ipa),h('p',{class:'mini muted'},form.evidenceRole),
    ...form.syllables.map(s=>button(String(s.ordinalOneBased)+' · '+s.onset+s.nucleus+s.lengthMark+(s.primaryStress?' · primary stress':''),
      ()=>inspect(form.id+':syllable'+s.ordinalOneBased,D.graph.entities.find(e=>e.id===form.id+':syllable'+s.ordinalOneBased)),'link-button')))));});
 return panel('Reading operations retain the missing distinctions',
  note('Two displayed bowl examples, four comparative pronunciation records, twelve analysed syllable occurrences. The source’s stated four-form extent remains unreconciled; comparative readings are different accounting units.'),
  table(['Source case','Contextual comparandum','Pausal reconstruction'],data.operationRows.map(r=>[r.values.lexeme,
   data.forms.find(f=>f.parent===r.id&&f.role==='contextual').ipa,data.forms.find(f=>f.parent===r.id&&f.role==='pausal').ipa])),
  label('Conditional query on the admitted source sample',chooser),result,
  h('h3',{},'What a discarded address changes'),
  h('p',{},'Rejoining through the shared surface nucleus produces four pairings from two original cases. Two combinations are excess relative to this sample.'),
  table(['Lexical address','Excess output'],data.transformationRegister.projectionRejoinResidual.excessCombinations.map(x=>[x.values.lexeme,x.values.outputNucleus])),
  h('p',{class:'mini muted'},'Lexeme, consonantal environment and source address each separate these two rows. This sample does not select the historical rule; a target-derived label supplies no independent prediction.'),
  h('h3',{},'The source units in the shared atlas and score'),...trees,
  h('h3',{},'Separate Tiberian prosodic conditions'),
  h('p',{},'The same D1 zaqef is contextual in Gen43:25 and pausal in Judg2:17 under the published analysis. Intonational and phonological domains remain distinct; these Tiberian conditions are not automatically transferred to the Babylonian comparison.'),
  button('Inspect source conditions, typed relations and prior art',()=>inspect('Source-native reading operations',data),'link-button'));
};
