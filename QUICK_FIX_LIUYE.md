# 快速修复刘野用户ID问题

## 问题
飞书卡片显示 **"用户(ou_b96c7...)"** 而不是 **"刘野"**

## 原因
用户ID写错了：`ou_b96c7ed...`（错）应为 `ou_b96c7cd...`（对）

## 一键修复

### Windows用户
```cmd
deploy_fix_liuye_user_id.bat
```

### Linux/Mac/Git Bash用户
```bash
bash deploy_fix_liuye_user_id.sh
```

## 验证

在飞书群发送：
```
@月报收集系统 状态
```

检查刘野的4个任务是否正确显示姓名。

## 完整文档
详见 [FIX_LIUYE_USER_ID.md](FIX_LIUYE_USER_ID.md)
