from pathlib import Path
R=Path('site/du/textbook/2hcl/unit6/jiaxinxi');s=(R.parent/'duoyuan/lesson-ui.js').read_text();s=s.replace("'p2-coins':3,'p3-relation':4,'p4-open':5,'p5-link':6,'p6-art':7","'p2-cause':3,'p3-example':4,'p4-tech':5,'p5-mislead':6,'p6-harm':7,'p7-sentence':8")
s=s.replace("if(state.position.view==='task'){", "if(state.position.view==='task'){enhanceTask(state);")
s=s.replace("enhance();watch();})();", "enhance();watch();})();")
pos=s.index('const observer=')
extra=r'''
function enhanceTask(state){
 const t=L.tasks[state.position.task];
 if(t.id==='whole-structure'&&!A.querySelector('.original-table')){
  const rows=[...A.querySelectorAll('.blank-row')],table=document.createElement('table');table.className='original-table';
  table.innerHTML='<thead><tr><th>结构与段落</th><th>主要内容</th></tr></thead><tbody></tbody>';
  const groups=[['开头：提出观点（1）',1],['主体：对观点进行论述（2）',2],['主体：对观点进行论述（3—4）',2],['主体：对观点进行论述（5—6）',2],['结尾：总结概括（7—8）',2]];let n=0;
  rows[0].before(table);for(const[label,count]of groups){const tr=document.createElement('tr'),a=document.createElement('td'),b=document.createElement('td');a.textContent=label;for(let j=0;j<count;j++)b.append(rows[n++]);tr.append(a,b);table.tBodies[0].append(tr)}
 }
 if(t.orderCards&&!A.querySelector('.order-bank')){
  const selects=[...A.querySelectorAll('[data-blank]')],bank=document.createElement('div'),slots=document.createElement('ol');bank.className='order-bank';slots.className='order-slots';bank.setAttribute('aria-label','点击选项依次排序');
  selects[0].closest('.blank-row').before(bank,slots);selects.forEach(s=>s.closest('.blank-row').hidden=true);
  function draw(){bank.replaceChildren();slots.replaceChildren();const used=selects.map(s=>s.value);for(const item of state.answers[t.id].wordOrder){const b=document.createElement('button');b.textContent=item;b.disabled=used.includes(item);b.onclick=()=>{const target=selects.find(s=>!s.value);if(target){target.value=item;target.dispatchEvent(new Event('change'));draw()}};bank.append(b)}selects.forEach((s,i)=>{const li=document.createElement('li'),b=document.createElement('button');b.textContent=s.value||'点击上方选项放入这里';b.setAttribute('aria-label','第'+(i+1)+'步，点击清空');b.onclick=()=>{s.value='';s.dispatchEvent(new Event('change'));draw()};li.append(b);slots.append(li)})}draw();
 }
}
function legacy(){const review=document.querySelector('#review');if(review.hidden||review.querySelector('.legacy-records'))return;const box=document.createElement('section');box.className='legacy-records';box.innerHTML='<h3>旧版记录</h3><p>如以前在本设备使用过旧精读学习单，可单独备份。不会删除或套用到新题。</p><button id="legacyBackup">备份本机旧版记录</button><p id="legacyStatus" role="status"></p>';review.append(box);box.querySelector('button').onclick=()=>{const entries={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(/u6l3|jiaxinxi/i.test(k)&&k!==K)entries[k]=localStorage.getItem(k)}if(!Object.keys(entries).length){box.querySelector('#legacyStatus').textContent='本设备未找到旧版记录。其他域名或设备的记录需在原处导出。';return}const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({schema:'jiaxinxi-legacy-export-v1',entries},null,2)],{type:'application/json'}));a.download='别上假信息的当_旧版记录.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);box.querySelector('#legacyStatus').textContent='旧记录已备份，原记录保留。'}}
const reviewObserver=new MutationObserver(()=>{reviewObserver.disconnect();legacy();reviewObserver.observe(document.querySelector('#review'),{childList:true})});reviewObserver.observe(document.querySelector('#review'),{childList:true});legacy();
'''
s=s[:pos]+extra+s[pos:];(R/'lesson-ui.js').write_text(s)
