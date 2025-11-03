#!/usr/bin/env python3
"""
Advanced Image Editor - クロスプラットフォーム開発環境セットアップスクリプト
Windows, macOS, Linux 完全対応の環境構築とデバッグ機能

【対応OS】
- Windows 10/11 (x64, ARM64)
- macOS 10.15+ (Intel, Apple Silicon)  
- Linux (Ubuntu, CentOS, Fedora, Arch)

【機能】
- 仮想環境の自動作成（OS別最適化）
- 依存関係の自動インストール（OS固有パッケージ含む）
- GUI Framework の検出・インストール
- システム要件の検証・診断
- 環境構築状況の詳細レポート
"""

import argparse
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class CrossPlatformSetup:
    """クロスプラットフォーム対応セットアップクラス"""
    
    def __init__(
        self,
        extras: Optional[List[str]] = None,
        recreate_venv: bool = False,
        venv_path: Optional[str] = None,
    ):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system()
        self.machine = platform.machine()
        self.version = platform.version()
        default_venv = ".venv_advanced_image_editor"
        self.venv_path = self.project_root / (venv_path or default_venv)
        self.extras = extras or []
        self.recreate_venv = recreate_venv
        
        # プラットフォーム情報
        self.platform_info = self._get_detailed_platform_info()
        
    def _get_detailed_platform_info(self) -> Dict[str, Any]:
        """詳細なプラットフォーム情報を取得"""
        info = {
            'system': self.system,
            'machine': self.machine,
            'version': self.version,
            'is_windows': self.system == 'Windows',
            'is_mac': self.system == 'Darwin', 
            'is_linux': self.system == 'Linux',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'python_executable': sys.executable,
        }
        
        # OS固有の詳細情報
        if info['is_windows']:
            info.update(self._get_windows_info())
        elif info['is_mac']:
            info.update(self._get_macos_info())
        elif info['is_linux']:
            info.update(self._get_linux_info())
            
        return info
    
    def _get_windows_info(self) -> Dict[str, Any]:
        """Windows固有情報"""
        return {
            'is_admin': self._check_windows_admin(),
            'powershell_available': shutil.which('powershell') is not None,
            'architecture': '64-bit' if platform.machine().endswith('64') else '32-bit'
        }
    
    def _get_macos_info(self) -> Dict[str, Any]:
        """macOS固有情報"""
        return {
            'is_apple_silicon': self.machine in ['arm64', 'Apple M1', 'Apple M2'],
            'homebrew_available': shutil.which('brew') is not None,
            'xcode_tools': self._check_xcode_tools(),
        }
    
    def _get_linux_info(self) -> Dict[str, Any]:
        """Linux固有情報"""
        distro_info = self._get_linux_distro()
        return {
            'distro': distro_info,
            'package_manager': self._detect_package_manager(),
            'display_server': os.environ.get('XDG_SESSION_TYPE', 'unknown'),
        }
    
    def _check_windows_admin(self) -> bool:
        """Windows管理者権限チェック"""
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore
        except Exception:
            return False
    
    def _check_xcode_tools(self) -> bool:
        """Xcode Command Line Toolsチェック"""
        try:
            subprocess.run(['xcode-select', '--version'], 
                         check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    def _get_linux_distro(self) -> str:
        """Linux ディストリビューション検出"""
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except Exception:
            pass
        return 'unknown'
    
    def _detect_package_manager(self) -> Optional[str]:
        """Linux パッケージマネージャー検出"""
        managers = ['apt', 'yum', 'dnf', 'pacman', 'zypper']
        for manager in managers:
            if shutil.which(manager):
                return manager
        return None
        
    def setup_environment(self):
        """開発環境の完全セットアップ"""
        print("🚀 Advanced Image Editor - クロスプラットフォーム環境セットアップ")
        print(f"📁 プロジェクトルート: {self.project_root}")
        self._show_platform_info()
        
        try:
            # 0. システム要件確認
            self._check_system_requirements()
            
            # 1. 仮想環境作成
            self.create_venv()
            
            # 2. 依存関係インストール
            self.install_dependencies()
            
            # 3. OS固有のセットアップ
            self._setup_platform_specific()
            
            # 4. GUI Framework 検出・インストール
            self.setup_gui_framework()
            
            # 5. 動作確認
            self.verify_installation()
            
            print("\n✅ セットアップ完了！")
            self.show_usage_instructions()
            
        except Exception as e:
            print(f"❌ セットアップエラー: {e}")
            self._show_debug_info()
            raise
    
    def _show_platform_info(self):
        """プラットフォーム情報表示"""
        info = self.platform_info
        print(f"💻 OS: {info['system']} ({info['machine']})")
        print(f"🐍 Python: {info['python_version']}")
        
        if info['is_windows']:
            print(f"🔒 管理者権限: {'✅' if info['is_admin'] else '❌'}")
            print(f"💾 アーキテクチャ: {info['architecture']}")
        elif info['is_mac']:
            chip_type = "Apple Silicon" if info['is_apple_silicon'] else "Intel"
            print(f"🔧 チップ: {chip_type}")
            print(f"🍺 Homebrew: {'✅' if info['homebrew_available'] else '❌'}")
        elif info['is_linux']:
            print(f"🐧 ディストリビューション: {info['distro']}")
            print(f"📦 パッケージマネージャー: {info.get('package_manager', 'N/A')}")
    
    def _check_system_requirements(self):
        """システム要件確認"""
        print("\n🔍 システム要件確認中...")
        
        # Python バージョン確認
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8以上が必要です")
        if sys.version_info >= (3, 13):
            raise RuntimeError(
                "Python 3.13 以降では依存ライブラリの互換ホイールが未提供です。"
                " pyenv等で Python 3.10 もしくは 3.11 を有効化してから再実行してください。"
            )
        print("✅ Python バージョン")
        
        # メモリ確認
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 2:
                print("⚠️  メモリ不足（2GB以上推奨）")
            else:
                print(f"✅ メモリ: {memory_gb:.1f}GB")
        except ImportError:
            print("ℹ️  メモリ情報取得不可（psutil未インストール）")
    
    def create_venv(self):
        """仮想環境作成"""
        if self.venv_path.exists() and self.recreate_venv:
            print(f"🗑️  既存の仮想環境を削除: {self.venv_path}")
            shutil.rmtree(self.venv_path)
        
        if self.venv_path.exists():
            print(f"📦 既存の仮想環境を検出: {self.venv_path}")
            return
            
        print("📦 仮想環境を作成中...")
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
        print(f"✅ 仮想環境作成完了: {self.venv_path}")
    
    def get_pip_command(self) -> str:
        """プラットフォーム別のpipコマンド取得"""
        if self.platform_info['is_windows']:
            return str(self.venv_path / "Scripts" / "pip")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def get_python_command(self) -> str:
        """プラットフォーム別のPythonコマンド取得"""
        if self.platform_info['is_windows']:
            return str(self.venv_path / "Scripts" / "python")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def install_dependencies(self):
        """依存関係インストール"""
        pip_cmd = self.get_pip_command()
        
        # pip upgrade
        print("⬆️  pip をアップグレード中...")
        self._run_pip(pip_cmd, ["install", "--upgrade", "pip", "setuptools", "wheel"])
        
        # Super-resolution stack
        self._install_core_numeric_stack(pip_cmd)
        self._install_torch_stack(pip_cmd)
        self._install_cv_stack(pip_cmd)

        # プロジェクト本体
        print("📋 プロジェクトパッケージをインストール中...")
        editable_target = "."
        if self.extras:
            editable_target = f".[{','.join(self.extras)}]"
        self._run_pip(pip_cmd, ["install", "-e", editable_target], cwd=self.project_root)

        # OS固有の依存関係
        self._install_platform_dependencies(pip_cmd)

    def _install_core_numeric_stack(self, pip_cmd: str) -> None:
        """NumPy を互換バージョンへ固定"""
        print("📦 NumPy を互換バージョンへ調整中 (1.26.4)...")
        self._run_pip(
            pip_cmd,
            [
                "install",
                "--upgrade",
                "--only-binary=:all:",
                "--index-url",
                "https://pypi.org/simple",
                "numpy==1.26.4",
            ],
        )

    def _install_torch_stack(self, pip_cmd: str) -> None:
        """PyTorch と torchvision を既知の安定構成で導入"""
        print("📦 PyTorch / TorchVision の安定バージョンを導入中...")
        torch_index = "https://download.pytorch.org/whl/cpu"
        extra_indexes = ["--extra-index-url", "https://pypi.org/simple"]
        self._run_pip(
            pip_cmd,
            [
                "install",
                "--upgrade",
                "--index-url",
                torch_index,
                *extra_indexes,
                "torch==2.1.2",
                "torchvision==0.16.2",
            ],
        )

    def _install_cv_stack(self, pip_cmd: str) -> None:
        """OpenCV と Real-ESRGAN を導入"""
        print("📦 OpenCV / Real-ESRGAN を導入中...")
        self._run_pip(
            pip_cmd,
            [
                "install",
                "--upgrade",
                "--no-deps",
                "opencv-contrib-python==4.10.0.84",
                "realesrgan>=0.3.0",
            ],
        )
        # basicsr が NumPy との互換性を確保できるよう、Wheel を強制
        self._run_pip(
            pip_cmd,
            [
                "install",
                "--upgrade",
                "basicsr==1.4.2",
            ],
        )

    def _install_platform_dependencies(self, pip_cmd: str):
        """OS固有の依存関係インストール"""
        info = self.platform_info
        
        if info['is_windows']:
            print("🪟 Windows固有パッケージをインストール中...")
            subprocess.run([pip_cmd, "install", "-e", ".[windows]"], 
                         cwd=self.project_root, check=False)  # オプション扱い
        elif info['is_mac']:
            print("🍎 macOS固有パッケージをインストール中...")
            subprocess.run([pip_cmd, "install", "-e", ".[macos]"], 
                         cwd=self.project_root, check=False)  # オプション扱い
        elif info['is_linux']:
            print("🐧 Linux固有パッケージをインストール中...")
            subprocess.run([pip_cmd, "install", "-e", ".[linux]"], 
                         cwd=self.project_root, check=False)  # オプション扱い
    
    def _setup_platform_specific(self):
        """OS固有のセットアップ"""
        info = self.platform_info
        
        if info['is_windows']:
            self._setup_windows()
        elif info['is_mac']:
            self._setup_macos()
        elif info['is_linux']:
            self._setup_linux()
    
    def _setup_windows(self):
        """Windows固有セットアップ"""
        print("🪟 Windows固有設定中...")
        # Windows Defender除外設定の提案など
        if not self.platform_info['is_admin']:
            print("💡 管理者権限での実行を推奨（パフォーマンス向上のため）")
    
    def _setup_macos(self):
        """macOS固有セットアップ"""
        print("🍎 macOS固有設定中...")
        if not self.platform_info['xcode_tools']:
            print("💡 Xcode Command Line Tools のインストールを推奨")
            print("   実行: xcode-select --install")
    
    def _setup_linux(self):
        """Linux固有セットアップ"""
        print("🐧 Linux固有設定中...")
        pkg_mgr = self.platform_info.get('package_manager')
        if pkg_mgr == 'apt':
            print("💡 追加パッケージ推奨: sudo apt install python3-tk python3-dev")
        elif pkg_mgr == 'yum' or pkg_mgr == 'dnf':
            print("💡 追加パッケージ推奨: sudo yum install tkinter python3-devel")
    
    def setup_gui_framework(self):
        """GUI Framework の検出とセットアップ"""
        gui_framework_paths = [
            Path.home() / "Development.local" / "lib" / "gui_framework",
            self.project_root.parent.parent / "lib" / "gui_framework",
            self.project_root / "lib" / "gui_framework"
        ]
        
        pip_cmd = self.get_pip_command()
        
        for path in gui_framework_paths:
            if path.exists() and (path / "setup.py").exists():
                print(f"🎨 GUI Framework 検出: {path}")
                print("📦 開発モードでインストール中...")
                subprocess.run([pip_cmd, "install", "-e", str(path)], check=True)
                print("✅ GUI Framework インストール完了")
                return
        
        print("ℹ️  GUI Framework が見つかりません（オプション）")
    
    def verify_installation(self):
        """インストール検証"""
        print("\n🧪 インストール検証中...")
        
        python_cmd = self.get_python_command()
        
        # 基本インポートテスト
        test_imports = [
            ("customtkinter", "GUI Framework"),
            ("cv2", "OpenCV"),
            ("PIL", "Pillow"),
            ("numpy", "NumPy"),
            ("scipy", "SciPy")
        ]
        
        for module, name in test_imports:
            try:
                subprocess.run([
                    python_cmd, "-c", f"import {module}; print('OK')"
                ], check=True, capture_output=True, text=True)
                print(f"✅ {name}")
            except subprocess.CalledProcessError:
                print(f"❌ {name} のインポートに失敗")
    
    def get_activate_command(self) -> str:
        """プラットフォーム別のactivateコマンド"""
        if self.platform_info['is_windows']:
            return str(self.venv_path / "Scripts" / "activate")
        else:
            return f"source {self.venv_path / 'bin' / 'activate'}"
    
    def show_usage_instructions(self):
        """使用方法の表示"""
        python_cmd = self.get_python_command()
        activate_cmd = self.get_activate_command()
        
        print(f"""
📋 使用方法:

1. 仮想環境の有効化:
   {activate_cmd}

2. アプリケーション起動:
   {python_cmd} src/main_plugin.py

3. 開発用エントリーポイント:
   advanced-image-editor

4. エイリアス:
   aie
        """)
    
    def _show_debug_info(self):
        """デバッグ情報表示"""
        print("\n🔍 デバッグ情報:")
        print(f"  - Python実行ファイル: {sys.executable}")
        print(f"  - 現在のディレクトリ: {os.getcwd()}")
        print(f"  - 仮想環境パス: {self.venv_path}")
        print(f"  - プラットフォーム情報: {self.platform_info}")

    def _run_pip(self, pip_cmd: str, args: List[str], cwd: Optional[Path] = None) -> None:
        """pip コマンドを実行して進捗を表示"""
        full_cmd = [pip_cmd, *args]
        subprocess.run(full_cmd, check=True, cwd=str(cwd) if cwd else None)

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Advanced Image Editor 開発環境セットアップ")
    parser.add_argument(
        "--extras",
        help="pip install -e .[extras] で追加するエキストラをカンマ区切りで指定（例: dev,docs）",
        default="",
    )
    parser.add_argument(
        "--recreate-venv",
        action="store_true",
        help="既存の .venv を削除して仮想環境を作り直す",
    )
    parser.add_argument(
        "--venv-path",
        default=".venv_advanced_image_editor",
        help="仮想環境の配置先（デフォルト: .venv_advanced_image_editor）",
    )
    args = parser.parse_args()

    extras = [item.strip() for item in args.extras.split(",") if item.strip()]
    
    try:
        setup = CrossPlatformSetup(
            extras=extras,
            recreate_venv=args.recreate_venv,
            venv_path=args.venv_path,
        )
        setup.setup_environment()
    except Exception as e:
        print(f"❌ セットアップエラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
