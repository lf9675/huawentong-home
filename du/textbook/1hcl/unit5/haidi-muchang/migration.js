/* Keep legacy answers as an exportable archive; changed questions are never remapped by index. */
(()=>{'use strict';const L=window.LESSON;
if(window.HWTTextbookConnection)return;
const key='huawentong-lesson-'+L.id+'-v1';let state={};try{state=JSON.parse(localStorage.getItem(key))||{}}catch{}
if(state.haidiLegacyArchived)return;
const archive=[];for(const k of ['haidi-worksheet-v2','worksheet:haidi-worksheet-v2']){try{const raw=localStorage.getItem(k);if(raw)archive.push({key:k,value:JSON.parse(raw)})}catch{}}
if(archive.length){state.schema='huawentong-lesson-v1';state.lessonId=L.id;state.contentVersion=L.version;state.sequenceVersion=L.sequenceVersion;state.legacyVersions=[...(state.legacyVersions||[]),{version:'haidi-worksheet-v2',records:archive}];state.haidiLegacyArchived=true;try{localStorage.setItem(key,JSON.stringify(state))}catch{}}
})();
