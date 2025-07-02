#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速构建脚本 - 一键式跨平台构建
适合初学者和快速部署使用
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🚀 CursorFreeVIP 快速构建工具")
    print("=" * 60)
    print(f"📱 系统：{platform.system()} {platform.release()}")
    print(f"🔧 架构：{platform.machine()}")
    print(f"🐍 Python：{sys.version.split()[0]}")
    print("=" * 60)

def check_requirements():
    """检查基本要求"""
    print("📋 检查构建要求...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    
    # 检查必要文件
    required_files = ["main.py", "build.py", "build.spec", "requirements.txt"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少必要文件：{file}")
            return False
    
    print("✅ 基本要求检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 安装构建依赖...")
    
    try:
        # 升级 pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # 安装 PyInstaller
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True, capture_output=True)
        
        # 安装项目依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print("✅ 依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败：{e}")
        return False

def build_executable():
    """构建可执行文件"""
    print("\n🔨 开始构建可执行文件...")
    
    try:
        # 清理旧的构建文件
        for dir_name in ["build", "dist", "__pycache__"]:
            if Path(dir_name).exists():
                print(f"🗑️  清理 {dir_name} 目录...")
                import shutil
                shutil.rmtree(dir_name)
        
        # 运行构建
        result = subprocess.run([sys.executable, "build.py"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 构建成功完成")
            return True
        else:
            print(f"❌ 构建失败：{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错：{e}")
        return False

def show_results():
    """显示构建结果"""
    print("\n📁 构建结果：")
    print("-" * 40)
    
    dist_path = Path("dist")
    if not dist_path.exists():
        print("❌ 未找到 dist 目录")
        return
    
    files = list(dist_path.iterdir())
    if not files:
        print("❌ dist 目录为空")
        return
    
    total_size = 0
    for file in files:
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"📄 {file.name} ({size_mb:.1f} MB)")
    
    print(f"\n📊 总大小：{total_size:.1f} MB")
    
    # 显示使用说明
    system = platform.system().lower()
    print(f"\n🚀 使用方法：")
    for file in files:
        if file.is_file():
            if system == "windows":
                print(f"   双击运行：{file.name}")
            else:
                print(f"   运行命令：./{file.name}")
                print(f"   或者：chmod +x {file.name} && ./{file.name}")

def main():
    """主函数"""
    print_banner()
    
    # 检查要求
    if not check_requirements():
        input("\n按 Enter 键退出...")
        return
    
    # 询问是否继续
    print(f"\n🤔 即将开始构建 {platform.system()} 平台的可执行文件")
    response = input("继续吗？(y/n): ").lower().strip()
    
    if response not in ['y', 'yes', '是', '']:
        print("👋 构建已取消")
        return
    
    # 安装依赖
    if not install_dependencies():
        input("\n按 Enter 键退出...")
        return
    
    # 构建
    if not build_executable():
        input("\n按 Enter 键退出...")
        return
    
    # 显示结果
    show_results()
    
    print("\n🎉 构建完成！")
    input("按 Enter 键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  构建被用户中断")
    except Exception as e:
        print(f"\n❌ 意外错误：{e}")
        input("按 Enter 键退出...")