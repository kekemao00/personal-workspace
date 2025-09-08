# 文件同步服务管理器 v2.0

这是一个功能完整的Python文件同步服务管理器，可以替代批处理脚本，提供更强大的功能和更好的用户体验。

## 🌟 主要特性

- **跨平台支持**: 同时支持Windows和Linux系统
- **服务管理**: 支持系统服务的安装、启动、停止、重启
- **自动同步**: 定时监控源文件变化并自动同步到目标目录
- **日志记录**: 详细的操作日志，支持查看和管理
- **配置管理**: 灵活的配置文件系统，支持在线编辑
- **交互界面**: 友好的菜单式操作界面
- **命令行支持**: 支持命令行参数直接操作

## 📋 系统要求

- Python 3.6+
- Linux系统需要systemd支持（用于服务管理）
- Windows系统支持手动模式运行

## 🚀 快速开始

### 1. 下载和设置权限
```bash
# 赋予执行权限
chmod +x file_sync_service.py
```

### 2. 首次运行
```bash
# 启动交互式菜单
python3 file_sync_service.py
```

### 3. 配置参数
在交互式菜单中选择"编辑配置"，或直接编辑配置文件：
- `SOURCE_DIR`: 源目录路径
- `TARGET_DIR`: 目标目录路径  
- `FILE_NAME`: 要同步的文件名
- `SERVICE_NAME`: 服务名称
- `SYNC_INTERVAL`: 同步检查间隔（秒）

## 📖 使用方法

### 交互式菜单模式
```bash
python3 file_sync_service.py
```
然后按照菜单提示进行操作。

### 命令行模式
```bash
# 安装服务
python3 file_sync_service.py install

# 启动服务
python3 file_sync_service.py start

# 停止服务
python3 file_sync_service.py stop

# 重启服务
python3 file_sync_service.py restart

# 查看状态
python3 file_sync_service.py status

# 查看日志
python3 file_sync_service.py logs

# 卸载服务
python3 file_sync_service.py uninstall
```

## 🔧 配置文件

程序会自动生成 `sync.config` 配置文件，包含以下参数：

```json
{
  "SOURCE_DIR": "AAA",
  "TARGET_DIR": "BBB",
  "FILE_NAME": "file.bin",
  "SERVICE_NAME": "FileSyncService",
  "SERVICE_DISPLAY_NAME": "文件同步服务",
  "SYNC_INTERVAL": 5,
  "RETRY_DELAY": 30
}
```

### 参数说明
- `SOURCE_DIR`: 源文件目录
- `TARGET_DIR`: 目标文件目录
- `FILE_NAME`: 要同步的文件名
- `SERVICE_NAME`: 系统服务名称
- `SERVICE_DISPLAY_NAME`: 服务显示名称
- `SYNC_INTERVAL`: 文件检查间隔（秒）
- `RETRY_DELAY`: 错误重试延迟（秒）

## 📁 文件结构

```
工作目录/
├── file_sync_service.py    # 主程序文件
├── sync.config            # 配置文件
├── sync.pid              # 进程ID文件
└── logs/                 # 日志目录
    └── sync_YYYYMMDD.log # 日志文件
```

## 🔍 功能详解

### 1. 服务管理
- **安装服务**: 在Linux系统上创建systemd服务
- **启动服务**: 启动文件同步服务
- **停止服务**: 停止正在运行的服务
- **重启服务**: 重启服务
- **查看状态**: 显示服务运行状态和配置信息

### 2. 文件同步
- 自动检测源文件变化
- 只在文件更新时进行同步
- 支持文件修改时间比较
- 自动创建目标目录

### 3. 日志管理
- 按日期分类的日志文件
- 详细的操作记录
- 支持日志查看和清空
- 错误信息记录

### 4. 配置管理
- 在线配置编辑
- 配置文件自动保存/加载
- 参数类型自动识别

## ⚠️ 注意事项

1. **权限要求**: 
   - Linux系统安装服务需要root权限
   - 确保对源目录有读权限，对目标目录有写权限

2. **目录路径**:
   - 使用绝对路径避免路径问题
   - 确保目录路径存在且可访问

3. **服务管理**:
   - Linux系统使用systemd管理服务
   - Windows系统使用手动模式运行

4. **文件同步**:
   - 基于文件修改时间进行同步判断
   - 只同步单个指定文件
   - 不支持目录递归同步

## 🐛 故障排除

### 常见问题

1. **服务启动失败**
   - 检查Python路径是否正确
   - 确认配置文件中的目录路径存在
   - 查看日志文件获取详细错误信息

2. **文件同步失败**
   - 检查源文件是否存在
   - 确认目标目录写权限
   - 查看日志了解具体错误

3. **权限问题**
   - 使用sudo运行需要管理员权限的操作
   - 检查文件和目录的访问权限

### 日志查看
```bash
# 查看今天的日志
tail -f logs/sync_$(date +%Y%m%d).log

# 查看服务状态（Linux）
systemctl status filesyncservice
```

## 🔄 升级和维护

### 备份配置
在升级前备份配置文件：
```bash
cp sync.config sync.config.backup
```

### 服务重载
修改配置后重启服务：
```bash
python3 file_sync_service.py restart
```

## 📞 技术支持

如果遇到问题，请：
1. 查看日志文件获取详细信息
2. 检查配置文件格式是否正确
3. 确认系统环境满足要求

---

**版本**: v2.0  
**作者**: Monica  
**更新时间**: 2025-08-07