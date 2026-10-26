// Keep all student routes in this one document, including paragraph deep links.
function offlineRoute(){
 const hash=location.hash.slice(1), comic=hash==='comics'||hash.startsWith('comic-p');
 if(/^read-p\d+$/.test(hash)){state.readP=Math.max(1,Math.min(D.paragraphs.length,Number(hash.slice(6))));save();switchView('read');}
 $('#lessonApp').hidden=comic;$('#comicView').hidden=!comic;$('#fileTools').hidden=hash!=='record';
 if(comic){renderComics();const p=hash.slice(7);if(p)requestAnimationFrame(()=>document.getElementById('p'+p)?.scrollIntoView());}
}
window.addEventListener('hashchange',offlineRoute);offlineRoute();
try{localStorage.setItem(KEY+'-probe','1');localStorage.removeItem(KEY+'-probe');}catch{showStorageWarning();}
$('#importRecord').onclick=()=>$('#recordFile').click();
$('#recordFile').onchange=async e=>{
 const file=e.target.files[0],status=$('#importStatus');if(!file)return;
 try{
  if(file.size>2000000)throw Error('File too large（文件过大）');
  const incoming=JSON.parse(await file.text());validateRecord(incoming);
  if(!confirm('Restore this backup? Current answers will be replaced. 恢复备份会替换当前作答；请先导出当前记录。'))return;
  state={...clean(),...incoming,identity:{...clean().identity,...incoming.identity},taskAt:{'1':0,'2':0,...incoming.taskAt}};
  save();renderRecord();status.textContent='Restored（已恢复）';
 }catch(err){status.textContent='Cannot restore（未导入）: '+err.message;}
 e.target.value='';
};
