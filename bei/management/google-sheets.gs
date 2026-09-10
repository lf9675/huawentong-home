// Install in a NEW spreadsheet-bound Apps Script project; never overwrite an old grades script.
// Only a secret-authenticated POST can write. GET never returns student records.
const HWT_HEADERS=['学习单ID','学习单','版本日期','班级','学号','姓名','提交ID','提交时间','作答次数','独立客观题得分','独立客观题总分','独立开放题教师分','独立开放题总分','待覆核题数','独立总分','独立满分','状态'];
function setupHWT(){
 const p=PropertiesService.getScriptProperties(),book=SpreadsheetApp.getActiveSpreadsheet();
 if(!book)throw new Error('请从要接收成绩的Google表格打开Apps Script。');
 p.setProperty('HWT_SPREADSHEET_ID',book.getId());
 if(!p.getProperty('HWT_SYNC_SECRET'))p.setProperty('HWT_SYNC_SECRET',Utilities.getUuid().replace(/-/g,'')+Utilities.getUuid().replace(/-/g,''));
 console.log('同步码（只粘贴到华文通教师后台，不发给学生）：'+p.getProperty('HWT_SYNC_SECRET'));
}
function hwtJSON(data){return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);}
function doGet(){return hwtJSON({ok:false,error:'POST required'});}
function hwtSafe(value){const s=String(value==null?'':value);return /^[\s]*[=+\-@]/.test(s)?"'"+s:s;}
function doPost(e){
 let lock;
 try{
  const raw=e&&e.postData&&e.postData.contents;if(!raw||raw.length>2000000)throw new Error('bad request');
  const b=JSON.parse(raw),p=PropertiesService.getScriptProperties(),expected=p.getProperty('HWT_SYNC_SECRET');
  if(!expected||typeof b.secret!=='string'||b.secret.length!==expected.length)throw new Error('unauthorized');
  let delta=0;for(let i=0;i<expected.length;i++)delta|=expected.charCodeAt(i)^b.secret.charCodeAt(i);if(delta)throw new Error('unauthorized');
  if(b.action==='ping')return hwtJSON({ok:true,kind:'hwt-grades-v1'});
  if(b.action!=='sync'||typeof b.requestId!=='string'||!Array.isArray(b.rows)||!b.rows.length||b.rows.length>2000||JSON.stringify(b.headers)!==JSON.stringify(HWT_HEADERS))throw new Error('invalid payload');
  const ids=new Set();for(const row of b.rows){if(!Array.isArray(row)||row.length!==HWT_HEADERS.length||!(/^[a-f0-9-]{36}$/i.test(row[6]))||ids.has(row[6]))throw new Error('invalid rows');ids.add(row[6]);}
  lock=LockService.getScriptLock();lock.waitLock(20000);
  const book=SpreadsheetApp.openById(p.getProperty('HWT_SPREADSHEET_ID'));
  let sheet=book.getSheetByName('华文通学习单成绩');if(!sheet)sheet=book.insertSheet('华文通学习单成绩');
  const width=HWT_HEADERS.length;
  if(sheet.getLastRow()&&JSON.stringify(sheet.getRange(1,1,1,width).getValues()[0])!==JSON.stringify(HWT_HEADERS))throw new Error('header mismatch');
  const rows=sheet.getLastRow()>1?sheet.getRange(2,1,sheet.getLastRow()-1,width).getValues():[],index=new Map(rows.map((r,i)=>[String(r[6]),i]));
  if(index.size!==rows.length)throw new Error('duplicate existing ids');
  for(const row of b.rows){const safe=row.map((v,i)=>typeof v==='number'?v:hwtSafe(v));if(index.has(row[6]))rows[index.get(row[6])]=safe;else{index.set(row[6],rows.length);rows.push(safe);}}
  if(rows.length>20000)throw new Error('sheet size limit');
  const data=[HWT_HEADERS,...rows];if(sheet.getMaxRows()<data.length)sheet.insertRowsAfter(sheet.getMaxRows(),data.length-sheet.getMaxRows());
  sheet.getRange(1,1,data.length,width).setNumberFormat('@').setValues(data);
  sheet.setFrozenRows(1);sheet.getRange(1,1,1,width).setBackground('#173b66').setFontColor('#ffffff').setFontWeight('bold');
  SpreadsheetApp.flush();
  // Verify only the rows in this request before acknowledging a successful save.
  const stored=sheet.getRange(2,1,rows.length,width).getValues(),byId=new Map(stored.map(r=>[String(r[6]),r]));
  for(const row of b.rows){const saved=byId.get(row[6]);if(!saved||saved.some((v,i)=>String(v)!==String(row[i])&&String(v)!==hwtSafe(row[i])))throw new Error('readback mismatch');}
  return hwtJSON({ok:true,requestId:b.requestId,saved:b.rows.length});
 }catch(error){return hwtJSON({ok:false,error:'保存未完成，请核对同步设置或重试。'});}
 finally{if(lock)lock.releaseLock();}
}
