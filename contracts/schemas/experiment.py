"""
実験・研究スキーマ - Experiment & Research Schemas

機械学習実験、データセット管理、モデル評価のためのPydanticモデル
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    """実験ステータス"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DatasetType(str, Enum):
    """データセットタイプ"""
    TRAINING = "training"
    VALIDATION = "validation"
    TEST = "test"
    INFERENCE = "inference"


class ModelType(str, Enum):
    """モデルタイプ"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    SEGMENTATION = "segmentation"
    DETECTION = "detection"
    ENHANCEMENT = "enhancement"


# =============================================================================
# データセット管理
# =============================================================================

class DatasetMetadata(BaseModel):
    """データセットメタデータ"""
    dataset_id: str = Field(..., description="データセットID")
    name: str = Field(..., description="データセット名")
    description: Optional[str] = Field(None, description="データセットの説明")
    dataset_type: DatasetType = Field(..., description="データセットタイプ")
    total_samples: int = Field(..., ge=0, description="総サンプル数")
    data_path: str = Field(..., description="データ保存パス")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")

    class Config:
        schema_extra = {
            "example": {
                "dataset_id": "image_enhancement_001",
                "name": "画像品質向上データセット",
                "description": "低品質画像から高品質画像への変換データセット",
                "dataset_type": "training",
                "total_samples": 10000,
                "data_path": "/data/datasets/enhancement_v1",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class DataSample(BaseModel):
    """データサンプル"""
    sample_id: str = Field(..., description="サンプルID")
    dataset_id: str = Field(..., description="所属データセットID")
    input_path: str = Field(..., description="入力データパス")
    target_path: Optional[str] = Field(None, description="ターゲットデータパス（教師あり学習用）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="サンプル固有のメタデータ")
    labels: Optional[Dict[str, Any]] = Field(None, description="ラベル情報")
    preprocessing_applied: List[str] = Field(default_factory=list, description="適用済み前処理のリスト")

    class Config:
        schema_extra = {
            "example": {
                "sample_id": "sample_001",
                "dataset_id": "image_enhancement_001",
                "input_path": "/data/input/low_quality_001.jpg",
                "target_path": "/data/target/high_quality_001.jpg",
                "metadata": {
                    "original_width": 1920,
                    "original_height": 1080,
                    "compression_quality": 60
                },
                "labels": {
                    "quality_score": 3.5,
                    "noise_level": "medium"
                },
                "preprocessing_applied": ["resize", "normalize"]
            }
        }


# =============================================================================
# 実験設定
# =============================================================================

class ExperimentConfig(BaseModel):
    """実験設定"""
    experiment_id: str = Field(..., description="実験ID")
    name: str = Field(..., description="実験名")
    description: Optional[str] = Field(None, description="実験の説明")
    model_type: ModelType = Field(..., description="使用するモデルタイプ")
    
    # データセット設定
    training_dataset_id: str = Field(..., description="訓練データセットID")
    validation_dataset_id: Optional[str] = Field(None, description="検証データセットID")
    test_dataset_id: Optional[str] = Field(None, description="テストデータセットID")
    
    # ハイパーパラメータ
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="ハイパーパラメータ")
    
    # 訓練設定
    epochs: int = Field(default=100, ge=1, description="エポック数")
    batch_size: int = Field(default=32, ge=1, description="バッチサイズ")
    learning_rate: float = Field(default=0.001, gt=0, description="学習率")
    
    # その他設定
    random_seed: int = Field(default=42, description="ランダムシード")
    output_dir: str = Field(..., description="出力ディレクトリ")
    
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")

    class Config:
        schema_extra = {
            "example": {
                "experiment_id": "exp_enhancement_001",
                "name": "基本画像品質向上実験",
                "description": "既存の画像処理プラグインを使用した品質向上手法の検証",
                "model_type": "enhancement",
                "training_dataset_id": "image_enhancement_001",
                "validation_dataset_id": "image_enhancement_val_001",
                "hyperparameters": {
                    "model_architecture": "unet",
                    "loss_function": "mse",
                    "optimizer": "adam"
                },
                "epochs": 50,
                "batch_size": 16,
                "learning_rate": 0.0001,
                "random_seed": 42,
                "output_dir": "/experiments/exp_enhancement_001",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


# =============================================================================
# 実験実行結果
# =============================================================================

class EvaluationMetrics(BaseModel):
    """評価指標"""
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="精度")
    precision: Optional[float] = Field(None, ge=0, le=1, description="適合率")
    recall: Optional[float] = Field(None, ge=0, le=1, description="再現率")
    f1_score: Optional[float] = Field(None, ge=0, le=1, description="F1スコア")
    
    # 画像品質指標
    psnr: Optional[float] = Field(None, description="PSNR")
    ssim: Optional[float] = Field(None, ge=0, le=1, description="SSIM")
    mse: Optional[float] = Field(None, ge=0, description="平均二乗誤差")
    
    # カスタム指標
    custom_metrics: Dict[str, float] = Field(default_factory=dict, description="カスタム評価指標")

    class Config:
        schema_extra = {
            "example": {
                "accuracy": 0.95,
                "precision": 0.92,
                "recall": 0.89,
                "f1_score": 0.905,
                "psnr": 28.5,
                "ssim": 0.85,
                "mse": 0.0123,
                "custom_metrics": {
                    "visual_quality_score": 4.2,
                    "processing_speed_fps": 30.5
                }
            }
        }


class ExperimentRun(BaseModel):
    """実験実行記録"""
    run_id: str = Field(..., description="実行ID")
    experiment_id: str = Field(..., description="実験ID")
    config: ExperimentConfig = Field(..., description="使用した実験設定")
    
    # 実行状態
    status: ExperimentStatus = Field(..., description="実行ステータス")
    start_time: datetime = Field(default_factory=datetime.now, description="開始時間")
    end_time: Optional[datetime] = Field(None, description="終了時間")
    duration_seconds: Optional[float] = Field(None, ge=0, description="実行時間（秒）")
    
    # 結果
    training_metrics: Dict[str, List[float]] = Field(default_factory=dict, description="訓練時の指標履歴")
    validation_metrics: Dict[str, List[float]] = Field(default_factory=dict, description="検証時の指標履歴")
    final_evaluation: Optional[EvaluationMetrics] = Field(None, description="最終評価結果")
    
    # ファイル
    model_path: Optional[str] = Field(None, description="保存されたモデルのパス")
    log_path: Optional[str] = Field(None, description="ログファイルのパス")
    artifacts_path: Optional[str] = Field(None, description="生成物保存パス")
    
    # エラー情報
    error_message: Optional[str] = Field(None, description="エラーメッセージ（失敗時）")
    error_traceback: Optional[str] = Field(None, description="エラートレースバック")

    class Config:
        schema_extra = {
            "example": {
                "run_id": "run_001",
                "experiment_id": "exp_enhancement_001",
                "status": "completed",
                "start_time": "2024-01-01T12:00:00Z",
                "end_time": "2024-01-01T14:30:00Z",
                "duration_seconds": 9000.0,
                "training_metrics": {
                    "loss": [0.5, 0.3, 0.2, 0.15],
                    "accuracy": [0.7, 0.8, 0.85, 0.9]
                },
                "validation_metrics": {
                    "loss": [0.6, 0.35, 0.25, 0.2],
                    "accuracy": [0.65, 0.75, 0.8, 0.85]
                },
                "final_evaluation": {
                    "accuracy": 0.85,
                    "psnr": 28.5,
                    "ssim": 0.85
                },
                "model_path": "/experiments/exp_enhancement_001/model.pkl",
                "log_path": "/experiments/exp_enhancement_001/training.log",
                "error_message": None
            }
        }


# =============================================================================
# モデル管理
# =============================================================================

class ModelMetadata(BaseModel):
    """モデルメタデータ"""
    model_id: str = Field(..., description="モデルID")
    name: str = Field(..., description="モデル名")
    model_type: ModelType = Field(..., description="モデルタイプ")
    version: str = Field(..., description="モデルバージョン")
    
    # 実験情報
    source_experiment_id: str = Field(..., description="元となった実験ID")
    source_run_id: str = Field(..., description="元となった実行ID")
    
    # ファイル情報
    model_path: str = Field(..., description="モデルファイルパス")
    model_size_bytes: int = Field(..., ge=0, description="モデルファイルサイズ")
    
    # 性能情報
    performance_metrics: EvaluationMetrics = Field(..., description="性能指標")
    
    # メタデータ
    training_dataset_id: str = Field(..., description="訓練に使用したデータセットID")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="使用したハイパーパラメータ")
    
    # 管理情報
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    created_by: Optional[str] = Field(None, description="作成者")
    tags: List[str] = Field(default_factory=list, description="タグ")
    notes: Optional[str] = Field(None, description="備考")

    class Config:
        schema_extra = {
            "example": {
                "model_id": "model_enhancement_v1_0",
                "name": "画像品質向上モデル v1.0",
                "model_type": "enhancement",
                "version": "1.0.0",
                "source_experiment_id": "exp_enhancement_001",
                "source_run_id": "run_001",
                "model_path": "/models/enhancement_v1_0.pkl",
                "model_size_bytes": 15728640,
                "performance_metrics": {
                    "accuracy": 0.85,
                    "psnr": 28.5,
                    "ssim": 0.85
                },
                "training_dataset_id": "image_enhancement_001",
                "hyperparameters": {
                    "model_architecture": "unet",
                    "learning_rate": 0.0001,
                    "batch_size": 16
                },
                "created_at": "2024-01-01T12:00:00Z",
                "created_by": "researcher_001",
                "tags": ["enhancement", "baseline", "production"],
                "notes": "最初の実用レベルモデル"
            }
        }