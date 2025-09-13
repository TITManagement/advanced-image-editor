#!/usr/bin/env python3
"""
高度処理プラグイン - Advanced Processing Plugin

モルフォロジー演算、輪郭検出、画像変形などの高度な画像処理を提供
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


class AdvancedProcessingPlugin(ImageProcessorPlugin):
    """高度処理プラグイン"""
    
    def __init__(self):
        super().__init__("advanced_processing", "1.0.0")
        self.morph_type = "none"
        self.morph_kernel_size = 5
        self.threshold_value = 127
        
    def get_display_name(self) -> str:
        return "高度処理"
    
    def get_description(self) -> str:
        return "モルフォロジー演算、輪郭検出、2値化などの高度な画像処理を提供します"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """高度処理UIを作成"""
        
        # モルフォロジー演算
        morph_frame = ctk.CTkFrame(parent)
        morph_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(morph_frame, text="モルフォロジー演算", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # カーネルサイズ
        self._sliders['kernel'], self._labels['kernel'] = PluginUIHelper.create_slider_with_label(
            parent=morph_frame,
            text="カーネルサイズ",
            from_=3,
            to=15,
            default_value=5,
            command=self._on_kernel_change,
            value_format="{:.0f}"
        )
        
        # モルフォロジー演算ボタン群
        morph_buttons_frame = ctk.CTkFrame(morph_frame)
        morph_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self._buttons['erosion'] = PluginUIHelper.create_button(
            morph_buttons_frame,
            text="収縮",
            command=lambda: self._apply_morphology("erosion"),
            width=80
        )
        
        self._buttons['dilation'] = PluginUIHelper.create_button(
            morph_buttons_frame,
            text="膨張",
            command=lambda: self._apply_morphology("dilation"),
            width=80
        )
        
        self._buttons['opening'] = PluginUIHelper.create_button(
            morph_buttons_frame,
            text="開放",
            command=lambda: self._apply_morphology("opening"),
            width=80
        )
        
        self._buttons['closing'] = PluginUIHelper.create_button(
            morph_buttons_frame,
            text="閉鎖",
            command=lambda: self._apply_morphology("closing"),
            width=80
        )
        
        # 2値化
        threshold_frame = ctk.CTkFrame(parent)
        threshold_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(threshold_frame, text="2値化", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 閾値スライダー
        self._sliders['threshold'], self._labels['threshold'] = PluginUIHelper.create_slider_with_label(
            parent=threshold_frame,
            text="閾値",
            from_=0,
            to=255,
            default_value=127,
            command=self._on_threshold_change,
            value_format="{:.0f}"
        )
        
        # 2値化実行ボタン
        self._buttons['binary'] = PluginUIHelper.create_button(
            threshold_frame,
            text="2値化実行",
            command=self._apply_binary_threshold
        )
        
        # その他の高度処理
        other_frame = ctk.CTkFrame(parent)
        other_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(other_frame, text="その他", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 輪郭検出ボタン
        self._buttons['contour'] = PluginUIHelper.create_button(
            other_frame,
            text="輪郭検出",
            command=self._apply_contour_detection
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent,
            text="リセット",
            command=self.reset_parameters
        )
    
    def _on_kernel_change(self, value: float) -> None:
        """カーネルサイズ変更時の処理"""
        self.morph_kernel_size = int(value)
        if self.morph_kernel_size % 2 == 0:  # 奇数にする
            self.morph_kernel_size += 1
        print(f"🔧 カーネルサイズ更新: {self.morph_kernel_size}")
    
    def _on_threshold_change(self, value: float) -> None:
        """閾値変更時の処理"""
        self.threshold_value = int(value)
        print(f"📐 閾値更新: {self.threshold_value}")
    
    def _apply_morphology(self, morph_type: str) -> None:
        """モルフォロジー演算適用"""
        self.morph_type = morph_type
        print(f"🔧 モルフォロジー演算: {morph_type}")
        if hasattr(self, 'morphology_callback'):
            self.morphology_callback(morph_type)
    
    def _apply_binary_threshold(self) -> None:
        """2値化実行"""
        print(f"📐 2値化実行: 閾値={self.threshold_value}")
        if hasattr(self, 'threshold_callback'):
            self.threshold_callback()
    
    def _apply_contour_detection(self) -> None:
        """輪郭検出実行"""
        print(f"🎯 輪郭検出実行")
        if hasattr(self, 'contour_callback'):
            self.contour_callback()
    
    def set_morphology_callback(self, callback):
        """モルフォロジー演算用のコールバックを設定"""
        self.morphology_callback = callback
    
    def set_threshold_callback(self, callback):
        """2値化用のコールバックを設定"""
        self.threshold_callback = callback
    
    def set_contour_callback(self, callback):
        """輪郭検出用のコールバックを設定"""
        self.contour_callback = callback
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """高度処理を適用（通常の処理では使用しない）"""
        # 高度処理は特殊なボタン操作で実行されるため、通常の処理では何もしない
        return image
    
    def apply_morphology_operation(self, image: Image.Image, operation: str) -> Image.Image:
        """モルフォロジー演算を適用"""
        try:
            print(f"🔧 モルフォロジー演算開始: {operation}")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # カーネル作成
            kernel = np.ones((self.morph_kernel_size, self.morph_kernel_size), np.uint8)
            
            # モルフォロジー演算実行
            if operation == "erosion":
                result = cv2.erode(gray_image, kernel, iterations=1)
            elif operation == "dilation":
                result = cv2.dilate(gray_image, kernel, iterations=1)
            elif operation == "opening":
                result = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
            elif operation == "closing":
                result = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
            else:
                result = gray_image
            
            # グレースケールをRGBに変換してPIL形式に戻す
            result_rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            result_image = Image.fromarray(result_rgb)
            
            print(f"✅ モルフォロジー演算完了: {operation}")
            return result_image
            
        except Exception as e:
            print(f"❌ モルフォロジー演算エラー ({operation}): {e}")
            return image
    
    def apply_binary_threshold(self, image: Image.Image) -> Image.Image:
        """2値化を適用"""
        try:
            print(f"📐 2値化開始: 閾値={self.threshold_value}")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 2値化実行
            _, binary_image = cv2.threshold(gray_image, self.threshold_value, 255, cv2.THRESH_BINARY)
            
            # グレースケールをRGBに変換してPIL形式に戻す
            binary_rgb = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)
            result_image = Image.fromarray(binary_rgb)
            
            print(f"✅ 2値化完了")
            return result_image
            
        except Exception as e:
            print(f"❌ 2値化エラー: {e}")
            return image
    
    def apply_contour_detection(self, image: Image.Image) -> Image.Image:
        """輪郭検出を適用"""
        try:
            print(f"🎯 輪郭検出開始")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 輪郭検出
            contours, _ = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 元画像に輪郭を描画
            result_image = cv_image.copy()
            cv2.drawContours(result_image, contours, -1, (0, 255, 0), 2)
            
            # PIL形式に戻す
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            
            print(f"✅ 輪郭検出完了: {len(contours)}個の輪郭を検出")
            return final_image
            
        except Exception as e:
            print(f"❌ 輪郭検出エラー: {e}")
            return image
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        print(f"🔄 高度処理パラメータリセット")
        super().reset_parameters()
        self.morph_type = "none"
        self.morph_kernel_size = 5
        self.threshold_value = 127
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'morph_type': self.morph_type,
            'kernel_size': self.morph_kernel_size,
            'threshold': self.threshold_value
        }