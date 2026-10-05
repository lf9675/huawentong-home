// Port of apps/zuowenpigai/prompts.py finalize_grade_fields; audit never changes scores.
import {norm} from './core.mjs';
export function finalize(f,exam,text,configs){
 const cfg=configs[exam],s=f.scores;if(!s||!Number.isFinite(s.content)||!Number.isFinite(s.language))throw Error('incomplete_grade');
 const cm=cfg.content_max,lm=cfg.language_max,practical=exam.startsWith('PRACTICAL'),notes=[];
 s.content=Math.max(0,Math.min(cm,s.content));s.language=Math.max(0,Math.min(lm,s.language));
 const [threshold,floor]=practical?[180,6]:exam==='HCL'?[480,16]:[320,11];
 const ex=f.language_floor_exception||{},qs=(ex.unclear_quotes||[]).filter(q=>typeof q==='string'&&norm(q).length>=4&&norm(text).includes(norm(q)));
 if(norm(text).length>=threshold&&s.language>0&&s.language<floor&&!(ex.applies===true&&qs.length>=3)){s.language=floor;f.language_floor_applied=true;}
 const red=(f.paragraph_feedback||[]).flatMap(p=>p.red_issues||[]).filter(x=>String(x.type).includes('错')&&!String(x.type).includes('病')&&!String(x.type).includes('标点')).length;
 if(Number.isFinite(s.language_band)){const typos=Math.max(Number.isFinite(s.typo_count)?Math.floor(s.typo_count):0,red);s.language=Math.max(0,Math.min(lm,Math.floor(s.language_band-Math.min(3*lm/30,0.5*lm/30*typos)+0.5)));}
 const cap=(field,value,why)=>{if(Number.isFinite(value)&&s[field]>value){notes.push(`${field==='content'?'内容':'语文'} ${s[field]}→${value}（${why}）`);s[field]=value;}};
 const g=f.content_gate;
 if(g&&typeof g==='object'){
  let level=g.c_level||'无';if(level==='无'&&(['life_logic_ok','detail_balance_ok','keyword_focus_ok'].some(k=>g[k]===false)||g.keyword_misread===true))level='较严重';
  if(g.core_detail_extent==='几乎没有')level='严重';else if(g.core_detail_extent==='仅一小段'&&level!=='严重')level='较严重';
  let lc;if(level==='严重'){cap('content',({30:14,20:9,10:4})[cm],'内容严重硬伤');lc=({30:19,20:12,10:6})[lm];}
  else if(level==='较严重'){cap('content',({30:16,20:11,10:6})[cm],'内容较严重硬伤');lc=({30:23,20:16,10:8})[lm];}
  const axis=Array.isArray(g.sub_point_axis)?g.sub_point_axis:[],off=axis.filter(x=>x&&![undefined,null,'','紧扣'].includes(x.verdict)).length;
  if(off){cap('content',(off>=axis.length?{30:12,20:8}:off*2>axis.length?{30:14,20:9}:{30:16,20:11})[cm],'分论点脱轴');if(level!=='严重'){level=off>=axis.length?'严重':'较严重';lc=(level==='严重'?{30:19,20:12}:{30:23,20:16})[lm];}}
  cap('language',lc,'内容硬伤联动顶');
  if(g.ending_lyric_ok===false&&!practical){const t=exam==='HCL'?44:29;if(s.content+s.language>t)cap('content',Math.max(0,t-s.language),'缺少结尾抒情议论');}
 }
 s.total=s.content+s.language;s.max=cfg.essay_total;if(notes.length)f.auto_caps=notes;
 const bounds=exam==='HCL'?[['A1',45],['A2',42],['B3',39],['B4',36],['C5',33],['C6',30]]:[['A1',.75],['A2',.70],['B3',.65],['B4',.60],['C5',.55],['C6',.50],['D7',.45],['E8',.40]].map(([g,p])=>[g,Math.round(p*cfg.essay_total)]);
 f.grade_estimate=bounds.find(([_,t])=>s.total>=t)?.[0]||(exam==='HCL'?'D7-F9':'F9');
 const next=[...bounds].reverse().find(([_,t])=>s.total<t);f.grade_distance=(next?`距离${next[0]}还差约${next[1]-s.total}分。`:'已达本次评估的最高等级。')+(typeof f.grade_distance==='string'?f.grade_distance:'');return f;
}
