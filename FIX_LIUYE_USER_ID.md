# 修复刘野用户ID映射问题

## 问题描述

在飞书卡片中，刘野负责的任务显示为 **"用户(ou_b96c7...)"** 而不是 **"刘野"**。

### 根本原因

配置文件中刘野的 Feishu Open ID 写错了：
- ❌ **错误**：`ou_b96c7**ed**4a604dc049569102d01c6c26d`
- ✅ **正确**：`ou_b96c7**cd**4a604dc049569102d01c6c26d`

注意第8-9个字符的差异：`ed` vs `cd`

### 影响范围

刘野负责的4个月报任务：
1. 月报-工程计划及执行情况
2. 月报-本月其他工作进展-技术管理
3. 月报-存在的问题及措施-总进度滞后方面、各分部工程进度、开工累计产值计划偏差方面
4. 月报-下月工作计划及安排-进度及产值方面

## 修复内容

### 1. tasks.yaml (4处修改)

```yaml
# 修改前
- title: 月报-工程计划及执行情况
  assignee_open_id: ou_b96c7ed4a604dc049569102d01c6c26d  # 刘野

# 修改后
- title: 月报-工程计划及执行情况
  assignee_open_id: ou_b96c7cd4a604dc049569102d01c6c26d  # 刘野
```

其他3处类似修改。

### 2. monthly_report_bot_ws_v1.1.py (1处修改)

```python
# 修改前
USER_ID_MAPPING = {
    # ... 其他用户 ...
    "ou_b96c7ed4a604dc049569102d01c6c26d": "刘野",
    # ... 其他用户 ...
}

# 修改后
USER_ID_MAPPING = {
    # ... 其他用户 ...
    "ou_b96c7cd4a604dc049569102d01c6c26d": "刘野",
    # ... 其他用户 ...
}
```

## 部署方法

### 方法1：自动部署脚本（推荐）

#### Linux/Mac/Git Bash:
```bash
bash deploy_fix_liuye_user_id.sh
```

#### Windows CMD:
```cmd
deploy_fix_liuye_user_id.bat
```

### 方法2：手动部署

```bash
# 1. 连接到服务器
ssh zhangmingbo123@34.125.160.193

# 2. 备份文件
cd ~/monthly-report-bot/monthly_report_bot_link_pack
cp tasks.yaml tasks.yaml.backup
cp monthly_report_bot_ws_v1.1.py monthly_report_bot_ws_v1.1.py.backup

# 3. 编辑 tasks.yaml
nano tasks.yaml
# 查找所有 ou_b96c7ed4a604dc049569102d01c6c26d
# 替换为 ou_b96c7cd4a604dc049569102d01c6c26d
# 应该有4处

# 4. 编辑 monthly_report_bot_ws_v1.1.py
nano monthly_report_bot_ws_v1.1.py
# 在 USER_ID_MAPPING 中查找刘野的条目
# 将 ou_b96c7ed4a604dc049569102d01c6c26d 改为 ou_b96c7cd4a604dc049569102d01c6c26d

# 5. 验证修改
grep "ou_b96c7cd4a604dc049569102d01c6c26d" tasks.yaml
# 应该显示4行

grep "ou_b96c7cd4a604dc049569102d01c6c26d" monthly_report_bot_ws_v1.1.py
# 应该显示1行包含 "刘野"

# 6. 重启机器人
cd ~/monthly-report-bot
pkill -f monthly_report_bot_ws_v1.1.py
sleep 2
cd monthly_report_bot_link_pack
nohup python3 monthly_report_bot_ws_v1.1.py > ../bot.log 2>&1 &

# 7. 检查启动状态
sleep 3
pgrep -f monthly_report_bot_ws_v1.1.py
tail -20 ../bot.log
```

## 验证修复

### 1. 检查配置文件

```bash
# 在服务器上执行
cd ~/monthly-report-bot/monthly_report_bot_link_pack

# 检查 tasks.yaml（应该有4处正确的ID）
grep -n "ou_b96c7cd4a604dc049569102d01c6c26d" tasks.yaml

# 检查 USER_ID_MAPPING（应该有1处）
grep -n "ou_b96c7cd4a604dc049569102d01c6c26d.*刘野" monthly_report_bot_ws_v1.1.py

# 确认没有旧ID残留（应该返回0）
grep -c "ou_b96c7ed4a604dc049569102d01c6c26d" tasks.yaml monthly_report_bot_ws_v1.1.py
```

### 2. 在飞书群中测试

在月报机器人所在的飞书群中发送：
```
@月报收集系统 状态
```

检查返回的卡片：
- ✅ 刘野的任务应该显示 **"<at>刘野</at>"** 而不是 **"用户(ou_b96c7...)"**
- ✅ 应该能正确 @刘野

## 验证清单

- [ ] 配置文件已正确修改（4处 + 1处）
- [ ] 没有旧ID残留
- [ ] 机器人已重启
- [ ] 机器人进程正在运行
- [ ] 日志没有错误
- [ ] 飞书卡片正确显示"刘野"
- [ ] @刘野 功能正常工作

## 其他用户映射验证

使用 `check_mappings.sh` 脚本验证所有用户ID映射：

```bash
bash check_mappings.sh
```

输出应该显示所有15个用户都已正确映射：
```
✅ ou_07443a67428d8741eab5eac851b754b9 -> 范明杰
✅ ou_0bbab538833c35081e8f5c3ef213e17e -> 熊黄平
✅ ou_17b6bee82dd946d92a322cc7dea40eb7 -> 马富凡
✅ ou_2f93cb9407ca5a281a92d1f5a72fdf7b -> 唐进
✅ ou_33d81ce8839d93132e4417530f60c4a9 -> 高雅慧
✅ ou_3b14801caa065a0074c7d6db8603f288 -> 袁阿虎
✅ ou_50c492f1d2b2ee2107c4e28ab4416732 -> 闵国政
✅ ou_5199fde738bcaedd5fcf4555b0adf7a0 -> 孙建敏
✅ ou_66ef2e056d0425ac560717a8b80395c3 -> 蒲星宇
✅ ou_9847326a1fea8db87079101775bd97a9 -> 王冠群
✅ ou_b96c7cd4a604dc049569102d01c6c26d -> 刘野
✅ ou_c9d7859417eb0344b310fcff095fa639 -> 李洪蛟
✅ ou_d85dd7bb7625ab3e3f8b129e54934aea -> 何寨
✅ ou_df1bfcd8e72f347c19e127154e7e618b -> 袁龙
✅ ou_f5338c49049621c36310e2215204d0be -> 景晓东
```

## 技术细节

### Feishu Open ID 格式

飞书的 Open ID 是一个固定长度的字符串：
- 格式：`ou_` + 32个十六进制字符
- 示例：`ou_b96c7cd4a604dc049569102d01c6c26d`
- 特点：区分大小写，每个用户唯一

### 为什么会出现这个问题？

1. **手工录入错误**：Open ID 很长，容易抄错
2. **字符相似**：`c`、`e`、`d` 等字符在某些字体下容易混淆
3. **缺少验证**：没有自动验证机制检查ID是否正确

### 预防措施

1. **使用API获取**：通过飞书API自动获取用户Open ID
2. **双重验证**：录入后立即测试
3. **定期检查**：使用脚本定期验证所有映射
4. **版本控制**：所有配置文件纳入Git版本控制

## 相关文件

- `tasks.yaml` - 任务配置文件
- `monthly_report_bot_ws_v1.1.py` - 机器人主程序（包含USER_ID_MAPPING）
- `check_mappings.sh` - 用户ID映射检查脚本
- `deploy_fix_liuye_user_id.sh` - 自动部署脚本（Linux/Mac/Git Bash）
- `deploy_fix_liuye_user_id.bat` - 自动部署脚本（Windows）

## 更新日志

- **2025-12-17**: 修复刘野的用户ID映射问题
  - tasks.yaml: 4处修改
  - monthly_report_bot_ws_v1.1.py: 1处修改
  - 验证所有15个用户映射正确
