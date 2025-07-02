# 多平台构建指南

## 📋 概述

本项目已经具备了完整的多平台构建能力，支持以下平台：

- **Windows** (x64)
- **macOS** (Intel x86_64 + Apple Silicon ARM64)
- **Linux** (x64 + ARM64)

## 🚀 支持的构建方式

### 1. 本地构建

#### Windows
```bash
# 方式1: 使用批处理脚本（推荐）
build.bat

# 方式2: 使用Python脚本
python build.py
```

#### macOS  
```bash
# 方式1: 使用命令脚本（推荐）
chmod +x build.mac.command
./build.mac.command

# 方式2: 使用Python脚本
python3 build.py
```

#### Linux
```bash
# 方式1: 使用shell脚本（推荐）
chmod +x build.sh
./build.sh

# 方式2: 使用Python脚本
python3 build.py
```

### 2. GitHub Actions 自动化构建

项目配置了完整的CI/CD流水线，支持：

- ✅ **Windows x64** - 在 `windows-latest` runner上构建
- ✅ **macOS ARM64** - 在 `macos-latest` runner上构建（Apple Silicon）
- ✅ **macOS Intel** - 在 `macos-latest` runner上使用 `arch -x86_64` 构建
- ✅ **Linux x64** - 在 `ubuntu-22.04` runner上构建
- ✅ **Linux ARM64** - 使用Docker容器交叉编译

## 🏗️ 构建配置详情

### PyInstaller配置 (`build.spec`)

```python
# 自动根据平台生成输出文件名
output_name = f"CursorFreeVIP_{version}_{os_type}"

# 支持的架构
target_arch = os.environ.get('TARGET_ARCH', None)  # 可通过环境变量指定
```

### 版本管理

- 版本号从 `.env` 文件中的 `VERSION` 变量读取
- GitHub Actions 支持手动指定版本或使用环境文件版本

## 📦 输出文件格式

| 平台 | 文件名格式 | 扩展名 |
|------|------------|--------|
| Windows | `CursorFreeVIP_{version}_windows` | `.exe` |
| macOS | `CursorFreeVIP_{version}_mac` | 无 |
| Linux | `CursorFreeVIP_{version}_linux` | 无 |

## 🔧 现有功能特性

### ✅ 已实现的功能

1. **多平台本地构建脚本**
   - Windows: 批处理脚本，支持管理员权限检查
   - macOS: shell脚本，支持虚拟环境管理
   - Linux: shell脚本，自动检查和安装依赖

2. **CI/CD自动化**
   - 5个平台的并行构建
   - 自动创建GitHub Release
   - SHA256校验和生成
   - 从CHANGELOG.md提取发布说明

3. **智能构建系统**
   - 自动清理构建缓存
   - 进度条和加载动画
   - 错误处理和回滚
   - 虚拟环境隔离

4. **版本管理**
   - 环境变量驱动的版本控制
   - 自动标签创建
   - 构建工件命名规范

## 🚀 改进建议

### 1. 添加更多平台支持

可以考虑添加以下平台：

```yaml
# 在 .github/workflows/build.yml 中添加
build-linux-arm32:
  runs-on: ubuntu-latest
  steps:
    - name: Build ARM32 executable
      run: |
        docker run --rm --platform linux/arm/v7 -v ${{ github.workspace }}:/app -w /app arm32v7/python:3.10-slim bash -c "..."

build-freebsd:
  runs-on: ubuntu-latest
  steps:
    - name: Build FreeBSD executable
      uses: vmactions/freebsd-vm@v0
      with:
        run: |
          pkg install -y python39 py39-pip
          python3.9 -m pip install -r requirements.txt
          python3.9 build.py
```

### 2. 增强的构建脚本

创建一个统一的构建脚本：

```python
# build_universal.py
import argparse
import platform
import subprocess
import sys

def build_for_platform(target_platform=None, target_arch=None):
    """统一的多平台构建函数"""
    current_platform = platform.system().lower()
    
    if target_platform and target_platform != current_platform:
        # 交叉编译逻辑
        cross_compile(target_platform, target_arch)
    else:
        # 本地编译
        native_compile(target_arch)

def cross_compile(target_platform, target_arch):
    """交叉编译支持"""
    # 使用Docker或其他交叉编译工具
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=["windows", "linux", "darwin"])
    parser.add_argument("--arch", choices=["x86_64", "arm64", "arm32"])
    args = parser.parse_args()
    
    build_for_platform(args.platform, args.arch)
```

### 3. 构建配置文件

创建 `build.config.json` 来管理构建配置：

```json
{
  "platforms": {
    "windows": {
      "architectures": ["x86_64"],
      "file_extension": ".exe",
      "build_requirements": ["pyinstaller", "pywin32"]
    },
    "linux": {
      "architectures": ["x86_64", "arm64", "arm32"],
      "file_extension": "",
      "build_requirements": ["pyinstaller"]
    },
    "darwin": {
      "architectures": ["x86_64", "arm64"],
      "file_extension": "",
      "build_requirements": ["pyinstaller"]
    }
  },
  "output": {
    "naming_convention": "CursorFreeVIP_{version}_{platform}_{arch}",
    "compression": true,
    "include_debug_symbols": false
  }
}
```

### 4. 容器化构建

创建 `Dockerfile.build` 用于一致的构建环境：

```dockerfile
FROM python:3.10-slim

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyinstaller

# 构建脚本
COPY . .

# 默认构建命令
CMD ["python", "build.py"]
```

### 5. 测试自动化

在构建流程中添加自动化测试：

```yaml
# 在 GitHub Actions 中添加测试步骤
- name: Test executable
  run: |
    # Windows
    if [ "${{ matrix.platform }}" == "windows" ]; then
      ./dist/CursorFreeVIP_*.exe --version
    else
      # Unix-like systems
      ./dist/CursorFreeVIP_* --version
    fi
```

## 📝 使用说明

### 触发自动构建

1. **手动触发**：
   - 进入GitHub Actions页面
   - 选择"Build Executables"工作流
   - 点击"Run workflow"
   - 选择是否使用.env文件中的版本或手动输入版本

2. **自动触发**：
   - 推送带有版本标签的提交
   - 创建Pull Request时自动构建

### 本地开发构建

```bash
# 1. 确保环境配置正确
python -m pip install -r requirements.txt

# 2. 设置版本号（可选）
echo "VERSION=1.0.0" > .env

# 3. 运行构建
python build.py
```

## 🛠️ 故障排除

### 常见问题

1. **构建失败**：检查依赖是否完整安装
2. **权限问题**：确保构建脚本有执行权限
3. **交叉编译问题**：确保Docker环境配置正确
4. **版本号问题**：检查.env文件格式是否正确

### 日志查看

- 本地构建：查看终端输出
- GitHub Actions：在Actions页面查看详细日志
- 构建产物：在Releases页面下载

## 🔮 未来规划

1. **增加更多平台支持**（FreeBSD、Android等）
2. **优化构建速度**（缓存、并行化）
3. **自动化测试覆盖**
4. **代码签名支持**
5. **分发包管理**（APT、Homebrew、Chocolatey等）

---

这个多平台构建系统为项目提供了强大的跨平台分发能力，确保用户在不同操作系统上都能获得一致的体验。