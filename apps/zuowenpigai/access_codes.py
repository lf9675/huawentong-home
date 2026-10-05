"""
访问码系统（P1 #4）— 一码通:一个随机码同时充当身份+密码
============================================================
设计要点(依据 C_商业化路线图):
- 零 PII:不收姓名/学号/学校,昵称由系统生成学生挑选(防捣乱)
- 只存 SHA-256 哈希,不存明文;明文仅在生成时显示一次
- 防泄露四层:额度封顶 / 每日限 3 篇 / 用量对学生可见 / 老师一键作废重发
- 独立模块,不改动 database.py;共用同一个 SQLite 文件
"""
import hashlib
import secrets
import random
from datetime import datetime, timedelta, timezone

from database import get_conn

# 新加坡时区(Streamlit Cloud 服务器是 UTC,"每日"限次必须按新加坡的日历日算)
SGT = timezone(timedelta(hours=8))

# 排除易混字符 0/O/1/I/L
CODE_CHARSET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
DAILY_LIMIT = 5  # 每码每天最多提交篇数(2026-07-05 由 3 调整为 5)

# 昵称词库:形容词 + 小动物,组合约 200 个,内测 30 人足够
NICK_ADJ = ["勤奋的", "冷静的", "勇敢的", "专注的", "开朗的", "细心的",
            "坚持的", "好学的", "阳光的", "沉稳的", "机灵的", "踏实的",
            "认真的", "乐观的", "灵巧的"]
NICK_ANIMAL = ["海豚", "小鹿", "猫头鹰", "企鹅", "小狮子", "熊猫",
               "雨燕", "白鲸", "小马", "刺猬", "松鼠", "信天翁", "小虎"]


def _now_sgt():
    return datetime.now(SGT)


def _hash(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode("utf-8")).hexdigest()


def init_access_tables():
    """幂等建表,student.py / codes.py 页面加载时调用"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS access_codes (
            id SERIAL PRIMARY KEY,
            code_hash TEXT UNIQUE NOT NULL,
            nickname TEXT DEFAULT '',
            exam_level TEXT DEFAULT 'HCL',
            essays_total INTEGER NOT NULL,
            essays_used INTEGER DEFAULT 0,
            expiry TEXT,
            is_active INTEGER DEFAULT 1,
            note TEXT DEFAULT '',
            created_at TEXT
        )
    """)
    # 2026-07-05 双轨额度:新作文额度(new_essays_*) + 总次数(essays_*)。
    # 老码 new_essays_total=0 表示不启用双轨,行为与旧版完全一致。
    c.execute("ALTER TABLE access_codes ADD COLUMN IF NOT EXISTS new_essays_total INTEGER DEFAULT 0")
    c.execute("ALTER TABLE access_codes ADD COLUMN IF NOT EXISTS new_essays_used INTEGER DEFAULT 0")
    # 2026-07-05:教师端小设置(如应用链接),免得每次登录重填
    c.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS code_usage_log (
            id SERIAL PRIMARY KEY,
            code_id INTEGER NOT NULL,
            used_at TEXT NOT NULL,
            submission_id INTEGER
        )
    """)
    # P1 #5:学生自带题目的元数据 + "学校老师给的分数"(免费校准样本)
    c.execute("""
        CREATE TABLE IF NOT EXISTS student_prompts (
            id SERIAL PRIMARY KEY,
            submission_id INTEGER NOT NULL,
            prompt_source TEXT,
            prompt_text TEXT,
            requirements TEXT,
            genre TEXT,
            school_score TEXT DEFAULT '',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────
# 生成
# ────────────────────────────────────────────────────────────

def _random_code() -> str:
    seg = lambda: "".join(secrets.choice(CODE_CHARSET) for _ in range(4))
    return f"HW-{seg()}-{seg()}"


def generate_codes(n, essays_total, valid_days, exam_level="HCL", note="",
                   new_essays_total=0):
    """批量生成 n 个码,返回明文列表(仅此一次机会看到明文)。
    essays_total = 总次数上限(含重交);new_essays_total = 其中新作文的篇数上限,
    传 0 表示不区分新作文/重交(旧行为)。"""
    conn = get_conn()
    c = conn.cursor()
    expiry = (_now_sgt() + timedelta(days=valid_days)).strftime("%Y-%m-%d")
    created = _now_sgt().isoformat()
    plain_codes = []
    while len(plain_codes) < n:
        code = _random_code()
        try:
            c.execute(
                "INSERT INTO access_codes (code_hash, exam_level, essays_total, new_essays_total, expiry, note, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (_hash(code), exam_level, essays_total, int(new_essays_total or 0), expiry, note, created))
            plain_codes.append(code)
        except Exception:
            conn.rollback()  # Postgres:失败语句会中止事务,必须回滚后才能重试
            continue  # 哈希撞库(概率极低),换一个重试
    conn.commit()
    conn.close()
    return plain_codes, expiry


# ────────────────────────────────────────────────────────────
# 校验与用量
# ────────────────────────────────────────────────────────────

def today_usage(code_id) -> int:
    """该码今天(新加坡时间)已提交几篇"""
    today = _now_sgt().strftime("%Y-%m-%d")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM code_usage_log WHERE code_id=%s AND used_at LIKE %s",
              (code_id, today + "%"))
    n = c.fetchone()[0]
    conn.close()
    return n


def validate_code(code: str):
    """校验访问码。返回 (ok: bool, info: dict|None, reason: str)"""
    if not code or not code.strip():
        return False, None, "请输入访问码。"
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM access_codes WHERE code_hash=%s", (_hash(code),))
    row = c.fetchone()
    conn.close()
    if row is None:
        return False, None, "访问码不存在,请检查有没有输错(注意横线也要输入)。"
    info = dict(row)
    if not info["is_active"]:
        return False, None, "这个访问码已被停用,请联系老师。"
    if info["expiry"] and _now_sgt().strftime("%Y-%m-%d") > info["expiry"]:
        return False, None, f"这个访问码已于 {info['expiry']} 过期,请联系老师。"
    if info["essays_used"] >= info["essays_total"]:
        return False, None, "这个访问码的批改次数已用完,请联系老师。"
    return True, info, ""


def check_can_submit(code_id, is_new_essay=True):
    """提交批改前的最终校验(防御性:总次数 + 新作文额度 + 每日限次)。返回 (ok, reason)。
    is_new_essay=False 表示"修改后重交",只占总次数,不占新作文额度。"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT essays_used, essays_total, is_active, "
              "COALESCE(new_essays_used,0) AS neu, COALESCE(new_essays_total,0) AS net "
              "FROM access_codes WHERE id=%s", (code_id,))
    row = c.fetchone()
    conn.close()
    if row is None or not row["is_active"]:
        return False, "访问码已失效,请联系老师。"
    if row["essays_used"] >= row["essays_total"]:
        return False, "批改总次数已用完,请联系老师。"
    if is_new_essay and row["net"] > 0 and row["neu"] >= row["net"]:
        return False, (f"新作文额度已用完({row['net']}/{row['net']})。"
                       f"你还可以把批改过的作文【修改后重交】,让老师看看你改得怎么样!")
    if today_usage(code_id) >= DAILY_LIMIT:
        return False, f"今天已经批改了 {DAILY_LIMIT} 篇啦,好好消化今天的反馈,明天再来!"
    return True, ""


def record_usage(code_id, submission_id=None, is_new_essay=True):
    """提交成功后记账:日志 + 总次数 +1;新作文再给新作文额度 +1"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO code_usage_log (code_id, used_at, submission_id) VALUES (%s, %s, %s)",
              (code_id, _now_sgt().isoformat(), submission_id))
    if is_new_essay:
        c.execute("UPDATE access_codes SET essays_used = essays_used + 1, "
                  "new_essays_used = COALESCE(new_essays_used,0) + 1 WHERE id=%s", (code_id,))
    else:
        c.execute("UPDATE access_codes SET essays_used = essays_used + 1 WHERE id=%s", (code_id,))
    conn.commit()
    conn.close()


def get_code_info(code_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM access_codes WHERE id=%s", (code_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


# ────────────────────────────────────────────────────────────
# 昵称
# ────────────────────────────────────────────────────────────

def nickname_candidates(k=6):
    combos = random.sample([(a, b) for a in NICK_ADJ for b in NICK_ANIMAL], k)
    return [a + b for a, b in combos]


def set_nickname(code_id, nickname):
    """只允许在昵称为空时设置一次"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE access_codes SET nickname=%s WHERE id=%s AND (nickname='' OR nickname IS NULL)",
              (nickname, code_id))
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────
# 老师端管理
# ────────────────────────────────────────────────────────────

def list_codes():
    """全部码 + 最近使用时间(倒序)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT a.*, (SELECT MAX(used_at) FROM code_usage_log l WHERE l.code_id = a.id) AS last_used
        FROM access_codes a ORDER BY a.id DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_usage_log(code_id, limit=20):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT used_at, submission_id FROM code_usage_log WHERE code_id=%s "
              "ORDER BY used_at DESC LIMIT %s", (code_id, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def deactivate_code(code_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE access_codes SET is_active=0 WHERE id=%s", (code_id,))
    conn.commit()
    conn.close()


def reissue_code(code_id):
    """作废旧码,把剩余额度转到新码。返回 (新明文码, 剩余额度, 有效期) 或 None"""
    info = get_code_info(code_id)
    if info is None:
        return None
    remaining = max(info["essays_total"] - info["essays_used"], 0)
    deactivate_code(code_id)
    conn = get_conn()
    c = conn.cursor()
    while True:
        new_code = _random_code()
        try:
            c.execute(
                "INSERT INTO access_codes (code_hash, nickname, exam_level, essays_total, expiry, note, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (_hash(new_code), info.get("nickname", ""), info.get("exam_level", "HCL"),
                 remaining, info.get("expiry"),
                 (info.get("note") or "") + f" [由码#{code_id}重发]",
                 _now_sgt().isoformat()))
            break
        except Exception:
            conn.rollback()  # Postgres:失败语句会中止事务,必须回滚后才能重试
            continue
    conn.commit()
    conn.close()
    return new_code, remaining, info.get("expiry")


# ────────────────────────────────────────────────────────────
# 学生自带题目 + 校准样本(P1 #5)
# ────────────────────────────────────────────────────────────

def save_student_prompt(submission_id, prompt_source, prompt_text,
                        requirements, genre, school_score=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO student_prompts
                 (submission_id, prompt_source, prompt_text, requirements, genre, school_score, created_at)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)""",
              (submission_id, prompt_source, prompt_text or "", requirements or "",
               genre or "", str(school_score or "").strip(), _now_sgt().isoformat()))
    conn.commit()
    conn.close()


def list_calibration_samples():
    """学生填了学校分数的提交 = 免费校准样本。返回 [学校分, AI分, 差值, ...]"""
    import json as _json
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT sp.submission_id, sp.genre, sp.prompt_text, sp.school_score,
               sp.created_at, s.feedback_json, s.student_name
        FROM student_prompts sp
        JOIN submissions s ON sp.submission_id = s.id
        WHERE sp.school_score != ''
        ORDER BY sp.id DESC
    """)
    rows = []
    for r in c.fetchall():
        d = dict(r)
        try:
            fb = _json.loads(d.pop("feedback_json") or "{}")
            _sc = fb.get("scores", {}) or {}
            d["ai_score"] = _sc.get("total")
            d["ai_content"] = _sc.get("content")
            d["ai_language"] = _sc.get("language")
            d["ai_grade"] = fb.get("grade_estimate", "")
        except Exception:
            d["ai_score"] = None
            d["ai_content"] = None
            d["ai_language"] = None
            d["ai_grade"] = ""
        try:
            diff = None
            if d["ai_score"] is not None:
                diff = round(float(d["ai_score"]) - float(d["school_score"]), 1)
            d["diff"] = diff
        except Exception:
            d["diff"] = None
        rows.append(d)
    conn.close()
    return rows


# ────────────────────────────────────────────────────────────
# 教师端设置 + 补充操作(2026-07-05 UX 修整)
# ────────────────────────────────────────────────────────────

def get_setting(key, default=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM app_settings WHERE key=%s", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else default


def set_setting(key, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO app_settings (key, value) VALUES (%s, %s)
                 ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value""",
              (key, value))
    conn.commit()
    conn.close()


def reactivate_code(code_id):
    """重新启用(修复:停用是单行道,误点无法撤销)。过期码启用后仍受有效期约束。"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE access_codes SET is_active=1 WHERE id=%s", (code_id,))
    conn.commit()
    conn.close()


def today_usage_map():
    """全部码的今日(新加坡日历日)用量,一条分组查询,供码列表'今日已用'列使用"""
    today = _now_sgt().strftime("%Y-%m-%d")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT code_id, COUNT(*) AS n FROM code_usage_log "
              "WHERE used_at LIKE %s GROUP BY code_id", (today + "%",))
    m = {r["code_id"]: r["n"] for r in c.fetchall()}
    conn.close()
    return m

