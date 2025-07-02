# 快速开始指南 - 多平台构建

## 🚀 新的构建方式

您的项目现在有两套构建系统：

### 1. 原有构建系统（继续可用）
- `build.py` - 原有的Python构建脚本
- `build.bat` - Windows批处理脚本
- `build.sh` - Linux shell脚本  
- `build.mac.command` - macOS脚本

### 2. 新的统一构建系统（推荐）
- `build_universal.py` - 统一的多平台构建脚本
- `build.config.json` - 构建配置文件
- `Dockerfile.build` - Docker容器构建环境

## 📋 使用新的构建系统

### 列出支持的平台
```bash
python build_universal.py --list
```

输出示例：
```
支持的平台和架构:
  windows: x86_64 (.exe)
  linux: x86_64, arm64 (无扩展名)
  darwin: x86_64, arm64 (无扩展名)
```

### 构建当前平台
```bash
# 自动检测当前平台并构建
python build_universal.py
```

### 构建指定平台
```bash
# 构建Linux x64
python build_universal.py --platform linux --arch x86_64

# 构建Windows
python build_universal.py --platform windows --arch x86_64

# 构建macOS ARM64
python build_universal.py --platform darwin --arch arm64
```

### 构建所有支持的平台
```bash
python build_universal.py --all
```

### 详细输出模式
```bash
python build_universal.py --verbose
```

## 🔧 配置自定义

编辑 `build.config.json` 来自定义构建配置：

```json
{
  "platforms": {
    "linux": {
      "architectures": ["x86_64", "arm64", "arm32"],
      "docker_images": {
        "arm32": "arm32v7/python:3.10-slim"
      }
    }
  },
  "output": {
    "naming_convention": "MyApp_{version}_{platform}_{arch}",
    "compression": true
  }
}
```

## 🐳 Docker构建

### 构建Docker镜像
```bash
docker build -f Dockerfile.build -t cursor-build .
```

### 使用Docker容器构建
```bash
# 构建当前平台
docker run --rm -v $(pwd):/app -w /app cursor-build

# 构建指定平台
docker run --rm -v $(pwd):/app -w /app cursor-build python build_universal.py --platform linux --arch arm64
```

## 📦 构建输出

构建完成后，文件将保存在 `dist/` 目录：

```
dist/
├── CursorFreeVIP_1.0.0_linux_x86_64
├── CursorFreeVIP_1.0.0_linux_arm64
├── CursorFreeVIP_1.0.0_windows_x86_64.exe
├── CursorFreeVIP_1.0.0_darwin_x86_64
├── CursorFreeVIP_1.0.0_darwin_arm64
└── checksums.txt                    # SHA256校验和
```

## ⚡ 快速构建命令

### 本地开发构建
```bash
# 快速构建当前平台
python build_universal.py

# 构建并查看详细信息
python build_universal.py --verbose
```

### CI/CD构建
```bash
# 构建所有平台（适用于CI环境）
python build_universal.py --all --verbose
```

### 交叉编译构建
```bash
# 在Linux上构建ARM64版本
python build_universal.py --platform linux --arch arm64

# 在Linux上构建Windows版本（需要Docker）
python build_universal.py --platform windows --arch x86_64
```

## 🛠️ 常见用法

### 开发调试
```bash
# 构建当前平台，不清理构建目录
python build_universal.py --no-clean --verbose
```

### 发布准备
```bash
# 构建所有平台并生成校验和
python build_universal.py --all
```

### 特定平台测试
```bash
# 只构建Linux ARM64版本
python build_universal.py --platform linux --arch arm64
```

## 🔍 故障排除

### 1. Docker未安装
如果需要交叉编译但Docker未安装：
```bash
# Ubuntu/Debian
sudo apt install docker.io

# macOS
brew install docker

# Windows
# 下载Docker Desktop
```

### 2. 权限问题
```bash
# 添加执行权限
chmod +x build_universal.py

# Docker权限问题
sudo usermod -aG docker $USER
# 注销并重新登录
```

### 3. 依赖缺失
```bash
# 安装Python依赖
pip install -r requirements.txt
pip install pyinstaller

# 安装系统依赖（Linux）
sudo apt-get install build-essential
```

## 🚀 GitHub Actions自动构建

项目已配置GitHub Actions自动构建，支持：
- ✅ Windows x64
- ✅ macOS Intel
- ✅ macOS ARM64 
- ✅ Linux x64
- ✅ Linux ARM64

触发方式：
1. 手动触发：GitHub Actions页面 → "Build Executables" → "Run workflow"
2. 推送标签：`git tag v1.0.0 && git push origin v1.0.0`

## 💡 最佳实践

### 本地开发
```bash
# 1. 日常开发构建
python build_universal.py --verbose

# 2. 测试多平台兼容性
python build_universal.py --all

# 3. 快速验证
python build_universal.py --no-clean
```

### 发布流程
```bash
# 1. 更新版本号
echo "VERSION=1.2.0" > .env

# 2. 构建所有平台
python build_universal.py --all --verbose

# 3. 验证输出文件
ls -la dist/
cat dist/checksums.txt

# 4. 推送并创建release
git add .
git commit -m "Release v1.2.0"
git tag v1.2.0
git push origin main v1.2.0
```

---

🎉 **恭喜！** 您现在拥有了一个强大的多平台构建系统，可以轻松为不同操作系统和架构构建您的应用程序。