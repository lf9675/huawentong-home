// Dedicated receiver for 善待生命. Create a NEW Apps Script project for this file.
// It can only write this workbook; it never returns student data to a browser.
const READING_BOOK='1NzoDK1KUuw-KW65S2Zs0R2RDYRXkIDDBFisfMhVxXO8';
const READING_ORIGIN='https://huawentong-home.lyqlym2015.workers.dev';
const READING_LESSON='2024-1hcl-narrative-shandaishengming';
const READING_IDS=['56','57','58A','58B','59','60'];
const READING_ALL=['r1','r2','r3','whole','56','57','58A','58B','59','60','transfer'];
const READING_HEADERS=['提交时间','班级','学号','姓名','学习单','已答原题小题数（共6）','原题满分','教师评分','批改状态','已查看参考题号','提交编号','56 首次答案','57 首次答案','58A 首次答案','58B 首次答案','59 首次答案','60 首次答案','56 当前答案','57 当前答案','58A 当前答案','58B 当前答案','59 当前答案','60 当前答案','段落与全文练习','新编迁移练习','记录校验值'];
function setupReading(){
 const sheet=SpreadsheetApp.openById(READING_BOOK).getSheetByName('Sheet1');
 if(!sheet)throw Error('找不到已核对的 Sheet1，请联系我。');
 const old=sheet.getRange(1,1,1,26).getValues()[0];
 if(old.some(v=>v!=='')&&JSON.stringify(old)!==JSON.stringify(READING_HEADERS))throw Error('表头与本接收程序不符；没有覆盖原内容。');
 if(old.every(v=>v==='')&&sheet.getLastRow()>0)throw Error('表内已有其他内容；没有覆盖。');
 sheet.getRange(1,1,1,26).setValues([READING_HEADERS]).setBackground('#f0f0f0').setFontColor('#000000').setFontWeight('bold').setWrap(true);
 sheet.setFrozenRows(1);sheet.setFrozenColumns(4);sheet.setRowHeight(1,48);
 sheet.setColumnWidth(1,165);sheet.setColumnWidths(2,2,70);sheet.setColumnWidths(4,2,120);sheet.setColumnWidths(6,4,110);sheet.setColumnWidths(10,2,180);sheet.setColumnWidths(12,14,320);sheet.hideColumns(26);
 sheet.getRange(2,8,sheet.getMaxRows()-1,1).setDataValidation(SpreadsheetApp.newDataValidation().requireNumberBetween(0,20).setAllowInvalid(false).setHelpText('教师填写0至20分；未批改请留空。').build());
 sheet.getRange(1,8).setNote('教师评分，0—20分；系统不按字数、关键词或是否填写自动给分。');
 if(!sheet.getFilter())sheet.getRange(1,1,sheet.getMaxRows(),25).createFilter();
 SpreadsheetApp.flush();
 if(JSON.stringify(sheet.getRange(1,1,1,26).getValues()[0])!==JSON.stringify(READING_HEADERS))throw Error('表头保存未确认，请重试。');
 console.log('阅读成绩表已准备好。下一步：部署 → 新建部署 → 网页应用。');
}
function doGet(){return ContentService.createTextOutput(JSON.stringify({ok:true,kind:'hwt-reading-shandai-v1',spreadsheetId:READING_BOOK,lesson:READING_LESSON})).setMimeType(ContentService.MimeType.JSON);}
function readingText(value,max,required){if(typeof value!=='string'||value.length>max||(required&&!/[\p{L}\p{N}]/u.test(value)))throw Error('invalid text');return value;}
function readingSafe(value){return /^[\s]*[=+\-@]/.test(value)?"'"+value:value;}
function readingPayload(b){
 if(!b||b.lesson!==READING_LESSON||!/^[-a-f0-9]{36}$/i.test(b.requestId)||!/^[-a-f0-9]{36}$/i.test(b.nonce))throw Error('invalid request');
 const student=b.student||{},answers=b.answers||{},first=b.first||{};
 const clean={lesson:READING_LESSON,requestId:b.requestId,student:{className:readingText(student.className,30,true).trim(),number:readingText(student.number,5,true).trim(),name:readingText(student.name,80,true).trim()},answers:{},first:{},references:[],version:readingText(b.version,60,true)};
 if(!/^\d{1,3}$/.test(clean.student.number))throw Error('invalid number');
 READING_ALL.forEach(id=>{clean.answers[id]=readingText(answers[id]||'',5000,READING_IDS.indexOf(id)>=0);clean.first[id]=readingText(first[id]||clean.answers[id],5000,READING_IDS.indexOf(id)>=0);});
 if(!Array.isArray(b.references)||b.references.some(id=>READING_ALL.indexOf(id)<0))throw Error('invalid references');
 clean.references=READING_ALL.filter(id=>b.references.indexOf(id)>=0);return clean;
}
function readingReply(data){
 const json=JSON.stringify(data).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
 return HtmlService.createHtmlOutput('<!doctype html><meta charset="utf-8"><p>'+ (data.ok?'Submission saved. You may close this page.':'Submission was not confirmed. Please retry in the worksheet.')+'</p><script>window.top.postMessage('+json+','+JSON.stringify(READING_ORIGIN)+');</script>').setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
function doPost(e){
 let b={},lock;
 try{
  const raw=e&&e.parameter&&e.parameter.payload;
  if(typeof raw!=='string'||raw.length>150000)throw Error('invalid payload');b=JSON.parse(raw);const p=readingPayload(b);
  const digest=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,JSON.stringify(p),Utilities.Charset.UTF_8).map(x=>('0'+(x&255).toString(16)).slice(-2)).join('');
  lock=LockService.getScriptLock();lock.waitLock(20000);
  const sheet=SpreadsheetApp.openById(READING_BOOK).getSheetByName('Sheet1');
  if(!sheet||JSON.stringify(sheet.getRange(1,1,1,26).getValues()[0])!==JSON.stringify(READING_HEADERS))throw Error('header mismatch');
  const last=sheet.getLastRow();if(last>20000)throw Error('capacity');
  const rows=last>1?sheet.getRange(2,11,last-1,16).getValues():[];
  const found=rows.findIndex(row=>row[0]===p.requestId);
  if(found>=0){if(rows[found][15]!==digest)throw Error('request conflict');return readingReply({kind:'hwt-reading-shandai-v1',ok:true,requestId:p.requestId,nonce:b.nonce,spreadsheetId:READING_BOOK,duplicate:true});}
  const index=last+1;if(index>sheet.getMaxRows())sheet.insertRowsAfter(sheet.getMaxRows(),100);
  const groups=['r1','r2','r3','whole'].map(id=>id+'：'+p.answers[id]).join('\n\n');
  const row=[Utilities.formatDate(new Date(),'Asia/Singapore','yyyy-MM-dd HH:mm:ss'),p.student.className,p.student.number,p.student.name,'善待生命',6,20,'','',p.references.join('、'),p.requestId,...READING_IDS.map(id=>p.first[id]),...READING_IDS.map(id=>p.answers[id]),groups,p.answers.transfer,digest].map(v=>typeof v==='string'?readingSafe(v):v);
  row[8]='=IF(H'+index+'="","待批改","已批改")';
  sheet.getRange(index,1,1,26).setValues([row]);SpreadsheetApp.flush();
  const stored=sheet.getRange(index,1,1,26).getValues()[0];
  if(stored[10]!==p.requestId||stored[25]!==digest||stored.some((v,i)=>i!==8&&String(v)!==String(row[i])&&String(v)!==String(row[i]).replace(/^'/,'')))throw Error('readback mismatch');
  return readingReply({kind:'hwt-reading-shandai-v1',ok:true,requestId:p.requestId,nonce:b.nonce,spreadsheetId:READING_BOOK});
 }catch(err){return readingReply({kind:'hwt-reading-shandai-v1',ok:false,requestId:typeof b.requestId==='string'?b.requestId:'',nonce:typeof b.nonce==='string'?b.nonce:'',spreadsheetId:READING_BOOK});}
 finally{if(lock)lock.releaseLock();}
}
