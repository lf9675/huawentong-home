/* Assignment-scoped storage keeps personal/legacy learning records untouched. */
(()=>{'use strict';const L=window.LESSON,configKey='hwt-textbook-connection-'+L.id;
let c=null;try{c=JSON.parse(localStorage.getItem(configKey))}catch{}
const match=location.hash.match(/^#classroom=([a-f0-9-]{36})\.([a-f0-9-]{36})\.([a-f0-9]{64})$/);
if(match){c={assignmentId:match[1],studentId:match[2],token:match[3]};history.replaceState(null,'',location.pathname+location.search);try{localStorage.setItem(configKey,JSON.stringify(c))}catch{c.volatile=true}}
if(c&&/^[a-f0-9-]{36}$/.test(c.assignmentId)&&/^[a-f0-9-]{36}$/.test(c.studentId)&&/^[a-f0-9]{64}$/.test(c.token)){
 window.LESSON_STORAGE_KEY='huawentong-lesson-'+L.id+'-v1-classroom-'+c.assignmentId+'-'+c.studentId;
 window.HWTTextbookConnection=c;
}
})();
