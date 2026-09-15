const SPREADSHEET_ID = '1_xft7XkfZTByvgWlgu-bVKZophK53FrwtabSurbC0mE';
const SHEET_NAME = '成绩';
const HEADERS = ['提交时间','姓名','班级','学号','学习单','年份','首次得分','最终得分','首次答案(JSON)','最终答案(JSON)','错题','尝试次数(JSON)','用时(秒)','提交ID','页面版本'];

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function getSheet_() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) sh = ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) {
    sh.getRange(1,1,1,HEADERS.length).setValues([HEADERS]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

function doGet(e) {
  try {
    getSheet_();
    return json_({ok:true, service:'hwt-cloze-result-v1', sheet:SHEET_NAME, time:new Date().toISOString()});
  } catch (err) {
    return json_({ok:false, error:String(err && err.message ? err.message : err)});
  }
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    const raw = (e && e.parameter && e.parameter.payload) ? e.parameter.payload : (e && e.postData ? e.postData.contents : '');
    const p = JSON.parse(raw || '{}');
    if (p.type !== 'hwt-cloze-result-v1') return json_({ok:false,error:'Unsupported payload type'});
    ['name','className','indexNo','lesson','year','submissionId'].forEach(k=>{ if(!String(p[k]||'').trim()) throw new Error('Missing '+k); });
    const sh = getSheet_();
    const last = sh.getLastRow();
    if (last >= 2) {
      const ids = sh.getRange(2,14,last-1,1).getDisplayValues().flat();
      if (ids.includes(String(p.submissionId))) return json_({ok:true,duplicate:true,submissionId:p.submissionId});
    }
    sh.appendRow([
      new Date(), String(p.name), String(p.className), String(p.indexNo), String(p.lesson), String(p.year),
      Number(p.firstScore||0), Number(p.finalScore||0), JSON.stringify(p.firstAnswers||{}), JSON.stringify(p.finalAnswers||{}),
      (p.wrongQuestions||[]).join(','), JSON.stringify(p.attempts||{}), Number(p.durationSec||0), String(p.submissionId), String(p.pageVersion||'')
    ]);
    return json_({ok:true,duplicate:false,submissionId:p.submissionId,row:sh.getLastRow()});
  } catch (err) {
    return json_({ok:false,error:String(err && err.message ? err.message : err)});
  } finally {
    try { lock.releaseLock(); } catch (_) {}
  }
}
