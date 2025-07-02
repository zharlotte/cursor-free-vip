# 🚀 GitHub 自动构建使用说明

## ✅ 你的项目已经配置好了！

你的项目**已经有** GitHub Actions 配置，可以在 GitHub 服务器上自动为所有平台构建可执行程序。

## 🎯 立即开始使用

### 方法 1: 推送代码自动构建（最简单）

```bash
git add .
git commit -m "更新代码"
git push origin main
```

**结果**: GitHub 会自动构建所有平台的可执行文件！

### 方法 2: 手动触发构建

1. 访问你的 GitHub 仓库
2. 点击 `Actions` 标签页
3. 选择 `Build Executables` 
4. 点击 `Run workflow` 按钮
5. 选择使用 `.env` 文件版本或手动输入版本
6. 点击 `Run workflow`

### 方法 3: 创建标签触发

```bash
git tag v1.11.04
git push origin v1.11.04
```

## 📦 在哪里找到构建结果？

构建完成后，去你的 GitHub 仓库：

1. 点击 `Releases` 标签页
2. 找到最新的发布版本  
3. 下载对应平台的可执行文件：
   - `*_windows.exe` - Windows
   - `*_mac_arm64` - macOS Apple Silicon
   - `*_mac_intel` - macOS Intel
   - `*_linux_x64` - Linux x64
   - `*_linux_arm64` - Linux ARM64

## ⏱️ 构建需要多长时间？

大约 **15-25 分钟**，所有平台同时构建。

## 🔍 如何查看构建状态？

1. 访问 GitHub 仓库的 `Actions` 页面
2. 查看运行状态：
   - 🔄 正在构建
   - ✅ 构建成功  
   - ❌ 构建失败

## 💡 提示

- **首次使用**: 直接推送代码到 `main` 分支即可
- **版本控制**: 编辑 `.env` 文件中的 `VERSION=1.11.03`
- **问题排查**: 查看 Actions 页面的构建日志

**总结**: 你的项目已经完全配置好了 GitHub 自动构建，只需要推送代码就会自动生成所有平台的可执行文件！🎉