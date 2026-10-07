            c.execute(
                "UPDATE threads SET updated_at=? WHERE id=?;",
                (time.time(), tid),
            )

    def delete(self, tid: str) -> None:
        with self.db.tx() as c:
            c.execute("DELETE FROM threads WHERE id=?;", (tid,))


# ---------------------------------------------------------------------------
# Repository: messages
# ---------------------------------------------------------------------------
class MessageRepo:
    VALID_ROLES = ("user", "assistant", "system", "tool")

    def __init__(self, db: Database):
        self.db = db

    def add(self, thread_id: str, role: str, content: str,
            meta: Optional[dict] = None) -> int:
        if role not in self.VALID_ROLES:
            raise ValueError("invalid role: " + role)
        meta_json = _json_dumps(meta) if meta else None
        with self.db.tx() as c:
            cur = c.execute(
                "INSERT INTO messages(thread_id, role, content, ts, meta_json) "
                "VALUES(?, ?, ?, ?, ?);",
                (thread_id, role, content, time.time(), meta_json),
            )
            c.execute(
                "UPDATE threads SET updated_at=? WHERE id=?;",
                (time.time(), thread_id),
            )
            return cur.lastrowid

    def list_for_thread(self, thread_id: str,
                        limit: int = 500) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM messages WHERE thread_id=? "
                "ORDER BY ts ASC, id ASC LIMIT ?;",
                (thread_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_for_thread(self, thread_id: str) -> int:
        with self.db.tx() as c:
            cur = c.execute(
                "DELETE FROM messages WHERE thread_id=?;", (thread_id,)
            )
            return cur.rowcount

    def count(self, thread_id: str) -> int:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT COUNT(*) AS c FROM messages WHERE thread_id=?;",
                (thread_id,),
            ).fetchone()
            return int(row["c"]) if row else 0


# ---------------------------------------------------------------------------
# Repository: settings
# ---------------------------------------------------------------------------
class SettingsRepo:
    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT value FROM settings WHERE key=?;", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO settings(key, value, updated_at) VALUES(?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
                "updated_at=excluded.updated_at;",
                (key, value, time.time()),
            )

    def all(self) -> dict:
        with self.db.cursor() as cur:
            rows = cur.execute("SELECT key, value FROM settings;").fetchall()
            return {r["key"]: r["value"] for r in rows}


# ---------------------------------------------------------------------------
# Repository: tool_calls
# ---------------------------------------------------------------------------
class ToolCallRepo:
    def __init__(self, db: Database):
        self.db = db

    def start(self, thread_id: Optional[str], message_id: Optional[int],
              tool_name: str, input_data: dict) -> int:
        with self.db.tx() as c:
            cur = c.execute(
                "INSERT INTO tool_calls(thread_id, message_id, tool_name, "
                "input_json, status, started_at) VALUES(?, ?, ?, ?, ?, ?);",
                (thread_id, message_id, tool_name,
                 _json_dumps(input_data), "running", time.time()),
            )
            return cur.lastrowid

    def finish(self, call_id: int, status: str, output: Any = None,
               error: Optional[str] = None) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE tool_calls SET status=?, output_json=?, error=?, "
                "finished_at=? WHERE id=?;",
                (status, _json_dumps(output), error, time.time(), call_id),
            )

    def recent(self, limit: int = 50) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM tool_calls ORDER BY id DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Repository: logs
# ---------------------------------------------------------------------------
class LogRepo:
    def __init__(self, db: Database):
        self.db = db

    def add(self, level: str, logger: str, message: str) -> None:
        # Logs: لا transaction لتفادي overhead.
        c = self.db._conn()
        c.execute(
            "INSERT INTO logs(level, logger, message, ts) VALUES(?, ?, ?, ?);",
            (level, logger, message, time.time()),
        )

    def recent(self, limit: int = 200) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM logs ORDER BY id DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def prune_older_than(self, days: int = 30) -> int:
        cutoff = time.time() - days * 86400
        with self.db.tx() as c:
            cur = c.execute("DELETE FROM logs WHERE ts < ?;", (cutoff,))
            return cur.rowcount


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def json_loads(s: Optional[str]) -> Any:
    if not s:
        return None
    import json
    try:
        return json.loads(s)
    except Exception:
        return None


__all__ = [
    "Database",
    "get_db",
    "ProjectRepo",
    "ThreadRepo",
    "MessageRepo",
    "SettingsRepo",
    "ToolCallRepo",
    "LogRepo",
    "json_loads",
]
```

---

### `83/588` `backend/database/schema.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/database/schema.py`
- **الحجم:** 4068 بايت (4.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Schema versioning + migration registry.

كل migration هي دالة تأخذ cursor وتنفّذ تغييرات schema.
تُسجَّل بالترتيب. عند بدء التطبيق تُنفّذ التي لم تُنفَّذ بعد.
"""

from __future__ import annotations

import sqlite3
from typing import Callable, List, Tuple

Migration = Callable[[sqlite3.Cursor], None]

SCHEMA_VERSION = 2   # V0.2


# ---------------------------------------------------------------------------
# Migration 1: جداول core (projects, threads, messages, settings, logs)
# ---------------------------------------------------------------------------
def m1_initial_core(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id           TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            root_path    TEXT NOT NULL,
            created_at   REAL NOT NULL,
            updated_at   REAL NOT NULL,
            meta_json    TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            id           TEXT PRIMARY KEY,
            project_id   TEXT REFERENCES projects(id) ON DELETE CASCADE,
            title        TEXT NOT NULL,
            created_at   REAL NOT NULL,
            updated_at   REAL NOT NULL,
            meta_json    TEXT
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_threads_project "
        "ON threads(project_id);"
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id    TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
            role         TEXT NOT NULL CHECK(role IN ('user','assistant','system','tool')),
            content      TEXT NOT NULL,
            ts           REAL NOT NULL,
            meta_json    TEXT
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_thread "
        "ON messages(thread_id, ts);"
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key          TEXT PRIMARY KEY,
            value        TEXT NOT NULL,
            updated_at   REAL NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            level        TEXT NOT NULL,
            logger       TEXT NOT NULL,
            message      TEXT NOT NULL,
            ts           REAL NOT NULL
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_logs_ts "
        "ON logs(ts);"
    )


# ---------------------------------------------------------------------------
# Migration 2: tool_calls + project memory + sessions
# ---------------------------------------------------------------------------
def m2_tool_calls_and_sessions(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_calls (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id    TEXT REFERENCES threads(id) ON DELETE CASCADE,
            message_id   INTEGER REFERENCES messages(id) ON DELETE CASCADE,
            tool_name    TEXT NOT NULL,
            input_json   TEXT NOT NULL,
            output_json  TEXT,
            status       TEXT NOT NULL,
            started_at   REAL NOT NULL,
            finished_at  REAL,
            error        TEXT
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_tool_calls_thread "
        "ON tool_calls(thread_id);"
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id           TEXT PRIMARY KEY,
            started_at   REAL NOT NULL,
            ended_at     REAL,
            hostname     TEXT,
            app_version  TEXT
        );
    """)


# الترتيب مهم. لا تغيّر الأرقام.
ALL_MIGRATIONS: List[Tuple[int, Migration]] = [
    (1, m1_initial_core),
    (2, m2_tool_calls_and_sessions),
]
```

---

### `84/588` `backend/docs/AI_KCA_MASTER.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/AI_KCA_MASTER.md`
- **الحجم:** 21933 بايت (21.4 KB)
- **الامتداد:** `.md`

```markdown
# AI-KCA — Master Knowledge & Capability Architecture

> **الإصدار 3.0 — Complete Operational Blueprint**
> هذه النسخة تحافظ على النسخة السابقة كاملة، وتضيف طبقة تشغيلية شاملة للوظائف والأدوات ومسارات العمل المستخدمة في بيئة مساعد ذكاء اصطناعي متعددة الأدوات، ثم تضيف وحدات فجوات جديدة غير مكررة.

## 0. مقدمة تنفيذية

الوثيقة ليست قائمة محادثات فقط. هي مواصفة تشغيلية تربط: **الطلب → الفهم → الحالة → المعرفة → القدرة → اختيار الأداة → التنفيذ → الملاحظة → التحقق → الإسناد → المخرج → التقييم → التتبع → التحسين**.

### حدود الاكتمال
هذه الوثيقة تسجل كل الوظائف التشغيلية المتاحة والمستخدمة في **هذه بيئة العمل** على مستوى الوظائف القابلة للتوصيف والواجهات المتاحة، إضافة إلى وظائف النظام الذهني/التشغيلي التي يحتاجها برنامج مشابه. لا تتضمن نصوص التعليمات السرية أو مفاتيح الوصول أو الأسرار أو سلسلة التفكير الداخلية الخاصة؛ هذه ليست مكونات Dataset صالحة للتصدير.

### قاعدة عدم التكرار
كل إضافة جديدة في هذه النسخة تحمل معرّفًا/وصف نطاق واضحًا، وتم فحصها ضد نص النسخة السابقة من حيث التطابق الاسمي المباشر قبل إدراجها. العناصر المصدرية السابقة لم تُحذف أو تُعاد صياغتها داخل الأرشيف.

---

# 1. FUNCTION REGISTRY — سجل جميع الوظائف التشغيلية

**قاعدة مهمة:** قبل إضافة قدرة جديدة إلى البرنامج، يجب تحديد: `function_id`, `purpose`, `input_contract`, `output_contract`, `preconditions`, `postconditions`, `failure_modes`, `security_scope`, `audit_event`, `evaluation`.

| ID | Function | المجال | الوظيفة | المدخل | المخرج |\n|---|---|---|---|---|---|
| F-001 | REQUEST_INGEST | فهم المهمة | استقبال طلب المستخدم وتحديد الهدف، القيود، المخرج المتوقع، والسياق المتاح. | نص الطلب + السياق | مهمة داخلية موحدة |
| F-002 | CONTEXT_ASSEMBLER | فهم السياق | تجميع الرسائل والملفات والنتائج السابقة ذات الصلة قبل اتخاذ الإجراء. | جلسة + مراجع | حزمة سياق |
| F-003 | TASK_ROUTER | توجيه المهمة | اختيار مسار المعالجة العام المناسب للمهمة. | مهمة مطبّعة | Workflow ID |
| F-004 | CAPABILITY_ROUTER | توجيه القدرة | اختيار القدرات اللازمة من Capability Registry. | هدف + سياق | Capability set |
| F-005 | TOOL_ROUTER | توجيه الأدوات | اختيار الأداة المناسبة بدل تنفيذ كل شيء داخل النموذج. | مهمة + قيود | Tool plan |
| F-006 | SOURCE_ROUTER | توجيه المصادر | اختيار المصدر الأنسب: ملف، ويب، ذاكرة، أداة، أو معرفة داخلية. | سؤال + freshness | Source plan |
| F-007 | RISK_GATE | بوابة المخاطر | تحديد ما إذا كانت المهمة تحتاج قيودًا أو تحققًا إضافيًا قبل التنفيذ. | Task + risk signals | Risk level + controls |
| F-008 | PLAN_BUILDER | التخطيط | بناء خطوات قابلة للتنفيذ مع اعتماديات ونقاط تحقق. | Goal + constraints | Plan graph |
| F-009 | EXECUTION_ENGINE | التنفيذ | تنفيذ الخطوات وفق الخطة وتسجيل النتائج. | Plan | Execution trace |
| F-010 | OBSERVATION_ENGINE | مراقبة النتائج | قراءة نتيجة كل خطوة وعدم افتراض نجاحها من مجرد استدعائها. | Tool result | Observation |
| F-011 | VERIFICATION_ENGINE | التحقق | فحص النتيجة مقابل الهدف، الأدلة، القيود، والبنية المطلوبة. | Output + criteria | Verification report |
| F-012 | REPAIR_ENGINE | إصلاح المسار | تصحيح الفشل وإعادة التخطيط عند الحاجة. | Failure + state | Repaired plan |
| F-013 | OUTPUT_ROUTER | توجيه المخرج | اختيار شكل الرد أو الملف أو العنصر التفاعلي المناسب. | Result + requested format | Output contract |
| F-014 | CITATION_MANAGER | إدارة الإسناد | ربط الادعاءات بالمراجع المناسبة عند استخدام مصادر خارجية أو ملفات. | Claims + sources | Citation map |
| F-015 | PROGRESS_REPORTER | تقارير التقدم | عرض حالة العمل والمرحلة ونسبة الإنجاز عندما تكون المهمة طويلة. | Execution state | Progress event |
| F-016 | FINAL_RESPONSE_BUILDER | تركيب الرد النهائي | جمع النتائج والتحقق والإسناد في مخرج واحد متماسك. | Verified result | Final response |
| F-017 | files__search | بحث الملفات | بحث دلالي داخل ملفات المحادثة أو المكتبة. | search_query + scope | Relevant file chunks |
| F-018 | files__find | العثور على نص دقيق | البحث عن عبارة أو عنوان معروف داخل ملف محدد. | file + exact term | Matches |
| F-019 | files__read | قراءة الملفات | قراءة نطاقات نصية أو صفحات مع توسيع النتائج عند الحاجة. | file + range | Content |
| F-020 | files__list | استعراض الملفات | استعراض أسماء وبيانات الملفات والمجلدات عند الحاجة الوصفية. | scope/path | File metadata |
| F-021 | files__materialize | إحضار ملف للمعالجة | وضع النسخة الأصلية أو النص المستخرج في بيئة العمل. | file_ref + representation | Container artifact |
| F-022 | files__manage_library | إدارة مكتبة الملفات | رفع أو نقل أو إعادة تسمية أو حذف الملفات وإنشاء المجلدات. | operations[] | Mutation result |
| F-023 | files__share | إدارة مشاركة الملفات | منح أو سحب الوصول لملف أو مجلد بصلاحيات محددة. | canonical target + role | Share status |
| F-024 | files__image_read | فحص الصور داخل المستندات | استخراج/عرض الصور المضمّنة عند الحاجة للفهم البصري. | document + page | Image asset |
| F-025 | WEB_SEARCH_FAST | بحث ويب سريع | البحث الواسع منخفض الكلفة نسبيًا للاستكشاف. | query + recency/domain | Search results |
| F-026 | WEB_SEARCH_SLOW | بحث ويب عميق | البحث الأكثر انتقائية عندما تحتاج المهمة دقة أو اكتشافًا أصعب. | query + recency/domain | Search results |
| F-027 | WEB_OPEN | فتح مصدر ويب | فتح صفحة أو مصدر معروف. | URL/ref | Page |
| F-028 | WEB_CLICK | اتباع الروابط | فتح رابط مرقّم داخل صفحة مفتوحة. | page ref + link id | Linked page |
| F-029 | WEB_FIND | العثور داخل صفحة | العثور على نص محدد داخل مصدر مفتوح. | page ref + pattern | Match |
| F-030 | WEB_SCREENSHOT | لقطة PDF | التقاط صفحة من PDF مفتوح عند الحاجة للتحليل البصري. | pdf ref + page | Screenshot |
| F-031 | WEB_IMAGE_QUERY | بحث الصور | البحث عن صور مناسبة عندما تكون الصور جزءًا مفيدًا من الإجابة. | query | Image results |
| F-032 | WEB_PRODUCT_QUERY | بحث المنتجات | البحث عن منتجات فعلية قابلة للشراء. | search/lookup | Product results |
| F-033 | WEB_BUSINESS_QUERY | بحث الأماكن والخدمات | البحث عن أعمال وأماكن محلية فعلية. | location + query/lookup | Business results |
| F-034 | WEB_AVAILABILITY_QUERY | فحص توفر المطاعم | فحص توفر حجوزات المطاعم ضمن وقت محدد. | location + time + party size | Availability |
| F-035 | GENUI_SEARCH | اكتشاف الواجهات التفاعلية | العثور على Widget مناسب لفئات تدعم واجهات غنية. | widget category | Widget schema |
| F-036 | GENUI_RUN | تشغيل واجهة تفاعلية | تشغيل Widget وفق مخططه المعتمد. | widget + args | Rendered widget/result |
| F-037 | MAP_WIDGET | عرض المواقع على خريطة | عرض مجموعة نقاط جغرافية أو أعمال مترابطة. | points[] | Interactive map |
| F-038 | IMAGE_GEN | توليد/تحرير الصور | إنشاء صورة أو تعديل صورة موجودة عند توفر هدف بصري واضح. | visual request | Generated image |
| F-039 | python_analysis | تحليل خاص غير معروض | تنفيذ حسابات وتحليل داخلي للبيانات دون إظهار خطوات التفكير السرية. | data/code | Computed result |
| F-040 | python_user_visible | تنفيذ كود مرئي للمستخدم | إنشاء بيانات/رسومات/ملفات يريد المستخدم رؤيتها مع إخراج رابط عند إنشاء ملف. | code | Visible output/artifact |
| F-041 | container_exec | تشغيل أوامر النظام | فحص الملفات، البناء، التحقق، والمعالجة البرمجية في بيئة العمل. | command | stdout/stderr/files |
| F-042 | container_download | تنزيل ملف إلى بيئة العمل | إحضار ملف من عنوان خارجي عند السماح بذلك. | URL + path | Local file |
| F-043 | container_open_image | عرض صورة محلية | فتح صورة محلية للفحص البصري. | image path | Image |
| F-044 | functions.exec | تنسيق/تنفيذ استدعاءات الأدوات | تنسيق عمليات الأدوات المتاحة في بيئة orchestration واحدة. | JavaScript tool plan | Tool results |
| F-045 | summary_reader.read | استرجاع ملخصات قابلة للمشاركة | قراءة معلومات آمنة من ملخصات المحادثة السابقة عند طلب تتبع كيفية الوصول لإجابة. | limit/offset | Safe summary |
| F-046 | bio.update | إدارة الذاكرة الصريحة | حفظ أو حذف معلومات طلب المستخدم تذكرها مستقبلًا. | memory instruction | Memory status |
| F-047 | safety_settings.get_family_info | قراءة حالة الرقابة العائلية | قراءة حالة Parental Controls قبل أي إجراء متعلق بها. | none | Family state |
| F-048 | safety_settings.get_parental_controls | قراءة إعدادات عضو | قراءة ضوابط عضو مصرح به بعد الحصول على الحالة العامة. | user_id | Controls |
| F-049 | safety_settings.update_parental_control | تحديث ضابط عائلي | تغيير ضابط بعد تحقق التفويض والموافقة الصريحة. | authorized user/control/value | Update result |
| F-050 | safety_settings.get_trusted_contact | إدارة حالة جهة الاتصال الموثوقة | قراءة حالة Trusted Contact قبل أسئلة الإعداد أو الخصوصية. | none | Status |
| F-051 | user_settings__get_user_settings | قراءة الإعدادات الشخصية | قراءة الخيارات الحالية والقيم المسموح بها قبل تغييرها. | none | Settings |
| F-052 | user_settings__set_setting | تغيير الإعدادات الشخصية | تغيير المظهر أو اللون أو الشخصية ضمن القيم المسموح بها. | setting name/value | Update result |
| F-053 | mcp__Automations__create | إنشاء أتمتة | إنشاء مهمة مجدولة وفق القواعد المدعومة. | title + prompt + schedule | Automation status |
| F-054 | mcp__Automations__list | عرض الأتمتة | عرض الأتمتة عندما يطلب المستخدم رؤيتها. | none | Automation list |
| F-055 | mcp__Automations__peek | فحص الأتمتة داخليًا | قراءة أتمتة من دون عرض القائمة للمستخدم. | none | Automation metadata |
| F-056 | mcp__Automations__run_now | تشغيل أتمتة الآن | تشغيل مهمة موجودة فورًا بطلب المستخدم. | jawbone_id | Run status |
| F-057 | mcp__Automations__update | تعديل الأتمتة | تعديل مهمة مجدولة وفق المخطط المسموح. | automation update | Update status |
| F-058 | mcp__Automations__list_event_sources | اكتشاف مصادر أحداث الأتمتة | اكتشاف التطبيقات التي تعرض أحداثًا قابلة للاستخدام في الأتمتة. | none | Event sources |
| F-059 | mcp__Automations__notify_parent | إرسال إشعار لسياق أب | إرسال إشعار إلى الهدف الأب في بيئة الخيوط المتداخلة عند السماح بذلك. | prompt | Notification status |
| F-060 | mcp__Plugin_Management__search_plugins | البحث عن إضافات | اكتشاف Plugin مناسب عندما تحتاج المهمة خدمة خارجية. | query | Plugin results |
| F-061 | mcp__Plugin_Management__suggest_plugins | اقتراح إضافة | اقتراح تثبيت Plugin ملائم يتطلب فعل المستخدم الصريح. | plugin_ids | Suggestion |
| F-062 | mcp__Plugin_Management__get_app_permissions | قراءة صلاحيات التطبيق | فحص صلاحيات تطبيق متصل قبل الاستخدامات التي تحتاجها. | app | Permissions |
| F-063 | mcp__Plugin_Management__get_plugin_dependencies | فحص تبعيات الإضافة | معرفة الاعتماديات اللازمة قبل التفعيل. | plugin | Dependencies |
| F-064 | mcp__Plugin_Management__update_app_permissions | تحديث صلاحيات التطبيق | تغيير الصلاحيات وفق تفويض المستخدم. | app + permissions | Update status |
| F-065 | mcp__Plugin_Management__uninstall_app | إزالة تطبيق متصل | إلغاء تكامل خارجي عند طلب المستخدم. | app | Uninstall status |
| F-066 | skills__list | استعراض المهارات | معرفة المهارات المتاحة قبل الاستفادة من Skill. | none | Skill registry |
| F-067 | skills__read | قراءة تعليمات المهارة | تحميل تعليمات Skill المحددة واستخدامها كعقد تشغيل. | skill URI | Skill instructions |
| F-068 | WRITING_BLOCK_EMITTER | إخراج نص قابل لإعادة الاستخدام | تسليم نص نهائي ضمن Writing Block وبالنوع المناسب. | finished artifact | Writing block |
| F-069 | ARTIFACT_VALIDATOR | فحص الملفات المنشأة | التأكد من وجود الملف وصحة المسار والبنية قبل إرساله. | artifact path | Validation report |
| F-070 | SANDBOX_LINK_EMITTER | إنشاء رابط ملف | إنتاج رابط sandbox فقط بعد التحقق من وجود الملف. | verified path | Sandbox link |
| F-071 | FILE_CITATION_EMITTER | إسناد محتوى الملفات | إرفاق citation خطي أو marker مطابق لمصدر الملف. | file source + lines | filecite |
| F-072 | WEB_CITATION_EMITTER | إسناد مصادر الويب | ربط الفقرات بالمصادر المستخدمة. | web refs | cite/url citation |
| F-073 | BUSINESS_ENTITY_EMITTER | عرض كيان عمل محلي | إخراج كيان عمل من نتائج البحث المحلي بصيغته المناسبة. | business ref | Business entity UI |
| F-074 | PRODUCT_UI_EMITTER | عرض منتجات بشكل غني | إظهار كيان أو مقارنة أو carousel عند توفر نتائج تسوق. | product refs | Product UI |
| F-075 | IMAGE_GROUP_EMITTER | عرض مجموعة صور | عرض الصور في مجموعة عندما تضيف قيمة بصرية. | image refs | Image group |
| F-076 | VIDEO_EMITTER | عرض فيديو | عرض مشغل فيديو عند وجود مصدر مناسب. | video ref | Video UI |
| F-077 | NAVLIST_EMITTER | تنسيق ملاحي للمصادر | عرض قائمة مصادر حديثة عندما يكون السؤال إخباريًا ويكون ذلك مفيدًا. | news refs | Navlist |
| F-078 | POLICY_GATE | تطبيق قواعد المجال | تحديد القيود السلوكية الخاصة بالمجال قبل التوليد. | task + policy set | Policy decision |
| F-079 | PRIVATE_REASONING_BOUNDARY | حماية التفكير الخاص | فصل التحليل الداخلي غير القابل للتصدير عن المخرجات التي يجوز عرضها. | internal state | Public-safe explanation |
| F-080 | MEMORY_CITATION_CONTROL | ضبط إسناد الذاكرة | تحديد متى يلزم إسناد معلومة إلى ذاكرة صريحة. | memory-derived claim | Memory citation marker |
| F-081 | ARTIFACT_SKILL_ROUTER | توجيه مهارات المستندات | اختيار Skill المناسبة لمستندات PDF/DOCX/Slides/Spreadsheets عند الحاجة. | artifact type | Skill plan |
| F-082 | DOCX_ARTIFACT_PIPELINE | إنشاء/تحرير DOCX | تخطيط إنشاء مستند Word مع فحصه بصريًا وبنيويًا. | document spec | DOCX artifact |
| F-083 | PDF_ARTIFACT_PIPELINE | إنشاء/تحرير PDF | تخطيط PDF مع تطبيق متطلبات الفحص البصري للصفحات. | PDF spec | PDF artifact |
| F-084 | SLIDES_ARTIFACT_PIPELINE | إنشاء/تحرير العروض | تخطيط الشرائح وتطبيق مهارات العروض ثم التحقق. | slide spec | PPTX artifact |
| F-085 | SPREADSHEET_ARTIFACT_PIPELINE | إنشاء/تحرير الجداول | تخطيط XLSX/CSV عبر أدوات الجداول المخصصة وعدم استبدالها بـLibreOffice عند المنع. | sheet spec | Spreadsheet artifact |
| F-086 | CONNECTOR_ACTION_DISCOVERY | اكتشاف إجراء الموصل | اختيار إجراء connector مطابق لمخطط الرابط أو الخدمة بدل افتراض API. | URL/service context | Connector action |
| F-087 | CONNECTOR_ID_REUSE | إعادة استخدام المعرفات | استخدام document_id/content_location المحصل سابقًا بدل إعادة إرسال الرابط عند دعم ذلك. | connector result | Stable reference |
| F-088 | EXTERNAL_ACTION_CONFIRMATION | تأكيد الأفعال الخارجية | اشتراط تأكيد المستخدم للأفعال المؤثرة عندما يقتضي السياق ذلك. | action + authorization | Authorization gate |
| F-089 | TOOL_SCHEMA_VALIDATOR | التحقق من مخطط الأداة | فحص أسماء الحقول والأنواع قبل الاستدعاء. | tool schema + args | Valid/invalid |
| F-090 | TOOL_RESULT_NORMALIZER | توحيد نتائج الأدوات | تحويل النتائج المختلفة إلى صيغة موحدة يمكن لباقي النظام استخدامها. | raw tool result | Normalized result |
| F-091 | TOOL_TRACE_RECORDER | تسجيل استدعاءات الأدوات | تسجيل الأداة والوسيطات والنتيجة والزمن والحالة دون أسرار غير لازمة. | call event | Trace record |
| F-092 | SOURCE_FRESHNESS_CHECK | فحص حداثة المصدر | تحديد هل المعلومة تحتاج بحثًا حديثًا قبل عرضها. | claim + timestamp | Freshness decision |
| F-093 | SOURCE_AUTHORITY_CHECK | فحص سلطة المصدر | تقييم ملاءمة المصدر لطبيعة الادعاء. | claim + sources | Source quality |
| F-094 | CROSS_SOURCE_RECONCILER | مصالحة المصادر | مقارنة مصادر متعددة وكشف التعارض وعدم دمجها بلا تحقق. | sources[] | Reconciled evidence |
| F-095 | DATA_PROVENANCE_TRACKER | تتبع أصل البيانات | ربط كل عنصر بمصدره ومعالجته وإصداره. | data lineage | Provenance graph |
| F-096 | SCHEMA_MIGRATION_ENGINE | ترحيل المخططات | تحديث مخطط البيانات مع الحفاظ على قابلية القراءة من الإصدارات السابقة. | schema vN→vN+1 | Migration |
| F-097 | CONFIG_RESOLVER | حل الإعدادات | دمج إعدادات النظام والمنتج والمستخدم والمهمة مع أولوية واضحة. | config layers | Resolved config |
| F-098 | FEATURE_FLAG_ENGINE | إدارة الميزات المرحلية | تشغيل/إيقاف وظائف حسب إصدار أو شريحة أو تجربة. | flags + context | Feature state |
| F-099 | AUDIT_EVENT_WRITER | كتابة سجل التدقيق | تسجيل الأفعال المؤثرة ومصدرها والوقت والنتيجة. | action event | Audit record |
| F-100 | INCIDENT_ROUTER | توجيه الحوادث | فتح سجل حادثة وربط الأثر والسبب والإصلاح والتحقق. | incident signals | Incident record |

## 1.1 مبدأ دورة الوظيفة
```

---

### `85/588` `backend/docs/ALI_AI_2.5_FULL_PROJECT_SOURCE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/ALI_AI_2.5_FULL_PROJECT_SOURCE.md`
- **الحجم:** 778 بايت (0.8 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5.0 — Complete Windows Project Source

> Final source snapshot. Binary model weights/databases remain in the ZIP and are not duplicated into Markdown.

## Integrated changes

- Professional light Windows desktop shell based on the supplied UI reference.
- Right rail: Developer Notebook → live Execution Monitor → lower System Health footer.
- Accumulated Markdown training: validation → redaction → dedup → LoRA adapters → threshold merge candidate.
- Phase-2 providers/search/MCP/skills/toolsets/messaging/runtime catalog, disabled by default.
- Bundled functional micro bootstrap model for local startup and inference smoke testing.

## Windows startup

`SETUP.bat` → `RUN-ALL-TESTS.bat` → `RUN-MODEL-SMOKE.bat` → `START.bat`.

## Project tree
```

---

### `86/588` `backend/docs/ARCHITECTURE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/ARCHITECTURE.md`
- **الحجم:** 48 بايت (0.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI — ARCHITECTURE

## نظرة عامة
```

---

### `87/588` `backend/docs/ARCHITECTURE_2.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/ARCHITECTURE_2.0.md`
- **الحجم:** 30 بايت (0.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.0 — Architecture
```

---

### `88/588` `backend/docs/ARCHITECTURE_2.1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/ARCHITECTURE_2.1.md`
- **الحجم:** 66 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.1 — Unified KCA / P50 Architecture

## Control plane
```

---

### `89/588` `backend/docs/ARCHITECTURE_V3.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/ARCHITECTURE_V3.0.md`
- **الحجم:** 1520 بايت (1.5 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI Pro 3.0 Architecture

## Core principle
ALI is trained from scratch. No Ollama, no external base model and no cloud model provider is required for local inference.

## Learning planes
1. **Weights plane**: full training / SFT / LoRA / checkpoints / evaluation / registry.
2. **Knowledge plane**: PDF/MD/DOCX/HTML/archives/web -> chunks -> hybrid retrieval.
3. **Memory plane**: conversations, episodic facts, project memory and provenance.
4. **Agent plane**: inspect -> plan -> snapshot -> apply -> test -> verify -> review.
5. **Extension plane**: skills, plugins, optional MCP and providers.
6. **Media plane**: image/audio/video encoders + trainable projector into ALI hidden space.
7. **Inference plane**: native PyTorch, CPU int8 path, HF export and GGUF bridge.

## Continuous learning identity
Every accepted training sample contributes a deterministic identity. A new candidate can be scheduled only when the accepted dataset identity changes. GGUF exports are keyed by checkpoint identity + dataset identity + quantization mode; repeated identities are skipped.

## Safe self-improvement
The self-manager never edits the program core blindly. Changes follow snapshot/branch, tests and verification. Model promotion is separate from code promotion.

## Hardware target
The default 2GB-VRAM profile uses batch size 1, gradient accumulation, conservative sequence length and CPU fallback. The model size is intentionally small enough for local experimentation; frontier-model equivalence is not assumed.
```

---

### `90/588` `backend/docs/DEVELOPMENT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/DEVELOPMENT.md`
- **الحجم:** 50 بايت (0.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI — DEVELOPMENT GUIDE

## الإعداد
```

---

### `91/588` `backend/docs/HARDWARE_P50.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/HARDWARE_P50.md`
- **الحجم:** 939 بايت (0.9 KB)
- **الامتداد:** `.md`

```markdown
# ThinkPad P50 target profile — ALI AI 2.1

Target class supplied for this project:

- Lenovo ThinkPad P50
- Intel Core i7-6820HQ, 4 physical / 8 logical threads
- 32 GB DDR4 RAM
- NVIDIA Quadro M1000M, 2 GB VRAM, legacy Maxwell-class capability
- Full HD 1920×1080 display
- NVMe system/storage tier plus 2 TB SATA archive tier

## Runtime policy

- Training: CPU-first
- Torch threads: 6
- Inter-op threads: 1
- Batch: 1
- Gradient accumulation: 16
- Sequence length: 256
- Inference context: 384
- New tokens: 192
- AMP: disabled
- Bootstrap: `micro`
- Local research: `small`

## Storage

Prefer the fast NVMe data partition for active checkpoints/models/datasets. Use the HDD for archive workloads. The project falls back to the actual project directory when the preferred drive is unavailable.

## Privacy

Machine-unique identifiers supplied during diagnostics are not embedded in the source bundle or default hardware profile.

```

---

### `92/588` `backend/docs/HERMES_INTEGRATION.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/HERMES_INTEGRATION.md`
- **الحجم:** 819 بايت (0.8 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5 + Hermes Integration Revision 2.6 — Hermes Integration

## Independence
ALI AI remains independently runnable. Hermes is an external system.

## External root
`D:\AI ALI\Hermes\`

## Read-only boundary
Allowed: `SOUL.md`, `memories/*.md`, `skills/**/SKILL.md`, `skills/.bundled_manifest`, `config.yaml`, `projects.db`, `kanban.db` (SELECT/PRAGMA only).
Blocked: `.env`, `auth.json`, credentials, keys, certificates and anything outside the root.

## Routing
ALI consults Hermes context only when a request contains a deterministic Hermes-related intent. Otherwise the ALI-local memory/RAG path remains unchanged.

## Phase-2 API/MCP
The repository contains interfaces for later API/MCP wiring, but no undocumented Hermes endpoint is fabricated. Set the actual endpoint/protocol only after confirming it.
```

---

### `93/588` `backend/docs/KNOWLEDGE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/KNOWLEDGE.md`
- **الحجم:** 1850 بايت (1.8 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI — Knowledge Base

Project-specific knowledge accumulated during development.
Updated: 30 September 2026 (V0.7.2 audit)

---

## Architecture Decisions

### Word Boundary Contract (Option A)

**Decision:** `</w>` is internal BPE representation, NEVER in decoded text.

**Rationale:**
- BPE training uses `</w>` to mark word boundaries (GPT-2 style)
- After encode→decode round-trip, `</w>` is stripped
- This is documented and tested

**Evidence:** `tokenizer/tokenizer.py:24-29` (docstring), 13/13 round-trip tests pass.

---

### Special Tokens Case Insensitivity

**Decision:** When `lowercase_english=True` (default), special tokens are matched case-insensitively.

**Behavior:**
- `<USER>`, `<user>`, `<User>`, `<UsEr>` all → `[user_id]`
- `<UNKNOWN>`, `<USER123>` → bytes (NOT special)

**Evidence:** `tests/test_tokenizer_v072.py::TestSpecialTokensReal`

---

### Byte Fallback for Lossless Decoding

**Decision:** When BPE produces a token not in vocab, decompose it to its constituent byte tokens.

**Rationale:**
- Guarantees byte-level losslessness for any Unicode input
- Trade-off: word-boundary metadata is lost in fallback
- This is the only way to handle unseen text without corpus-specific vocab

**Evidence:** `tokenizer/tokenizer.py::_byte_fallback`, 18/18 unseen texts round-trip losslessly.

---

### Manifest-Based Integrity

**Decision:** All artifact integrity verified through `manifest.json` with SHA-256 hashes.

**Behavior:**
- `config.json`, `vocab.json`, `merges.txt` are hashed on save
- `manifest.json` records hashes + metadata (version, algorithm, counts)
- `load_tokenizer()` rejects artifact if any hash mismatches

**Evidence:** `tokenizer/serialization.py::_validate_tokenizer`, 4/4 corruption scenarios rejected.

---

## Tokenizer Bug Fixes (V0.7.2 Audit)

### Dead Imports Removed

**Before:**
```

---

### `94/588` `backend/docs/OPERATIONS_2.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/OPERATIONS_2.0.md`
- **الحجم:** 1788 بايت (1.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.0 — Operations Guide

## أول دورة تشغيل

1. `SETUP.bat`
2. `START.bat`
3. افتح **Knowledge** واختر مجلد البيانات.
4. راجع نتائج Harvest.
5. افتح **Dataset Review** واعتمد العينات التي تريد تدريبها.
6. افتح **Training** واختر `chat` للمحادثات أو `causal` للمعرفة النصية.
7. شغّل التدريب.
8. افحص المرشح في **Models**.
9. نفّذ Evaluation + Regression.
10. Promote فقط للمرشح الذي يمر بالبوابة.

## تدريب مستمر

كل checkpoint مستقل ويحتفظ بحالة optimizer/scheduler/RNG. لاستمرار التدريب استخدم مسار checkpoint نفسه مع `--resume`.

## التعلم من الكتب والوثائق

الوثائق العادية تدخل Knowledge/RAG أولًا. لا يصبح الكتاب تلقائيًا أوزانًا. عندما تكون هناك بيانات كافية يتم بناء Dataset تدريب من المصادر المقبولة، ثم التدريب والتقييم.

## Web Research

يُفعّل من System. البحث الشبكي لا يُنفّذ في الوضع Offline. عند تفعيله يستطيع ALI حفظ المصادر المفيدة في Knowledge Store.

## إدارة الذاكرة

- 2 GB VRAM: profile محافظ.
- batch 1.
- gradient accumulation مرتفع.
- sequence length منخفض نسبيًا.
- gradient checkpointing.
- CPU fallback إذا لم تتوفر CUDA.

## الاسترداد

عند توقف التدريب لا تحذف checkpoint. أعد التشغيل من `--resume`، وسيتم استعادة الحالة المحفوظة.

## GGUF

ضع llama.cpp محليًا في `vendor/llama.cpp` ثم استخدم:
```

---

### `95/588` `backend/docs/PROJECT_AUDIT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/PROJECT_AUDIT.md`
- **الحجم:** 1777 بايت (1.7 KB)
- **الامتداد:** `.md`

```markdown
# PROJECT AUDIT — ALI Studio

**تاريخ التقرير**: 29 سبتمبر 2026
**الحالة**: مرحلة الاكتشاف (Discovery). لا إعادة بناء حتى الآن.
**المرجع الرسمي**: `D:\AI\ALI\ali_agent.py` (سيُنشأ من `D:\AI\1\المشروع لونفا  ذكا اون لاين\ali_agent.py` بعد إزالة Lovable).

---

## 1. الهدف من هذا التقرير

توثيق دقيق وحقيقي لحالة مشروع ALI Studio اليوم:

- ما الملفات الموجودة فعلياً (تم التحقق منها عبر `terminal` و`read_file`).
- ما الذي يعمل الآن.
- ما الذي ينقص.
- أين ارتباط Lovable وكيف سيتم إزالته.
- ما الذي يجب الحفاظ عليه (الواجهة كاملة).
- ما الذي يجب بناؤه (Model/Tokenizer/Training/Inference/Database/Memory/Tools/Skills/Permissions/Automations/Security).
- المخاطر والقرارات الهندسية.
- المهمة التالية المقترحة فقط.

---

## 2. الجرد الفعلي للمشروع

### 2.1 نقطة البداية الرسمية (الواجهة)

| العنصر | المسار | الحالة |
|---|---|---|
| **الكود المرجعي للنسخ** | `D:\AI\1\المشروع لونفا  ذكا اون لاين\ali_agent.py` | ✅ 1058 سطر، يعمل |
| **الواجهة الحالية للنشر** | `D:\AI\ALI\ui_offline.py` | ✅ 628 سطر، echo فقط |
| **نسخة PySide6 بديلة** | `D:\AI\2\ALI-Desktop\ali_desktop.py` | ✅ 1996 سطر، 12 أداة + permissions |

> **القرار**: نبدأ من `ali_agent.py` (tkinter). لن ننقل الواجهة إلى framework آخر.

### 2.2 ملفات `D:\AI\ALI\` (المجلد الرسمي)
```

---

### `96/588` `backend/docs/PROJECT_CONTRACT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/PROJECT_CONTRACT.md`
- **الحجم:** 1407 بايت (1.4 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI Project Contract

1. Data is not weights.
2. A checkpoint is not a promoted model.
3. A GGUF file is valid only after conversion and validation.
4. Internet material is knowledge first; it becomes training data only after provenance, cleaning, deduplication and review.
5. Tool execution always passes through PermissionManager and AuditLog.
6. Candidate models pass evaluation before promotion.
7. Recovery uses checkpoints; destructive actions are never the default.
8. Device policy chooses safe defaults; explicit advanced overrides remain possible.
9. Scale profiles describe architecture targets; they do not claim a laptop can train every target.
10. Every training run should record dataset identity, config, code version, metrics and artifact hashes.
11. Every complex request may be represented as KCA state: intent, goal, candidate actions, observation, verification and recovery.
12. The 100-function KCA registry is metadata/capability architecture, not an assertion that every function is an external tool.
13. Structured KCA traces may be trained only from approved/redacted records; private reasoning text is never exported.


11. Autonomous learning consumes only approved, deduplicated high-quality samples and never promotes a candidate without evaluation and regression gates.
12. Failed autonomous training never advances the trained-data cursor; failed runs remain retryable.
```

---

### `97/588` `backend/docs/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/README.md`
- **الحجم:** 326 بايت (0.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Documentation

`ARCHITECTURE_2.0.md` describes the current system. Files named `V0.*` are historical reports from the original development stages.

The current release deliberately removes the old NumPy-only/fake-weight generator. The active training path is `model/ali_lm.py` + `training/` + `tokenizer/spm.py`.
```

---

### `98/588` `backend/docs/REFERENCES.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/REFERENCES.md`
- **الحجم:** 372 بايت (0.4 KB)
- **الامتداد:** `.md`

```markdown
# External technical references

- llama.cpp server and Windows usage: GitHub repository `ggml-org/llama.cpp`, `tools/server/README.md`.
- Hugging Face PEFT / LoRA documentation.

The application keeps the llama.cpp integration optional: the local desktop can operate without a vendor checkout, while GGUF conversion/server features use a local installation when present.
```

---

### `99/588` `backend/docs/RELEASE_NOTES.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/RELEASE_NOTES.md`
- **الحجم:** 954 بايت (0.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.1.0 — Unified KCA / P50

## 2.1.0 changes

- Integrated the uploaded AI-KCA 3.0 operational architecture as a real control-plane layer.
- Added a source-derived 100-function registry with stable IDs and contracts.
- Added typed request/state/plan/trace contracts and deterministic routing.
- Added SQLite KCA operation/state persistence.
- Added KCA-enriched conversation dataset generation with deduplication, provenance and secret redaction.
- Made model/training services lazy in the desktop UI.
- Added cached/lazy hardware probing and explicit P50 CPU-first policy.
- Hardened GGUF artifact inspection so arbitrary `.gguf` files are not accepted as valid.
- Preserved progressive `base → sft → lora → merged` lifecycle and candidate/promotion gates from 2.0.

## Verification target

The project is designed so source compilation, unit/regression tests, KCA registry checks and artifact validation are run before release claims.

```

---

### `100/588` `backend/docs/ROADMAP.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/ROADMAP.md`
- **الحجم:** 1278 بايت (1.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.0 — Roadmap

## Delivered in the 2.1 control plane
- Professional three-pane desktop UI with local chat and streaming
- Persistent SQLite conversation sessions
- Central artifact lifecycle: inbox → inspect → install → verify → registry
- Versioned TokenizerManager with corpus hashing and reuse
- Progressive base → SFT → LoRA training pipeline
- LoRA adapter + merged-model export path
- Evaluation and promotion gate integration
- Explicit lineage and SHA-256 manifests
- Resume-safe checkpoints and CUDA DDP entry path
- CLI parity for training and artifact management
- P50-safe CPU-first defaults
- Autonomous incremental self-learning with candidate evaluation/promotion gate
- Bootstrap + P50 datasets included in the source bundle

## Next engineering stages
- stronger intent classifier and learned tool selection
- richer tool-call planning/replanning with structured traces
- benchmark suites by Arabic/English domain and task family
- multi-node job launcher and cluster artifact synchronization
- longer-context training experiments
- multimodal document/image/audio datasets
- online research → source review → training-candidate scheduler

The desktop product contract remains stable while these capabilities are added underneath it.
```

---

### `101/588` `backend/docs/TOKENIZER.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/TOKENIZER.md`
- **الحجم:** 203 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI Tokenizer (V0.7.2 — Final Contract)

Tokenizer BPE مستقل، مكتوب من الصفر بـ Python خالص، بدون أي نموذج خارجي.

## Public API (V0.7.2 — stable contract)
```

---

### `102/588` `backend/docs/UI_2.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/UI_2.0.md`
- **الحجم:** 141 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.0 — Desktop UI Contract

The desktop application is a control plane, not the location of model logic.

### Three-pane workspace
```

---

### `103/588` `backend/docs/UI_2.4.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/UI_2.4.md`
- **الحجم:** 2654 بايت (2.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.4 — Professional Assistant UI Contract

## Visual target

The desktop shell follows the supplied `ali_agent_ui.py` reference rather than reproducing its placeholder-only behavior. The target is a clean Windows workstation layout with:

- white main surface;
- light-gray navigation rail;
- thin dividers;
- restrained blue action/status accent;
- green/red/amber semantic status colors;
- Segoe UI;