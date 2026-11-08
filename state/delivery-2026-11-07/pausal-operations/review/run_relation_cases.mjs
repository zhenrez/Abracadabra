import fs from 'node:fs';import crypto from 'node:crypto';
import {readingDependency,minimalReadingRefinements,queryReadings,readingJoinResidual} from '../../../../dist/reading-relations.js';
const dir=new URL('.',import.meta.url),src=new URL('../../../../src/reading-relations.ts',import.meta.url),dist=new URL('../../../../dist/reading-relations.js',import.meta.url);
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');const start={source:sha(src),dist:sha(dist)};
const cases=JSON.parse(fs.readFileSync(new URL('relation-cases.json',dir),'utf8'));
const output=cases.map(c=>{try{return {id:c.id,fd:readingDependency(c.rows,c.base,c.output),refinements:minimalReadingRefinements(c.rows,c.base,c.candidates,c.output),query:queryReadings(c.rows,c.conditions,c.output),join:readingJoinResidual(c.rows,c.left,c.right)}}catch(e){return {id:c.id,error:String(e)}}});
const malformed=[];for(const conditions of [[],['a'],'a',null]){try{malformed.push({conditions,result:queryReadings(cases[0].rows,conditions,cases[0].output)})}catch(e){malformed.push({conditions,error:String(e)})}}
const finish={source:sha(src),dist:sha(dist)};
fs.writeFileSync(new URL('relation-actual.json',dir),JSON.stringify({start,finish,output,malformed},null,2)+'\n');console.log(JSON.stringify({cases:output.length,sourceStable:JSON.stringify(start)===JSON.stringify(finish)}));
