# PWM — Password Manager CLI

一个安全的本地命令行密码管理工具，使用 AES-256-GCM 加密存储你的账号和密码。

## 安全特性

- **AES-256-GCM** 认证加密 — 防止数据篡改
- **PBKDF2-SHA256** 密钥派生（60万次迭代）— 防暴力破解
- **每次加密使用新随机 nonce** — 防 nonce 重用攻击
- **错误次数限制** — 默认5次失败后锁定10分钟
- **自动锁定** — 默认5分钟无操作自动锁定
- **剪贴板自动清除** — 默认30秒后清除复制的密码
- **加密备份** — 导出文件已加密，明文永不到磁盘

## 安装

### 1. 安装依赖

```bash
pip install cryptography
```

### 2. 安装 PWM

```bash
cd "Password memory"
pip install -e .
```

安装完成后，`pwm` 命令即可在终端中使用。

## 快速上手

### 1. 初始化密码库

```bash
pwm init
```

输入并确认主密码。密码库文件将创建在 `~/.pwm/vault.json`。

### 2. 添加账号

```bash
# 交互式添加
pwm add

# 命令行添加（自动生成密码）
pwm add -s github.com -u myemail@test.com -g

# 命令行添加（手动输入密码）
pwm add -s google.com -u myemail@test.com -p mypassword123
```

### 3. 查看账号

```bash
# 列出所有账号（密码掩码显示）
pwm list

# 按分类筛选
pwm list -c 工作

# 显示密码明文
pwm list --show-passwords
```

### 4. 查看详情

```bash
# 查看并自动复制密码到剪贴板（30秒后自动清除）
pwm show github.com
```

### 5. 搜索账号

```bash
# 按服务名或分类搜索
pwm search github

# 仅搜索分类
pwm search 工作 --category-only
```

### 6. 编辑账号

```bash
# 修改用户名
pwm edit github.com -u newemail@test.com

# 生成新密码
pwm edit github.com -g

# 修改分类
pwm edit github.com -c 开发
```

### 7. 删除账号

```bash
pwm delete github.com
# 跳过确认
pwm delete github.com -f
```

### 8. 生成随机密码

```bash
# 默认20位
pwm gen

# 指定长度
pwm gen -l 32

# 易读模式（无歧义字符）
pwm gen -l 16 --easy

# 仅使用字母和数字
pwm gen --no-symbols

# 生成并复制到剪贴板
pwm gen -c
```

### 9. 备份与恢复

```bash
# 导出加密备份
pwm export backup.pwmbackup

# 导入备份（合并模式，跳过重复）
pwm import backup.pwmbackup

# 导入备份（替换模式，覆盖所有账号）
pwm import backup.pwmbackup --replace
```

**注意**：导入时两个密码库必须使用相同的主密码。

### 10. 安全操作

```bash
# 手动锁定
pwm lock

# 修改主密码
pwm changepw
```

### 11. 配置管理

```bash
# 查看配置
pwm config

# 修改自动锁定时间（秒，0 = 关闭）
pwm config --set auto_lock_timeout 600

# 修改剪贴板清除时间（秒，0 = 关闭）
pwm config --set clipboard_clear_timeout 15

# 修改最大错误次数
pwm config --set max_failed_attempts 3

# 修改锁定持续时间（秒）
pwm config --set lockout_duration 1800
```

## 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `auto_lock_timeout` | 300 | 自动锁定超时（秒），0=关闭 |
| `clipboard_clear_timeout` | 30 | 剪贴板清除超时（秒），0=关闭 |
| `max_failed_attempts` | 5 | 锁定前最大错误次数 |
| `lockout_duration` | 600 | 锁定时长（秒） |

## 数据存储

- **位置**: `~/.pwm/vault.json`
- **格式**: 加密的 JSON 文件
- **加密**: AES-256-GCM，每次写入使用新的随机 nonce
- **密钥**: 通过 PBKDF2-SHA256 从主密码派生，60万次迭代

## 安全建议

1. 选择一个强主密码（推荐 12 字符以上，包含大小写字母、数字和符号）
2. 定期导出备份到安全位置
3. 不要与他人分享密码库文件
4. 记住你的主密码 — 没有 "忘记密码" 功能

## 卸载

```bash
pip uninstall pwm
# 密码库文件仍需手动删除
rm ~/.pwm/vault.json
```
