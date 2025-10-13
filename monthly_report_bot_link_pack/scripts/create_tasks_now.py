import os
import sys
import asyncio
from pathlib import Path

# 确保可从项目根目录导入主模块
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import monthly_report_bot_final_interactive as m


async def main() -> int:
    errors = m.validate_env_vars()
    if errors:
        print("ENV_ERRORS:", errors)
        return 2

    if not m.init_lark_client():
        print("INIT_FAIL")
        return 3

    ok = await m.create_tasks()
    print("CREATE_TASKS:", ok)
    if ok:
        try:
            card = m.build_task_creation_card()
            await m.send_card_to_chat(card)
            print("SEND_CARD: OK")
        except Exception as e:
            print("SEND_CARD_FAIL:", e)
    return 0 if ok else 4


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except Exception as e:
        print("FATAL:", e)
        exit_code = 5
    sys.exit(exit_code)


