"""
実験基盤フレームワーク - Experiment Framework Base

機械学習実験の前処理、学習、評価を管理する基本フレームワーク
既存の画像処理プラグインと連携可能
"""

import os
import sys
import json
import time
import pickle
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import traceback

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.model_selection import train_test_split

# 既存のプラグインシステムを利用
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
try:
    from core.plugin_base import PluginManager, ImageProcessorPlugin
    from plugins.basic.basic_plugin import BasicAdjustmentPlugin
    from plugins.density.density_plugin import DensityAdjustmentPlugin
    from plugins.filters.filters_plugin import FilterPlugin
    from plugins.advanced.advanced_plugin import AdvancedProcessingPlugin
    PLUGINS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ プラグインインポート警告: {e}")
    PLUGINS_AVAILABLE = False

# スキーマ
from contracts.schemas.experiment import (
    ExperimentConfig, ExperimentRun, ExperimentStatus,
    DatasetMetadata, DataSample, EvaluationMetrics
)
from contracts.schemas.image_processing import ProcessingStatus


class ExperimentFramework:
    """実験フレームワークの基底クラス"""
    
    def __init__(self, experiment_config: ExperimentConfig):
        self.config = experiment_config
        self.experiment_dir = Path(experiment_config.output_dir)
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
        
        # ログ設定
        self.log_file = self.experiment_dir / "experiment.log"
        
        # 既存プラグインマネージャーの初期化
        self.plugin_manager = None
        if PLUGINS_AVAILABLE:
            self._initialize_plugins()
    
    def _initialize_plugins(self):
        """既存プラグインシステムを初期化"""
        try:
            self.plugin_manager = PluginManager()
            
            # 基本プラグインを登録
            plugins = [
                BasicAdjustmentPlugin(),
                DensityAdjustmentPlugin(),
                FilterPlugin(),
                AdvancedProcessingPlugin()
            ]
            
            for plugin in plugins:
                self.plugin_manager.register_plugin(plugin)
            
            self.log(f"✅ {len(plugins)}個のプラグインを登録しました")
            
        except Exception as e:
            self.log(f"⚠️ プラグイン初期化エラー: {e}")
            self.plugin_manager = None
    
    def log(self, message: str, level: str = "INFO"):
        """ログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # コンソール出力
        print(log_entry)
        
        # ファイル出力
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"⚠️ ログファイル書き込みエラー: {e}")
    
    def save_experiment_metadata(self, run_id: str, metadata: Dict[str, Any]):
        """実験メタデータ保存"""
        metadata_file = self.experiment_dir / f"metadata_{run_id}.json"
        
        try:
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            self.log(f"✅ メタデータ保存: {metadata_file}")
            
        except Exception as e:
            self.log(f"❌ メタデータ保存エラー: {e}", "ERROR")


class ImageProcessingExperiment(ExperimentFramework):
    """画像処理実験クラス"""
    
    def __init__(self, experiment_config: ExperimentConfig):
        super().__init__(experiment_config)
        self.training_data = []
        self.validation_data = []
        self.test_data = []
    
    def load_dataset(self, dataset_metadata: DatasetMetadata) -> List[DataSample]:
        """データセット読み込み"""
        self.log(f"📦 データセット読み込み開始: {dataset_metadata.name}")
        
        try:
            # データパスからサンプルを読み込み
            data_path = Path(dataset_metadata.data_path)
            samples = []
            
            if data_path.exists():
                # 画像ファイルを検索
                image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
                image_files = []
                
                for ext in image_extensions:
                    image_files.extend(data_path.glob(f"**/*{ext}"))
                    image_files.extend(data_path.glob(f"**/*{ext.upper()}"))
                
                for i, image_file in enumerate(image_files):
                    sample = DataSample(
                        sample_id=f"{dataset_metadata.dataset_id}_sample_{i:04d}",
                        dataset_id=dataset_metadata.dataset_id,
                        input_path=str(image_file),
                        metadata={
                            "file_size": image_file.stat().st_size,
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    samples.append(sample)
                
                self.log(f"✅ {len(samples)}個のサンプルを読み込みました")
            else:
                self.log(f"⚠️ データパスが見つかりません: {data_path}", "WARNING")
            
            return samples
            
        except Exception as e:
            self.log(f"❌ データセット読み込みエラー: {e}", "ERROR")
            return []
    
    def preprocess_data(self, samples: List[DataSample]) -> List[Dict[str, Any]]:
        """データ前処理"""
        self.log("🔄 データ前処理開始")
        
        processed_data = []
        
        for sample in samples:
            try:
                # 画像ファイルの基本情報を取得
                input_path = Path(sample.input_path)
                
                if input_path.exists():
                    processed_sample = {
                        "sample_id": sample.sample_id,
                        "input_path": str(input_path),
                        "metadata": sample.metadata,
                        "processed_at": datetime.now().isoformat()
                    }
                    processed_data.append(processed_sample)
                
            except Exception as e:
                self.log(f"⚠️ サンプル前処理エラー: {sample.sample_id}, {e}", "WARNING")
                continue
        
        self.log(f"✅ {len(processed_data)}個のサンプルを前処理しました")
        return processed_data
    
    def apply_processing_pipeline(self, sample_data: Dict[str, Any], 
                                plugin_params: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """既存プラグインを使用した処理パイプライン適用"""
        if not self.plugin_manager:
            self.log("⚠️ プラグインマネージャーが利用できません", "WARNING")
            return sample_data
        
        try:
            from PIL import Image
            
            # 入力画像を読み込み
            input_image = Image.open(sample_data["input_path"])
            result_image = input_image.copy()
            
            processing_results = []
            
            # 各プラグインを順次適用
            for plugin in self.plugin_manager.get_enabled_plugins():
                plugin_name = plugin.name
                
                if plugin_name in plugin_params:
                    params = plugin_params[plugin_name]
                    
                    # パラメータを設定
                    for param_name, value in params.items():
                        if param_name in plugin._sliders:
                            plugin._sliders[param_name].set(value)
                    
                    # 処理実行
                    start_time = time.time()
                    result_image = plugin.process_image(result_image, **params)
                    processing_time = time.time() - start_time
                    
                    processing_results.append({
                        "plugin": plugin_name,
                        "parameters": params,
                        "processing_time": processing_time,
                        "status": "completed"
                    })
                    
                    self.log(f"🔧 {plugin_name} 処理完了 ({processing_time:.3f}s)")
            
            # 結果画像を保存
            output_path = self.experiment_dir / "processed" / f"{sample_data['sample_id']}_processed.jpg"
            output_path.parent.mkdir(exist_ok=True)
            result_image.save(output_path)
            
            # 結果データを更新
            result_data = sample_data.copy()
            result_data.update({
                "output_path": str(output_path),
                "processing_results": processing_results,
                "total_processing_time": sum(r["processing_time"] for r in processing_results)
            })
            
            return result_data
            
        except Exception as e:
            self.log(f"❌ パイプライン処理エラー: {e}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            return sample_data
    
    def run_experiment(self, run_id: Optional[str] = None) -> ExperimentRun:
        """実験実行"""
        if not run_id:
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.log(f"🚀 実験実行開始: {run_id}")
        start_time = datetime.now()
        
        try:
            # 実験実行記録を作成
            experiment_run = ExperimentRun(
                run_id=run_id,
                experiment_id=self.config.experiment_id,
                config=self.config,
                status=ExperimentStatus.RUNNING,
                start_time=start_time
            )
            
            # データセット読み込み（サンプル）
            sample_dataset = DatasetMetadata(
                dataset_id=self.config.training_dataset_id,
                name="Training Dataset",
                dataset_type="training",
                total_samples=0,
                data_path="SampleImage/"  # サンプル画像ディレクトリ
            )
            
            samples = self.load_dataset(sample_dataset)
            processed_data = self.preprocess_data(samples)
            
            # プラグインパラメータ設定（例）
            plugin_params = {
                "basic_adjustment": {
                    "brightness": self.config.hyperparameters.get("brightness", 10.0),
                    "contrast": self.config.hyperparameters.get("contrast", 5.0),
                    "saturation": self.config.hyperparameters.get("saturation", 0.0)
                },
                "density_adjustment": {
                    "gamma": self.config.hyperparameters.get("gamma", 1.2),
                    "shadow": self.config.hyperparameters.get("shadow", -5.0),
                    "highlight": self.config.hyperparameters.get("highlight", 5.0)
                }
            }
            
            # 各サンプルに処理を適用
            results = []
            for sample_data in processed_data:
                result = self.apply_processing_pipeline(sample_data, plugin_params)
                results.append(result)
            
            # 評価実行
            evaluation_metrics = self.evaluate_results(results)
            
            # 実験終了
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            experiment_run.status = ExperimentStatus.COMPLETED
            experiment_run.end_time = end_time
            experiment_run.duration_seconds = duration
            experiment_run.final_evaluation = evaluation_metrics
            experiment_run.artifacts_path = str(self.experiment_dir)
            experiment_run.log_path = str(self.log_file)
            
            self.log(f"🎉 実験完了: {run_id} (実行時間: {duration:.2f}秒)")
            
            # 結果保存
            self.save_experiment_metadata(run_id, {
                "run_id": run_id,
                "config": self.config.dict(),
                "results": results,
                "evaluation": evaluation_metrics.dict() if evaluation_metrics else None,
                "duration_seconds": duration
            })
            
            return experiment_run
            
        except Exception as e:
            self.log(f"❌ 実験実行エラー: {e}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            
            # エラー時の実験記録更新
            experiment_run.status = ExperimentStatus.FAILED
            experiment_run.error_message = str(e)
            experiment_run.error_traceback = traceback.format_exc()
            
            return experiment_run
    
    def evaluate_results(self, results: List[Dict[str, Any]]) -> Optional[EvaluationMetrics]:
        """結果評価"""
        self.log("📊 結果評価開始")
        
        try:
            # 基本的な処理性能指標を計算
            processing_times = [r.get("total_processing_time", 0) for r in results]
            success_count = len([r for r in results if "output_path" in r])
            
            avg_processing_time = np.mean(processing_times) if processing_times else 0
            success_rate = success_count / len(results) if results else 0
            
            # カスタム評価指標
            custom_metrics = {
                "samples_processed": len(results),
                "success_count": success_count,
                "success_rate": success_rate,
                "avg_processing_time": avg_processing_time,
                "total_processing_time": sum(processing_times)
            }
            
            evaluation_metrics = EvaluationMetrics(
                accuracy=success_rate,
                custom_metrics=custom_metrics
            )
            
            self.log(f"✅ 評価完了: 成功率 {success_rate:.2%}, 平均処理時間 {avg_processing_time:.3f}秒")
            
            return evaluation_metrics
            
        except Exception as e:
            self.log(f"❌ 評価エラー: {e}", "ERROR")
            return None


def create_sample_experiment() -> ExperimentConfig:
    """サンプル実験設定を作成"""
    experiment_config = ExperimentConfig(
        experiment_id="sample_exp_001",
        name="サンプル画像処理実験",
        description="既存プラグインを使用した基本的な画像処理実験",
        model_type="enhancement",
        training_dataset_id="sample_dataset",
        hyperparameters={
            "brightness": 10.0,
            "contrast": 5.0,
            "saturation": 0.0,
            "gamma": 1.2,
            "shadow": -5.0,
            "highlight": 5.0
        },
        epochs=1,  # 画像処理の場合は1回の処理
        output_dir="data/experiments/sample_exp_001"
    )
    
    return experiment_config


if __name__ == "__main__":
    """スタンドアロン実行時のテスト"""
    print("🧪 実験フレームワークテスト開始")
    
    # サンプル実験設定を作成
    config = create_sample_experiment()
    
    # 実験インスタンス作成
    experiment = ImageProcessingExperiment(config)
    
    # 実験実行
    result = experiment.run_experiment()
    
    print(f"\n🎯 実験結果:")
    print(f"  実験ID: {result.experiment_id}")
    print(f"  実行ID: {result.run_id}")
    print(f"  ステータス: {result.status}")
    print(f"  実行時間: {result.duration_seconds:.2f}秒")
    
    if result.final_evaluation:
        print(f"  評価結果: {result.final_evaluation.custom_metrics}")
    
    print("\n🏁 実験フレームワークテスト完了")