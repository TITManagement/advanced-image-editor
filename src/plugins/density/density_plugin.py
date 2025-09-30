#!/usr/bin/env python3
"""
濃度調整プラグイン - Density Adjustment Plugin

ガンマ補正、シャドウ/ハイライト調整、色温度調整を提供
"""

import numpy as np
import cv2
from PIL import Image
import customtkinter as ctk
from typing import Dict, Any, Union

# 相対インポートでcore moduleを使用
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_base import ImageProcessorPlugin, PluginUIHelper

# カーブエディタのインポート
try:
    from ui.curve_editor import CurveEditor
    CURVE_EDITOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ カーブエディタインポート警告: {e}")
    CURVE_EDITOR_AVAILABLE = False


class DensityAdjustmentPlugin(ImageProcessorPlugin):
    def set_update_image_callback(self, callback):
        """画像表示コールバックをセット"""
        self.update_image_callback = callback

    def on_histogram_equalization(self):
        """ヒストグラム均等化ボタンのイベントハンドラ"""
        if hasattr(self, 'histogram_callback') and callable(self.histogram_callback):
            self.histogram_callback()
        else:
            print("[DEBUG] histogram_callback 未設定: ヒストグラム均等化は実行されません")
    def set_image(self, image: Image.Image):
        """外部から画像をセットするためのメソッド"""
        self.image = image
        print(f"[DEBUG] set_image: self.image={{type(self.image)}}")
        self._on_parameter_change()  # 画像セット時に即座にUI反映

    def on_curve_change(self, curve_data):
        """ガンマカーブ変更時のコールバック"""
        print(f"[DEBUG] on_curve_change: curve_data={curve_data[:5]} ... {curve_data[-5:]}")
        self.gamma_lut = curve_data  # LUTを保存
        self._on_parameter_change()
    def setup_main_ui(self, parent):
        """濃度調整タブのUI部品生成（main_plugin.pyから呼び出される）"""
        self.create_ui(parent)
    def create_ui(self, parent):
        print("[DEBUG] DensityAdjustmentPlugin.create_ui called", parent, type(parent))
        try:
            print(f"[DEBUG] parent.winfo_children(before): {parent.winfo_children()}")
            print(f"[DEBUG] parent.winfo_geometry(before): {parent.winfo_geometry()}")
        except Exception as e:
            print(f"[DEBUG] parent info error (before): {e}")
        """濃度調整タブのUI部品生成（analysis_plugin.pyの方針に準拠）"""
        if not hasattr(self, '_sliders'):
            self._sliders = {}
        if not hasattr(self, '_labels'):
            self._labels = {}
        if not hasattr(self, '_buttons'):
            self._buttons = {}

        # --- カーブエディタ（常時表示） ---
        if CURVE_EDITOR_AVAILABLE:
            self.gamma_curve_frame = ctk.CTkFrame(parent)
            self.gamma_curve_frame.pack(side="top", fill="x", padx=5, pady=2)
            ctk.CTkLabel(self.gamma_curve_frame, text="ガンマカーブ", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(2, 0))
            self.curve_editor = CurveEditor(self.gamma_curve_frame)
            self.curve_editor.pack(fill="x", padx=5, pady=2)
            self.curve_editor.on_curve_change = self.on_curve_change

        # --- ガンマスライダーUI削除（カーブエディタのみ表示） ---

        # --- シャドウ調整（1行表示） ---
        row_shadow = ctk.CTkFrame(parent)
        row_shadow.pack(side="top", fill="x", padx=5, pady=2)
        label_shadow = ctk.CTkLabel(row_shadow, text="シャドウ", font=("Arial", 11))
        label_shadow.pack(side="left", padx=3)
        self._sliders['shadow'], self._labels['shadow'] = PluginUIHelper.create_slider_with_label(
            parent=row_shadow,
            text=None,
            from_=-100,
            to=100,
            default_value=0,
            command=self.on_shadow_change,
            value_format="{:.0f}"
        )
        self._labels['shadow'].pack(side="left", padx=6)

        # --- ハイライト調整（1行表示） ---
        row_highlight = ctk.CTkFrame(parent)
        row_highlight.pack(side="top", fill="x", padx=5, pady=2)
        label_highlight = ctk.CTkLabel(row_highlight, text="ハイライト", font=("Arial", 11))
        label_highlight.pack(side="left", padx=3)
        self._sliders['highlight'], self._labels['highlight'] = PluginUIHelper.create_slider_with_label(
            parent=row_highlight,
            text=None,
            from_=-100,
            to=100,
            default_value=0,
            command=self.on_highlight_change,
            value_format="{:.0f}"
        )
        self._labels['highlight'].pack(side="left", padx=6)

        # --- 色温度調整（1行表示） ---
        row_temp = ctk.CTkFrame(parent)
        row_temp.pack(side="top", fill="x", padx=5, pady=2)
        label_temp = ctk.CTkLabel(row_temp, text="色温度", font=("Arial", 11))
        label_temp.pack(side="left", padx=3)
        self._sliders['temperature'], self._labels['temperature'] = PluginUIHelper.create_slider_with_label(
            parent=row_temp,
            text=None,
            from_=-100,
            to=100,
            default_value=0,
            command=self.on_temperature_change,
            value_format="{:.0f}"
        )
        self._labels['temperature'].pack(side="left", padx=6)

        # --- 2値化セクション（1行表示） ---
        row_threshold = ctk.CTkFrame(parent)
        row_threshold.pack(side="top", fill="x", padx=5, pady=2)
        label_threshold = ctk.CTkLabel(row_threshold, text="閾値", font=("Arial", 11))
        label_threshold.pack(side="left", padx=3)
        self._sliders['threshold'], self._labels['threshold'] = PluginUIHelper.create_slider_with_label(
            parent=row_threshold,
            text=None,
            from_=0,
            to=255,
            default_value=127,
            command=self.on_threshold_change,
            value_format="{:.0f}"
        )
        self._labels['threshold'].pack(side="left", padx=6)
        self._buttons['binary'] = PluginUIHelper.create_button(
            row_threshold,
            text="2値化実行",
            command=lambda: (self.binary_threshold_callback() if hasattr(self, 'binary_threshold_callback') and callable(self.binary_threshold_callback) else self.on_apply_binary_threshold()) if self.image is not None else None
        )

        # --- ヒストグラム均等化 ---
        ctk.CTkLabel(parent, text="ヒストグラム均等化", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_hist = ctk.CTkFrame(parent)
        row_hist.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['histogram'] = PluginUIHelper.create_button(
            row_hist,
            text="ヒストグラム均等化",
            command=lambda: self.on_histogram_equalization() if self.image is not None else None
        )

        # --- リセットボタン ---
        row_reset = ctk.CTkFrame(parent)
        row_reset.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['reset'] = PluginUIHelper.create_button(
            row_reset,
            text="リセット",
            command=self.reset_parameters
        )

        # --- （下方のカーブエディタ生成・配置は削除） ---

    # 初期表示（カーブエディタのみ表示）
        try:
            print(f"[DEBUG] parent.winfo_children(after): {parent.winfo_children()}")
            print(f"[DEBUG] parent.winfo_geometry(after): {parent.winfo_geometry()}")
        except Exception as e:
            print(f"[DEBUG] parent info error (after): {e}")

    def _on_parameter_change(self):
        print("[DEBUG] 濃度調整 _on_parameter_change 発動")
        # 画像処理APIを呼び出し、結果を表示
        if self.image is not None:
            processed = self.process_image(self.image)
            if hasattr(self, 'update_image_callback') and callable(self.update_image_callback):
                self.update_image_callback(processed)
            else:
                print("[DEBUG] update_image_callback 未設定: 画像表示は更新されません")

    """濃度調整プラグイン"""
    def __init__(self):
        super().__init__("density_adjustment", "1.0.0")
        self.image = None
        self.gamma_value = 1.0
        self.shadow_value = 0
        self.highlight_value = 0
        self.temperature_value = 0
        self.threshold_value = 127

        # カーブエディタ用の変数
        self.use_curve_gamma = False  # カーブベースガンマ補正を使用するかどうか
        self.gamma_lut = None  # ガンマ補正用LUT

        # 個別機能の状態追跡
        self.applied_binary = False
        self.gamma_slider_frame = None
        self.gamma_curve_frame = None
        self.histogram_callback = None
        self.applied_histogram = False
        
    def process_image(self, image):
        """カーブエディタのLUTでガンマ補正＋シャドウ・ハイライト調整"""
        import numpy as np
        from PIL import Image
        print(f"[DEBUG] process_image: shadow={self.shadow_value}, highlight={self.highlight_value}")
        img_array = np.array(image)
        # --- ガンマカーブ補正 ---
        if hasattr(self, 'gamma_lut') and self.gamma_lut is not None:
            lut = self.gamma_lut
        else:
            lut = np.arange(256, dtype=np.uint8)
        print(f"[DEBUG] gamma_lut: {lut[:5]} ... {lut[-5:]}")
        for c in range(img_array.shape[2]):
            img_array[..., c] = lut[img_array[..., c]]
        # --- シャドウ・ハイライト調整 ---
        img_array = self.apply_shadow_highlight(img_array, self.shadow_value, self.highlight_value)
        result_image = Image.fromarray(img_array)
        return result_image

    def apply_shadow_highlight(self, img_array, shadow_value, highlight_value):
        import numpy as np
        print(f"[DEBUG] apply_shadow_highlight: shadow_value={shadow_value}, highlight_value={highlight_value}")
        luminance = img_array.mean(axis=2)
        shadow_mask = (luminance < 128)[:, :, np.newaxis]
        highlight_mask = (luminance >= 128)[:, :, np.newaxis]
        img_array = img_array.astype(np.int16)
        img_array_shadow = np.where(shadow_mask, np.clip(img_array + shadow_value, 0, 255), img_array)
        img_array_result = np.where(highlight_mask, np.clip(img_array_shadow + highlight_value, 0, 255), img_array_shadow)
        return img_array_result.astype(np.uint8)

    def set_histogram_callback(self, callback):
        """ヒストグラム均等化用コールバック登録"""
        self.histogram_callback = callback

    def set_threshold_callback(self, callback):
        """2値化用コールバック登録"""
        self.binary_threshold_callback = callback
    def get_display_name(self) -> str:
        return "濃度調整"
    
    def get_description(self) -> str:
        return "ガンマ補正、シャドウ/ハイライト調整、色温度調整を提供します"
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        params: Dict[str, Any] = {
            'shadow': self.shadow_value,
            'highlight': self.highlight_value,
            'temperature': self.temperature_value,
            'threshold': self.threshold_value
        }
        return params

    # --- 2値化関連 ---
    def setup_threshold_ui(self, parent):
        """2値化UI部品生成"""
        if not hasattr(self, '_sliders'):
            self._sliders = {}
        if not hasattr(self, '_labels'):
            self._labels = {}
        if not hasattr(self, '_buttons'):
            self._buttons = {}
        threshold_frame = ctk.CTkFrame(parent)
        threshold_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(threshold_frame, text="2値化", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        self._sliders['threshold'], self._labels['threshold'] = PluginUIHelper.create_slider_with_label(
            parent=threshold_frame,
            text="閾値",
            from_=0,
            to=255,
            default_value=127,
            command=self.on_threshold_change,
            value_format="{:.0f}"
        )
        self._buttons['binary'] = PluginUIHelper.create_button(
            threshold_frame,
            text="2値化実行",
            command=lambda: (self.binary_threshold_callback() if hasattr(self, 'binary_threshold_callback') and callable(self.binary_threshold_callback) else self.on_apply_binary_threshold()) if self.image is not None else None
        )

    def set_binary_threshold_callback(self, callback):
        """2値化用のコールバックを設定"""
        self.binary_threshold_callback = callback

    def process_binary_threshold(self, image: Image.Image) -> Image.Image:
        """2値化処理API"""
        return self.apply_binary_threshold(image)

    def on_threshold_change(self, value: float) -> None:
        """閾値変更時の処理（イベントハンドラ）"""
        self.threshold_value = int(value)
        if hasattr(self, '_labels') and 'threshold' in self._labels:
            self._labels['threshold'].configure(text=f"{self.threshold_value}")
        print(f"📐 閾値更新: {self.threshold_value}")
        self._on_parameter_change()

    def on_apply_binary_threshold(self) -> None:
        """2値化実行（イベントハンドラ）"""
        self.applied_binary = True
        print(f"📐 2値化実行: 閾値={self.threshold_value}")
        if hasattr(self, 'binary_threshold_callback') and callable(self.binary_threshold_callback):
            self.binary_threshold_callback()

    def on_gamma_change(self, value: float) -> None:
        """ガンマ値変更時の処理"""
        self.gamma_value = float(value)
        if hasattr(self, '_labels') and 'gamma' in self._labels:
            self._labels['gamma'].configure(text=f"{self.gamma_value:.2f}")
        print(f"🟣 ガンマ値更新: {self.gamma_value}")
        self._on_parameter_change()

    def on_shadow_change(self, value: float) -> None:
        """シャドウ値変更時の処理"""
        self.shadow_value = int(value)
        print(f"[DEBUG] on_shadow_change: value={value}, self.shadow_value={self.shadow_value}, self.image={type(self.image)}")
        if hasattr(self, '_labels') and 'shadow' in self._labels:
            self._labels['shadow'].configure(text=f"{self.shadow_value}")
        print(f"🌑 シャドウ値更新: {self.shadow_value}")
        self._on_parameter_change()

    def on_highlight_change(self, value: float) -> None:
        """ハイライト値変更時の処理"""
        self.highlight_value = int(value)
        print(f"[DEBUG] on_highlight_change: value={value}, self.highlight_value={self.highlight_value}, self.image={type(self.image)}")
        if hasattr(self, '_labels') and 'highlight' in self._labels:
            self._labels['highlight'].configure(text=f"{self.highlight_value}")
        print(f"💡 ハイライト値更新: {self.highlight_value}")
        self._on_parameter_change()

    def on_temperature_change(self, value: float) -> None:
        """色温度値変更時の処理"""
        self.temperature_value = int(value)
        if hasattr(self, '_labels') and 'temperature' in self._labels:
            self._labels['temperature'].configure(text=f"{self.temperature_value}")
        print(f"🌡️ 色温度値更新: {self.temperature_value}")
        self._on_parameter_change()

    def apply_binary_threshold(self, image: Image.Image) -> Image.Image:
        """2値化を適用"""
        try:
            print(f"📐 2値化開始: 閾値={self.threshold_value}")
            print(f"[DEBUG] threshold_value type: {type(self.threshold_value)}, value: {self.threshold_value}")
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            _, binary_image = cv2.threshold(gray_image, int(self.threshold_value), 255, cv2.THRESH_BINARY)
            binary_rgb = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2RGB)
            result_image = Image.fromarray(binary_rgb)
            print(f"✅ 2値化完了")
            return result_image
        except Exception as e:
            print(f"❌ 2値化エラー: {e}")
            return image

    def set_update_image_callback(self, callback):
        """画像表示コールバックをセット"""
        self.update_image_callback = callback


