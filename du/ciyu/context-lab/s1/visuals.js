'use strict';
function visual(w){
 const tx=(x,y,t)=>`<text x="${x}" y="${y}" text-anchor="middle" fill="#334e4b" stroke="none" font-size="18">${esc(t)}</text>`;
 const svg=(body,label)=>`<figure class="diagram"><svg viewBox="0 0 420 170" role="img" aria-label="${esc(label)}"><g fill="none" stroke="#386e69" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">${body}</g></svg><figcaption>${esc(label)}</figcaption></figure>`;
 if(w.word==='循环')return svg(`<path d="M100 65C110 15 310 15 320 65M320 90C310 140 110 140 100 90"/><path d="m307 49 13 16 10-19M89 108l11-18 13 16"/><rect x="60" y="60" width="80" height="36" rx="9" fill="#d8ebf1"/><rect x="280" y="60" width="80" height="36" rx="9" fill="#d8ebf1"/>${tx(100,85,'水池')}${tx(320,85,'喷泉')}${tx(210,164,'水流出去，再流回来')}`,'循环：沿过程反复进行');
 if(w.word==='镶嵌')return svg(`<rect x="45" y="25" width="110" height="105" rx="5"/><path d="M61 41h78v72H61Z" stroke-dasharray="5 5"/><path d="M178 76h53m-13-10 13 10-13 10"/><rect x="260" y="25" width="110" height="105" rx="5"/><rect x="276" y="41" width="78" height="72" fill="#8cb8d7"/>${tx(100,159,'空出的框位')}${tx(315,159,'玻璃装入并固定')}`,'镶嵌：嵌入其中，不是放在旁边');
 if(w.word==='凸')return svg(`<path d="M35 100h45V50h55v50h50M240 65h45v50h55V65h50"/><path d="M30 100h160m45-35h160" stroke="#b7c7c1" stroke-dasharray="5 5"/>${tx(110,149,'凸：高出周围')}${tx(315,149,'凹：低于周围')}`,'比较表面高度：凸与凹');
 if(w.word==='横梁')return svg(`<rect x="90" y="55" width="25" height="90" fill="#c8dcd0"/><rect x="305" y="55" width="25" height="90" fill="#c8dcd0"/><rect x="65" y="35" width="290" height="22" fill="#e4b774"/>${tx(210,24,'横梁：横向支撑')}${tx(105,168,'柱')}${tx(319,168,'柱')}`,'横梁与竖直柱子的方向对比');
 if(w.word==='山谷')return svg(`<path d="M22 126 109 30l88 98L309 25l89 104" fill="#dfebd8"/><path d="M180 126q30-10 60 0" stroke="#62a7c2"/>${tx(210,164,'山与山之间的低处')}`,'山谷的位置示意');
 if(w.word==='溢')return svg(`<path d="M130 25v105h150V25"/><path d="M134 35h144M276 35q33-8 31 25v47" stroke="#4b9dbf"/><path d="M301 99l6 10 6-10"/>${tx(210,161,'水太满，从杯口流出')}`,'溢：过满而流出；不同于杯底漏水');
 if(w.word==='撇')return svg(`<path d="M160 25q-12 60-62 95" stroke="#bd4738" stroke-width="11"/><path d="M254 25q9 61 65 95" stroke="#9db1a8" stroke-width="11"/>${tx(123,155,'撇：向左下')}${tx(297,155,'捺：向右下')}`,'笔画方向示意，不是完整笔顺动画');
 if(w.word==='季度')return svg(`${[0,1,2,3].map((g)=>`<rect x="${15+g*100}" y="25" width="90" height="65" rx="8" fill="${g%2?'#e8dfc5':'#d4e4dc'}"/>${tx(60+g*100,51,'第'+(g+1)+'季度')}${tx(60+g*100,78,(g*3+1)+'—'+(g*3+3)+'月')}`).join('')}${tx(210,141,'一年12个月 ÷ 4 = 每季度3个月')}`,'季度按三个月划分');
 if(w.word==='截至')return svg(`<path d="M30 75h355m-14-10 14 10-14 10"/><path d="M220 36v79" stroke="#bd4738"/><circle cx="80" cy="75" r="5" fill="#386e69"/><circle cx="150" cy="75" r="5" fill="#386e69"/>${tx(130,36,'已统计的部分')}${tx(221,140,'星期五：统计到这里')}${tx(318,39,'以后可能增加')}`,'截至：指出统计的时间边界');
 if(w.word==='记账'||w.word==='帐篷')return `<div class="parts"><div><b class="han">账</b><span>贝：联系钱财</span><strong>记账 · 收支</strong></div><div><b class="han">帐</b><span>巾：联系布帛</span><strong>帐篷 · 遮盖</strong></div></div>`;
 if(!w.nodes?.length)return '';
 return `<figure class="diagram"><div class="node-row">${w.nodes.map((n,i)=>`${i?'<span class="flow-arrow" aria-hidden="true">→</span>':''}<div class="node">${pictogram(n.icon)}<span>${esc(n.label)}</span></div>`).join('')}</div><figcaption>意思与情境示意</figcaption></figure>`;
}
