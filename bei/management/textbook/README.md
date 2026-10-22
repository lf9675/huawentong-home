# Textbook collection v1 — 2026-10-22

Pilot: `s1u2l1`, content version `20261022-1` (世界各地的新年风俗).

## Architecture
- Existing lesson-v1 engine remains the reading/exercise UI. It gains an opt-in storage key, save event and restore method. Only the pilot loads cloud-bootstrap.js/cloud.js.
- Personal legacy localStorage keys are unchanged. Classroom answers have keys scoped to assignment and student. No old local record is automatically uploaded.
- Existing teacher session validation (`hwt_sessions`) is reused. Teacher-only endpoint operations verify the hashed, unexpired session server-side.
- Student links carry a 256-bit credential in a URL fragment, immediately removed from the address bar and saved on that device. The server stores only SHA-256 hashes. A link is a bearer credential, not a verified personal identity; distribute privately and rotate after leakage.
- Supabase `hwt-textbook` edge function contains the pinned pilot content. Objective answers are recalculated server-side at subitem level. Written answers always remain pending a teacher review; no AI scoring.
- Five additive `hwt_tb_*` tables; all have RLS and no anon/authenticated grants. Service-only invoker RPCs atomically create assignments, save responses and preserve first answers. No changes to existing classroom, essay, import-workspace or Google configuration.
- Request UUID + payload hash deduplicate retries. Student revision prevents stale-device writes. An append-only receipt stores each accepted submission; first response remains immutable while latest answers and revision text update. All timestamps used for receipt/collection are server-generated; client first-answer timestamps are unverified learning metadata.
- Class roster is frozen when creating an assignment (1–80 numbers). To change participation, create a new task; old records remain. No real roster is seeded.
- Status: 未收到 / 已进入 / 进行中 / 已交齐. 已交齐 requires an explicit final receipt with all 8 submitted tasks, even if some objective answers are wrong or written answers await review.
- The teacher view polls every 15s while visible; polling pauses while a student detail view is open to protect unsaved feedback. Student sync debounces saved submissions by 1.8s and retries failed pending requests every 15s while open. This is not a background service worker.
- Default collection expiry 30 days, configurable 1–90. Teacher can close/reopen within that expiry. Existing records are retained; there is no automatic deletion policy.

## Deployment
1. Apply `supabase/sql/hwt-textbook.sql` once. Migration name: `hwt_textbook_collection_v1`.
2. Deploy `supabase/functions/hwt-textbook/{index.ts,core.mjs,lesson.json}` as `hwt-textbook`, verify_jwt=false because all data operations implement their own teacher/student authentication. The anonymous health action returns only version metadata. Service-role key remains in server environment.
3. Deploy the static repository to the existing huawentong-home Worker. `.assetsignore` already excludes `/supabase/**` and `/tests/**`.
4. Visit `/bei/management/textbook/`. Existing `/bei/login.html` supports a restricted `/bei/` return path.
5. Sign in, create a task, privately distribute per-student links. Use only synthetic students for the first live acceptance test, then close that test task.

## Validation
Run `node --experimental-strip-types --test tests/textbook*.test.mjs`.
Database transactional checks: create → invalid credential → submit all 8 → identical retry → different payload conflict → stale revision → correction retains first → teacher review → review conflict → closed class → rotated credential. Fixtures rolled back.
Browser acceptance uses a separate local mock server and explicitly fictional data, not production teacher credentials or student records. Checked teacher counts, student opt-in, incorrect-first/corrected-latest and teacher review updates. 16 automated tests cover validation, auth boundaries and offline queue/final-submit recovery. Browser testing uses Chromium; a physical iPad/Safari and authenticated live classroom remain deployment acceptance gates.

## Limits and rollback
- Public lesson answers are already available in the teaching package; this is formative feedback, not a secure examination system.
- Server accepts only the pinned pilot schema. Future lessons/versions require a deliberate new fixture and validator review.
- New live dashboard is separate from the prior owner-private import workspace. Do not make that private workspace public or claim it has live collection.
- Removing cloud scripts from pilot reading.html rolls back frontend collection; existing records and personal exercises stay intact. Close assignments to stop submissions. Do not drop tables during rollback.
- The downloadable old lesson packages remain offline-only and explicitly labeled; existing PPT/pedagogical content is unchanged.
