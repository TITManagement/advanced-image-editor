#!/usr/bin/env python3
"""
Phase 1 統合テスト - データサイエンス基盤の動作確認

Phase 1で構築した各コンポーネントの統合テスト
"""

import sys
import os
from pathlib import Path

# パスを設定
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_schema_imports():
    """スキーマのインポートテスト"""
    print("🔍 スキーマインポートテスト...")
    
    try:
        from contracts.schemas.image_processing import (
            BasicAdjustmentParams,
            DensityAdjustmentParams,
            ProcessingStatus,
            ImageMetadata
        )
        from contracts.schemas.experiment import (
            ExperimentConfig,
            DatasetMetadata,
            ModelType
        )
        print("✅ 全スキーマのインポートが成功")
        return True
    except Exception as e:
        print(f"❌ スキーマインポートエラー: {e}")
        return False

def test_schema_validation():
    """スキーマバリデーションテスト"""
    print("🔍 スキーマバリデーションテスト...")
    
    try:
        from contracts.schemas.image_processing import BasicAdjustmentParams
        
        # 正常なパラメータ
        valid_params = BasicAdjustmentParams(
            brightness=10.0,
            contrast=5.0,
            saturation=15.0
        )
        print(f"✅ 正常なパラメータ: {valid_params}")
        
        # 範囲外パラメータ（エラーになることを確認）
        try:
            invalid_params = BasicAdjustmentParams(
                brightness=200.0,  # 範囲外
                contrast=5.0,
                saturation=15.0
            )
            print("❌ バリデーションが機能していません")
            return False
        except ValueError:
            print("✅ バリデーションが正常に機能")
        
        return True
    except Exception as e:
        print(f"❌ スキーマバリデーションエラー: {e}")
        return False

def test_database_connection():
    """データベース接続テスト"""
    print("🔍 データベース接続テスト...")
    
    try:
        from data.db.database_schema import DatabaseManager
        
        # テスト用データベース
        db_manager = DatabaseManager("data/db/test.duckdb")
        db_manager.initialize_schema()
        
        # 接続テスト
        conn = db_manager.connect()
        result = conn.execute("SELECT 1 as test").fetchone()
        
        if result and result[0] == 1:
            print("✅ データベース接続成功")
            db_manager.close()
            return True
        else:
            print("❌ データベース接続結果が異常")
            return False
            
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return False

def test_api_structure():
    """API構造テスト"""
    print("🔍 API構造テスト...")
    
    try:
        from contracts.api.image_processing_api import router as image_router
        from contracts.api.experiment_api import router as experiment_router
        
        # ルーターが存在することを確認
        image_routes = len(image_router.routes)
        experiment_routes = len(experiment_router.routes)
        
        print(f"✅ 画像処理API: {image_routes}個のルート")
        print(f"✅ 実験管理API: {experiment_routes}個のルート")
        
        return True
    except Exception as e:
        print(f"❌ API構造テスト エラー: {e}")
        return False

def test_plugin_integration():
    """既存プラグインとの統合テスト"""
    print("🔍 プラグイン統合テスト...")
    
    try:
        from core.plugin_base import PluginManager
        from plugins.basic.basic_plugin import BasicAdjustmentPlugin
        
        # プラグインマネージャー作成
        manager = PluginManager()
        plugin = BasicAdjustmentPlugin()
        manager.register_plugin(plugin)
        
        # パラメータ設定テスト
        from contracts.schemas.image_processing import BasicAdjustmentParams
        params = BasicAdjustmentParams(brightness=10, contrast=5, saturation=0)
        
        print(f"✅ プラグインパラメータ: {params}")
        print("✅ プラグイン統合成功")
        
        return True
    except Exception as e:
        print(f"❌ プラグイン統合エラー: {e}")
        return False

def test_directory_structure():
    """ディレクトリ構造テスト"""
    print("🔍 ディレクトリ構造テスト...")
    
    required_dirs = [
        "contracts/schemas",
        "contracts/api", 
        "data/db",
        "data/raw",
        "data/processed",
        "scripts/experiments",
        "scripts/etl"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ 不足ディレクトリ: {missing_dirs}")
        return False
    else:
        print("✅ 全ディレクトリが存在")
        return True

def test_file_structure():
    """ファイル構造テスト"""
    print("🔍 ファイル構造テスト...")
    
    required_files = [
        "contracts/schemas/image_processing.py",
        "contracts/schemas/experiment.py",
        "contracts/api/image_processing_api.py", 
        "contracts/api/experiment_api.py",
        "data/db/database_schema.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 不足ファイル: {missing_files}")
        return False
    else:
        print("✅ 全ファイルが存在")
        return True

def test_requirements():
    """必要パッケージテスト"""
    print("🔍 必要パッケージテスト...")
    
    required_packages = [
        "pydantic",
        "fastapi", 
        "duckdb",
        "pandas",
        "numpy",
        "sklearn"  # scikit-learnのインポート名
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 不足パッケージ: {missing_packages}")
        return False
    else:
        print("✅ 全必要パッケージがインストール済み")
        return True

def main():
    """統合テストメイン実行"""
    print("🚀 Phase 1 統合テスト開始")
    print("=" * 50)
    
    tests = [
        ("ディレクトリ構造", test_directory_structure),
        ("ファイル構造", test_file_structure),
        ("必要パッケージ", test_requirements),
        ("スキーマインポート", test_schema_imports),
        ("スキーマバリデーション", test_schema_validation),
        ("データベース接続", test_database_connection),
        ("API構造", test_api_structure),
        ("プラグイン統合", test_plugin_integration)
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
    print("📊 Phase 1 統合テスト結果:")
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if passed:
            passed_tests += 1
    
    print(f"\n合計: {passed_tests}/{total_tests} テスト通過")
    
    if passed_tests == total_tests:
        print("🎉 全てのPhase 1統合テストが通過しました！")
        print("📋 構築完了:")
        print("  ✅ 契約スキーマ定義 (Pydantic)")
        print("  ✅ データベース設計 (DuckDB)")
        print("  ✅ API設計 (FastAPI)")
        print("  ✅ 実験フレームワーク基盤")
        print("  ✅ 既存プラグインとの統合")
        return 0
    else:
        print(f"⚠️ {total_tests - passed_tests}個のテストが失敗しました。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)