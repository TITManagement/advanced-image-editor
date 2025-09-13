#!/usr/bin/env python3
"""
濃度調整プラグイン - Density Adjustment Plugin

ガンマ補正、シャドウ/ハイライト調整、色温度調整を提供
"""

import numpy as np
import cv2
from PIL import Image
import customtkinter as ctk
from typing import Dict, Any

# 相対インポートでcore moduleを使用
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_base import ImageProcessorPlugin, PluginUIHelper


class DensityAdjustmentPlugin(ImageProcessorPlugin):
    """濃度調整プラグイン"""
    
    def __init__(self):
        super().__init__("density_adjustment", "1.0.0")
        self.gamma_value = 1.0
        self.shadow_value = 0
        self.highlight_value = 0
        self.temperature_value = 0
        
    def get_display_name(self) -> str:
        return "濃度調整"
    
    def get_description(self) -> str:
        return "ガンマ補正、シャドウ/ハイライト調整、色温度調整を提供します"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """濃度調整UIを作成"""
        
        # ガンマ補正
        self._sliders['gamma'], self._labels['gamma'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="ガンマ補正",
            from_=0.1,
            to=3.0,
            default_value=1.0,
            command=self._on_gamma_change,
            value_format="{:.2f}"
        )
        
        # シャドウ調整
        self._sliders['shadow'], self._labels['shadow'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="シャドウ",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_shadow_change,
            value_format="{:.0f}"
        )
        
        # ハイライト調整
        self._sliders['highlight'], self._labels['highlight'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="ハイライト",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_highlight_change,
            value_format="{:.0f}"
        )
        
        # 色温度調整
        self._sliders['temperature'], self._labels['temperature'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="色温度",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_temperature_change,
            value_format="{:.0f}"
        )
        
        # ヒストグラム均等化ボタン
        self._buttons['histogram'] = PluginUIHelper.create_button(
            parent=parent,
            text="ヒストグラム均等化",
            command=self._on_histogram_equalization
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent=parent,
            text="リセット",
            command=self.reset_parameters
        )
    
    def _on_gamma_change(self, value: float) -> None:
        """ガンマ値変更時の処理"""
        self.gamma_value = float(value)
        if hasattr(self, '_labels') and 'gamma' in self._labels:
            self._labels['gamma'].configure(text=f"{self.gamma_value:.2f}")
        print(f"🔍 ガンマ値更新: {self.gamma_value:.2f}")
        self._on_parameter_change()
    
    def _on_shadow_change(self, value: float) -> None:
        """シャドウ値変更時の処理"""
        self.shadow_value = int(value)
        if hasattr(self, '_labels') and 'shadow' in self._labels:
            self._labels['shadow'].configure(text=f"{self.shadow_value}")
        print(f"🌑 シャドウ値更新: {self.shadow_value}")
        self._on_parameter_change()
    
    def _on_highlight_change(self, value: float) -> None:
        """ハイライト値変更時の処理"""
        self.highlight_value = int(value)
        if hasattr(self, '_labels') and 'highlight' in self._labels:
            self._labels['highlight'].configure(text=f"{self.highlight_value}")
        print(f"💡 ハイライト値更新: {self.highlight_value}")
        self._on_parameter_change()
    
    def _on_temperature_change(self, value: float) -> None:
        """色温度値変更時の処理"""
        self.temperature_value = int(value)
        if hasattr(self, '_labels') and 'temperature' in self._labels:
            self._labels['temperature'].configure(text=f"{self.temperature_value}")
        print(f"🌡️ 色温度値更新: {self.temperature_value}")
        self._on_parameter_change()
    
    def _on_histogram_equalization(self) -> None:
        """ヒストグラム均等化実行"""
        print(f"📊 ヒストグラム均等化実行")
        # このボタンは特別な処理として扱い、パラメータ変更コールバックを呼び出す
        if hasattr(self, 'histogram_callback'):
            self.histogram_callback()
    
    def set_histogram_callback(self, callback):
        """ヒストグラム均等化用の特別なコールバックを設定"""
        self.histogram_callback = callback
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """濃度調整を適用"""
        try:
            if not image:
                return image
            
            print(f"🔄 濃度調整開始...")
            result_image = image.copy()
            
            # NumPy配列に変換
            img_array = np.array(result_image, dtype=np.float32)
            
            # ガンマ補正
            if self.gamma_value != 1.0:
                print(f"🎯 ガンマ補正適用: {self.gamma_value}")
                img_array = img_array / 255.0
                img_array = np.power(img_array, 1.0 / self.gamma_value)
                img_array = img_array * 255.0
            
            # シャドウ/ハイライト調整
            if self.shadow_value != 0 or self.highlight_value != 0:
                print(f"🌗 シャドウ/ハイライト調整: シャドウ={self.shadow_value}, ハイライト={self.highlight_value}")
                img_array = self._apply_shadow_highlight(img_array)
            
            # 色温度調整
            if self.temperature_value != 0:
                print(f"🌡️ 色温度調整: {self.temperature_value}")
                img_array = self._apply_temperature(img_array)
            
            # 0-255の範囲にクリップ
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            result_image = Image.fromarray(img_array)
            
            print(f"✅ 濃度調整完了")
            return result_image
            
        except Exception as e:
            print(f"❌ 濃度調整エラー: {e}")
            return image
    
    def _apply_shadow_highlight(self, img_array: np.ndarray) -> np.ndarray:
        """シャドウ/ハイライト調整を適用"""
        img_normalized = img_array / 255.0
        
        # シャドウ調整（暗部を明るく）
        if self.shadow_value != 0:
            shadow_factor = self.shadow_value / 100.0
            mask = img_normalized < 0.5  # 暗部マスク
            img_normalized = np.where(mask, 
                                    img_normalized + shadow_factor * (0.5 - img_normalized), 
                                    img_normalized)
        
        # ハイライト調整（明部を暗く）  
        if self.highlight_value != 0:
            highlight_factor = self.highlight_value / 100.0
            mask = img_normalized > 0.5  # 明部マスク
            img_normalized = np.where(mask,
                                    img_normalized - highlight_factor * (img_normalized - 0.5),
                                    img_normalized)
        
        return img_normalized * 255.0
    
    def _apply_temperature(self, img_array: np.ndarray) -> np.ndarray:
        """色温度調整を適用"""
        if self.temperature_value > 0:  # 暖色系
            factor = self.temperature_value / 100.0
            img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1.0 + factor * 0.3), 0, 255)  # 赤を強化
            img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1.0 - factor * 0.2), 0, 255)  # 青を弱化
        else:  # 寒色系
            factor = abs(self.temperature_value) / 100.0
            img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1.0 - factor * 0.2), 0, 255)  # 赤を弱化
            img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1.0 + factor * 0.3), 0, 255)  # 青を強化
        
        return img_array
    
    def apply_histogram_equalization(self, image: Image.Image) -> Image.Image:
        """ヒストグラム均等化を適用"""
        try:
            print(f"📊 ヒストグラム均等化開始...")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # YUVカラースペースに変換してY（輝度）チャンネルのみ均等化
            yuv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2YUV)
            yuv_image[:, :, 0] = cv2.equalizeHist(yuv_image[:, :, 0])
            
            # BGRに戻してPIL形式に変換
            cv_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)
            result_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            
            print(f"✅ ヒストグラム均等化完了")
            return result_image
            
        except Exception as e:
            print(f"❌ ヒストグラム均等化エラー: {e}")
            return image
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        print(f"🔄 濃度調整パラメータリセット")
        
        # まず基底クラスのリセットを実行（スライダーの値をリセット）
        super().reset_parameters()
        
        # スライダーの値変更後、手動で変数を同期
        self.gamma_value = 1.0
        self.shadow_value = 0
        self.highlight_value = 0
        self.temperature_value = 0
        
        # スライダーの値を明示的に設定してコールバックを強制実行
        if 'gamma' in self._sliders:
            self._sliders['gamma'].set(1.0)
        if 'shadow' in self._sliders:
            self._sliders['shadow'].set(0)
        if 'highlight' in self._sliders:
            self._sliders['highlight'].set(0)
        if 'temperature' in self._sliders:
            self._sliders['temperature'].set(0)
        
        # パラメータ変更を通知
        self._on_parameter_change()
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        # 実際の変数値を返す（スライダーの値ではなく）
        return {
            'gamma': self.gamma_value,
            'shadow': self.shadow_value,
            'highlight': self.highlight_value,
            'temperature': self.temperature_value
        }