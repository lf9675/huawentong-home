/* Legacy pages call window.storage. Classroom keys must never read personal records. */
(()=>{if(!window.HWTTextbookConnection)return;const key=window.LESSON_STORAGE_KEY;window.storage={get:async()=>({value:localStorage.getItem(key)}),set:async(_key,value)=>{localStorage.setItem(key,value)},delete:async()=>{localStorage.removeItem(key)}};})();
