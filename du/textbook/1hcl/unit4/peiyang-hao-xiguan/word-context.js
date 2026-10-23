/* Connect the lesson engine to the shared personal wordbook. */
window.HWT_WORD_CONTEXT=()=>{
 const l=window.LESSON,words=window.LESSON_WORDS||{};
 const examplesMap=Object.fromEntries(Object.entries(words).filter(([word,d])=>l.paragraphs[d.paragraph-1]?.includes(word)).map(([word,d])=>[word,{text:l.paragraphs[d.paragraph-1],label:l.id.endsWith('-vocab')?'词语练习语境':'海报：'+l.paragraphLabels[d.paragraph-1]}]));
 return {lessonId:l.id,lessonTitle:l.title,grade:l.grade,unit:l.unit,paragraphs:l.paragraphs,examplesMap};
};
window.HWT_WORD_LEXICON=()=>window.LESSON_WORDS||{};
