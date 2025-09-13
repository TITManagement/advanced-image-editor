#!/usr/bin/env python3
"""
Cross-Platform Installation Script for Advanced Image Editor
macOS / Linux / Windows 対応のインストールスクリプト
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_platform_info():
    """プラットフォーム情報を取得"""
    system = platform.system().lower()
    return {
        'system': system,
        'is_windows': system == 'windows',
        'is_mac': system == 'darwin',
        'is_linux': system == 'linux'
    }

def get_python_executable():
    """プラットフォームに応じたPython実行ファイルパスを取得"""
    platform_info = get_platform_info()
    
    if platform_info['is_windows']:
        return [
            Path(".venv") / "Scripts" / "python.exe",
            Path("venv") / "Scripts" / "python.exe",
            "python.exe",
            "python"
        ]
    else:
        return [
            Path(".venv") / "bin" / "python",
            Path("venv") / "bin" / "python", 
            "python3",
            "python"
        ]

def find_python():
    """利用可能なPython実行ファイルを検索"""
    candidates = get_python_executable()
    
    for python_path in candidates:
        try:
            if isinstance(python_path, Path):
                if python_path.exists():
                    return str(python_path)
            else:
                # コマンドとして存在するかチェック
                result = subprocess.run([python_path, "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return python_path
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    
    return None

def create_venv():
    """仮想環境を作成"""
    platform_info = get_platform_info()
    
    print("🔧 仮想環境を作成中...")
    
    # Python実行ファイルを検索
    python_cmd = find_python()
    if not python_cmd:
        print("❌ Python実行ファイルが見つかりません")
        return False
    
    try:
        # 仮想環境作成
        subprocess.run([python_cmd, "-m", "venv", ".venv"], check=True)
        print("✅ 仮想環境作成完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 仮想環境作成エラー: {e}")
        return False

def setup_gui_framework_path():
    """gui_frameworkライブラリのパスをセットアップ"""
    try:
        # プロジェクトルートから相対パスでgui_frameworkを探索
        project_root = Path(__file__).parent
        gui_framework_paths = [
            project_root / ".." / ".." / "lib" / "gui_framework",  # ../../lib/gui_framework
            project_root / ".." / "lib" / "gui_framework",        # ../lib/gui_framework  
            project_root / "lib" / "gui_framework",               # ./lib/gui_framework
        ]
        
        for gui_path in gui_framework_paths:
            if gui_path.exists() and (gui_path / "__init__.py").exists():
                print(f"✅ gui_framework発見: {gui_path.relative_to(project_root)}")
                return str(gui_path.parent.resolve())
        
        print("⚠️ gui_frameworkが見つかりません。基本機能のみで動作します。")
        return None
    except Exception as e:
        print(f"⚠️ gui_frameworkパス設定エラー: {e}")
        return None

def install_dependencies():
    """依存関係をインストール"""
    platform_info = get_platform_info()
    
    # 仮想環境内のPython実行ファイルパス
    if platform_info['is_windows']:
        venv_python = Path(".venv") / "Scripts" / "python.exe"
        pip_cmd = Path(".venv") / "Scripts" / "pip.exe"
    else:
        venv_python = Path(".venv") / "bin" / "python"
        pip_cmd = Path(".venv") / "bin" / "pip"
    
    if not venv_python.exists():
        print("❌ 仮想環境が見つかりません")
        return False
    
    try:
        print("📦 依存関係をインストール中...")
        
        # pipをアップグレード
        subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # requirements.txtから依存関係をインストール
        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # gui_frameworkパスをセットアップ
        gui_lib_path = setup_gui_framework_path()
        if gui_lib_path:
            # gui_frameworkを開発モードでインストール（オプション）
            gui_framework_path = Path(gui_lib_path) / "gui_framework"
            if gui_framework_path.exists():
                print("🔧 gui_frameworkを開発モードでインストール中...")
                subprocess.run([str(venv_python), "-m", "pip", "install", "-e", str(gui_framework_path)], 
                             check=False)  # エラーでも継続
        
        print("✅ 依存関係インストール完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依存関係インストールエラー: {e}")
        return False

def show_run_instructions():
    """実行方法を表示"""
    platform_info = get_platform_info()
    
    print("\n🎨 Advanced Image Editor セットアップ完了!")
    print("\n【実行方法】")
    
    if platform_info['is_windows']:
        print("Windows (PowerShell/コマンドプロンプト):")
        print("  .venv\\Scripts\\python.exe src\\main_plugin.py")
        print("\n  または仮想環境をアクティベート後:")
        print("  .venv\\Scripts\\Activate.ps1  # PowerShell")
        print("  .venv\\Scripts\\activate.bat  # コマンドプロンプト") 
        print("  python src\\main_plugin.py")
    else:
        system_name = "macOS" if platform_info['is_mac'] else "Linux"
        print(f"{system_name}:")
        print("  .venv/bin/python src/main_plugin.py")
        print("\n  または仮想環境をアクティベート後:")
        print("  source .venv/bin/activate")
        print("  python src/main_plugin.py")

def main():
    """メイン処理"""
    print("🚀 Advanced Image Editor セットアップを開始します...")
    
    platform_info = get_platform_info()
    system_name = {
        'windows': 'Windows',
        'darwin': 'macOS', 
        'linux': 'Linux'
    }.get(platform_info['system'], 'Unknown')
    
    print(f"🖥️  検出されたプラットフォーム: {system_name}")
    
    # requirements.txtの存在確認
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt が見つかりません")
        return 1
    
    # 仮想環境作成
    if not Path(".venv").exists():
        if not create_venv():
            return 1
    else:
        print("ℹ️  仮想環境は既に存在します")
    
    # 依存関係インストール
    if not install_dependencies():
        return 1
    
    # 実行方法を表示
    show_run_instructions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())