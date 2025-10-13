#!/usr/bin/env python3
"""
フィルター処理プラグイン - Filter Processing Plugin

ガウシアンブラー、シャープニング、ノイズ除去、エンボス、エッジ検出などのフィルター処理を提供
"""

import numpy as np
import cv2
from PIL import Image, ImageFilter
import customtkinter as ctk
import threading
from typing import Dict, Any, Optional

# 相対インポートでcore moduleを使用
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_base import ImageProcessorPlugin
from .presenter import FilterProcessingPresenter


class FilterProcessingPlugin(ImageProcessorPlugin):
    """
    フィルター処理プラグイン (FilterProcessingPlugin)
    --------------------------------------------------
    設計方針:
    - analysis_plugin.pyの設計パターンに準拠
    - 外部APIはパブリックメソッド (アンダースコアなし) として公開
    - 内部処理はプライベートメソッド (先頭にアンダースコア) として隠蔽
    - ガウシアンブラー、シャープニング、特殊フィルター、モルフォロジー演算、輪郭検出を提供

    推奨メソッド並び順:
    1. 初期化・基本情報
    2. コールバック設定（外部API）
    3. UI生成・操作（外部API）
    4. 画像処理API（外部API）
    5. イベントハンドラ・内部処理（プライベート）
    6. 特殊処理メソッド（プライベート）
    7. ヘルパーメソッド（プライベート）
    """

    # ===============================
    # 1. 初期化・基本情報
    # ===============================
    
    def __init__(self):
        super().__init__("filter_processing", "1.0.0")
        
        # --- パラメータ値（プライベート属性） ---
        self._blur_strength = 0
        self._sharpen_strength = 0.0
        self._current_filter = "none"
        self._morph_kernel_size = 5
        
        # --- 機能状態追跡 ---
        self._applied_special_filter = None
        self._applied_morphology = None
        self._applied_contour = False
        
        # --- UI要素辞書 ---
        self._sliders: Dict[str, Any] = {}
        self._labels: Dict[str, Any] = {}
        self._buttons: Dict[str, Any] = {}
        self._pending_button_states: Dict[str, str] = {}
        
        # Presenter
        self.presenter: Optional[FilterProcessingPresenter] = None
        
        # --- コールバック関数 ---
        self._parameter_change_callback = None
        self._special_filter_callback = None
        self._morphology_callback = None
        self._contour_callback = None
        self._undo_special_filter_callback = None
        self._undo_morphology_callback = None
        self._undo_contour_callback = None
        

        
    def get_display_name(self) -> str:
        """プラグインの表示名を取得"""
        return "フィルター処理"
    
    def get_description(self) -> str:
        """プラグインの説明を取得"""
        return "ガウシアンブラー、シャープニング、特殊フィルター、モルフォロジー演算、輪郭検出を提供します"

    # ===============================
    # 2. コールバック設定（外部API）
    # ===============================
    
    def set_parameter_change_callback(self, callback):
        """パラメータ変更用のコールバックを設定"""
        self._parameter_change_callback = callback
    
    def set_special_filter_callback(self, callback):
        """特殊フィルター用のコールバックを設定"""
        self._special_filter_callback = callback
    
    def set_morphology_callback(self, callback):
        """モルフォロジー演算用のコールバックを設定"""
        self._morphology_callback = callback
    
    def set_contour_callback(self, callback):
        """輪郭検出用のコールバックを設定"""
        self._contour_callback = callback
    
    def set_undo_special_filter_callback(self, callback):
        """特殊フィルターundo用のコールバックを設定"""
        self._undo_special_filter_callback = callback
    
    def set_undo_morphology_callback(self, callback):
        """モルフォロジー演算undo用のコールバックを設定"""
        self._undo_morphology_callback = callback
    
    def set_undo_contour_callback(self, callback):
        """輪郭検出undo用のコールバックを設定"""
        self._undo_contour_callback = callback

    # ===============================
    # 3. UI生成・操作（外部API）
    # ===============================

    def setup_ui(self, parent) -> None:
        if self.presenter is None:
            self.presenter = FilterProcessingPresenter(self)
        self.presenter.build(parent)

    def attach_ui(self, sliders: Dict[str, Any], labels: Dict[str, Any], buttons: Dict[str, Any]) -> None:
        self._sliders = sliders
        self._labels = labels
        self._buttons = buttons
        self._apply_pending_button_states()
    
    def create_ui(self, parent) -> None:
        """古い呼び出し互換: Presenter 経由で UI を構築"""
        self.setup_ui(parent)
        return

        # 以下は旧UI実装（互換用に残すが未使用）
        self._sliders['blur'], self._labels['blur'] = SmartSlider.create(
            parent=parent,
            text="ガウシアンブラー",
            from_=0,
            to=20,
            default_value=0,
            command=self._on_blur_change,
            value_format="{:.0f}",
            value_type=int
        )
        
        # シャープニング強度（SmartSlider使用）
        self._sliders['sharpen'], self._labels['sharpen'] = SmartSlider.create(
            parent=parent,
            text="シャープニング",
            from_=0,
            to=10,
            default_value=0,
            command=self._on_sharpen_change,
            value_format="{:.1f}",
            value_type=float
        )
        
        # フィルターボタン群
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(filter_frame, text="特殊フィルター", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # ノイズ除去セクション
        denoise_section = ctk.CTkFrame(filter_frame)
        denoise_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['denoise'] = PluginUIHelper.create_button(
            denoise_section,
            text="ノイズ除去",
            command=lambda: self._apply_special_filter("denoise"),
            width=100
        )
        self._buttons['denoise'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_denoise'] = PluginUIHelper.create_button(
            denoise_section,
            text="🔄 取消",
            command=lambda: self._undo_special_filter("denoise"),
            width=60
        )
        self._buttons['undo_denoise'].pack(side="left")
        self._buttons['undo_denoise'].configure(state="disabled")
        
        # エンボスセクション
        emboss_section = ctk.CTkFrame(filter_frame)
        emboss_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['emboss'] = PluginUIHelper.create_button(
            emboss_section,
            text="エンボス",
            command=lambda: self._apply_special_filter("emboss"),
            width=100
        )
        self._buttons['emboss'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_emboss'] = PluginUIHelper.create_button(
            emboss_section,
            text="🔄 取消",
            command=lambda: self._undo_special_filter("emboss"),
            width=60
        )
        self._buttons['undo_emboss'].pack(side="left")
        self._buttons['undo_emboss'].configure(state="disabled")
        
        # エッジ検出セクション
        edge_section = ctk.CTkFrame(filter_frame)
        edge_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['edge'] = PluginUIHelper.create_button(
            edge_section,
            text="エッジ検出",
            command=lambda: self._apply_special_filter("edge"),
            width=100
        )
        self._buttons['edge'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_edge'] = PluginUIHelper.create_button(
            edge_section,
            text="🔄 取消",
            command=lambda: self._undo_special_filter("edge"),
            width=60
        )
        self._buttons['undo_edge'].pack(side="left")
        self._buttons['undo_edge'].configure(state="disabled")
        
        # モルフォロジー演算セクション
        morph_frame = ctk.CTkFrame(parent)
        morph_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(morph_frame, text="モルフォロジー演算", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # カーネルサイズ（SmartSlider使用）
        self._sliders['kernel'], self._labels['kernel'] = SmartSlider.create(
            parent=morph_frame,
            text="カーネルサイズ",
            from_=3,
            to=15,
            default_value=5,
            command=self._on_kernel_change,
            value_format="{:.0f}",
            value_type=int
        )
        
        # モルフォロジー演算ボタン群
        morph_buttons_frame = ctk.CTkFrame(morph_frame)
        morph_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        # 操作ボタン行
        morph_ops_frame = ctk.CTkFrame(morph_buttons_frame)
        morph_ops_frame.pack(fill="x", pady=(0, 3))
        
        self._buttons['erosion'] = PluginUIHelper.create_button(
            morph_ops_frame,
            text="侵食",
            command=lambda: self._apply_morphology("erosion"),
            width=80
        )
        self._buttons['erosion'].pack(side="left", padx=(0, 2))
        
        self._buttons['dilation'] = PluginUIHelper.create_button(
            morph_ops_frame,
            text="膨張",
            command=lambda: self._apply_morphology("dilation"),
            width=80
        )
        self._buttons['dilation'].pack(side="left", padx=2)
        
        self._buttons['opening'] = PluginUIHelper.create_button(
            morph_ops_frame,
            text="開放",
            command=lambda: self._apply_morphology("opening"),
            width=80
        )
        self._buttons['opening'].pack(side="left", padx=2)
        
        self._buttons['closing'] = PluginUIHelper.create_button(
            morph_ops_frame,
            text="閉鎖",
            command=lambda: self._apply_morphology("closing"),
            width=80
        )
        self._buttons['closing'].pack(side="left", padx=(2, 0))
        
        # undoボタン行
        morph_undo_frame = ctk.CTkFrame(morph_buttons_frame)
        morph_undo_frame.pack(fill="x")
        
        self._buttons['undo_morphology'] = PluginUIHelper.create_button(
            morph_undo_frame,
            text="🔄 モルフォロジー取消",
            command=self._undo_morphology,
            width=180
        )
        self._buttons['undo_morphology'].pack(anchor="w")
        self._buttons['undo_morphology'].configure(state="disabled")
        
        # 輪郭検出セクション
        contour_frame = ctk.CTkFrame(parent)
        contour_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(contour_frame, text="輪郭検出", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 輪郭検出ボタンセクション
        contour_section = ctk.CTkFrame(contour_frame)
        contour_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['contour'] = PluginUIHelper.create_button(
            contour_section,
            text="輪郭検出",
            command=self._apply_contour_detection,
            width=100
        )
        self._buttons['contour'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_contour'] = PluginUIHelper.create_button(
            contour_section,
            text="🔄 取消",
            command=self._undo_contour,
            width=60
        )
        self._buttons['undo_contour'].pack(side="left")
        self._buttons['undo_contour'].configure(state="disabled")
    
    # ===============================
    # 5. イベントハンドラー（コールバック）
    # ===============================
    
    def _on_parameter_change(self):
        """パラメータ変更時の共通処理"""
        # フィルタープラグインでは、parameter_change_callbackを呼び出して
        # 全体の画像処理パイプラインを実行する
        if hasattr(self, '_parameter_change_callback') and self._parameter_change_callback:
            self._parameter_change_callback()
    
    def _on_blur_change(self, value: float) -> None:
        """ブラー強度変更時のコールバック"""
        self._blur_strength = int(round(value))
        self._on_parameter_change()
    
    def _on_sharpen_change(self, value: float) -> None:
        """シャープニング強度変更時のコールバック"""
        self._sharpen_strength = float(round(value, 1))
        self._on_parameter_change()
    
    def _on_kernel_change(self, value: float) -> None:
        """カーネルサイズ変更時のコールバック"""
        kernel_size = int(round(value))
        # 奇数にする
        self._morph_kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        self._on_parameter_change()

    # ===============================
    # 6. アクション・リセット処理
    # ===============================
    
    def _apply_special_filter(self, filter_type: str) -> None:
        """特殊フィルター適用"""
        self._current_filter = filter_type
        self._applied_special_filter = filter_type
        print(f"✨ 特殊フィルター適用: {filter_type}")
        
        # undoボタンを有効化
        self._enable_undo_button(f"undo_{filter_type}")
        
        if self._special_filter_callback:
            self._special_filter_callback(filter_type)
    
    def _apply_morphology(self, morph_type: str) -> None:
        """モルフォロジー演算適用"""
        self._applied_morphology = morph_type
        print(f"🔧 モルフォロジー演算: {morph_type}")
        
        # undoボタンを有効化
        self._enable_undo_button("undo_morphology")
        
        if self._morphology_callback:
            self._morphology_callback(morph_type)
    
    def _apply_contour_detection(self) -> None:
        """輪郭検出実行"""
        self._applied_contour = True
        print(f"🎯 輪郭検出実行")
        
        # undoボタンを有効化
        self._enable_undo_button("undo_contour")
        
        if self._contour_callback:
            self._contour_callback()
    
    def _enable_undo_button(self, button_name: str) -> None:
        """undoボタンを有効化"""
        self._set_button_state(button_name, ctk.NORMAL)
    
    def _disable_undo_button(self, button_name: str) -> None:
        """undoボタンを無効化"""
        self._set_button_state(button_name, ctk.DISABLED)
    
    def _get_button(self, button_name: str):
        """ボタン参照を解決"""
        button = self._buttons.get(button_name)
        if not button and self.presenter is not None:
            presenter_button = self.presenter.buttons.get(button_name)
            if presenter_button:
                self._buttons[button_name] = presenter_button
                button = presenter_button
        return button

    def _set_button_state(self, button_name: str, desired_state: str) -> None:
        """指定したundoボタンの状態を設定。未生成の場合は保留"""
        # Presenter経由の更新を優先して適用
        if self.presenter:
            try:
                updated = self.presenter.set_button_state(button_name, desired_state)
            except Exception as exc:
                print(f"[DEBUG] presenter経由のボタン状態更新失敗: {button_name} -> {desired_state}, error={exc}")
                updated = False
            if updated:
                self._pending_button_states.pop(button_name, None)
                return

        button = self._get_button(button_name)
        if not button:
            self._pending_button_states[button_name] = desired_state
            print(f"[DEBUG] undoボタン未接続のため状態を保留: {button_name} -> {desired_state}")
            return
        
        try:
            before_state = getattr(button, "cget", lambda x: None)("state")
            button.configure(state=desired_state)
            after_state = getattr(button, "cget", lambda x: None)("state")
            print(f"[DEBUG] undoボタン状態更新: {button_name} {before_state} -> {after_state}, widget={button}")
        except Exception as exc:
            print(f"[DEBUG] undoボタン状態更新失敗: {button_name} -> {desired_state}, error={exc}")
            return
        finally:
            self._pending_button_states.pop(button_name, None)

    def _apply_pending_button_states(self) -> None:
        """未適用のボタン状態を適用"""
        if not self._pending_button_states:
            return
        pending = dict(self._pending_button_states)
        for button_name, desired_state in pending.items():
            self._set_button_state(button_name, desired_state)
    
    def _undo_special_filter(self, filter_type: str) -> None:
        """特殊フィルターのundo"""
        print(f"🔄 特殊フィルター取消ボタン押下: {filter_type}")
        
        # 状態をリセット
        self._applied_special_filter = None
        self._current_filter = "none"
        
        # undoボタンを無効化
        self._disable_undo_button(f"undo_{filter_type}")
        
        # コールバックがあれば実行
        if self._undo_special_filter_callback:
            self._undo_special_filter_callback(filter_type)
    
    def _undo_morphology(self) -> None:
        """モルフォロジー演算のundo"""
        print(f"🔄 モルフォロジー取消ボタン押下")
        
        # 状態をリセット
        self._applied_morphology = None
        
        # undoボタンを無効化
        self._disable_undo_button("undo_morphology")
        
        # コールバックがあれば実行
        if self._undo_morphology_callback:
            self._undo_morphology_callback()
    
    def _undo_contour(self) -> None:
        """輪郭検出のundo"""
        print(f"🔄 輪郭取消ボタン押下")
        
        # 状態をリセット
        self._applied_contour = False
        
        # undoボタンを無効化
        self._disable_undo_button("undo_contour")
        
        # コールバックがあれば実行
        if self._undo_contour_callback:
            self._undo_contour_callback()
    

    
    # ===============================
    # 4. 画像処理API（外部API）
    # ===============================
    
    def process_image(self, image: Image.Image) -> Image.Image:
        """
        フィルター処理を適用
        
        Args:
            image (Image.Image): 処理対象の画像
            
        Returns:
            Image.Image: 処理後の画像（エラー時は元画像）
        """
        if image is None:
            self._log_error("Input image is None")
            return image
            
        try:
            processed_image = image.copy()
            
            # ガウシアンブラーの適用
            processed_image = self._apply_gaussian_blur(processed_image)
            
            # シャープニングの適用
            processed_image = self._apply_sharpening(processed_image)
            
            return processed_image
            
        except Exception as e:
            self._log_error(f"Image processing error: {e}")
            return image  # フォールバック: 元画像を返す

    def _apply_gaussian_blur(self, image: Image.Image) -> Image.Image:
        """ガウシアンブラーを適用"""
        if self._blur_strength <= 0:
            return image
        
        try:
            # カーネルサイズの計算（奇数にする）
            kernel_size = int(self._blur_strength * 2) + 1
            kernel_size = max(1, min(kernel_size, 51))  # 制限値適用 (1-51)
            
            if kernel_size <= 1:
                return image
            
            # OpenCVでガウシアンブラーを適用
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            blurred = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
            return Image.fromarray(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
            
        except Exception as e:
            self._log_error(f"Gaussian blur error: {e}")
            return image

    def _apply_sharpening(self, image: Image.Image) -> Image.Image:
        """シャープニングを適用"""
        if self._sharpen_strength <= 0:
            return image
        
        try:
            clamped_strength = max(0.0, min(self._sharpen_strength, 10.0))  # 制限値適用
            
            if clamped_strength <= 5:
                return self._apply_mild_sharpening(image, clamped_strength)
            else:
                return self._apply_strong_sharpening(image, clamped_strength)
                
        except Exception as e:
            self._log_error(f"Sharpening error: {e}")
            return image

    def _apply_mild_sharpening(self, image: Image.Image, strength: float) -> Image.Image:
        """軽度〜中程度のシャープニング（PIL UnsharpMask使用）"""
        try:
            enhancer_factor = 1.0 + (strength / 2.0)
            radius = min(2 + int(strength / 3), 5)
            percent = int(enhancer_factor * 150)
            threshold = max(0, int(strength / 5))
            
            return image.filter(ImageFilter.UnsharpMask(
                radius=radius, 
                percent=percent, 
                threshold=threshold
            ))
        except Exception as e:
            self._log_error(f"Mild sharpening error: {e}")
            return image

    def _apply_strong_sharpening(self, image: Image.Image, strength: float) -> Image.Image:
        """強度のシャープニング（OpenCVカーネル使用）"""
        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 強力なシャープニングカーネル
            normalized_strength = (strength - 5) / 5.0  # 0-1の範囲に正規化
            kernel = np.array([
                [-1, -1, -1],
                [-1, 9 + normalized_strength * 8, -1],  # 中央値を動的に調整
                [-1, -1, -1]
            ], dtype=np.float32)
            
            sharpened = cv2.filter2D(cv_image, -1, kernel)
            return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
            
        except Exception as e:
            self._log_error(f"Strong sharpening error: {e}")
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
            
            self._enable_undo_button(f"undo_{filter_type}")
            print(f"✅ 特殊フィルター完了: {filter_type}")
            return result_image
            
        except Exception as e:
            print(f"❌ 特殊フィルターエラー ({filter_type}): {e}")
            return image
    
    def apply_morphology_operation(self, image: Image.Image, operation: str) -> Image.Image:
        """モルフォロジー演算を適用"""
        try:
            print(f"🔧 モルフォロジー演算開始: {operation}")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # カーネル作成
            kernel = np.ones((self._morph_kernel_size, self._morph_kernel_size), np.uint8)
            
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
            self._enable_undo_button("undo_morphology")
            return result_image
            
        except Exception as e:
            print(f"❌ モルフォロジー演算エラー ({operation}): {e}")
            return image
    
    def apply_contour_detection(self, image: Image.Image) -> Image.Image:
        """輪郭検出を適用"""
        try:
            print(f"🎯 輪郭検出開始")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 画像の前処理で輪郭をより明確にする
            # ガウシアンブラーでノイズを軽減
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # 適応的閾値処理でエッジを強調
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 内部輪郭も含めて検出（RETR_TREEを使用）
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # 面積が小さすぎる輪郭をフィルタリング（ノイズ除去）
            min_area = 100  # 最小面積
            filtered_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    filtered_contours.append(contour)
            
            # 元画像に輪郭を描画
            result_image = cv_image.copy()
            
            # 細い輪郭線で描画（視認性を保ちつつ繊細な表現）
            cv2.drawContours(result_image, filtered_contours, -1, (0, 255, 0), 1)  # 緑色、太さ1（細線）
            
            # PIL形式に戻す
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            
            print(f"✅ 輪郭検出完了: {len(contours)}個の輪郭を検出 ({len(filtered_contours)}個を描画)")
            self._enable_undo_button("undo_contour")
            return final_image
            
        except Exception as e:
            print(f"❌ 輪郭検出エラー: {e}")
            return image
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'blur': self._blur_strength,
            'sharpen': self._sharpen_strength,
            'filter': self._current_filter,
            'kernel': self._morph_kernel_size
        }

    def reset_parameters(self) -> None:
        """全パラメータをリセット"""
        try:
            # パラメータ値をリセット
            self._blur_strength = 0
            self._sharpen_strength = 0.0
            self._current_filter = "none"
            self._morph_kernel_size = 5
            
            # 機能状態をリセット
            self._applied_special_filter = None
            self._applied_morphology = None
            self._applied_contour = False
            
            # スライダーとラベルをリセット（安全性チェック付き）
            if 'blur' in self._sliders and self._sliders['blur']:
                self._sliders['blur'].set(0)
                self._update_value_label('blur', 0)
            if 'sharpen' in self._sliders and self._sliders['sharpen']:
                self._sliders['sharpen'].set(0.0)
                self._update_value_label('sharpen', 0.0)
            if 'kernel' in self._sliders and self._sliders['kernel']:
                self._sliders['kernel'].set(5)
                self._update_value_label('kernel', 5)
            
            # undoボタンを無効化
            for button_name in ['undo_denoise', 'undo_emboss', 'undo_edge', 'undo_morphology', 'undo_contour']:
                self._disable_undo_button(button_name)
                
            print("✅ フィルター処理パラメータリセット完了")
            
        except Exception as e:
            print(f"❌ フィルターリセットエラー: {e}")
        
        self._on_parameter_change()

    # ===============================
    # 7. 内部ヘルパーメソッド（プライベート）
    # ===============================
    

    def _update_value_label(self, parameter: str, value) -> None:
        """値ラベルの更新"""
        if parameter in self._labels:
            if isinstance(value, float):
                self._labels[parameter].configure(text=f"{value:.1f}")
            else:
                self._labels[parameter].configure(text=f"{value:.0f}")
    
    def _log_error(self, message: str) -> None:
        """エラーログの出力"""
        print(f"[ERROR] FilterProcessingPlugin: {message}")
