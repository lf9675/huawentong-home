/**
 * Receiver for 选词填空（2025） only. NOT deployed by committing this file.
 * Create a separate Apps Script project; do not overwrite the old vocabulary receiver.
 * Uses the exact teacher-designated spreadsheet. Reads expose no student records.
 */
const VCFG={sheetId:'1XWGz1BBY4K5AfVsmZSYnqxXvlie2j2wiVFV0ZRF0-VE',lessonId:'2hcl-xuanci-2025',title:'选词填空（2025）',protocol:'hwt-vocab-progress-v1',progress:'选词填空2025-进度',details:'选词填空2025-逐题'};
const VPHEAD=['更新时间','学习单','班级','学号','姓名','已核对题数','首次答对','首次正确率','当前答对','累计错题','待重做','重做正确','状态','已提交版本','记录ID','首次开始时间','最近提交ID','校验值','作答快照'];
const VDHEAD=['更新时间','学习单','班级','学号','姓名','题号','首次答案','初答对错','当前答案','当前核对','答错次数','最近错答','最近重做答案','重做结果','记录ID','版本'];
const VANS={16:['名落孙山'],17:['络绎不绝'],18:['诡异'],19:['品学兼优'],20:['妥善'],21:['苦口婆心'],22:['好逸恶劳'],23:['烦躁'],24:['屡见不鲜'],25:['潜移默化','逐渐'],26:['每况愈下'],27:['日新月异'],28:['立竿见影'],29:['囫囵吞枣'],30:['名列前茅']};
function vjson(x){return ContentService.createTextOutput(JSON.stringify(x)).setMimeType(ContentService.MimeType.JSON);}
function vnorm(x){return String(x||'').normalize('NFKC').replace(/[\s\u200b\uFEFF]/g,'');}
function vright(id,x){return VANS[id].indexOf(vnorm(x))>=0;}
function vtext(x){const s=String(x==null?'':x);return /^[\s]*[=+\-@]/.test(s)?"'"+s:s;}
function vsafe(row){return row.map(x=>typeof x==='number'?x:vtext(x));}
function vensure(book,name,headers){let sh=book.getSheetByName(name);if(!sh)sh=book.insertSheet(name);if(sh.getMaxColumns()<headers.length)sh.insertColumnsAfter(sh.getMaxColumns(),headers.length-sh.getMaxColumns());if(sh.getLastRow()===0){sh.getRange(1,1,1,headers.length).setValues([headers]);sh.setFrozenRows(1);sh.getRange(1,1,1,headers.length).setBackground('#f0f0f0').setFontColor('#000000').setFontWeight('bold');sh.setColumnWidths(1,headers.length,130);sh.setColumnWidth(1,165);sh.setColumnWidth(2,180);sh.setColumnWidth(5,160);sh.getRange(1,1,1,headers.length).setWrap(true);}else if(JSON.stringify(sh.getRange(1,1,1,headers.length).getValues()[0])!==JSON.stringify(headers))throw Error('header mismatch');return sh;}
function setupVocabProgress(){const b=SpreadsheetApp.openById(VCFG.sheetId),p=vensure(b,VCFG.progress,VPHEAD),d=vensure(b,VCFG.details,VDHEAD);p.hideColumns(14,6);d.hideColumns(15,2);SpreadsheetApp.flush();}
function doGet(){return vjson({ok:true,protocol:VCFG.protocol,spreadsheetId:VCFG.sheetId,lessonId:VCFG.lessonId,writeMethod:'POST'});}
function vrow(sh,row,values){if(row>sh.getMaxRows())sh.insertRowsAfter(sh.getMaxRows(),row-sh.getMaxRows());sh.getRange(row,1,1,values.length).setValues([vsafe(values)]);}
function doPost(e){let lock;try{
 const raw=e&&e.postData&&e.postData.contents;if(typeof raw!=='string'||raw.length>55000)throw Error('request too large');const b=JSON.parse(raw);
 if(b.action!=='vocabProgress'||b.protocol!==VCFG.protocol||b.lessonId!==VCFG.lessonId||b.spreadsheetId!==VCFG.sheetId)throw Error('wrong receiver');
 if(typeof b.sessionId!=='string'||!(/^[a-f0-9-]{36}$/i.test(b.sessionId))||!Number.isInteger(b.revision)||b.revision<1||b.submissionId!==b.sessionId+':'+b.revision)throw Error('invalid submission');
 const student=b.student;if(!student||typeof student.name!=='string'||!student.name.trim()||student.name.length>60||typeof student.cls!=='string'||!student.cls.trim()||student.cls.length>24||!/^\d{1,3}$/.test(student.sid))throw Error('student required');
 if(!Array.isArray(b.questions)||b.questions.length!==15||new Set(b.questions.map(q=>q.id)).size!==15||b.questions.some(q=>!VANS[q.id]||typeof q.current!=='string'||q.current.length>400||(q.first&&(typeof q.first.answer!=='string'||q.first.answer.length>400))))throw Error('invalid questions');
 const hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,raw,Utilities.Charset.UTF_8).map(v=>('0'+((v+256)%256).toString(16)).slice(-2)).join('');
 lock=LockService.getScriptLock();lock.waitLock(20000);const book=SpreadsheetApp.openById(VCFG.sheetId),p=vensure(book,VCFG.progress,VPHEAD),d=vensure(book,VCFG.details,VDHEAD);
 const rows=p.getLastRow()>1?p.getRange(2,1,p.getLastRow()-1,VPHEAD.length).getValues():[],index=rows.findIndex(r=>String(r[14])===b.sessionId),old=index>=0?rows[index]:null;
 const receipt=()=>({ok:true,saved:true,protocol:VCFG.protocol,spreadsheetId:VCFG.sheetId,lessonId:VCFG.lessonId,submissionId:b.submissionId,revision:b.revision});
 if(old){if(String(old[2])!==vtext(student.cls)||String(old[3])!==vtext(student.sid)||String(old[4])!==vtext(student.name))throw Error('identity mismatch');if(Number(old[13])>b.revision)return vjson(Object.assign(receipt(),{superseded:true}));if(Number(old[13])===b.revision){if(String(old[17])!==hash)throw Error('revision conflict');return vjson(Object.assign(receipt(),{duplicate:true}));}}
 const previous=old?JSON.parse(String(old[18])):null,byId=new Map((previous?.questions||[]).map(q=>[q.id,q]));
 const questions=b.questions.map(q=>Object.assign({},q,{first:byId.get(q.id)?.first||q.first||null})).sort((a,b)=>a.id-b.id);
 const now=Utilities.formatDate(new Date(),'Asia/Singapore','yyyy-MM-dd HH:mm:ss');let completed=0,firstRight=0,currentRight=0,mistakes=0,reviewed=0;
 const detailRows=questions.map(q=>{const first=q.first,checked=q.checked&&vnorm(q.current)===vnorm(q.checked.answer),currentOK=checked&&vright(q.id,q.checked.answer),m=q.mistake,lastReview=m?.lastReview;
 if(first){completed++;if(vright(q.id,first.answer))firstRight++;}if(currentOK)currentRight++;
 const hadMistake=!!m||(first&&!vright(q.id,first.answer));if(hadMistake)mistakes++;const reviewOK=hadMistake&&lastReview&&vright(q.id,lastReview.answer)&&m.status==='reviewed';if(reviewOK)reviewed++;
 return [now,VCFG.title,student.cls,student.sid,student.name,q.id,first?first.answer:'未作答',first?(vright(q.id,first.answer)?'对':'错'):'未作答',q.current||'',checked?(currentOK?'对':'错'):'待核对',Math.max(hadMistake?1:0,Math.min(Number(m?.wrongCount)||0,999)),String(m?.lastWrong||''),String(lastReview?.answer||''),lastReview?(reviewOK?'重做正确':'待重做'):(hadMistake?'待重做':'无错题'),b.sessionId+':'+q.id,b.revision];});
 const drows=d.getLastRow()>1?d.getRange(2,1,d.getLastRow()-1,VDHEAD.length).getValues():[],dindex=new Map(drows.map((r,i)=>[String(r[14]),i+2]));let next=d.getLastRow()+1;
 for(const row of detailRows){const n=dindex.get(row[14])||next++;dindex.set(row[14],n);vrow(d,n,row);}SpreadsheetApp.flush();
 for(const row of detailRows){const n=dindex.get(row[14]);if(n&&JSON.stringify(d.getRange(n,1,1,row.length).getValues()[0].map(String))!==JSON.stringify(vsafe(row).map(String)))throw Error('detail verification failed');}
 const stored={questions},progress=[now,VCFG.title,student.cls,student.sid,student.name,completed,firstRight,completed?Math.round(firstRight/completed*100)+'%':'—',currentRight,mistakes,mistakes-reviewed,reviewed,completed===15?'已完成初答':'进行中',b.revision,b.sessionId,old?old[15]:now,b.submissionId,hash,JSON.stringify(stored)];
 const rowNumber=index>=0?index+2:p.getLastRow()+1;vrow(p,rowNumber,progress);SpreadsheetApp.flush();const verify=p.getRange(rowNumber,1,1,progress.length).getValues()[0];if(String(verify[16])!==b.submissionId||String(verify[17])!==hash||Number(verify[13])!==b.revision)throw Error('save not verified');
 return vjson(receipt());
 }catch(err){return vjson({ok:false,saved:false,error:'未能完成保存，请保留本机答案后重试。'});}finally{if(lock)lock.releaseLock();}}
