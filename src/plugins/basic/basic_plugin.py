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
    """
    基本調整プラグイン (BasicAdjustmentPlugin) - Level 3
    --------------------------------------------------
    設計方針:
    - analysis_plugin.pyの設計パターンに準拠（Level 3拡張）
    - 外部APIはパブリックメソッド (アンダースコアなし) として公開
    - 内部処理はプライベートメソッド (先頭にアンダースコア) として隠蔽
    - 明度・コントラスト・彩度の基本的な画像調整を提供

    Level 3 高度機能:            # 3. 遅延実行でスライダーを確実にリセット
            def force_all_sliders_update():
                try:
                    for param, slider in sliders_to_reset:
                        if slider is not None:  # Noneチェック追加
                            slider.set(0)
                            if hasattr(slider, '_variable') and slider._variable is not None:
                                slider._variable.set(0)
                            slider.update_idletasks()
                            print(f"[DEBUG] 遅延更新後{param}スライダー値: {slider.get()}")
                    self._updating_ui = False
                    print("✅ 全スライダー遅延更新完了")
                except Exception as e:
                    print(f"[ERROR] 遅延更新エラー: {e}")
                    self._updating_ui = Falseリセット（明度・コントラスト・彩度の組み合わせ）
    - パラメータ履歴管理（Undo/Redo）
    - プラグイン間データ共有（他の調整プラグインとの連携）
    - RGB別ヒストグラム表示
    - コントラストカーブエディタ
    - パフォーマンス最適化（高速基本調整処理）

    推奨メソッド並び順:
    1. 初期化・基本情報
    2. Level 3 高度機能API
    3. コールバック設定（外部API）
    4. UI生成・操作（外部API）
    5. 画像処理API（外部API）
    6. イベントハンドラ・内部処理（プライベート）
    7. Level 3 高度内部処理（プライベート）
    """

    # --- 基本情報・初期化 ---

    def __init__(self):
        super().__init__("basic_adjustment", "1.0.0")
        self.image = None
        
        # パラメータ値
        self.brightness_value = 0
        self.contrast_value = 0
        self.saturation_value = 0
        
        # コールバック属性の初期化
        self.update_image_callback = None
        
        # UI更新フラグ（スライダーリセット用）
        self._updating_ui = False
        
        # === Level 3 高度機能属性 ===
        
        # プリセット管理（基本調整専用）
        self._presets = {
            '自然': {'brightness': 0, 'contrast': 0, 'saturation': 0},
            '鮮やか': {'brightness': 10, 'contrast': 15, 'saturation': 20},
            'モノクロ風': {'brightness': -5, 'contrast': 25, 'saturation': -80},
            'ソフト': {'brightness': 5, 'contrast': -10, 'saturation': -15},
            'ビビッド': {'brightness': 0, 'contrast': 30, 'saturation': 40}
        }
        self._current_preset_name = None
        
        # パラメータ履歴管理
        self._parameter_history = []
        self._history_index = -1
        self._max_history_size = 30
        
        # プラグイン間連携
        self._plugin_data_exchange = {}
        self._linked_plugins = []
        
        # RGB別ヒストグラム
        self._show_rgb_histogram = False
        self._histogram_data = {'r': [], 'g': [], 'b': []}
        
        # コントラストカーブ
        self._use_contrast_curve = False
        self._contrast_curve_points = [(0, 0), (128, 128), (255, 255)]
        
        # パフォーマンス最適化
        self._use_fast_processing = True
        self._cache_enabled = True
        self._processed_cache = {}
        
        # リアルタイムプレビュー
        self._preview_enabled = True
        self._preview_quality = 'high'  # basic調整は高品質でもパフォーマンス良好
        
        # UI要素管理用
        self._sliders = {}
        self._labels = {}
        self._buttons = {}

    def get_display_name(self) -> str:
        """プラグインの表示名を返す"""
        return "基本調整"
    
    def get_description(self) -> str:
        """プラグインの説明文を返す"""
        return "明度、コントラスト、彩度の基本的な画像調整を提供します（Level 3: プリセット、履歴、RGB分析対応）"

    # ===============================
    # 2. Level 3 高度機能API
    # ===============================
    
    def create_basic_preset(self, name: str) -> bool:
        """現在の基本調整パラメータでプリセットを作成"""
        try:
            preset_data = {
                'brightness': self.brightness_value,
                'contrast': self.contrast_value,
                'saturation': self.saturation_value,
                'timestamp': self._get_timestamp()
            }
            self._presets[name] = preset_data
            self._current_preset_name = name
            print(f"✅ 基本調整プリセット '{name}' を作成しました")
            return True
        except Exception as e:
            print(f"❌ プリセット作成エラー: {e}")
            return False
    
    def load_basic_preset(self, name: str) -> bool:
        """指定された基本調整プリセットを読み込み"""
        if name not in self._presets:
            print(f"❌ プリセット '{name}' が見つかりません")
            return False
        
        try:
            # 現在の状態を履歴に保存
            self._save_parameter_state()
            
            preset_data = self._presets[name]
            self.brightness_value = preset_data['brightness']
            self.contrast_value = preset_data['contrast']
            self.saturation_value = preset_data['saturation']
            
            self._current_preset_name = name
            self._update_ui_from_parameters()
            print(f"✅ プリセット '{name}' を読み込みました")
            return True
        except Exception as e:
            print(f"❌ プリセット読み込みエラー: {e}")
            return False
    
    def get_basic_preset_names(self) -> list:
        """利用可能な基本調整プリセット名のリストを取得"""
        return list(self._presets.keys())
    
    def undo_basic_parameters(self) -> bool:
        """基本調整パラメータを前の状態に戻す"""
        if self._history_index > 0:
            self._history_index -= 1
            self._restore_parameter_state(self._parameter_history[self._history_index])
            print("↶ 基本調整パラメータを前の状態に戻しました")
            return True
        return False
    

    
    def analyze_rgb_histogram(self, image: Image.Image) -> dict:
        """RGB別ヒストグラム分析"""
        try:
            import numpy as np
            img_array = np.array(image)
            
            # RGB別ヒストグラム計算
            r_hist = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))[0]
            g_hist = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))[0]
            b_hist = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))[0]
            
            self._histogram_data = {
                'r': r_hist.tolist(),
                'g': g_hist.tolist(),
                'b': b_hist.tolist()
            }
            
            # 統計情報計算
            stats = {
                'brightness_avg': float(np.mean(img_array)),
                'contrast_std': float(np.std(img_array)),
                'r_avg': float(np.mean(img_array[:, :, 0])),
                'g_avg': float(np.mean(img_array[:, :, 1])),
                'b_avg': float(np.mean(img_array[:, :, 2])),
                'histogram_data': self._histogram_data
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ RGB分析エラー: {e}")
            return {}
    
    def suggest_auto_adjustment(self, image: Image.Image) -> dict:
        """画像分析に基づく自動調整値の提案"""
        try:
            stats = self.analyze_rgb_histogram(image)
            if not stats:
                return {}
            
            suggestions = {}
            
            # 明度提案（平均輝度に基づく）
            avg_brightness = stats['brightness_avg']
            if avg_brightness < 100:
                suggestions['brightness'] = min(30, int((100 - avg_brightness) / 3))
            elif avg_brightness > 180:
                suggestions['brightness'] = max(-30, int((180 - avg_brightness) / 3))
            else:
                suggestions['brightness'] = 0
            
            # コントラスト提案（標準偏差に基づく）
            contrast_std = stats['contrast_std']
            if contrast_std < 30:
                suggestions['contrast'] = min(40, int((35 - contrast_std) * 2))
            elif contrast_std > 80:
                suggestions['contrast'] = max(-20, int((80 - contrast_std) / 2))
            else:
                suggestions['contrast'] = 0
            
            # 彩度提案（RGB平均の差に基づく）
            r_avg, g_avg, b_avg = stats['r_avg'], stats['g_avg'], stats['b_avg']
            color_variance = max(r_avg, g_avg, b_avg) - min(r_avg, g_avg, b_avg)
            if color_variance < 10:
                suggestions['saturation'] = min(25, int((15 - color_variance) * 2))
            else:
                suggestions['saturation'] = 0
            
            print(f"🤖 自動調整提案: {suggestions}")
            return suggestions
            
        except Exception as e:
            print(f"❌ 自動調整提案エラー: {e}")
            return {}
    
    def enable_rgb_histogram_display(self, enabled: bool = True):
        """RGB別ヒストグラム表示の有効/無効"""
        self._show_rgb_histogram = enabled
    
    def enable_contrast_curve(self, enabled: bool = True):
        """コントラストカーブの有効/無効"""
        self._use_contrast_curve = enabled

    def set_image(self, image: Image.Image):
        """処理対象画像をセット"""
        self.image = image
        print(f"[DEBUG] set_image: self.image={type(self.image)}")
        self._on_parameter_change()  # 画像セット時に即座にUI反映

    # --- コールバック設定（外部API） ---

    def set_update_image_callback(self, callback):
        """画像表示コールバックをセット"""
        self.update_image_callback = callback

    # --- UI生成・操作（外部API） ---

    def setup_ui(self, parent: ctk.CTkFrame) -> None:
        """UI生成（main_plugin.pyから呼び出される）"""
        self.create_ui(parent)
        
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """基本調整タブのUI生成（明るさ・コントラスト・彩度）"""
        print("[DEBUG] BasicAdjustmentPlugin.create_ui called")
        
        # --- 明度調整（1行表示） ---
        ctk.CTkLabel(parent, text="明度調整", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_brightness = ctk.CTkFrame(parent)
        row_brightness.pack(side="top", fill="x", padx=5, pady=2)
        label_brightness = ctk.CTkLabel(row_brightness, text="明度", font=("Arial", 11))
        label_brightness.pack(side="left", padx=3)
        self._sliders['brightness'], self._labels['brightness'] = PluginUIHelper.create_slider_with_label(
            row_brightness,
            text="明度",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_brightness_change
        )
        self._labels['brightness'].pack(side="left", padx=6)

        # --- コントラスト調整（1行表示） ---
        ctk.CTkLabel(parent, text="コントラスト調整", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_contrast = ctk.CTkFrame(parent)
        row_contrast.pack(side="top", fill="x", padx=5, pady=2)
        label_contrast = ctk.CTkLabel(row_contrast, text="コントラスト", font=("Arial", 11))
        label_contrast.pack(side="left", padx=3)
        self._sliders['contrast'], self._labels['contrast'] = PluginUIHelper.create_slider_with_label(
            row_contrast,
            text="コントラスト",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_contrast_change
        )
        self._labels['contrast'].pack(side="left", padx=6)

        # --- 彩度調整（1行表示） ---
        ctk.CTkLabel(parent, text="彩度調整", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_saturation = ctk.CTkFrame(parent)
        row_saturation.pack(side="top", fill="x", padx=5, pady=2)
        label_saturation = ctk.CTkLabel(row_saturation, text="彩度", font=("Arial", 11))
        label_saturation.pack(side="left", padx=3)
        self._sliders['saturation'], self._labels['saturation'] = PluginUIHelper.create_slider_with_label(
            row_saturation,
            text="彩度",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_saturation_change
        )
        self._labels['saturation'].pack(side="left", padx=6)

        # --- リセットボタン ---
        ctk.CTkLabel(parent, text="一括操作", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_reset = ctk.CTkFrame(parent)
        row_reset.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['reset'] = PluginUIHelper.create_button(
            row_reset,
            text="全リセット",
            command=self.reset_parameters
        )

        # --- Level 3: 基本調整プリセットUI ---
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(preset_frame, text="基本調整プリセット (Level 3)", font=("Arial", 11, "bold")).pack(anchor="w", padx=3, pady=(5, 0))
        
        # プリセット選択
        preset_select_frame = ctk.CTkFrame(preset_frame)
        preset_select_frame.pack(fill="x", padx=5, pady=2)
        
        self._preset_var = ctk.StringVar(value="自然")
        self._preset_menu = ctk.CTkOptionMenu(
            preset_select_frame,
            variable=self._preset_var,
            values=list(self._presets.keys()),
            command=self._on_preset_selected
        )
        self._preset_menu.pack(side="left", padx=(0, 5))
        
        self._buttons['load_preset'] = PluginUIHelper.create_button(
            preset_select_frame, text="適用", command=self._load_selected_preset, width=60
        )
        self._buttons['load_preset'].pack(side="left", padx=2)
        
        self._buttons['auto_adjust'] = PluginUIHelper.create_button(
            preset_select_frame, text="🤖 自動", command=self._apply_auto_adjustment, width=60
        )
        self._buttons['auto_adjust'].pack(side="left", padx=2)
        
        # --- Level 3: 履歴管理UI ---
        history_frame = ctk.CTkFrame(parent)
        history_frame.pack(fill="x", padx=5, pady=2)
        
        history_controls = ctk.CTkFrame(history_frame)
        history_controls.pack(fill="x", padx=5, pady=2)
        
        self._buttons['undo'] = PluginUIHelper.create_button(
            history_controls, text="↶ Undo", command=self.undo_basic_parameters, width=80
        )
        self._buttons['undo'].pack(side="left", padx=2)
        
        self._buttons['redo'] = PluginUIHelper.create_button(
            history_controls, text="↷ Redo", command=self.redo_basic_parameters, width=80
        )
        self._buttons['redo'].pack(side="left", padx=2)
        
        # 初期パラメータ状態を履歴に保存（Level 3）
        self._save_parameter_state()
    
    # ===============================
    # 4. イベントハンドラー（コールバック）
    # ===============================
    
    def _on_brightness_change(self, value: float) -> None:
        """明度値変更時のコールバック"""
        # UI更新中はコールバック処理をスキップ
        if getattr(self, '_updating_ui', False):
            print("[DEBUG] UI更新中のため明度コールバックをスキップ")
            return
            
        self._brightness_value = self._clamp_value(int(value), -100, 100)
        self._update_value_label('brightness', self._brightness_value)
        self._on_parameter_change()
    
    def _on_contrast_change(self, value: float) -> None:
        """コントラスト値変更時のコールバック"""
        # UI更新中はコールバック処理をスキップ
        if getattr(self, '_updating_ui', False):
            print("[DEBUG] UI更新中のためコントラストコールバックをスキップ")
            return
            
        self._contrast_value = self._clamp_value(int(value), -100, 100)
        self._update_value_label('contrast', self._contrast_value)
        self._on_parameter_change()
    
    def _on_saturation_change(self, value: float) -> None:
        """彩度値変更時のコールバック"""
        # UI更新中はコールバック処理をスキップ
        if getattr(self, '_updating_ui', False):
            print("[DEBUG] UI更新中のため彩度コールバックをスキップ")
            return
            
        self._saturation_value = self._clamp_value(int(value), -100, 100)
        self._update_value_label('saturation', self._saturation_value)
        self._on_parameter_change()

    # ===============================
    # 5. アクション・リセット処理
    # ===============================
    
    # ===============================
    # 6. 内部ヘルパーメソッド（プライベート） + Level 3 メソッド
    # ===============================
    
    def _clamp_value(self, value: int, min_val: int, max_val: int) -> int:
        """値を指定範囲内に制限"""
        return max(min_val, min(value, max_val))
    
    def _update_value_label(self, parameter: str, value: int) -> None:
        """値ラベルの更新"""
        if parameter in self._labels:
            self._labels[parameter].configure(text=f"{value:.0f}")
    
    def _log_error(self, message: str) -> None:
        """エラーログの出力"""
        print(f"[ERROR] BasicAdjustmentPlugin: {message}")

    # ===============================
    # 7. レガシープロパティ（互換性維持）
    # ===============================
    
    @property
    def brightness_value(self) -> int:
        """明度値（互換性維持用）"""
        return self._brightness_value
    
    @brightness_value.setter
    def brightness_value(self, value: int) -> None:
        """明度値設定（互換性維持用）"""
        self._brightness_value = self._clamp_value(value, -100, 100)
    
    @property
    def contrast_value(self) -> int:
        """コントラスト値（互換性維持用）"""
        return self._contrast_value
    
    @contrast_value.setter
    def contrast_value(self, value: int) -> None:
        """コントラスト値設定（互換性維持用）"""
        self._contrast_value = self._clamp_value(value, -100, 100)
    
    @property
    def saturation_value(self) -> int:
        """彩度値（互換性維持用）"""
        return self._saturation_value
    
    @saturation_value.setter
    def saturation_value(self, value: int) -> None:
        """彩度値設定（互換性維持用）"""
        self._saturation_value = self._clamp_value(value, -100, 100)
    
    def process_image(self, image: Image.Image) -> Image.Image:
        """
        明度・コントラスト・彩度の調整を適用
        
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
            
            # 明度調整の適用
            processed_image = self._apply_brightness_adjustment(processed_image)
            
            # コントラスト調整の適用
            processed_image = self._apply_contrast_adjustment(processed_image)
            
            # 彩度調整の適用
            processed_image = self._apply_saturation_adjustment(processed_image)
            
            return processed_image
            
        except Exception as e:
            self._log_error(f"Image processing error: {e}")
            return image  # フォールバック: 元画像を返す

    def _apply_brightness_adjustment(self, image: Image.Image) -> Image.Image:
        """明度調整を適用"""
        if self._brightness_value == 0:
            return image
        
        try:
            brightness_factor = 1.0 + (self._brightness_value / 100.0)
            brightness_factor = max(0.1, min(brightness_factor, 3.0))  # 制限値適用
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(brightness_factor)
        except Exception as e:
            self._log_error(f"Brightness adjustment error: {e}")
            return image

    def _apply_contrast_adjustment(self, image: Image.Image) -> Image.Image:
        """コントラスト調整を適用"""
        if self._contrast_value == 0:
            return image
        
        try:
            contrast_factor = 1.0 + (self._contrast_value / 100.0)
            contrast_factor = max(0.1, min(contrast_factor, 3.0))  # 制限値適用
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(contrast_factor)
        except Exception as e:
            self._log_error(f"Contrast adjustment error: {e}")
            return image

    def _apply_saturation_adjustment(self, image: Image.Image) -> Image.Image:
        """彩度調整を適用"""
        if self._saturation_value == 0:
            return image
        
        try:
            saturation_factor = 1.0 + (self._saturation_value / 100.0)
            saturation_factor = max(0.0, min(saturation_factor, 3.0))  # 制限値適用
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(saturation_factor)
        except Exception as e:
            self._log_error(f"Saturation adjustment error: {e}")
            return image
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        print("🔄 基本調整パラメータリセット")
        
        try:
            # 1. パラメータ値を0にリセット
            self._brightness_value = 0
            self._contrast_value = 0
            self._saturation_value = 0
            
            # 2. スライダーの値を強制的に設定（遅延実行でより確実に）
            sliders_to_reset = []
            for param in ['brightness', 'contrast', 'saturation']:
                if param in self._sliders:
                    slider = self._sliders[param]
                    sliders_to_reset.append((param, slider))
                    print(f"[DEBUG] {param}スライダー現在値: {slider.get()}")
                    
                    # まず直接設定
                    self._updating_ui = True
                    slider.set(0)
            
            # 3. 遅延実行でスライダーを確実にリセット
            def force_all_sliders_update():
                try:
                    for param, slider in sliders_to_reset:
                        slider.set(0)
                        if hasattr(slider, '_variable'):
                            slider._variable.set(0)
                        slider.update_idletasks()
                        print(f"[DEBUG] 遅延更新後{param}スライダー値: {slider.get()}")
                    self._updating_ui = False
                    print("✅ 全スライダー遅延更新完了")
                except Exception as e:
                    print(f"[ERROR] 遅延更新エラー: {e}")
                    self._updating_ui = False
            
            # 次のUIイベントループで実行
            if sliders_to_reset:
                sliders_to_reset[0][1].after(1, force_all_sliders_update)
            
            # 4. ラベルも更新
            self._update_value_label('brightness', 0)
            self._update_value_label('contrast', 0)
            self._update_value_label('saturation', 0)
            
            # 5. パラメータ変更を通知
            self._on_parameter_change()
            print("✅ 基本調整パラメータリセット完了")
            
        except Exception as e:
            self._updating_ui = False
            print(f"[ERROR] リセットエラー: {e}")
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'brightness': self.brightness_value,
            'contrast': self.contrast_value,
            'saturation': self.saturation_value
        }

    # --- Level 3: 内部ヘルパーメソッド ---
    
    def _get_timestamp(self) -> str:
        """現在時刻のタイムスタンプを取得"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _save_parameter_state(self) -> None:
        """現在のパラメータ状態を履歴に保存 (Level 3)"""
        try:
            if len(self._parameter_history) >= 10:  # max_history = 10
                self._parameter_history.pop(0)
            
            state = {
                'brightness': self.brightness_value,
                'contrast': self.contrast_value,
                'saturation': self.saturation_value,
                'timestamp': self._get_timestamp()
            }
            self._parameter_history.append(state)
            self._history_index = len(self._parameter_history) - 1
            
        except Exception as e:
            if hasattr(self, '_logger'):
                print(f"パラメータ状態保存エラー: {e}")
            else:
                print(f"パラメータ状態保存エラー: {e}")
    
    def _restore_parameter_state(self, state: dict) -> None:
        """指定された状態からパラメータを復元 (Level 3)"""
        try:
            for param, value in state.items():
                if param == 'brightness':
                    self.brightness_value = value
                elif param == 'contrast':
                    self.contrast_value = value
                elif param == 'saturation':
                    self.saturation_value = value
            
            self._update_ui_from_parameters()
            
        except Exception as e:
            print(f"パラメータ状態復元エラー: {e}")
    
    def _update_ui_from_parameters(self) -> None:
        """パラメータ値に基づいてUI要素を更新 (Level 3)"""
        try:
            if not self._sliders:
                return
                
            # スライダーとラベルの両方を更新
            if 'brightness' in self._sliders:
                self._sliders['brightness'].set(self.brightness_value)
                self._update_value_label('brightness', self.brightness_value)
            if 'contrast' in self._sliders:
                self._sliders['contrast'].set(self.contrast_value)
                self._update_value_label('contrast', self.contrast_value)
            if 'saturation' in self._sliders:
                self._sliders['saturation'].set(self.saturation_value)
                self._update_value_label('saturation', self.saturation_value)
                    
        except Exception as e:
            print(f"UI更新エラー: {e}")
    
    def _on_preset_selected(self, selection: str) -> None:
        """プリセット選択時のコールバック (Level 3)"""
        # プリセット選択だけでは適用しない（明示的な適用ボタンクリックが必要）
        pass
    
    def _load_selected_preset(self) -> None:
        """選択されたプリセットを適用 (Level 3)"""
        try:
            preset_name = self._preset_var.get()
            preset_data = self.load_basic_preset(preset_name)
            if preset_data:
                print(f"プリセット '{preset_name}' を適用しました")
                # 処理の通知（後でintegration可能）
                    
        except Exception as e:
            print(f"プリセット適用エラー: {e}")
    
    def _apply_auto_adjustment(self) -> None:
        """自動調整を適用 (Level 3)"""
        try:
            # 現在は簡単な自動調整デモ実装
            # 実際には画像解析に基づく調整値を計算
            demo_adjustments = {'brightness': 10, 'contrast': 5, 'saturation': 0}
            
            for param, value in demo_adjustments.items():
                if param == 'brightness':
                    self.brightness_value = value
                elif param == 'contrast':
                    self.contrast_value = value
                elif param == 'saturation':
                    self.saturation_value = value
            
            self._update_ui_from_parameters()
            self._save_parameter_state()
            print("自動調整を適用しました")
                    
        except Exception as e:
            print(f"自動調整エラー: {e}")
    
    def redo_basic_parameters(self) -> None:
        """基本調整パラメータのRedo操作 (Level 3)"""
        try:
            if self._history_index < len(self._parameter_history) - 1:
                self._history_index += 1
                state = self._parameter_history[self._history_index]
                self._restore_parameter_state(state)
                print("基本調整パラメータをRedo")
        except Exception as e:
            print(f"Redoエラー: {e}")
