/* Lesson-specific presentation; shared engine and shared wordbook stay unchanged. */
(()=>{'use strict';const L=window.LESSON,host=document.querySelector('#activity');
function draw(){const s=window.LessonEngine?.state();if(s?.position.view!=='task')return;const t=L.tasks[s.position.task];if(!t||host.dataset.renderedTask===t.id&&host.querySelector('.haidi-support'))return;
 const mark=document.createElement('div');mark.className='haidi-support';host.dataset.renderedTask=t.id;
 if(t.id==='discussion'){const h=document.createElement('h3');h.textContent='先口头练习拟人句';mark.append(h);for(const x of ['星星在夜空中________。','春天来了，花儿________。','一阵风吹来，树叶在风中________。']){const p=document.createElement('p');p.className='question';p.textContent=x;mark.append(p)}const tip=document.createElement('p');tip.textContent='让事物有人的动作、神态或情感。说完后，再完成读后说。';mark.append(tip);host.querySelector('details')?.remove();}
 host.insertBefore(mark,host.querySelector('.concept')||host.querySelector('.actions'));
 if(['sea','return'].includes(t.id)){
  const b=document.createElement('button');b.type='button';b.textContent='先核对点选与取证';b.className='support-check';const msg=document.createElement('p');msg.setAttribute('role','status');let tries=0;
  b.onclick=()=>{const a=window.LessonEngine.state().answers[t.id];const ok=window.LessonEngine.objective(t,a);tries++;msg.textContent=ok?'点选和取证已齐。书面解释仍由你完成，再提交比较。':tries===1?'请回原文检查点选和证据范围；需要多句的地方不能只选一句。':t.id==='sea'?'先检查三个成语和两个词义；水晶宫依据要有“透明”与鱼虾，鲨鱼依据要有“一咬—咬不动—溜走”。':'检查第3段、第5—8段的地点与内容；第9段取证要同时有“巨浪”和“宁静”。';b.disabled=true;setTimeout(()=>b.disabled=false,5000)};
  const submit=host.querySelector('#submit');submit.parentElement.before(b,msg);
 }
}
new MutationObserver(draw).observe(host,{childList:true});draw();
})();
