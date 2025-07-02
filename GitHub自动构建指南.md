# 🌐 GitHub Actions 自动构建指南

## 🎯 概述

你的项目已经配置了 GitHub Actions，可以在 GitHub 服务器上自动构建 **Linux**、**macOS** 和 **Windows** 的可执行程序。

## 🚀 三种触发方式

### 1. 自动触发（推荐）

#### 方式 A: 推送代码到主分支
```bash
git add .
git commit -m "更新代码"
git push origin main    # 或 master
```
**结果**: 自动开始构建，使用 `.env` 文件中的版本号

#### 方式 B: 推送版本标签
```bash
# 创建并推送 tag
git tag v1.11.04
git push origin v1.11.04
```
**结果**: 自动开始构建，使用 tag 中的版本号

### 2. 手动触发

在 GitHub 网站上手动启动构建：

1. 进入你的 GitHub 仓库
2. 点击 **Actions** 标签页  
3. 选择 **Build Executables** 工作流
4. 点击 **Run workflow** 按钮
5. 选择版本来源：
   - **Use version from .env file**: 使用 `.env` 文件中的版本
   - **Manual version**: 手动输入版本号
6. 点击 **Run workflow** 开始构建

### 3. 发布触发

创建 GitHub Release 时自动触发构建。

## 📁 构建结果

### 自动生成的文件

构建完成后，会在 **Releases** 页面自动创建发布，包含：

- `CursorFreeVIP_{version}_windows.exe` - Windows 可执行文件
- `CursorFreeVIP_{version}_mac_arm64` - macOS Apple Silicon 版本
- `CursorFreeVIP_{version}_mac_intel` - macOS Intel 版本  
- `CursorFreeVIP_{version}_linux_x64` - Linux x64 版本
- `CursorFreeVIP_{version}_linux_arm64` - Linux ARM64 版本

### 文件校验

每个文件都包含 SHA256 校验和，确保下载完整性。

## 🔍 查看构建状态

### 实时监控
1. 访问仓库的 **Actions** 页面
2. 查看运行中的工作流
3. 点击具体任务查看详细日志

### 构建时间
- **总时间**: 约 15-25 分钟
- **Windows**: ~5 分钟
- **macOS**: ~8 分钟  
- **Linux**: ~7 分钟

### 构建状态标识
- 🔄 **Running** - 正在构建
- ✅ **Success** - 构建成功
- ❌ **Failed** - 构建失败
- ⏹️ **Cancelled** - 已取消

## ⚙️ 配置说明

### 版本号管理

编辑 `.env` 文件设置版本：
```
VERSION=1.11.03
```

### 触发条件

**自动触发文件变更时忽略**：
- Markdown 文件 (`*.md`)
- `.gitignore` 文件  
- `LICENSE` 文件

### 构建平台

| 平台 | 运行环境 | 架构 | Python 版本 |
|------|----------|------|-------------|
| Windows | `windows-latest` | x64 | 3.11 |
| macOS ARM | `macos-latest` | arm64 | 3.11 |
| macOS Intel | `macos-latest` | x86_64 | 3.11 |
| Linux x64 | `ubuntu-22.04` | x64 | 3.11 |
| Linux ARM64 | `ubuntu-latest` + Docker | arm64 | 3.11 |

## 🛠️ 故障排除

### 常见问题

#### 构建失败
1. **检查版本号**: 确保 `.env` 文件中版本号格式正确
2. **检查依赖**: 确保 `requirements.txt` 包含所有必要依赖
3. **查看日志**: 在 Actions 页面查看详细错误信息

#### 缺少 Release
- 确保 `CHANGELOG.md` 包含对应版本的更新说明
- 检查版本号格式是否正确

#### 权限问题
- 确保仓库有 **Write** 权限
- 检查 `GITHUB_TOKEN` 权限

### 高级调试

1. **Fork 仓库测试**: 在自己的 fork 中测试构建
2. **本地验证**: 使用本地构建脚本验证代码
3. **依赖更新**: 更新 `requirements.txt` 中的包版本

## 🎁 使用构建结果

### 下载文件

1. 进入仓库的 **Releases** 页面
2. 找到对应版本的发布
3. 下载需要的平台文件

### 验证文件完整性

```bash
# Linux/macOS
sha256sum CursorFreeVIP_1.11.03_linux_x64

# Windows (PowerShell)
Get-FileHash CursorFreeVIP_1.11.03_windows.exe -Algorithm SHA256
```

### 运行程序

**Linux/macOS:**
```bash
chmod +x CursorFreeVIP_1.11.03_linux_x64
./CursorFreeVIP_1.11.03_linux_x64
```

**Windows:**
双击 `.exe` 文件

## 📈 工作流优化

### 加速构建

1. **缓存依赖**: 已启用 pip 缓存
2. **并行构建**: 所有平台同时构建
3. **按需触发**: 忽略文档更改

### 自定义构建

编辑 `.github/workflows/build.yml` 可以：
- 添加新的目标平台
- 修改 Python 版本
- 自定义输出文件名
- 添加额外的构建步骤

## ✨ 最佳实践

### 发布流程

1. **开发阶段**: 在本地使用 `python3 快速构建.py` 测试
2. **测试阶段**: 推送到 GitHub 触发自动构建
3. **发布阶段**: 创建 tag 或 Release 正式发布

### 版本管理

```bash
# 版本号规范：major.minor.patch
VERSION=1.11.03

# 开发版本
VERSION=1.11.03-dev

# 发布候选版本  
VERSION=1.11.03-rc1
```

## 🎉 完成！

现在你的项目具备完整的自动化构建能力：

✅ **自动构建** - 推送代码即可触发  
✅ **多平台支持** - 5 个不同平台和架构  
✅ **自动发布** - 构建完成自动创建 Release  
✅ **文件校验** - SHA256 确保完整性  
✅ **灵活触发** - 支持多种触发方式  

推送你的代码到 GitHub，观看自动构建的魔法吧！ 🪄