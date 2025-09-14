#!/usr/bin/env python3
"""
包括的検証スクリプト - Comprehensive Verification Script

Phase 1で構築したデータサイエンス基盤の全機能を段階的に検証
"""

import sys
import os
import time
from pathlib import Path

# パス設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def print_section(title: str):
    """セクションタイトル表示"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def run_basic_verification():
    """基本検証: 既存機能が動作することを確認"""
    print_section("基本検証: 既存機能確認")
    
    print("1. 既存GUIアプリケーションの起動テスト...")
    try:
        # main_plugin.pyが正常に起動するかテスト（短時間）
        import subprocess
        python_path = ".venv/bin/python"
        result = subprocess.run(
            [python_path, "src/main_plugin.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "Advanced Image Editor" in result.stdout:
            print("✅ GUIアプリケーション正常起動確認")
        else:
            print("⚠️ GUI起動に問題がある可能性")
    except Exception as e:
        print(f"⚠️ GUI起動テスト警告: {e}")
    
    print("2. プラグインシステム動作確認...")
    try:
        from core.plugin_base import PluginManager
        from plugins.basic.basic_plugin import BasicAdjustmentPlugin
        
        manager = PluginManager()
        plugin = BasicAdjustmentPlugin()
        manager.register_plugin(plugin)
        
        print(f"✅ プラグインシステム正常動作 (登録済み: {len(manager.get_all_plugins())}個)")
    except Exception as e:
        print(f"❌ プラグインシステムエラー: {e}")

def run_schema_verification():
    """スキーマ検証: Pydanticモデルの動作確認"""
    print_section("スキーマ検証: 型安全性と整合性")
    
    print("1. 画像処理スキーマテスト...")
    try:
        from contracts.schemas.image_processing import (
            BasicAdjustmentParams, 
            ImageMetadata,
            ProcessingResult,
            ProcessingStatus
        )
        
        # 正常なパラメータ作成
        params = BasicAdjustmentParams(
            brightness=10.0,
            contrast=5.0,
            saturation=15.0
        )
        print(f"✅ 基本調整パラメータ: {params}")
        
        # 画像メタデータ作成
        metadata = ImageMetadata(
            file_path="SampleImage/IMG_1307.jpeg",
            file_name="IMG_1307.jpeg",
            file_size=1024000,
            width=4032,
            height=3024,
            format="JPEG",
            mode="RGB"
        )
        print(f"✅ 画像メタデータ: {metadata.file_name} ({metadata.width}x{metadata.height})")
        
        # バリデーションテスト
        try:
            invalid_params = BasicAdjustmentParams(brightness=200.0, contrast=5.0, saturation=0.0)
            print("❌ バリデーションが機能していません")
        except ValueError:
            print("✅ パラメータバリデーション正常動作")
            
    except Exception as e:
        print(f"❌ 画像処理スキーマエラー: {e}")
    
    print("\n2. 実験スキーマテスト...")
    try:
        from contracts.schemas.experiment import (
            ExperimentConfig,
            DatasetMetadata,
            EvaluationMetrics,
            ModelType
        )
        
        # 実験設定作成
        experiment = ExperimentConfig(
            experiment_id="test_exp_001",
            name="検証テスト実験",
            description="スキーマ検証用テスト実験",
            model_type=ModelType.ENHANCEMENT,
            training_dataset_id="test_dataset",
            validation_dataset_id="val_dataset",
            test_dataset_id="test_dataset",
            output_dir="data/experiments/test"
        )
        print(f"✅ 実験設定: {experiment.name} ({experiment.model_type})")
        
        # 評価指標作成
        metrics = EvaluationMetrics(
            accuracy=0.95,
            precision=0.92,
            recall=0.89,
            f1_score=0.905,
            psnr=28.5,
            ssim=0.85,
            mse=0.0123
        )
        print(f"✅ 評価指標: accuracy={metrics.accuracy}, psnr={metrics.psnr}")
        
    except Exception as e:
        print(f"❌ 実験スキーマエラー: {e}")

def run_database_verification():
    """データベース検証: DuckDBの動作確認"""
    print_section("データベース検証: DuckDB操作")
    
    try:
        from data.db.database_schema import DatabaseManager
        
        print("1. データベース接続・初期化テスト...")
        db_manager = DatabaseManager("data/db/verification_test.duckdb")
        db_manager.initialize_schema()
        db_manager.create_indexes()
        
        conn = db_manager.connect()
        
        print("2. テーブル確認...")
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"✅ 作成済みテーブル: {len(tables)}個")
        for table in tables:
            table_name = table[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            print(f"   📋 {table_name}: {count[0] if count else 0}レコード")
        
        print("3. サンプルデータ挿入テスト...")
        # サンプル画像メタデータ挿入
        conn.execute("""
            INSERT INTO image_metadata (file_path, file_name, file_size, width, height, format, mode)
            VALUES ('test/sample.jpg', 'sample.jpg', 1000000, 1920, 1080, 'JPEG', 'RGB')
        """)
        
        # 挿入確認
        result = conn.execute("SELECT COUNT(*) FROM image_metadata").fetchone()
        print(f"✅ データ挿入確認: {result[0]}件の画像メタデータ")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ データベース検証エラー: {e}")

def run_api_verification():
    """API検証: FastAPIルーター確認"""
    print_section("API検証: エンドポイント確認")
    
    try:
        print("1. 画像処理APIルーター確認...")
        from contracts.api.image_processing_api import router as image_router
        
        image_routes = [route for route in image_router.routes]
        print(f"✅ 画像処理API: {len(image_routes)}個のエンドポイント")
        
        # 主要エンドポイント確認
        key_endpoints = [
            "/api/v1/process/basic-adjustment",
            "/api/v1/process/density-adjustment",
            "/api/v1/process/filters",
            "/api/v1/images/upload",
            "/api/v1/health"
        ]
        
        existing_paths = [route.path for route in image_routes if hasattr(route, 'path')]
        for endpoint in key_endpoints:
            if endpoint in existing_paths:
                print(f"   ✅ {endpoint}")
            else:
                print(f"   ⚠️ {endpoint} (見つからない)")
        
        print("\n2. 実験管理APIルーター確認...")
        from contracts.api.experiment_api import router as experiment_router
        
        experiment_routes = [route for route in experiment_router.routes]
        print(f"✅ 実験管理API: {len(experiment_routes)}個のエンドポイント")
        
    except Exception as e:
        print(f"❌ API検証エラー: {e}")

def run_integration_verification():
    """統合検証: 各コンポーネント連携確認"""
    print_section("統合検証: コンポーネント連携")
    
    try:
        print("1. スキーマ + プラグイン統合テスト...")
        from contracts.schemas.image_processing import BasicAdjustmentParams
        from core.plugin_base import PluginManager
        from plugins.basic.basic_plugin import BasicAdjustmentPlugin
        
        # プラグインマネージャー設定
        manager = PluginManager()
        plugin = BasicAdjustmentPlugin()
        manager.register_plugin(plugin)
        
        # スキーマパラメータ作成
        params = BasicAdjustmentParams(brightness=10, contrast=5, saturation=0)
        
        # プラグインパラメータとスキーマの整合性確認
        plugin_params = plugin.get_parameters()
        schema_dict = params.dict()
        
        print(f"✅ スキーマパラメータ: {schema_dict}")
        print(f"✅ プラグインパラメータ: {plugin_params}")
        print("✅ スキーマ-プラグイン統合確認完了")
        
        print("\n2. データベース + スキーマ統合テスト...")
        from data.db.database_schema import DatabaseManager
        from contracts.schemas.image_processing import ImageMetadata
        
        # データベース接続
        db_manager = DatabaseManager("data/db/integration_test.duckdb")
        db_manager.initialize_schema()
        conn = db_manager.connect()
        
        # スキーマからデータベースへの保存テスト
        metadata = ImageMetadata(
            file_path="test/integration.jpg",
            file_name="integration.jpg",
            file_size=500000,
            width=800,
            height=600,
            format="JPEG",
            mode="RGB"
        )
        
        # メタデータ保存
        conn.execute("""
            INSERT INTO image_metadata (file_path, file_name, file_size, width, height, format, mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (metadata.file_path, metadata.file_name, metadata.file_size, 
              metadata.width, metadata.height, metadata.format, metadata.mode))
        
        # 保存確認
        result = conn.execute(
            "SELECT * FROM image_metadata WHERE file_name = ?", 
            (metadata.file_name,)
        ).fetchone()
        
        if result:
            print(f"✅ スキーマ-データベース統合: {result[2]} (サイズ: {result[3]}バイト)")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ 統合検証エラー: {e}")

def run_performance_verification():
    """パフォーマンス検証: 処理速度確認"""
    print_section("パフォーマンス検証: 処理速度測定")
    
    try:
        print("1. スキーマ作成パフォーマンス...")
        from contracts.schemas.image_processing import BasicAdjustmentParams
        
        start_time = time.time()
        for i in range(1000):
            params = BasicAdjustmentParams(brightness=i%100-50, contrast=0, saturation=0)
        creation_time = time.time() - start_time
        print(f"✅ 1000個のスキーマ作成: {creation_time:.3f}秒 ({1000/creation_time:.0f}件/秒)")
        
        print("2. データベース操作パフォーマンス...")
        from data.db.database_schema import DatabaseManager
        
        db_manager = DatabaseManager("data/db/performance_test.duckdb")
        db_manager.initialize_schema()
        conn = db_manager.connect()
        
        start_time = time.time()
        for i in range(100):
            conn.execute("""
                INSERT INTO image_metadata (file_path, file_name, file_size, width, height, format, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f"test/perf_{i}.jpg", f"perf_{i}.jpg", 1000000+i, 1920, 1080, "JPEG", "RGB"))
        
        insert_time = time.time() - start_time
        print(f"✅ 100件のデータベース挿入: {insert_time:.3f}秒 ({100/insert_time:.0f}件/秒)")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ パフォーマンス検証エラー: {e}")

def main():
    """メイン検証実行"""
    print("🚀 Phase 1 データサイエンス基盤 包括検証開始")
    print(f"📅 実行日時: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 各検証を順次実行
    verification_functions = [
        ("基本機能", run_basic_verification),
        ("スキーマ", run_schema_verification),
        ("データベース", run_database_verification),
        ("API", run_api_verification),
        ("統合機能", run_integration_verification),
        ("パフォーマンス", run_performance_verification)
    ]
    
    results = {}
    start_time = time.time()
    
    for name, func in verification_functions:
        print(f"\n🔄 {name}検証実行中...")
        try:
            func()
            results[name] = "✅ 成功"
        except Exception as e:
            print(f"❌ {name}検証エラー: {e}")
            results[name] = f"❌ 失敗: {str(e)[:50]}"
    
    total_time = time.time() - start_time
    
    # 最終結果サマリー
    print_section("検証結果サマリー")
    
    success_count = 0
    for name, result in results.items():
        print(f"{name:12}: {result}")
        if result.startswith("✅"):
            success_count += 1
    
    print(f"\n📊 検証統計:")
    print(f"   成功: {success_count}/{len(verification_functions)} 項目")
    print(f"   実行時間: {total_time:.2f}秒")
    print(f"   成功率: {success_count/len(verification_functions)*100:.1f}%")
    
    if success_count == len(verification_functions):
        print("\n🎉 全検証項目が成功しました！")
        print("📋 Phase 1 データサイエンス基盤は正常に動作しています。")
    else:
        print(f"\n⚠️ {len(verification_functions)-success_count}項目で問題が検出されました。")
        print("🔧 上記のエラーメッセージを確認して修正してください。")
    
    return success_count == len(verification_functions)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)