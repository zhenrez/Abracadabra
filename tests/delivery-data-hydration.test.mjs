import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
test('compressed offline dataset hydrates every canonical value and shares only identical graph records',async()=>{
 const original=JSON.parse(fs.readFileSync(new URL('../web/delivery-2026-11-07/data.json',import.meta.url),'utf8'));
 globalThis.window={};vm.runInThisContext(fs.readFileSync(new URL('../web/delivery-2026-11-07/data.js',import.meta.url),'utf8'),{filename:'SUNNY-offline-data.js'});
 await window.SUNNY_DATA_READY;
 assert.deepEqual(window.SUNNY_DELIVERY,original,'No value may be lost or changed by compression/reference hydration');
 const graph=window.SUNNY_DELIVERY.graph,m=window.SUNNY_DELIVERY.modules;
 assert.equal(m['native-class-constructors'].entities[0],graph.entities.find(e=>e.id===m['native-class-constructors'].entities[0].id));
 assert.equal(window.SUNNY_INDIAN_HIERARCHY,m['indian-hierarchy']);assert.equal(window.SUNNY_CHINESE_EXPANDED,m['chinese-expanded']);
 assert.equal(window.SUNNY_WESTERN_EXPANDED,m['western-expanded']);assert.equal(window.SUNNY_BIBLICAL_GENEALOGIES,m['biblical-genealogies']);
 delete globalThis.window;
});
