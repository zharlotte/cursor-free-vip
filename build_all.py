#!/usr/bin/env python3
"""
统一跨平台构建脚本
支持 Linux、macOS 和 Windows 系统
"""

import os
import sys
import platform
import subprocess
import shutil
import venv
from pathlib import Path
from logo import print_logo

class Color:
    """控制台颜色常量"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Color.WHITE):
    """打印彩色文本"""
    print(f"{color}{text}{Color.END}")

def check_python_version():
    """检查 Python 版本"""
    print_colored("🐍 检查 Python 版本...", Color.YELLOW)
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored(f"❌ Python 版本过低: {version.major}.{version.minor}", Color.RED)
        print_colored("需要 Python 3.8 或更高版本", Color.RED)
        return False
    
    print_colored(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}", Color.GREEN)
    return True

def get_system_info():
    """获取系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print_colored(f"🖥️  操作系统: {platform.system()}", Color.CYAN)
    print_colored(f"🏗️  架构: {platform.machine()}", Color.CYAN)
    
    return system, machine

def check_system_requirements(system):
    """检查系统要求"""
    print_colored("📋 检查系统要求...", Color.YELLOW)
    
    if system == "linux":
        # 检查是否有必要的系统包
        try:
            subprocess.run(["python3", "--version"], check=True, capture_output=True)
            print_colored("✅ python3 已安装", Color.GREEN)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_colored("❌ 需要安装 python3", Color.RED)
            print_colored("运行: sudo apt-get install python3 python3-pip python3-venv python3-dev", Color.YELLOW)
            return False
            
    elif system == "darwin":  # macOS
        # 检查 Xcode Command Line Tools
        try:
            subprocess.run(["xcode-select", "--version"], check=True, capture_output=True)
            print_colored("✅ Xcode Command Line Tools 已安装", Color.GREEN)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_colored("⚠️  建议安装 Xcode Command Line Tools", Color.YELLOW)
            print_colored("运行: xcode-select --install", Color.YELLOW)
    
    elif system == "windows":
        # Windows 通常不需要额外检查
        print_colored("✅ Windows 系统检查通过", Color.GREEN)
    
    return True

def create_virtual_environment():
    """创建虚拟环境"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_colored("🗑️  删除已存在的虚拟环境...", Color.YELLOW)
        shutil.rmtree(venv_path)
    
    print_colored("📦 创建虚拟环境...", Color.YELLOW)
    venv.create(venv_path, with_pip=True)
    
    return venv_path

def get_activation_command(system, venv_path):
    """获取虚拟环境激活命令"""
    if system == "windows":
        return str(venv_path / "Scripts" / "activate.bat")
    else:
        return f"source {venv_path / 'bin' / 'activate'}"

def get_python_executable(system, venv_path):
    """获取虚拟环境中的 Python 可执行文件路径"""
    if system == "windows":
        return str(venv_path / "Scripts" / "python.exe")
    else:
        return str(venv_path / "bin" / "python")

def install_dependencies(python_exe):
    """安装依赖包"""
    print_colored("📥 升级 pip...", Color.YELLOW)
    subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    print_colored("📥 安装项目依赖...", Color.YELLOW)
    subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def build_executable(python_exe, system):
    """构建可执行文件"""
    print_colored("🔨 开始构建可执行文件...", Color.YELLOW)
    
    # 清理之前的构建
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # 运行构建脚本
    subprocess.run([python_exe, "build.py"], check=True)

def verify_build(system):
    """验证构建结果"""
    print_colored("🔍 验证构建结果...", Color.YELLOW)
    
    dist_path = Path("dist")
    if not dist_path.exists():
        print_colored("❌ dist 目录不存在", Color.RED)
        return False
    
    # 查找生成的可执行文件
    executables = []
    for file in dist_path.iterdir():
        if file.is_file():
            if system == "windows" and file.suffix == ".exe":
                executables.append(file)
            elif system in ["linux", "darwin"] and file.suffix == "":
                executables.append(file)
    
    if not executables:
        print_colored("❌ 未找到可执行文件", Color.RED)
        return False
    
    for exe in executables:
        file_size = exe.stat().st_size / (1024 * 1024)  # MB
        print_colored(f"✅ 生成可执行文件: {exe.name} ({file_size:.1f} MB)", Color.GREEN)
    
    return True

def cleanup_environment(venv_path):
    """清理虚拟环境"""
    print_colored("🧹 清理虚拟环境...", Color.YELLOW)
    if venv_path.exists():
        shutil.rmtree(venv_path)

def print_usage_instructions(system):
    """打印使用说明"""
    print_colored("\n📖 使用说明:", Color.CYAN)
    print_colored("─" * 50, Color.CYAN)
    
    dist_path = Path("dist")
    if dist_path.exists():
        for file in dist_path.iterdir():
            if file.is_file():
                if system == "windows" and file.suffix == ".exe":
                    print_colored(f"🚀 运行: {file}", Color.GREEN)
                elif system in ["linux", "darwin"] and file.suffix == "":
                    print_colored(f"🚀 运行: ./{file}", Color.GREEN)
                    print_colored(f"   或: chmod +x {file} && ./{file}", Color.YELLOW)

def main():
    """主函数"""
    # 清屏并显示 logo
    os.system("cls" if platform.system() == "Windows" else "clear")
    print_logo()
    
    print_colored("🎯 跨平台构建脚本", Color.BOLD + Color.CYAN)
    print_colored("═" * 60, Color.CYAN)
    
    try:
        # 检查 Python 版本
        if not check_python_version():
            sys.exit(1)
        
        # 获取系统信息
        system, machine = get_system_info()
        
        # 检查系统要求
        if not check_system_requirements(system):
            sys.exit(1)
        
        # 创建虚拟环境
        venv_path = create_virtual_environment()
        
        # 获取 Python 可执行文件路径
        python_exe = get_python_executable(system, venv_path)
        
        # 安装依赖
        install_dependencies(python_exe)
        
        # 构建可执行文件
        build_executable(python_exe, system)
        
        # 验证构建结果
        if verify_build(system):
            print_colored("\n🎉 构建成功完成!", Color.BOLD + Color.GREEN)
            print_usage_instructions(system)
        else:
            print_colored("\n❌ 构建失败", Color.RED)
            sys.exit(1)
        
    except subprocess.CalledProcessError as e:
        print_colored(f"\n❌ 构建过程中出现错误: {e}", Color.RED)
        sys.exit(1)
    except KeyboardInterrupt:
        print_colored("\n⚠️  构建被用户中断", Color.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ 意外错误: {e}", Color.RED)
        sys.exit(1)
    finally:
        # 清理虚拟环境
        if 'venv_path' in locals():
            cleanup_environment(venv_path)
    
    print_colored("\n✨ 构建流程完成", Color.CYAN)

if __name__ == "__main__":
    main()