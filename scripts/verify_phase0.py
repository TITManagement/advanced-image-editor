#!/usr/bin/env python3
"""
Phase 0 動作確認スクリプト
既存機能が新しいディレクトリ構造追加後も正常に動作することを確認
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def test_imports():
    """基本的なインポートテスト"""
    print("🔍 基本インポートテスト開始...")
    
    try:
        # PYTHONPATHを設定してsrcディレクトリを追加
        import sys
        import os
        src_path = os.path.join(os.getcwd(), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # 既存のコアモジュールをテスト
        import core.plugin_base
        import editor.image_editor
        import plugins.basic.basic_plugin
        import plugins.density.density_plugin
        import plugins.filters.filters_plugin
        import plugins.advanced.advanced_plugin
        import ui.main_window
        import utils.image_utils
        print("✅ 全ての既存モジュールのインポートが成功")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_basic_functionality():
    """基本機能のテスト（GUI起動なし）"""
    print("🔍 基本機能テスト開始...")
    
    try:
        # PYTHONPATHを設定してsrcディレクトリを追加
        import sys
        import os
        src_path = os.path.join(os.getcwd(), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # サンプル画像の存在確認
        sample_image = Path("SampleImage/IMG_1307.jpeg")
        if not sample_image.exists():
            print(f"❌ サンプル画像が見つかりません: {sample_image}")
            return False
        print(f"✅ サンプル画像確認: {sample_image}")
        
        # プラグインシステムの基本テスト
        from core.plugin_base import ImageProcessorPlugin, PluginManager
        from plugins.basic.basic_plugin import BasicAdjustmentPlugin
        
        # プラグインマネージャー作成テスト
        manager = PluginManager()
        print("✅ プラグインマネージャー作成成功")
        
        # プラグインインスタンス作成テスト
        plugin = BasicAdjustmentPlugin()
        print("✅ プラグインインスタンス作成成功")
        
        # プラグイン登録テスト
        manager.register_plugin(plugin)
        print("✅ プラグイン登録成功")
        
        return True
    except Exception as e:
        print(f"❌ 基本機能テストエラー: {e}")
        return False

def test_gui_startup():
    """GUI起動テスト（短時間で終了）"""
    print("🔍 GUI起動テスト開始...")
    
    # Python実行パスを取得
    python_path = "/Users/tinoue/Development.local/app/advanced-image-editor/.venv/bin/python"
    
    try:
        # main_plugin.pyを非対話モードで起動
        process = subprocess.Popen(
            [python_path, "src/main_plugin.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 3秒待機（起動確認）
        time.sleep(3)
        
        # プロセスが動作中か確認
        if process.poll() is None:
            print("✅ GUI アプリケーション正常起動")
            # プロセス終了
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ GUI起動失敗:")
            print(f"stdout: {stdout[:500]}...")
            print(f"stderr: {stderr[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ GUI起動テストエラー: {e}")
        return False

def test_directory_structure():
    """新しいディレクトリ構造の確認"""
    print("🔍 新しいディレクトリ構造テスト...")
    
    required_dirs = [
        "contracts",
        "contracts/schemas", 
        "contracts/api",
        "data",
        "data/db",
        "data/raw", 
        "data/processed",
        "scripts",
        "scripts/experiments",
        "scripts/etl"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} が見つかりません")
            all_exist = False
    
    return all_exist

def main():
    """メインテスト実行"""
    print("🚀 Phase 0 動作確認テスト開始")
    print("=" * 50)
    
    # カレントディレクトリ確認
    current_dir = os.getcwd()
    print(f"📁 実行ディレクトリ: {current_dir}")
    
    # テスト実行
    tests = [
        ("ディレクトリ構造確認", test_directory_structure),
        ("基本インポート", test_imports),
        ("基本機能", test_basic_functionality),
        ("GUI起動", test_gui_startup)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name}テスト...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}テスト中にエラー: {e}")
            results[test_name] = False
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 全てのテストが通過しました！Phase 0の構造追加は成功です。")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました。確認が必要です。")
        return 1

if __name__ == "__main__":
    sys.exit(main())