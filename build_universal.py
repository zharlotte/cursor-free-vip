#!/usr/bin/env python3
"""
Universal Multi-Platform Build Script
支持本地构建、交叉编译和Docker容器构建
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
import threading
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

class Colors:
    """控制台颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class BuildConfig:
    """构建配置管理"""
    
    def __init__(self, config_file: str = "build.config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """加载构建配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Colors.YELLOW}警告: 配置文件 {self.config_file} 不存在，使用默认配置{Colors.END}")
            return self._default_config()
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}错误: 配置文件解析失败: {e}{Colors.END}")
            sys.exit(1)
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "platforms": {
                "windows": {"architectures": ["x86_64"], "file_extension": ".exe"},
                "linux": {"architectures": ["x86_64"], "file_extension": ""},
                "darwin": {"architectures": ["x86_64"], "file_extension": ""}
            },
            "output": {
                "naming_convention": "CursorFreeVIP_{version}_{platform}_{arch}",
                "directory": "dist"
            }
        }
    
    def get_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return list(self.config["platforms"].keys())
    
    def get_architectures(self, platform: str) -> List[str]:
        """获取平台支持的架构列表"""
        return self.config["platforms"].get(platform, {}).get("architectures", [])
    
    def get_file_extension(self, platform: str) -> str:
        """获取平台的文件扩展名"""
        return self.config["platforms"].get(platform, {}).get("file_extension", "")

class BuildLogger:
    """构建日志管理"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.start_time = time.time()
    
    def info(self, message: str):
        """信息日志"""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")
    
    def success(self, message: str):
        """成功日志"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def warning(self, message: str):
        """警告日志"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def error(self, message: str):
        """错误日志"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def debug(self, message: str):
        """调试日志"""
        if self.verbose:
            print(f"{Colors.PURPLE}🐛 {message}{Colors.END}")
    
    def elapsed_time(self) -> str:
        """获取经过的时间"""
        elapsed = time.time() - self.start_time
        return f"{elapsed:.2f}秒"

class LoadingAnimation:
    """加载动画"""
    
    def __init__(self):
        self.is_running = False
        self.animation_thread = None
    
    def start(self, message: str = "构建中"):
        """开始动画"""
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate, args=(message,))
        self.animation_thread.start()
    
    def stop(self):
        """停止动画"""
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        print("\r" + " " * 70 + "\r", end="", flush=True)
    
    def _animate(self, message: str):
        """动画效果"""
        animation = "|/-\\"
        idx = 0
        while self.is_running:
            print(f"\r{message} {animation[idx % len(animation)]}", end="", flush=True)
            idx += 1
            time.sleep(0.1)

class UniversalBuilder:
    """通用构建器"""
    
    def __init__(self, config: BuildConfig, logger: BuildLogger):
        self.config = config
        self.logger = logger
        self.version = self._get_version()
        
    def _get_version(self) -> str:
        """获取版本号"""
        load_dotenv()
        version = os.getenv('VERSION', '1.0.0')
        self.logger.info(f"构建版本: {version}")
        return version
    
    def _detect_current_platform(self) -> str:
        """检测当前平台"""
        system = platform.system().lower()
        if system == "darwin":
            return "darwin"
        return system
    
    def _detect_current_arch(self) -> str:
        """检测当前架构"""
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            return "x86_64"
        elif machine in ["arm64", "aarch64"]:
            return "arm64"
        elif machine.startswith("arm"):
            return "arm32"
        return machine
    
    def _clean_build_directory(self):
        """清理构建目录"""
        self.logger.info("清理构建目录...")
        dirs_to_clean = ['build', 'dist', '__pycache__']
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                self.logger.debug(f"已删除目录: {dir_name}")
    
    def _setup_environment(self):
        """设置构建环境"""
        self.logger.info("设置构建环境...")
        
        # 创建输出目录
        output_dir = self.config.config["output"]["directory"]
        os.makedirs(output_dir, exist_ok=True)
        
        # 检查Python版本
        python_version = sys.version_info
        self.logger.debug(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查依赖
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查构建依赖"""
        self.logger.info("检查构建依赖...")
        
        try:
            import PyInstaller
            self.logger.debug(f"PyInstaller版本: {PyInstaller.__version__}")
        except ImportError:
            self.logger.error("PyInstaller未安装，请运行: pip install pyinstaller")
            sys.exit(1)
    
    def _get_output_name(self, platform: str, arch: str) -> str:
        """生成输出文件名"""
        naming_convention = self.config.config["output"]["naming_convention"]
        name = naming_convention.format(
            version=self.version,
            platform=platform,
            arch=arch
        )
        extension = self.config.get_file_extension(platform)
        return f"{name}{extension}"
    
    def _build_native(self, platform: str, arch: str) -> bool:
        """本地构建"""
        self.logger.info(f"开始本地构建: {platform} {arch}")
        
        output_name = self._get_output_name(platform, arch)
        
        # 设置环境变量
        env = os.environ.copy()
        env['VERSION'] = self.version
        if arch != self._detect_current_arch():
            env['TARGET_ARCH'] = arch
        
        # 构建命令
        cmd = ['pyinstaller', '--clean', '--noconfirm', 'build.spec']
        
        animation = LoadingAnimation()
        try:
            animation.start("构建进行中")
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800  # 30分钟超时
            )
            
            animation.stop()
            
            if result.returncode == 0:
                # 重命名输出文件
                original_name = f"CursorFreeVIP_{self.version}_{platform}"
                if platform == "windows":
                    original_name += ".exe"
                
                original_path = os.path.join("dist", original_name)
                new_path = os.path.join("dist", output_name)
                
                if os.path.exists(original_path) and original_path != new_path:
                    os.rename(original_path, new_path)
                
                if os.path.exists(new_path):
                    self.logger.success(f"构建成功: {new_path}")
                    return True
                else:
                    self.logger.error("构建失败: 输出文件不存在")
                    return False
            else:
                self.logger.error(f"构建失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            animation.stop()
            self.logger.error("构建超时")
            return False
        except Exception as e:
            animation.stop()
            self.logger.error(f"构建异常: {str(e)}")
            return False
    
    def _build_docker(self, platform: str, arch: str) -> bool:
        """Docker容器构建"""
        self.logger.info(f"开始Docker构建: {platform} {arch}")
        
        docker_images = self.config.config["platforms"][platform].get("docker_images", {})
        if arch not in docker_images:
            self.logger.error(f"不支持的架构: {platform} {arch}")
            return False
        
        docker_image = docker_images[arch]
        output_name = self._get_output_name(platform, arch)
        
        # Docker命令
        docker_cmd = [
            'docker', 'run', '--rm',
            f'--platform=linux/{arch}' if arch == 'arm64' else '--platform=linux/amd64',
            '-v', f'{os.getcwd()}:/app',
            '-w', '/app',
            docker_image,
            'bash', '-c',
            f'''
            apt-get update && apt-get install -y build-essential
            pip install --upgrade pip
            pip install pyinstaller
            pip install -r requirements.txt
            VERSION={self.version} python -m PyInstaller build.spec
            mv /app/dist/CursorFreeVIP_{self.version}_{platform} /app/dist/{output_name}
            '''
        ]
        
        animation = LoadingAnimation()
        try:
            animation.start("Docker构建进行中")
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=2400  # 40分钟超时
            )
            
            animation.stop()
            
            if result.returncode == 0:
                output_path = os.path.join("dist", output_name)
                if os.path.exists(output_path):
                    self.logger.success(f"Docker构建成功: {output_path}")
                    return True
                else:
                    self.logger.error("Docker构建失败: 输出文件不存在")
                    return False
            else:
                self.logger.error(f"Docker构建失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            animation.stop()
            self.logger.error("Docker构建超时")
            return False
        except Exception as e:
            animation.stop()
            self.logger.error(f"Docker构建异常: {str(e)}")
            return False
    
    def build(self, target_platform: Optional[str] = None, target_arch: Optional[str] = None) -> bool:
        """执行构建"""
        self.logger.info(f"开始多平台构建 (总用时: {self.logger.elapsed_time()})")
        
        # 清理和设置环境
        if self.config.config.get("build", {}).get("clean_before_build", True):
            self._clean_build_directory()
        
        self._setup_environment()
        
        current_platform = self._detect_current_platform()
        current_arch = self._detect_current_arch()
        
        # 确定要构建的平台和架构
        if target_platform:
            platforms = [target_platform] if target_platform in self.config.get_platforms() else []
        else:
            platforms = [current_platform]  # 默认只构建当前平台
        
        if not platforms:
            self.logger.error(f"不支持的平台: {target_platform}")
            return False
        
        success_count = 0
        total_count = 0
        
        for platform in platforms:
            architectures = [target_arch] if target_arch else self.config.get_architectures(platform)
            
            for arch in architectures:
                total_count += 1
                self.logger.info(f"构建 {platform} {arch}")
                
                # 判断是否需要交叉编译
                need_cross_compile = (
                    platform != current_platform or 
                    arch != current_arch
                )
                
                if need_cross_compile and self.config.config["platforms"][platform].get("cross_compile"):
                    # 使用Docker交叉编译
                    if self._build_docker(platform, arch):
                        success_count += 1
                else:
                    # 本地构建
                    if self._build_native(platform, arch):
                        success_count += 1
        
        # 生成校验和
        if success_count > 0 and self.config.config["output"].get("calculate_checksums", True):
            self._generate_checksums()
        
        self.logger.info(f"构建完成: {success_count}/{total_count} 成功 (总用时: {self.logger.elapsed_time()})")
        return success_count == total_count
    
    def _generate_checksums(self):
        """生成校验和"""
        self.logger.info("生成SHA256校验和...")
        
        dist_dir = self.config.config["output"]["directory"]
        checksum_file = os.path.join(dist_dir, "checksums.txt")
        
        with open(checksum_file, 'w') as f:
            for file_path in Path(dist_dir).glob("CursorFreeVIP_*"):
                if file_path.is_file() and file_path.name != "checksums.txt":
                    # 计算SHA256
                    import hashlib
                    sha256_hash = hashlib.sha256()
                    with open(file_path, "rb") as fb:
                        for byte_block in iter(lambda: fb.read(4096), b""):
                            sha256_hash.update(byte_block)
                    
                    checksum = sha256_hash.hexdigest()
                    f.write(f"{checksum}  {file_path.name}\n")
                    self.logger.debug(f"{file_path.name}: {checksum}")
        
        self.logger.success(f"校验和已保存到: {checksum_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Universal Multi-Platform Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 构建当前平台
  %(prog)s --platform linux          # 构建Linux平台
  %(prog)s --platform windows --arch x86_64  # 构建Windows x64
  %(prog)s --all                     # 构建所有支持的平台
  %(prog)s --list                    # 列出支持的平台和架构
        """
    )
    
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "darwin"],
        help="目标平台"
    )
    
    parser.add_argument(
        "--arch",
        choices=["x86_64", "arm64", "arm32"],
        help="目标架构"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="构建所有支持的平台"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出支持的平台和架构"
    )
    
    parser.add_argument(
        "--config",
        default="build.config.json",
        help="构建配置文件路径"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="不清理构建目录"
    )
    
    args = parser.parse_args()
    
    # 初始化组件
    config = BuildConfig(args.config)
    logger = BuildLogger(args.verbose)
    
    # 列出支持的平台
    if args.list:
        print(f"{Colors.BOLD}支持的平台和架构:{Colors.END}")
        for platform in config.get_platforms():
            archs = ", ".join(config.get_architectures(platform))
            ext = config.get_file_extension(platform) or "无扩展名"
            print(f"  {Colors.CYAN}{platform}{Colors.END}: {archs} ({ext})")
        return
    
    # 修改配置
    if args.no_clean:
        config.config["build"]["clean_before_build"] = False
    
    # 创建构建器
    builder = UniversalBuilder(config, logger)
    
    # 执行构建
    if args.all:
        # 构建所有平台
        success = True
        for platform in config.get_platforms():
            for arch in config.get_architectures(platform):
                if not builder.build(platform, arch):
                    success = False
        sys.exit(0 if success else 1)
    else:
        # 构建指定平台
        success = builder.build(args.platform, args.arch)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()