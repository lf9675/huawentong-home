# Textbook collection v2 — 2026-10-22

Coverage: 21 published lessons (4 Secondary 1 HCL, 17 Secondary 2 HCL), 286 steps. Teacher workflow: grade → lesson → classroom assignment. The original pilot `s1u2l1` and its stored versions remain compatible.

## Architecture
- Existing lesson-v1 engine remains the reading/exercise UI. It gains an opt-in storage key, save event and restore method. All 18 shared-engine reading pages load cloud-bootstrap.js/cloud.js. 团圆饭 and the two earlier worksheets use narrow adapters to retain their existing UIs.
- Personal legacy localStorage keys are unchanged. Classroom answers have keys scoped to assignment and student. No old local record is automatically uploaded.
- Existing teacher session validation (`hwt_sessions`) is reused. Teacher-only endpoint operations verify the hashed, unexpired session server-side.
- Student links carry a 256-bit credential in a URL fragment, immediately removed from the address bar and saved on that device. The server stores only SHA-256 hashes. A link is a bearer credential, not a verified personal identity; distribute privately and rotate after leakage.
- Supabase `hwt-textbook` edge function contains server snapshots generated from the published content. Objective answers are recalculated server-side at subitem level. Written answers always remain pending a teacher review; no AI scoring.
- Five additive `hwt_tb_*` tables; all have RLS and no anon/authenticated grants. Service-only invoker RPCs atomically create assignments, save responses and preserve first answers. No changes to existing classroom, essay, import-workspace or Google configuration.
- Request UUID + payload hash deduplicate retries. Student revision prevents stale-device writes. An append-only receipt stores each accepted submission; first response remains immutable while latest answers and revision text update. All timestamps used for receipt/collection are server-generated; client first-answer timestamps are unverified learning metadata.
- Class roster is frozen when creating an assignment (1–80 numbers). To change participation, create a new task; old records remain. No real roster is seeded.
- Status: 未收到 / 已进入 / 进行中 / 已交齐. 已交齐 requires an explicit final receipt with all of that assignment’s submitted steps, even if some objective answers are wrong or written answers await review.
- The teacher view polls every 15s while visible; polling pauses while a student detail view is open to protect unsaved feedback. Student sync debounces saved submissions by 1.8s and retries failed pending requests every 15s while open. This is not a background service worker.
- Default collection expiry 30 days, configurable 1–90. Teacher can close/reopen within that expiry. Existing records are retained; there is no automatic deletion policy.

## Deployment
1. Apply `supabase/sql/hwt-textbook.sql` once. Migration name: `hwt_textbook_collection_v1`.
2. Deploy `supabase/functions/hwt-textbook/{index.ts,core.mjs,lesson.json,lessons.json}` as `hwt-textbook`, verify_jwt=false because all data operations implement their own teacher/student authentication. The anonymous health action returns only version metadata. Service-role key remains in server environment.
3. Deploy the static repository to the existing huawentong-home Worker. `.assetsignore` already excludes `/supabase/**` and `/tests/**`.
4. Visit `/bei/management/textbook/`. Existing `/bei/login.html` supports a restricted `/bei/` return path.
5. Sign in, create a task, privately distribute per-student links. Use only synthetic students for the first live acceptance test, then close that test task.

## Validation
Run `node --experimental-strip-types --test tests/textbook*.test.mjs`.
Database transactional checks: create → invalid credential → submit all 8 → identical retry → different payload conflict → stale revision → correction retains first → teacher review → review conflict → closed class → rotated credential. Fixtures rolled back.
Browser acceptance uses a separate local mock server and explicitly fictional data, not production teacher credentials or student records. Checked teacher counts, student opt-in, incorrect-first/corrected-latest and teacher review updates. 45 automated tests cover validation, auth boundaries and offline queue/final-submit recovery. Browser testing uses Chromium; a physical iPad/Safari and authenticated live classroom remain deployment acceptance gates.

## Limits and rollback
- Public lesson answers are already available in the teaching package; this is formative feedback, not a secure examination system.
- Run `node scripts/build-textbook-catalog.mjs` to regenerate both catalog.json and lessons.json after lesson changes. Only published reading packages and the two explicit earlier worksheet sources enter this catalog; the larger wordbook title list is not a list of finished packages. New assignment snapshots are frozen; existing assignments keep their original JSON. An incompatible content revision is rejected, not silently regraded.
- New live dashboard is separate from the prior owner-private import workspace. Do not make that private workspace public or claim it has live collection.
- Removing cloud scripts from the connected reading pages rolls back frontend collection; existing records and personal exercises stay intact. Close assignments to stop submissions. Do not drop tables during rollback.
- The downloadable old lesson packages remain offline-only and explicitly labeled; existing PPT/pedagogical content is unchanged.

## Multi-lesson release details
- Selection filters assignments by exact lesson ID, remembers the last selection and supports `?lesson=...` links from lesson homepages. Student links always use the selected assignment’s reading path, including during rotation.
- Existing `subjective` and `discussion` modes normalize to `written` only in server metadata. The student’s original question wording, sequence, choices and images stay intact. Oral activities record an explicit “展开讲评” action, with no automatic correct/incorrect judgment or implied oral grade.
- Evidence matching is recalculated from the server’s frozen paragraphs. Shared-engine predicates match the existing p/terms/requiredTerms rules. 团圆饭 retains its ordered/unordered evidence rules and punctuation selection rules.
- Dedicated identity and picture navigation writers now respect the classroom storage key. Old record bridges do not copy personal archives into a classroom record. The personal wordbook remains separate.
- Earlier worksheets: click choices as before; “提交开放题” freezes the first written answer, later submissions update the latest answer. Classroom final submission uses the collection flow, without presenting the legacy word-count score as a final grade. The existing teacher-led live voting page for 我为狮城做贡献 stays on its original workflow.
- No SQL migration is needed for v2, no old rows are rewritten, and no mock student data is deployed. The isolated preview server is outside this repository.
- Automated coverage includes all 21 full submissions, every lesson’s empty-roster metrics, wrong evidence, field grading, correct selected-lesson creation, retries, old pilot compatibility, and scoped storage. Browser acceptance samples the shared engine, 团圆饭 and earlier worksheet adapters with fictional users.
