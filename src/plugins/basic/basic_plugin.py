#!/usr/bin/env python3
"""
基本調整プラグイン - Basic Adjustment Plugin

明度、コントラスト、彩度の基本的な画像調整を提供
"""

from PIL import Image, ImageEnhance
import customtkinter as ctk
from typing import Dict, Any

# 相対インポートでcore moduleを使用
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_base import ImageProcessorPlugin, PluginUIHelper


class BasicAdjustmentPlugin(ImageProcessorPlugin):
    """基本調整プラグイン"""
    
    def __init__(self):
        super().__init__("basic_adjustment", "1.0.0")
        self.brightness_value = 0
        self.contrast_value = 0
        self.saturation_value = 0
        
    def get_display_name(self) -> str:
        return "基本調整"
    
    def get_description(self) -> str:
        return "明度、コントラスト、彩度の基本的な画像調整を提供します"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """基本調整UIを作成"""
        
        # 明度調整
        self._sliders['brightness'], self._labels['brightness'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="明度",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_brightness_change,
            value_format="{:.0f}"
        )
        
        # コントラスト調整
        self._sliders['contrast'], self._labels['contrast'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="コントラスト",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_contrast_change,
            value_format="{:.0f}"
        )
        
        # 彩度調整
        self._sliders['saturation'], self._labels['saturation'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="彩度",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_saturation_change,
            value_format="{:.0f}"
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent=parent,
            text="リセット",
            command=self.reset_parameters
        )
    
    def _on_brightness_change(self, value: float) -> None:
        """明度値変更時の処理"""
        old_value = self.brightness_value
        self.brightness_value = int(value)
        
        # 【UIアプリ重要対策】詳細ログで値の変化を監視（本番では削除可能）
        # スライダーの挙動問題をデバッグするための仕組み
        print(f"🔆 明度コールバック: 受信値={value:.3f}, 設定値={self.brightness_value}, 前回値={old_value}")
        
        # 【エラー検出】範囲外チェック（CustomTkinter特有の問題検出用）
        if value < -100 or value > 100:
            print(f"⚠️ 明度値が範囲外: {value:.3f} (有効範囲: -100〜100)")
        
        # 【コールバック最適化】基底クラスの統一コールバックシステムを使用
        # 画像処理の実行をトリガーする
        self._on_parameter_change()
    
    def _on_contrast_change(self, value: float) -> None:
        """コントラスト値変更時の処理"""
        self.contrast_value = int(value)
        print(f"📊 コントラスト値更新: {self.contrast_value}")
        self._on_parameter_change()
    
    def _on_saturation_change(self, value: float) -> None:
        """彩度値変更時の処理"""
        self.saturation_value = int(value)
        print(f"🌈 彩度値更新: {self.saturation_value}")
        self._on_parameter_change()
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """基本調整を適用"""
        try:
            if not image:
                return image
            
            print(f"🔄 基本調整開始...")
            result_image = image.copy()
            
            # 明度調整
            if self.brightness_value != 0:
                print(f"🔆 明度調整: {self.brightness_value}")
                brightness_factor = (self.brightness_value + 100) / 100.0
                enhancer = ImageEnhance.Brightness(result_image)
                result_image = enhancer.enhance(brightness_factor)
            
            # コントラスト調整
            if self.contrast_value != 0:
                print(f"📊 コントラスト調整: {self.contrast_value}")
                contrast_factor = (self.contrast_value + 100) / 100.0
                enhancer = ImageEnhance.Contrast(result_image)
                result_image = enhancer.enhance(contrast_factor)
            
            # 彩度調整
            if self.saturation_value != 0:
                print(f"🌈 彩度調整: {self.saturation_value}")
                saturation_factor = (self.saturation_value + 100) / 100.0
                enhancer = ImageEnhance.Color(result_image)
                result_image = enhancer.enhance(saturation_factor)
            
            print(f"✅ 基本調整完了")
            return result_image
            
        except Exception as e:
            print(f"❌ 基本調整エラー: {e}")
            return image
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        print(f"🔄 基本調整パラメータリセット")
        
        # まず基底クラスのリセットを実行（スライダーの値をリセット）
        super().reset_parameters()
        
        # スライダーの値変更後、手動で変数を同期
        self.brightness_value = 0
        self.contrast_value = 0
        self.saturation_value = 0
        
        # スライダーの値を明示的に設定してコールバックを強制実行
        if 'brightness' in self._sliders:
            self._sliders['brightness'].set(0)
        if 'contrast' in self._sliders:
            self._sliders['contrast'].set(0)
        if 'saturation' in self._sliders:
            self._sliders['saturation'].set(0)
        
        # パラメータ変更を通知
        self._on_parameter_change()
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'brightness': self.brightness_value,
            'contrast': self.contrast_value,
            'saturation': self.saturation_value
        }