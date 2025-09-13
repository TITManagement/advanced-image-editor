#!/usr/bin/env python3
"""
フィルター処理プラグイン - Filter Processing Plugin

ガウシアンブラー、シャープニング、ノイズ除去、エンボス、エッジ検出などのフィルター処理を提供
"""

import numpy as np
import cv2
from PIL import Image, ImageFilter
import customtkinter as ctk
from typing import Dict, Any

# 相対インポートでcore moduleを使用
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_base import ImageProcessorPlugin, PluginUIHelper


class FilterProcessingPlugin(ImageProcessorPlugin):
    """フィルター処理プラグイン"""
    
    def __init__(self):
        super().__init__("filter_processing", "1.0.0")
        self.blur_strength = 0
        self.sharpen_strength = 0
        self.current_filter = "none"
        
    def get_display_name(self) -> str:
        return "フィルター処理"
    
    def get_description(self) -> str:
        return "ガウシアンブラー、シャープニング(0-10強度)、ノイズ除去などのフィルター処理を提供します"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """フィルター処理UIを作成"""
        
        # ブラー強度
        self._sliders['blur'], self._labels['blur'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="ガウシアンブラー",
            from_=0,
            to=20,
            default_value=0,
            command=self._on_blur_change,
            value_format="{:.0f}"
        )
        
        # シャープニング強度
        self._sliders['sharpen'], self._labels['sharpen'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="シャープニング",
            from_=0,
            to=10,
            default_value=0,
            command=self._on_sharpen_change,
            value_format="{:.1f}"
        )
        
        # フィルターボタン群
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(filter_frame, text="特殊フィルター", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # ノイズ除去ボタン
        self._buttons['denoise'] = PluginUIHelper.create_button(
            filter_frame,
            text="ノイズ除去",
            command=lambda: self._apply_special_filter("denoise")
        )
        
        # エンボスボタン
        self._buttons['emboss'] = PluginUIHelper.create_button(
            filter_frame,
            text="エンボス",
            command=lambda: self._apply_special_filter("emboss")
        )
        
        # エッジ検出ボタン
        self._buttons['edge'] = PluginUIHelper.create_button(
            filter_frame,
            text="エッジ検出",
            command=lambda: self._apply_special_filter("edge")
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent,
            text="リセット",
            command=self.reset_parameters
        )
    
    def _on_blur_change(self, value: float) -> None:
        """ブラー強度変更時の処理"""
        self.blur_strength = int(value)
        if hasattr(self, '_labels') and 'blur' in self._labels:
            self._labels['blur'].configure(text=f"{self.blur_strength}")
        print(f"🌀 ブラー強度更新: {self.blur_strength}")
        self._on_parameter_change()
    
    def _on_sharpen_change(self, value: float) -> None:
        """シャープニング強度変更時の処理"""
        self.sharpen_strength = float(value)
        if hasattr(self, '_labels') and 'sharpen' in self._labels:
            self._labels['sharpen'].configure(text=f"{self.sharpen_strength:.1f}")
        print(f"🔪 シャープニング強度更新: {self.sharpen_strength}")
        self._on_parameter_change()
    
    def _apply_special_filter(self, filter_type: str) -> None:
        """特殊フィルター適用"""
        self.current_filter = filter_type
        print(f"✨ 特殊フィルター適用: {filter_type}")
        if hasattr(self, 'special_filter_callback'):
            self.special_filter_callback(filter_type)
    
    def set_special_filter_callback(self, callback):
        """特殊フィルター用のコールバックを設定"""
        self.special_filter_callback = callback
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """フィルター処理を適用"""
        try:
            if not image:
                return image
            
            print(f"🔄 フィルター処理開始...")
            print(f"   📊 ブラー強度: {self.blur_strength}")
            print(f"   📊 シャープニング強度: {self.sharpen_strength}")
            
            result_image = image.copy()
            
            # ガウシアンブラー
            if self.blur_strength > 0:
                print(f"🌀 ガウシアンブラー適用: {self.blur_strength}")
                # OpenCVでガウシアンブラーを適用
                cv_image = cv2.cvtColor(np.array(result_image), cv2.COLOR_RGB2BGR)
                kernel_size = int(self.blur_strength * 2) + 1  # 奇数にする
                if kernel_size > 1:
                    cv_image = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
                    result_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
                    print(f"   ✅ ブラー適用完了: カーネルサイズ={kernel_size}")
            
            # シャープニング
            if self.sharpen_strength > 0:
                print(f"🔪 シャープニング適用: {self.sharpen_strength}")
                
                # 2段階のシャープニング処理
                if self.sharpen_strength <= 5:
                    # 軽度〜中程度: PILのUnsharpMaskを使用
                    enhancer_factor = 1.0 + (self.sharpen_strength / 2.0)
                    radius = min(2 + int(self.sharpen_strength / 3), 5)
                    percent = int(enhancer_factor * 150)
                    threshold = max(0, int(self.sharpen_strength / 5))
                    
                    result_image = result_image.filter(ImageFilter.UnsharpMask(
                        radius=radius, 
                        percent=percent, 
                        threshold=threshold
                    ))
                    print(f"   ✅ PIL シャープニング: factor={enhancer_factor:.2f}, radius={radius}, percent={percent}")
                    
                else:
                    # 強度: OpenCVカーネルベースのシャープニング
                    cv_image = cv2.cvtColor(np.array(result_image), cv2.COLOR_RGB2BGR)
                    
                    # 強力なシャープニングカーネル
                    strength = (self.sharpen_strength - 5) / 5.0  # 0-1の範囲に正規化
                    kernel = np.array([
                        [-1, -1, -1],
                        [-1, 9 + strength * 8, -1],  # 中央値を動的に調整
                        [-1, -1, -1]
                    ], dtype=np.float32)
                    
                    sharpened = cv2.filter2D(cv_image, -1, kernel)
                    result_image = Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
                    print(f"   ✅ OpenCV シャープニング: strength={strength:.2f}, center={9 + strength * 8:.2f}")
                    
                print(f"   🔪 シャープニング適用完了")
            
            print(f"✅ フィルター処理完了")
            return result_image
            
        except Exception as e:
            print(f"❌ フィルター処理エラー: {e}")
            import traceback
            traceback.print_exc()
            return image
    
    def apply_special_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """特殊フィルターを適用"""
        try:
            print(f"✨ 特殊フィルター開始: {filter_type}")
            
            if filter_type == "denoise":
                # ノイズ除去 (OpenCVのfastNlMeansDenoising)
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                denoised = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
                result_image = Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
                
            elif filter_type == "emboss":
                # エンボス効果
                result_image = image.filter(ImageFilter.EMBOSS)
                
            elif filter_type == "edge":
                # エッジ検出 (Cannyエッジ検出)
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
                edges = cv2.Canny(cv_image, 100, 200)
                # グレースケールをRGBに変換
                edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                result_image = Image.fromarray(edges_rgb)
                
            else:
                result_image = image
            
            print(f"✅ 特殊フィルター完了: {filter_type}")
            return result_image
            
        except Exception as e:
            print(f"❌ 特殊フィルターエラー ({filter_type}): {e}")
            return image
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        print(f"🔄 フィルターパラメータリセット")
        
        # まず基底クラスのリセットを実行（スライダーの値をリセット）
        super().reset_parameters()
        
        # スライダーの値変更後、手動で変数を同期
        self.blur_strength = 0
        self.sharpen_strength = 0
        self.current_filter = "none"
        
        # スライダーの値を明示的に設定してコールバックを強制実行
        if 'blur' in self._sliders:
            self._sliders['blur'].set(0)
        if 'sharpen' in self._sliders:
            self._sliders['sharpen'].set(0)
        
        # パラメータ変更を通知
        self._on_parameter_change()
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'blur': self.blur_strength,
            'sharpen': self.sharpen_strength,
            'filter': self.current_filter
        }