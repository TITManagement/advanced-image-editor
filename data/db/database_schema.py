"""
DuckDB データベース初期化とスキーマ設定

画像処理データ、実験履歴、モデル管理用のテーブルを定義
PostgreSQL移行を見据えたスキーマ設計
"""

import duckdb
from pathlib import Path
from datetime import datetime
from typing import Optional


class DatabaseManager:
    """DuckDBデータベースマネージャー"""
    
    def __init__(self, db_path: str = "data/db/advanced_image_editor.duckdb"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """データベース接続"""
        if self.connection is None:
            self.connection = duckdb.connect(str(self.db_path))
        return self.connection
    
    def close(self):
        """データベース接続を閉じる"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_schema(self):
        """データベーススキーマを初期化"""
        conn = self.connect()
        
        # 既存テーブルを削除（開発段階用）
        # conn.execute("DROP TABLE IF EXISTS processing_results CASCADE")
        # conn.execute("DROP TABLE IF EXISTS image_metadata CASCADE")
        # conn.execute("DROP TABLE IF EXISTS experiments CASCADE")
        # conn.execute("DROP TABLE IF EXISTS datasets CASCADE")
        # conn.execute("DROP TABLE IF EXISTS models CASCADE")
        
        # テーブル作成
        self._create_image_metadata_table(conn)
        self._create_processing_results_table(conn)
        self._create_datasets_table(conn)
        self._create_data_samples_table(conn)
        self._create_experiments_table(conn)
        self._create_experiment_runs_table(conn)
        self._create_models_table(conn)
        
        print("✅ データベーススキーマが初期化されました")
    
    def _create_image_metadata_table(self, conn):
        """画像メタデータテーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS image_metadata (
                id INTEGER PRIMARY KEY,
                file_path VARCHAR NOT NULL,
                file_name VARCHAR NOT NULL,
                file_size BIGINT NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                format VARCHAR NOT NULL,
                mode VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- インデックス用
                UNIQUE(file_path)
            )
        """)
    
    def _create_processing_results_table(self, conn):
        """処理結果テーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processing_results (
                id INTEGER PRIMARY KEY,
                plugin_name VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                processing_time REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT,
                
                -- 入力画像
                input_image_id INTEGER,
                FOREIGN KEY (input_image_id) REFERENCES image_metadata(id),
                
                -- 出力画像
                output_image_id INTEGER,
                FOREIGN KEY (output_image_id) REFERENCES image_metadata(id),
                
                -- パラメータ（JSON形式）
                parameters JSON,
                
                -- パイプライン関連
                pipeline_id VARCHAR,
                execution_id VARCHAR,
                step_index INTEGER
            )
        """)
    
    def _create_datasets_table(self, conn):
        """データセットテーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY,
                dataset_id VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT,
                dataset_type VARCHAR NOT NULL,
                total_samples INTEGER DEFAULT 0,
                data_path VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _create_data_samples_table(self, conn):
        """データサンプルテーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_samples (
                id INTEGER PRIMARY KEY,
                sample_id VARCHAR UNIQUE NOT NULL,
                dataset_id VARCHAR NOT NULL,
                input_path VARCHAR NOT NULL,
                target_path VARCHAR,
                metadata JSON,
                labels JSON,
                preprocessing_applied JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
            )
        """)
    
    def _create_experiments_table(self, conn):
        """実験テーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY,
                experiment_id VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT,
                model_type VARCHAR NOT NULL,
                training_dataset_id VARCHAR,
                validation_dataset_id VARCHAR,
                test_dataset_id VARCHAR,
                hyperparameters JSON,
                epochs INTEGER DEFAULT 100,
                batch_size INTEGER DEFAULT 32,
                learning_rate REAL DEFAULT 0.001,
                random_seed INTEGER DEFAULT 42,
                output_dir VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (training_dataset_id) REFERENCES datasets(dataset_id),
                FOREIGN KEY (validation_dataset_id) REFERENCES datasets(dataset_id),
                FOREIGN KEY (test_dataset_id) REFERENCES datasets(dataset_id)
            )
        """)
    
    def _create_experiment_runs_table(self, conn):
        """実験実行テーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS experiment_runs (
                id INTEGER PRIMARY KEY,
                run_id VARCHAR UNIQUE NOT NULL,
                experiment_id VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds REAL,
                training_metrics JSON,
                validation_metrics JSON,
                final_evaluation JSON,
                model_path VARCHAR,
                log_path VARCHAR,
                artifacts_path VARCHAR,
                error_message TEXT,
                error_traceback TEXT,
                
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        """)
    
    def _create_models_table(self, conn):
        """モデルテーブル作成"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY,
                model_id VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                model_type VARCHAR NOT NULL,
                version VARCHAR NOT NULL,
                source_experiment_id VARCHAR NOT NULL,
                source_run_id VARCHAR NOT NULL,
                model_path VARCHAR NOT NULL,
                model_size_bytes BIGINT NOT NULL,
                performance_metrics JSON,
                training_dataset_id VARCHAR,
                hyperparameters JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR,
                tags JSON,
                notes TEXT,
                
                FOREIGN KEY (source_experiment_id) REFERENCES experiments(experiment_id),
                FOREIGN KEY (source_run_id) REFERENCES experiment_runs(run_id),
                FOREIGN KEY (training_dataset_id) REFERENCES datasets(dataset_id)
            )
        """)
    
    def create_indexes(self):
        """パフォーマンス向上のためのインデックス作成"""
        conn = self.connect()
        
        # よく検索されるカラムにインデックス作成
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_processing_results_plugin ON processing_results(plugin_name)",
            "CREATE INDEX IF NOT EXISTS idx_processing_results_timestamp ON processing_results(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_processing_results_pipeline ON processing_results(pipeline_id)",
            "CREATE INDEX IF NOT EXISTS idx_data_samples_dataset ON data_samples(dataset_id)",
            "CREATE INDEX IF NOT EXISTS idx_experiment_runs_status ON experiment_runs(status)",
            "CREATE INDEX IF NOT EXISTS idx_experiment_runs_experiment ON experiment_runs(experiment_id)",
            "CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type)",
            "CREATE INDEX IF NOT EXISTS idx_models_created ON models(created_at)",
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        print("✅ インデックスが作成されました")
    
    def get_sample_data_queries(self):
        """サンプルデータ挿入用のクエリを取得"""
        return [
            # サンプル画像メタデータ
            """
            INSERT INTO image_metadata (file_path, file_name, file_size, width, height, format, mode)
            VALUES 
                ('SampleImage/IMG_1307.jpeg', 'IMG_1307.jpeg', 1024000, 4032, 3024, 'JPEG', 'RGB'),
                ('data/processed/IMG_1307_enhanced.jpeg', 'IMG_1307_enhanced.jpeg', 1124000, 4032, 3024, 'JPEG', 'RGB')
            """,
            
            # サンプルデータセット
            """
            INSERT INTO datasets (dataset_id, name, description, dataset_type, total_samples, data_path)
            VALUES 
                ('sample_dataset_001', 'サンプル画像データセット', '開発・テスト用の小規模データセット', 'training', 1, 'SampleImage/'),
                ('test_dataset_001', 'テスト用データセット', '機能テスト用データセット', 'test', 1, 'data/processed/')
            """,
            
            # サンプル実験
            """
            INSERT INTO experiments (experiment_id, name, description, model_type, training_dataset_id, output_dir)
            VALUES 
                ('exp_basic_001', '基本画質向上実験', '既存プラグインを使用した基本的な画質向上テスト', 'enhancement', 'sample_dataset_001', 'data/experiments/exp_basic_001')
            """
        ]


def initialize_database(db_path: str = "data/db/advanced_image_editor.duckdb"):
    """データベースを初期化する関数"""
    db_manager = DatabaseManager(db_path)
    
    try:
        # スキーマ初期化
        db_manager.initialize_schema()
        
        # インデックス作成
        db_manager.create_indexes()
        
        # サンプルデータ挿入（オプション）
        conn = db_manager.connect()
        sample_queries = db_manager.get_sample_data_queries()
        
        for query in sample_queries:
            try:
                conn.execute(query)
                print(f"✅ サンプルデータ挿入完了")
            except Exception as e:
                print(f"⚠️ サンプルデータ挿入スキップ（既存データの可能性）: {e}")
        
        # データベース情報表示
        print("\n📊 データベース情報:")
        tables = conn.execute("SHOW TABLES").fetchall()
        for table in tables:
            table_name = table[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"  📋 {table_name}: {count} レコード")
        
        return db_manager
        
    except Exception as e:
        print(f"❌ データベース初期化エラー: {e}")
        db_manager.close()
        raise
    
    finally:
        # 接続は開いたまま（使用後にクローズ）
        pass


if __name__ == "__main__":
    # スタンドアロン実行時にデータベースを初期化
    db_manager = initialize_database()
    print("\n🎉 データベース初期化が完了しました！")
    db_manager.close()