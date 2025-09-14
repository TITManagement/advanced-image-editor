"""
画像処理基本スキーマ - Basic Image Processing Schemas

既存の画像処理プラグインのパラメータと結果を型安全に管理するPydanticモデル
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field, field_validator


class ProcessingStatus(str, Enum):
    """処理ステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FilterType(str, Enum):
    """フィルタータイプ"""
    NONE = "none"
    BLUR = "blur"
    SHARPEN = "sharpen"
    EDGE = "edge"
    EMBOSS = "emboss"


class MorphologyType(str, Enum):
    """モルフォロジー処理タイプ"""
    NONE = "none"
    EROSION = "erosion"
    DILATION = "dilation"
    OPENING = "opening"
    CLOSING = "closing"


# =============================================================================
# 基本調整パラメータ
# =============================================================================

class BasicAdjustmentParams(BaseModel):
    """基本調整パラメータ"""
    brightness: float = Field(default=0.0, ge=-100, le=100, description="明度調整 (-100〜100)")
    contrast: float = Field(default=0.0, ge=-100, le=100, description="コントラスト調整 (-100〜100)")
    saturation: float = Field(default=0.0, ge=-100, le=100, description="彩度調整 (-100〜100)")

    class Config:
        schema_extra = {
            "example": {
                "brightness": 10.0,
                "contrast": 5.0,
                "saturation": 15.0
            }
        }


class DensityAdjustmentParams(BaseModel):
    """濃度調整パラメータ"""
    gamma: float = Field(default=1.0, ge=0.1, le=3.0, description="ガンマ値 (0.1〜3.0)")
    shadow: float = Field(default=0.0, ge=-100, le=100, description="シャドウ調整 (-100〜100)")
    highlight: float = Field(default=0.0, ge=-100, le=100, description="ハイライト調整 (-100〜100)")
    temperature: float = Field(default=0.0, ge=-100, le=100, description="色温度調整 (-100〜100)")

    class Config:
        schema_extra = {
            "example": {
                "gamma": 1.2,
                "shadow": -10.0,
                "highlight": 5.0,
                "temperature": 0.0
            }
        }


class FilterParams(BaseModel):
    """フィルター処理パラメータ"""
    blur: float = Field(default=0.0, ge=0, le=10, description="ぼかし強度 (0〜10)")
    sharpen: float = Field(default=0.0, ge=0, le=10, description="シャープネス強度 (0〜10)")
    filter_type: FilterType = Field(default=FilterType.NONE, description="フィルタータイプ")

    class Config:
        schema_extra = {
            "example": {
                "blur": 0.5,
                "sharpen": 1.2,
                "filter_type": "sharpen"
            }
        }


class AdvancedProcessingParams(BaseModel):
    """高度処理パラメータ"""
    morph_type: MorphologyType = Field(default=MorphologyType.NONE, description="モルフォロジー処理タイプ")
    kernel_size: int = Field(default=5, ge=3, le=15, description="カーネルサイズ (3〜15の奇数)")
    threshold: int = Field(default=127, ge=0, le=255, description="閾値 (0〜255)")

    @field_validator('kernel_size')
    @classmethod
    def kernel_size_must_be_odd(cls, v):
        if v % 2 == 0:
            raise ValueError('カーネルサイズは奇数である必要があります')
        return v

    class Config:
        schema_extra = {
            "example": {
                "morph_type": "opening",
                "kernel_size": 7,
                "threshold": 127
            }
        }


# =============================================================================
# 画像メタデータ
# =============================================================================

class ImageMetadata(BaseModel):
    """画像メタデータ"""
    file_path: str = Field(..., description="ファイルパス")
    file_name: str = Field(..., description="ファイル名")
    file_size: int = Field(..., ge=0, description="ファイルサイズ（バイト）")
    width: int = Field(..., ge=1, description="画像幅")
    height: int = Field(..., ge=1, description="画像高さ")
    format: str = Field(..., description="画像フォーマット (JPEG, PNG, etc.)")
    mode: str = Field(..., description="カラーモード (RGB, RGBA, L, etc.)")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")

    class Config:
        schema_extra = {
            "example": {
                "file_path": "/path/to/image.jpg",
                "file_name": "sample_image.jpg",
                "file_size": 1024000,
                "width": 1920,
                "height": 1080,
                "format": "JPEG",
                "mode": "RGB",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


# =============================================================================
# 処理結果
# =============================================================================

class ProcessingResult(BaseModel):
    """処理結果基底クラス"""
    plugin_name: str = Field(..., description="使用したプラグイン名")
    status: ProcessingStatus = Field(..., description="処理ステータス")
    processing_time: float = Field(..., ge=0, description="処理時間（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="処理実行日時")
    error_message: Optional[str] = Field(None, description="エラーメッセージ（失敗時）")

    class Config:
        schema_extra = {
            "example": {
                "plugin_name": "basic_adjustment",
                "status": "completed",
                "processing_time": 0.15,
                "timestamp": "2024-01-01T12:00:00Z",
                "error_message": None
            }
        }


class BasicAdjustmentResult(ProcessingResult):
    """基本調整処理結果"""
    parameters: BasicAdjustmentParams = Field(..., description="使用したパラメータ")
    output_metadata: ImageMetadata = Field(..., description="出力画像メタデータ")


class DensityAdjustmentResult(ProcessingResult):
    """濃度調整処理結果"""
    parameters: DensityAdjustmentParams = Field(..., description="使用したパラメータ")
    output_metadata: ImageMetadata = Field(..., description="出力画像メタデータ")


class FilterResult(ProcessingResult):
    """フィルター処理結果"""
    parameters: FilterParams = Field(..., description="使用したパラメータ")
    output_metadata: ImageMetadata = Field(..., description="出力画像メタデータ")


class AdvancedProcessingResult(ProcessingResult):
    """高度処理結果"""
    parameters: AdvancedProcessingParams = Field(..., description="使用したパラメータ")
    output_metadata: ImageMetadata = Field(..., description="出力画像メタデータ")


# =============================================================================
# パイプライン処理
# =============================================================================

class ProcessingPipeline(BaseModel):
    """処理パイプライン定義"""
    pipeline_id: str = Field(..., description="パイプラインID")
    name: str = Field(..., description="パイプライン名")
    description: Optional[str] = Field(None, description="パイプラインの説明")
    steps: List[Dict[str, Any]] = Field(..., description="処理ステップのリスト")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")

    class Config:
        schema_extra = {
            "example": {
                "pipeline_id": "standard_enhancement",
                "name": "標準画質向上パイプライン",
                "description": "基本調整とシャープネスを組み合わせた標準的な画質向上処理",
                "steps": [
                    {"plugin": "basic_adjustment", "params": {"brightness": 5, "contrast": 10}},
                    {"plugin": "filters", "params": {"sharpen": 1.5, "filter_type": "sharpen"}}
                ],
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class PipelineResult(BaseModel):
    """パイプライン実行結果"""
    pipeline_id: str = Field(..., description="実行したパイプラインID")
    execution_id: str = Field(..., description="実行ID（ユニーク）")
    input_metadata: ImageMetadata = Field(..., description="入力画像メタデータ")
    results: List[ProcessingResult] = Field(..., description="各ステップの処理結果")
    total_processing_time: float = Field(..., ge=0, description="総処理時間（秒）")
    final_output_metadata: ImageMetadata = Field(..., description="最終出力画像メタデータ")
    status: ProcessingStatus = Field(..., description="パイプライン全体のステータス")
    timestamp: datetime = Field(default_factory=datetime.now, description="実行開始日時")

    class Config:
        schema_extra = {
            "example": {
                "pipeline_id": "standard_enhancement",
                "execution_id": "exec_20240101_120000_001",
                "input_metadata": {
                    "file_path": "/input/sample.jpg",
                    "file_name": "sample.jpg",
                    "width": 1920,
                    "height": 1080,
                    "format": "JPEG"
                },
                "results": [],
                "total_processing_time": 0.35,
                "final_output_metadata": {
                    "file_path": "/output/sample_enhanced.jpg",
                    "file_name": "sample_enhanced.jpg",
                    "width": 1920,
                    "height": 1080,
                    "format": "JPEG"
                },
                "status": "completed",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }