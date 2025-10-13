# 项目文件审计与结构盘点（V1.1）

## 目的
本文对当前仓库的文件与目录进行盘点，标注入口脚本、日志与测试分布，并给出不破坏现有结构的轻量整理建议参考。本次仅新增文档，不涉及代码与脚本改动。

## 当前结构总览（基于提供的目录快照）
- app/
  - WebSocket 相关：`main_ws.py`、`main_ws_simple.py`、`ws_wrapper.py`
  - 包初始化：`__init__.py`
- scripts/
  - 启动/测试脚本：`start_ws.py`、`start_http_callback.bat`、`start_ws.bat`、`start_ws_test.bat` 等
  - 集成/连通性测试：`test_main_integration.py`、`test_ws_connection.py`、`test_simple_official.py` 等
- docs/
  - 已有指南与总结文档：如 `WS_CONNECTION_SOLUTION.md`、`WEBHOOK_SETUP.md` 等
- 根目录主要文件（节选）：
  - 运行入口与工具：
    - Webhook：`webhook_server.py`、`simple_webhook_server.py`、`simple_public_server.py`
    - 长轮询：`long_polling_bot.py`、`long_polling_handler.py`
    - 官方 SDK/WS：`monthly_report_bot_final.py`、`monthly_report_bot_with_chat.py`、`lark_sdk_handler.py`、`lark_official_handler.py`
    - 诊断/辅助：`diagnose_feishu_config.py`、`check_*` 系列、`send_*` 系列
  - 配置/清单：`requirements_v1_1.txt`、`requirements_ws.txt`、`tasks.yaml`、`natapp.ini`
  - 批处理启动：`start_final.bat`、`start_webhook.bat`、`start_long_polling.bat`
  - 日志与产物（示例）：`*.log`、`created_tasks.json`、`task_stats.json`、`comprehensive_test_results.json`、`test_report_v1_1_*.json`
- tests/
  - 基础测试：`tests/test_basic.py`
- 根目录测试脚本（与 scripts/ 下存在重名前缀）
  - 如：`test_webhook.py`、`test_long_polling.py`、`test_message_reply.py`、`test_welcome_card.py` 等

## 入口与运行方式（归纳）
- WebSocket（官方/自研包装）
  - 入口：`app/main_ws.py`、`app/main_ws_simple.py`、`app/ws_wrapper.py`、根目录的 `start_ws.py`、`scripts/start_ws.py`
- HTTP Callback（Webhook）
  - 入口：`webhook_server.py`、`simple_webhook_server.py`、`simple_public_server.py`、`scripts/start_http_callback.py/.bat`
- 长轮询
  - 入口：`long_polling_bot.py`、`start_long_polling.bat`
- 官方 SDK 直连
  - 入口：`scripts/start_official_ws.py/.bat` 及 `monthly_report_bot_official_backup.py` 等

## 日志与产物分布（现状）
- 日志：`*.log`（示例：`monthly_report_bot_final.log`、`long_polling_bot.log`、`webhook_server.log`、`event_subscription.log` 等）
- 数据/中间结果：`created_tasks.json`、`task_stats.json`
- 报表/测试产物：`comprehensive_test_results.json`、`test_report_v1_1_*.json`

问题与影响：
- 日志、报表、数据文件与代码混放在仓库根目录，目录视觉噪声较高，且容易被误纳入版本控制或被工具误清理。
- scripts/ 与根目录同时存在以 `test_*.py` 命名的测试脚本，可能被 `pytest` 重复发现或造成歧义。

## 测试与工具（概览）
- 测试分布：
  - 单测：`tests/test_basic.py`
  - 其他测试与集成脚本：根目录与 `scripts/` 目录下大量 `test_*.py`
- 命名约定：已存在的测试多以 `test_*.py` 形式，易被 `pytest` 自动发现。

## 轻量整理建议（保持兼容，后续可逐步落地）
1) 引入输出目录分层（不移动代码）：
   - 建议新增但暂不强制使用的目录：`logs/`、`reports/`、`data/`
   - 日志统一输出到 `logs/`；报表/测试结果输出到 `reports/`；运行产生的 JSON 数据输出到 `data/`
2) 避免测试重名与误发现：
   - `scripts/` 中用于人工/集成触发的脚本建议去除 `test_` 前缀（如改为 `run_*.py`），避免被 `pytest` 作为测试收集
3) 依赖清单统一：
   - 评估 `requirements_v1_1.txt` 与 `requirements_ws.txt` 的差异，沉淀主清单（如 `requirements.txt`）并在 README 标注差异化安装方式

以上为建议方向，后续变更可分批、小步实施，以确保现有流程零中断。

## 回滚
本次仅新增文档，无需回滚代码。若需撤销，删除本文件即可。













