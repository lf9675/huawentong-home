import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {SHEET_HEADERS,sendSheet} from '../supabase/functions/hwt-classroom/management.ts';
let passed=0;async function test(name,fn){await fn();passed++;console.log('PASS '+name);}
const secret='fixture-only-sync-code-'.repeat(3),values=[];
const sheet={getLastRow:()=>values.length,getMaxRows:()=>3000,setFrozenRows(){},getRange(r,c,h,w){return {getValues(){return Array.from({length:h},(_,i)=>Array.from({length:w},(_,j)=>values[r-1+i]?.[c-1+j]??''));},setNumberFormat(){return this;},setValues(rows){rows.forEach((row,i)=>values[r-1+i]=[...row]);return this;},setBackground(){return this;},setFontColor(){return this;},setFontWeight(){return this;}};}};
const ctx={console,PropertiesService:{getScriptProperties:()=>({getProperty:k=>k==='HWT_SYNC_SECRET'?secret:'fixture-sheet'})},ContentService:{MimeType:{JSON:'json'},createTextOutput:s=>({setMimeType:()=>JSON.parse(s)})},LockService:{getScriptLock:()=>({waitLock(){},releaseLock(){}})},SpreadsheetApp:{openById:()=>({getSheetByName:()=>sheet}),flush(){}}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(new URL('../bei/management/google-sheets.gs',import.meta.url),'utf8'),ctx);
const post=body=>ctx.doPost({postData:{contents:JSON.stringify(body)}});
const row=['lesson','test','date','TEST','01','=HYPERLINK("bad")','00000000-0000-4000-8000-000000000001','date',1,0,1,'',2,1,'',3,'待教师覆核'];
await test('Sheets receiver rejects missing secret without touching sheet',()=>{assert.equal(post({action:'sync'}).ok,false);assert.equal(values.length,0);});
await test('connection check returns no student records',()=>{const r=post({action:'ping',secret});assert.equal(r.ok,true);assert.equal(r.kind,'hwt-grades-v1');assert.equal(values.length,0);});
await test('first save is verified and formula-like names are literal',()=>{const r=post({action:'sync',secret,requestId:'test-1',headers:SHEET_HEADERS,rows:[row]});assert.equal(r.ok,true);assert.equal(r.saved,1);assert.equal(values.length,2);assert.ok(values[1][5].startsWith("'="));assert.equal(values[1][4],'01');});
await test('repeating a sync updates marks without duplicating a submission',()=>{const newer=[...row];newer[11]=1;newer[13]=0;newer[14]=1;newer[16]='已提交';assert.equal(post({action:'sync',secret,requestId:'test-2',headers:SHEET_HEADERS,rows:[newer]}).ok,true);assert.equal(values.length,2);assert.equal(values[1][11],1);});
await test('receiver refuses unexpected header or duplicate ids',()=>{assert.equal(post({action:'sync',secret,requestId:'x',headers:['bad'],rows:[row]}).ok,false);assert.equal(post({action:'sync',secret,requestId:'x',headers:SHEET_HEADERS,rows:[row,row]}).ok,false);});
await test('Google redirect does not forward secret to response URL',async()=>{let n=0;globalThis.fetch=async(url,opts)=>{n++;if(n===1){assert.equal(JSON.parse(opts.body).secret,secret);return new Response(null,{status:302,headers:{location:'https://script.googleusercontent.com/macros/echo?fixture=1'}});}assert.equal(opts.body,undefined);return Response.json({ok:true,kind:'hwt-grades-v1'});};assert.equal((await sendSheet({url:'https://script.google.com/macros/s/fixture/exec',secret},{action:'ping'})).ok,true);assert.equal(n,2);});
await test('non-Google redirects are rejected',async()=>{let n=0;globalThis.fetch=async()=>{n++;return new Response(null,{status:302,headers:{location:'https://example.com'}});};await assert.rejects(sendSheet({url:'https://script.google.com/macros/s/fixture/exec',secret},{action:'ping'}));assert.equal(n,1);});
console.log(JSON.stringify({passed,mode:'simulated Apps Script; no Google account writes'}));
