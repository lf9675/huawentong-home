(()=>{'use strict';
const L=window.LESSON,activity=document.querySelector('#activity'),source=document.querySelector('#source');
function enhance(){
 const select=document.querySelector('[data-field="thread"]');
 if(select&&!document.querySelector('#threadTable')){
  const section=document.createElement('section');section.id='threadTable';
  const h=document.createElement('h3');h.textContent='课本七行内容';section.append(h);
  const table=document.createElement('table');table.className='thread-table';
  for(const [p,text] of L.threadRows){const tr=document.createElement('tr'),th=document.createElement('th'),td=document.createElement('td');th.textContent='第'+p+'段';td.textContent=text;tr.append(th,td);table.append(tr)}section.append(table);
  const map=document.createElement('p');map.className='kai';map.id='threadMap';section.append(map);
  const label=select.previousElementSibling,choice=activity.querySelector('fieldset');
  if(choice)choice.before(section,label,select);else label.before(section);
  const sync=()=>{map.textContent='情节概括：包〔'+(select.value||'　　')+'〕 → 传〔'+(select.value||'　　')+'〕 → 吃到〔'+(select.value||'　　')+'〕。';};select.addEventListener('change',sync);sync();
 }
 if(document.querySelector('#p1')&&window.LessonEngine.state().position.view==='read'&&!document.querySelector('#firstOral')){
  const d=document.createElement('details');d.id='firstOral';d.className='read-intro';const s=document.createElement('summary');s.textContent='口头想一想';const p=document.createElement('p');p.textContent='中国北方人为什么喜欢在大年三十吃饺子？先说你的想法。';d.append(s,p);source.append(d);
 }
}
new MutationObserver(enhance).observe(activity,{childList:true});enhance();
})();