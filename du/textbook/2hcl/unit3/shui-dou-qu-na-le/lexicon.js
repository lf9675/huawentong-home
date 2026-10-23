window.LESSON_WORDS={
  "艰巨": {
    "meaning": "困难很多，任务繁重。",
    "en": "very difficult and demanding"
  },
  "昂贵": {
    "meaning": "价格或成本很高。",
    "en": "expensive; costing a great deal"
  },
  "消耗": {
    "meaning": "在使用过程中逐渐耗去。",
    "en": "use up gradually"
  },
  "干旱": {
    "meaning": "长时间降雨不足而缺水。",
    "en": "drought; a long period with too little rain"
  },
  "趋势": {
    "meaning": "整体发展的方向。",
    "en": "the general direction of change; a trend"
  },
  "因素": {
    "meaning": "影响结果的原因或条件。",
    "en": "a factor that influences a result"
  },
  "水喉": {
    "meaning": "本地日常用语，指水龙头。文中“四大水喉”比喻供水来源。",
    "en": "a tap; the passage's Four National Taps refer figuratively to water sources"
  },
  "新生水": {
    "meaning": "经处理净化、供再使用的再生水。",
    "en": "NEWater; treated and purified reclaimed water for reuse"
  },
  "淡化水": {
    "meaning": "把海水中的盐分去除后得到的水。",
    "en": "desalinated water; seawater with the salt removed"
  },
  "能源": {
    "meaning": "能提供能量的资源。",
    "en": "resources that provide energy"
  },
  "运输": {
    "meaning": "把人或物从一个地方送到另一个地方。",
    "en": "transport people or goods from one place to another"
  },
  "扩大": {
    "meaning": "使范围或规模变大。",
    "en": "increase the size or scale"
  },
  "集水区": {
    "meaning": "收集雨水并让雨水流入蓄水池的地区。",
    "en": "a water catchment area that collects rainwater for reservoirs"
  },
  "蓄水池": {
    "meaning": "用来储存水的地方。",
    "en": "a reservoir or place for storing water"
  },
  "有限": {
    "meaning": "有一定限制，并不是无穷无尽。",
    "en": "limited in amount or scope; not endless"
  },
  "需求": {
    "meaning": "需要的数量或内容。",
    "en": "demand; the amount or kind of something needed"
  },
  "比例": {
    "meaning": "一部分与整体或另一部分的数量关系。",
    "en": "the relationship between a part and a whole, or between two quantities"
  },
  "平均": {
    "meaning": "把总量按人数等均分所得的数。",
    "en": "an average; a total shared equally across people or units"
  },
  "浴室": {
    "meaning": "供人洗澡的房间。",
    "en": "a room used for bathing"
  },
  "目标": {
    "meaning": "希望达到的结果。",
    "en": "a goal; the result one hopes to reach"
  },
  "来之不易": {
    "meaning": "得到它并不容易，需要付出努力或资源。",
    "en": "hard-won; requiring effort or resources to obtain"
  },
  "开源节流": {
    "meaning": "增加来源，同时减少不必要的消耗。文中指拓展水源并节约用水。",
    "en": "increase sources and reduce waste; here, expand water supply while conserving water"
  },
  "可持续发展": {
    "meaning": "发展时也顾及未来的需要，避免耗尽资源。",
    "en": "sustainable development that meets needs without exhausting resources for the future"
  }
};
window.HWT_WORD_LEXICON=()=>window.LESSON_WORDS;
window.HWT_WORD_CONTEXT=()=>({lessonId:window.LESSON.id,grade:2,unit:3,lessonTitle:window.LESSON.title,paragraphs:window.LESSON.paragraphs,examplesMap:Object.fromEntries(Object.keys(window.LESSON_WORDS).map(w=>{const i=window.LESSON.paragraphs.findIndex(p=>p.includes(w));return [w,i>=0?{text:(window.LESSON.paragraphs[i].match(/[^。！？]+[。！？]?/g)||[]).find(s=>s.includes(w)),label:"第"+(i+1)+"部分"}:{}]}))});
