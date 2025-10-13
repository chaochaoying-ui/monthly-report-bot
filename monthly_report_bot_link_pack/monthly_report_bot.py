#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月报机器人（链接版 23 日逻辑）— v1.2 2025-08-14
--------------------------------
- 17 日：从 tasks.yaml 创建任务 + 群内分工卡片
- 18–22 日：统计进度，群里发布进度卡片，并私聊未完成责任人
- 23 日：不导出 PDF，直接在群里推送 **文件链接 + 最终提醒**

依赖： pip install requests pyyaml pytz

必填环境变量：
  APP_ID, APP_SECRET   —— 应用凭证
  CHAT_ID              —— 群 ID（oc_...）

可选环境变量：
  FILE_URL             —— 23 日群里推送的文件链接（如 /file/ 开头的原件地址，或任意可访问链接）
  TZ                   —— 默认 America/Argentina/Buenos_Aires
  TASKS_FILE           —— 默认 ./tasks.yaml
  STATE_FILE           —— 默认 ./.tasks_state.json
"""

from __future__ import annotations
import os, time, json, math, datetime, logging, sys
from typing import Dict, List, Tuple
import requests, yaml, pytz

# 打印调试信息
print("="*50)
print("Python 版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("环境变量:")
for key in ["APP_ID", "APP_SECRET", "CHAT_ID", "FILE_URL", "TZ"]:
    print(f"  {key}: {os.environ.get(key, '未设置')}")
print("="*50)

FEISHU = "https://open.feishu.cn/open-apis"

APP_ID     = os.environ.get("APP_ID", "").strip()
APP_SECRET = os.environ.get("APP_SECRET", "").strip()
CHAT_ID    = os.environ.get("CHAT_ID", "").strip()
FILE_URL   = os.environ.get("FILE_URL", "").strip()
TZ_NAME    = os.environ.get("TZ", "America/Argentina/Buenos_Aires")
TZ         = pytz.timezone(TZ_NAME)

# 使用绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, os.environ.get("TASKS_FILE", "tasks.yaml"))
STATE_FILE = os.path.join(BASE_DIR, os.environ.get("STATE_FILE", ".tasks_state.json"))
REQUEST_TIMEOUT = 10

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # 确保日志输出到控制台
    ]
)

# ---------------------------
# 工具函数
# ---------------------------

def tenant_token() -> str:
    """获取租户访问令牌（tenant_access_token）"""
    url = f"{FEISHU}/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}

    logging.info("请求租户令牌: URL=%s, app_id=%s", url, APP_ID)

    try:
        r = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        logging.info("获取租户令牌响应 code=%s", data.get("code"))
        if data.get("code", 0) != 0:
            raise RuntimeError(f"获取租户令牌失败: {data.get('msg')} (code={data.get('code')})")

        # 兼容两种返回结构
        return data.get("tenant_access_token") or data.get("data", {}).get("tenant_access_token", "")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"网络请求失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"处理响应失败: {str(e)}")


def validate_env_vars() -> list:
    """验证环境变量有效性（不过度卡死长度，避免误判）"""
    errors = []
    if not APP_ID:
        errors.append("APP_ID 未设置")
    elif not APP_ID.startswith("cli_"):
        errors.append(f"APP_ID 格式无效: '{APP_ID}' (应以 cli_ 开头)")

    if not APP_SECRET:
        errors.append("APP_SECRET 未设置")

    if not CHAT_ID:
        errors.append("CHAT_ID 未设置")
    elif not CHAT_ID.startswith("oc_"):
        errors.append(f"CHAT_ID 格式无效: '{CHAT_ID}' (应以 oc_ 开头)")

    return errors


def api_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


def send_group_text(token: str, text: str):
    """向群聊发送文本消息（IM v1）"""
    url = f"{FEISHU}/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    content = json.dumps({"text": text}, ensure_ascii=False)
    payload = {"receive_id": CHAT_ID, "msg_type": "text", "content": content}
    r = requests.post(url, params=params, headers=api_headers(token), json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()


def send_group_card(token: str, card: Dict):
    """向群聊发送交互卡片（IM v1，content 传卡片 JSON 字符串）"""
    url = f"{FEISHU}/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    # 飞书卡片发送以 content=卡片JSON字符串 为标准做法
    content = json.dumps(card, ensure_ascii=False)
    payload = {"receive_id": CHAT_ID, "msg_type": "interactive", "content": content}
    r = requests.post(url, params=params, headers=api_headers(token), json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()


def dm_text_by_open_id(token: str, open_id: str, text: str):
    """按 open_id 发送私聊文本消息"""
    url = f"{FEISHU}/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    content = json.dumps({"text": text}, ensure_ascii=False)
    payload = {"receive_id": open_id, "msg_type": "text", "content": content}
    r = requests.post(url, params=params, headers=api_headers(token), json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()


def create_task(token: str, summary: str, assignee_open_id: str, due_ts: int, description: str = "") -> str:
    """
    使用 Tasks v1 创建任务：
    - origin.platform_i18n_name 需要传 **JSON 字符串**
    - due 使用 { time: "秒", timezone, is_all_day }
    - v1 没有 `assignee` 字段；用 collaborator_ids 表达执行者/负责人
    """
    url = f"{FEISHU}/task/v1/tasks"
    params = {"user_id_type": "open_id"}

    origin = {
        "platform_i18n_name": json.dumps({"zh_cn": "月报机器人", "en_us": "Monthly Report Bot"}, ensure_ascii=False),
        "href": {"url": "https://open.feishu.cn/", "title": "月报任务"}
    }

    body = {
        "summary": summary,
        "description": description or "",
        "due": {
            "time": str(int(due_ts)),
            "timezone": TZ_NAME,
            "is_all_day": False
        },
        "origin": origin,
        "can_edit": True,
    }

    if assignee_open_id:
        body["collaborator_ids"] = [assignee_open_id]

    logging.info("创建任务请求体(v1): %s", json.dumps(body, indent=2, ensure_ascii=False))
    r = requests.post(url, params=params, headers=api_headers(token), json=body, timeout=REQUEST_TIMEOUT)
    logging.info("响应状态码: %s", r.status_code)
    logging.info("响应内容: %s", r.text)
    r.raise_for_status()

    data = r.json()
    if data.get("code", 0) != 0:
        raise RuntimeError(f"create task failed: {data}")

    # 兼容两种返回结构
    task_id = (data.get("data", {}).get("task", {}) or {}).get("id") or data.get("data", {}).get("id")
    if not task_id:
        raise RuntimeError(f"no task id in response: {data}")
    return task_id


def get_task(token: str, task_id: str) -> Dict:
    url = f"{FEISHU}/task/v1/tasks/{task_id}"
    params = {"user_id_type": "open_id"}
    r = requests.get(url, params=params, headers=api_headers(token), timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json().get("data", {})  # { "task": {...} }


def is_task_completed(task_detail: Dict) -> bool:
    """
    v1 常见完成判断：
    - data.task.complete_time != "0" 视为完成
    - 兼容存在 status/is_completed 的情况
    """
    task = task_detail.get("task") or task_detail
    status = (task or {}).get("status")
    if status and str(status).lower() in {"done", "completed", "finish", "finished"}:
        return True
    if (task or {}).get("is_completed") is True:
        return True
    complete_time = (task or {}).get("complete_time")
    if complete_time and str(complete_time) != "0":
        return True
    return False


def load_state() -> Dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": []}


def save_state(state: Dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ---------------------------
# 业务流程
# ---------------------------

def run_17_create_and_announce(token: str):
    logging.info("执行17日任务: 创建任务并发送公告")
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            items = yaml.safe_load(f) or []
            if not isinstance(items, list):
                raise ValueError("tasks.yaml 顶层应为列表(list)")
    except Exception as e:
        logging.error("读取任务文件失败: %s", str(e))
        return

    # 到期时间：本月 23 日 23:59:00
    now = datetime.datetime.now(TZ)
    due_dt = now.replace(day=23, hour=23, minute=59, second=0, microsecond=0)
    # 若今天>23，防止越月错误，顺延到下月 23
    if now.day > 23:
        # 到下个月的23号
        month = now.month + 1 if now.month < 12 else 1
        year = now.year if now.month < 12 else now.year + 1
        due_dt = now.replace(year=year, month=month, day=23, hour=23, minute=59, second=0, microsecond=0)

    due_ts = int(due_dt.timestamp())
    logging.info("任务到期时间戳: %s", due_ts)

    state = load_state()
    created_rows = []

    for it in items:
        title = str(it.get("title", "")).strip()
        assignee = str(it.get("assignee_open_id", "") or "").strip()
        doc_url = str(it.get("doc_url", "") or "").strip()
        desc = f"👉 请完善：{doc_url}" if doc_url else ""

        if not title:
            logging.error("任务标题不能为空，已跳过一条")
            continue

        if len(title) > 256:
            logging.warning("任务标题过长(%d字符)，截断为256字符: %s", len(title), title)
            title = title[:256]

        try:
            logging.info("创建任务: '%s' (负责人/执行者 open_id: %s)", title, assignee or "未指定")
            task_id = create_task(token, title, assignee, due_ts, desc)
            created_rows.append({"title": title, "assignee_open_id": assignee, "task_id": task_id})
        except Exception as e:
            logging.error("创建任务失败: %s", str(e))
            continue

    state["tasks"] = created_rows
    save_state(state)

    if not created_rows:
        logging.error("没有创建任何任务")
        return

    rows_md = []
    for row in created_rows:
        mention = f"<at id={row['assignee_open_id']}></at>" if row["assignee_open_id"] else "未指定"
        rows_md.append(f"• **{row['title']}** — {mention}")

    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "📌 本月月报任务已创建（截至 23 日 23:59）"}},
        "elements": [{"tag": "markdown", "content": "\n".join(rows_md)}]
    }

    try:
        send_group_card(token, card)
        logging.info("任务创建完成，公告已发送")
    except Exception as e:
        logging.error("发送卡片失败: %s", str(e))


def collect_progress(token: str) -> Tuple[List[Dict], List[Dict]]:
    state = load_state()
    done, pending = [], []
    for row in state.get("tasks", []):
        try:
            detail = get_task(token, row["task_id"])
            if is_task_completed(detail):
                done.append(row)
            else:
                pending.append(row)
        except Exception as e:
            logging.warning("获取任务 %s 失败: %s", row.get("task_id"), e)
            pending.append(row)
    return done, pending


def run_18_22_remind_and_stats(token: str):
    logging.info("执行18-22日任务: 发送进度提醒")
    done, pending = collect_progress(token)
    total = len(done) + len(pending)
    pct = 0 if total == 0 else math.floor(len(done) * 100 / total)

    list_md = []
    if pending:
        list_md.append("**未完成清单：**")
        for p in pending:
            mention = f"<at id={p.get('assignee_open_id')}></at>" if p.get("assignee_open_id") else "未指定"
            list_md.append(f"- {p['title']} — {mention}")
    else:
        list_md.append("🎉 所有任务已完成")

    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"📊 月报进度 {len(done)}/{total}（{pct}%）"}},
        "elements": [{"tag": "markdown", "content": "\n".join(list_md)}]
    }

    try:
        send_group_card(token, card)
        logging.info("进度卡片已发送")
    except Exception as e:
        logging.error("发送进度卡片失败: %s", str(e))

    # 发送私信提醒
    for p in pending:
        if not p.get("assignee_open_id"):
            continue
        dm = (
            f"📌 月报提醒：\n"
            f"任务《{p['title']}》仍未完成，请在 23 日 23:59 前完成填报。\n"
            f"如已完成请在任务中标记完成。感谢配合！"
        )
        try:
            dm_text_by_open_id(token, p["assignee_open_id"], dm)
            logging.info("已发送私信提醒给: %s", p["assignee_open_id"])
        except Exception as e:
            logging.warning("私信发送失败 %s: %s", p["assignee_open_id"], e)


def run_23_link_and_final(token: str):
    logging.info("执行23日任务: 发送最终链接和提醒")
    link = FILE_URL or os.environ.get("DOC_URL", "").strip()
    if not link:
        send_group_text(token, "⚠️ 未配置 FILE_URL（请设置为 /file/… 或任意可访问的文档链接）。")
        logging.error("未配置 FILE_URL")
        return

    done, pending = collect_progress(token)
    total = len(done) + len(pending)
    pct = 0 if total == 0 else math.floor(len(done) * 100 / total)

    elements = [{
        "tag": "action",
        "actions": [{
            "tag": "button",
            "text": {"tag": "plain_text", "content": "🔗 打开本月月报文件"},
            "url": link,
            "type": "primary"
        }]
    }]

    if pending:
        md = ["**未完成清单（请尽快补齐并在任务中完成）：**"]
        for p in pending:
            mention = f"<at id={p['assignee_open_id']}></at>" if p["assignee_open_id"] else "未指定"
            md.append(f"- {p['title']} — {mention}")
        elements.insert(0, {"tag": "markdown", "content": "\n".join(md)})

    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"📦 月报文件链接（进度 {len(done)}/{total}，{pct}%）"}},
        "elements": elements
    }

    try:
        send_group_card(token, card)
        logging.info("最终链接卡片已发送")
    except Exception as e:
        logging.error("发送最终链接卡片失败: %s", str(e))

    # 发送最后提醒
    for p in pending:
        if not p.get("assignee_open_id"):
            continue
        dm = (
            f"⏰ 最后提醒：月报任务《{p['title']}》尚未完成，"
            f"请于今日 23:59 前完成并在任务中标记完成。"
        )
        try:
            dm_text_by_open_id(token, p["assignee_open_id"], dm)
            logging.info("已发送最后提醒给: %s", p["assignee_open_id"])
        except Exception as e:
            logging.warning("最后提醒发送失败 %s: %s", p["assignee_open_id"], e)

# ---------------------------
# 入口
# ---------------------------

def main():
    logging.info("="*50)
    logging.info("开始执行月报机器人")
    
    # 验证环境变量
    env_errors = validate_env_vars()
    if env_errors:
        for error in env_errors:
            logging.error(error)
        logging.error("环境变量验证失败，脚本终止")
        return

    # 当前日期
    now = datetime.datetime.now(TZ)
    day = now.day
    logging.info("当前日期: %s, %s日", now.strftime("%Y-%m-%d %H:%M:%S"), day)

    # 获取访问令牌
    try:
        token = tenant_token()
        if not token:
            logging.error("获取的令牌为空")
            return
        logging.info("成功获取飞书访问令牌")
    except Exception as e:
        logging.error("获取飞书访问令牌失败: %s", str(e))
        return

    # 强制启用测试模式
    TEST_MODE = True
    if TEST_MODE:
        logging.info("===== 测试模式激活 =====")
        # 测试17日功能（创建任务+发送卡片）
        logging.info("测试17日功能: 任务创建和公告")
        run_17_create_and_announce(token)

        # 测试18-22日功能
        logging.info("等待10秒后测试18-22日功能...")
        time.sleep(10)
        logging.info("测试18-22日功能: 进度统计和提醒")
        run_18_22_remind_and_stats(token)

        # 测试23日功能
        logging.info("等待10秒后测试23日功能...")
        time.sleep(10)
        logging.info("测试23日功能: 最终链接和提醒")
        run_23_link_and_final(token)

        logging.info("测试完成！请检查测试群消息")
        return

    # ... 正常逻辑 ...


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("程序发生未捕获异常")
        print(f"发生错误: {str(e)}")
    finally:
        print("="*50)
        print("程序执行完毕")
        input("按 Enter 键退出...")
        