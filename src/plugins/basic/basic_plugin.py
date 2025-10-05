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
from utils.smart_slider import SmartSlider


class BasicAdjustmentPlugin(ImageProcessorPlugin):
    """
    基本調整プラグイン (BasicAdjustmentPlugin) - Level 3
    --------------------------------------------------
    設計方針:
    - analysis_plugin.pyの設計パターンに準拠（Level 3拡張）
    - 外部APIはパブリックメソッド (アンダースコアなし) として公開
    - 内部処理はプライベートメソッド (先頭にアンダースコア) として隠蔽
    - 明度・コントラスト・彩度の基本的な画像調整を提供

    Level 3 高度機能:
    - プリセット機能（明度・コントラスト・彩度の組み合わせ）
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
        
        # パラメータ値（内部変数を先に初期化）
        self._brightness_value = 0
        self._contrast_value = 0
        self._saturation_value = 0
        
        # プロパティ経由で設定（setterを通す）
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
            'ビビッド': {'brightness': 0, 'contrast': 30, 'saturation': 40},
            'おまかせ調整': 'auto'  # 画像解析に基づく最適な調整値を自動設定
        }
        self._current_preset_name = None
        

        
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
        
        # チャタリング対策
        self._update_timer = None

    def get_display_name(self) -> str:
        """プラグインの表示名を返す"""
        return "基本調整"
    
    def get_description(self) -> str:
        """プラグインの説明文を返す"""
        return "明度、コントラスト、彩度の基本的な画像調整を提供します（Level 3: プリセット、RGB分析対応）"

    # ===============================
    # 2. Level 3 高度機能API
    # ===============================
    
    def create_basic_preset(self, name: str) -> bool:
        """現在の基本調整パラメータでプリセットを作成"""
        try:
            preset_data = {
                'brightness': self.brightness_value,
                'contrast': self.contrast_value,
                'saturation': self.saturation_value
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
        print(f"[DEBUG] BasicAdjustmentPlugin.set_image: image設定完了")

    # --- コールバック設定（外部API） ---

    def set_update_image_callback(self, callback):
        """画像表示コールバックをセット"""
        self.update_image_callback = callback
        print(f"[DEBUG] BasicAdjustmentPlugin.set_update_image_callback: callback設定完了")

    # --- UI生成・操作（外部API） ---

    def setup_ui(self, parent: ctk.CTkFrame) -> None:
        """UI生成（main_plugin.pyから呼び出される）"""
        self.create_ui(parent)
        
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """基本調整タブのUI生成（明るさ・コントラスト・彩度）"""
        print("[DEBUG] BasicAdjustmentPlugin.create_ui called")
        
        # --- 明度調整（SmartSlider使用） ---
        self._sliders['brightness'], self._labels['brightness'] = SmartSlider.create(
            parent=parent,
            text="明度調整",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_brightness_change,
            value_format="{:.0f}",
            value_type=int
        )

        # --- コントラスト調整（SmartSlider使用） ---
        self._sliders['contrast'], self._labels['contrast'] = SmartSlider.create(
            parent=parent,
            text="コントラスト調整",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_contrast_change,
            value_format="{:.0f}",
            value_type=int
        )

        # --- 彩度調整（SmartSlider使用） ---
        self._sliders['saturation'], self._labels['saturation'] = SmartSlider.create(
            parent=parent,
            text="彩度調整",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_saturation_change,
            value_format="{:.0f}",
            value_type=int
        )

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
        ctk.CTkLabel(preset_frame, text="基本調整プリセット", font=("Arial", 11, "bold")).pack(anchor="w", padx=3, pady=(5, 0))
        
        # プリセット選択
        preset_select_frame = ctk.CTkFrame(preset_frame)
        preset_select_frame.pack(fill="x", padx=5, pady=2)
        
        self._preset_var = ctk.StringVar(value="おまかせ調整")
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
        

    
    # ===============================
    # 4. イベントハンドラー（コールバック）
    # ===============================
    
    def _on_brightness_change(self, value: int) -> None:
        """明度値変更時のコールバック（SmartSlider対応）"""
        if getattr(self, '_updating_ui', False):
            return
        
        # SmartSliderでオーバーシュート対策・チャタリング防止済み
        self.brightness_value = value
        self._on_parameter_change()

    def _on_contrast_change(self, value: int) -> None:
        """コントラスト値変更時のコールバック（SmartSlider対応）"""
        if getattr(self, '_updating_ui', False):
            return
        
        # SmartSliderでオーバーシュート対策・チャタリング防止済み
        self.contrast_value = value
        self._on_parameter_change()

    def _on_saturation_change(self, value: int) -> None:
        """彩度値変更時のコールバック（SmartSlider対応）"""
        if getattr(self, '_updating_ui', False):
            return
        
        # SmartSliderでオーバーシュート対策・チャタリング防止済み
        self.saturation_value = value
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
        clamped_value = self._clamp_value(int(round(value)), -100, 100)
        self._brightness_value = clamped_value
    
    @property
    def contrast_value(self) -> int:
        """コントラスト値（互換性維持用）"""
        return self._contrast_value
    
    @contrast_value.setter
    def contrast_value(self, value: int) -> None:
        """コントラスト値設定（互換性維持用）"""
        clamped_value = self._clamp_value(int(round(value)), -100, 100)
        self._contrast_value = clamped_value
    
    @property
    def saturation_value(self) -> int:
        """彩度値（互換性維持用）"""
        return self._saturation_value
    
    @saturation_value.setter
    def saturation_value(self, value: int) -> None:
        """彩度値設定（互換性維持用）"""
        clamped_value = self._clamp_value(int(round(value)), -100, 100)
        self._saturation_value = clamped_value
    
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
        if self.brightness_value == 0:  # プロパティを使用
            return image
        
        try:
            brightness_factor = 1.0 + (self.brightness_value / 100.0)  # プロパティを使用
            brightness_factor = max(0.1, min(brightness_factor, 3.0))
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(brightness_factor)
        except Exception as e:
            self._log_error(f"Brightness adjustment error: {e}")
            return image

    def _apply_contrast_adjustment(self, image: Image.Image) -> Image.Image:
        """コントラスト調整を適用"""
        if self.contrast_value == 0:  # プロパティを使用に修正
            return image
    
        try:
            contrast_factor = 1.0 + (self.contrast_value / 100.0)  # プロパティを使用に修正
            contrast_factor = max(0.1, min(contrast_factor, 3.0))  # 制限値適用
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(contrast_factor)
        except Exception as e:
            self._log_error(f"Contrast adjustment error: {e}")
            return image

    def _apply_saturation_adjustment(self, image: Image.Image) -> Image.Image:
        """彩度調整を適用"""
        if self.saturation_value == 0:  # プロパティを使用に修正
            return image
    
        try:
            saturation_factor = 1.0 + (self.saturation_value / 100.0)  # プロパティを使用に修正
            saturation_factor = max(0.0, min(saturation_factor, 3.0))  # 制限値適用
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(saturation_factor)
        except Exception as e:
            self._log_error(f"Saturation adjustment error: {e}")
            return image
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        try:
            # UI更新フラグを設定
            self._updating_ui = True
            
            # パラメータ値を直接リセット
            self._brightness_value = 0
            self._contrast_value = 0
            self._saturation_value = 0
            
            # スライダーとラベルをリセット
            for param in ['brightness', 'contrast', 'saturation']:
                if param in self._sliders and self._sliders[param]:
                    self._sliders[param].set(0)
                self._update_value_label(param, 0)
            
            # UI更新フラグを解除
            self._updating_ui = False
            
            # 画像更新
            self._on_parameter_change()
            print("✅ 基本調整パラメータリセット完了")
            
        except Exception as e:
            self._updating_ui = False
            print(f"❌ リセットエラー: {e}")
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'brightness': self.brightness_value,
            'contrast': self.contrast_value,
            'saturation': self.saturation_value
        }

    # --- Level 3: 内部ヘルパーメソッド ---
    

    

    
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
            if preset_name not in self._presets:
                print(f"❌ プリセット '{preset_name}' が見つかりません")
                return
            
            # おまかせ調整の場合は専用処理
            if preset_name == 'おまかせ調整':
                self._apply_auto_adjustment()
                return
            
            # UI更新フラグを設定（コールバック干渉を防止）
            self._updating_ui = True
            
            # プリセット値を取得
            preset_data = self._presets[preset_name]
            
            # パラメータ値を更新
            self.brightness_value = preset_data['brightness']
            self.contrast_value = preset_data['contrast']  
            self.saturation_value = preset_data['saturation']
            
            # スライダーとラベルを更新
            if 'brightness' in self._sliders:
                self._sliders['brightness'].set(preset_data['brightness'])
                self._update_value_label('brightness', preset_data['brightness'])
            if 'contrast' in self._sliders:
                self._sliders['contrast'].set(preset_data['contrast'])
                self._update_value_label('contrast', preset_data['contrast'])
            if 'saturation' in self._sliders:
                self._sliders['saturation'].set(preset_data['saturation'])
                self._update_value_label('saturation', preset_data['saturation'])

            # UI更新フラグを解除
            self._updating_ui = False
            
            # 画像処理（画像とコールバックが設定されている場合のみ）
            if self.image and self.update_image_callback:
                self._on_parameter_change()
            
            print(f"✅ プリセット '{preset_name}' を適用しました")
            
        except Exception as e:
            self._updating_ui = False  # エラー時もフラグを確実に解除
            print(f"❌ プリセット適用エラー: {e}")

    def _apply_auto_adjustment(self) -> None:
        """自動調整を適用 (Level 3)"""
        try:
            if self.image is None:
                print("❌ 画像が読み込まれていません")
                return
                
            # UI更新フラグを設定
            self._updating_ui = True
            
            # 画像分析に基づく自動調整
            suggestions = self.suggest_auto_adjustment(self.image)
            if not suggestions:
                print("❌ 自動調整の計算に失敗しました")
                self._updating_ui = False
                return
            
            # 提案された値を適用
            self.brightness_value = suggestions.get('brightness', 0)
            self.contrast_value = suggestions.get('contrast', 0)
            self.saturation_value = suggestions.get('saturation', 0)
            
            # UIを更新
            self._update_ui_from_parameters()
            
            # UI更新フラグを解除
            self._updating_ui = False
            
            # 画像を更新
            self._on_parameter_change()
            
            print(f"🤖 自動調整適用: {suggestions}")
            
        except Exception as e:
            self._updating_ui = False  # エラー時もフラグを確実に解除
            print(f"❌ 自動調整エラー: {e}")


    
    def _on_parameter_change(self) -> None:
        """パラメータ変更時の共通処理（チャタリング対策付き）"""
        if not (self.image and self.update_image_callback):
            return
        
        # 既存のタイマーをキャンセル
        if self._update_timer:
            self._update_timer.cancel()
        
        # 100ms後に画像処理を実行（チャタリング対策）
        def delayed_update():
            if self.image and self.update_image_callback:
                processed_image = self.process_image(self.image)
                self.update_image_callback(processed_image)
            self._update_timer = None
        
        import threading
        self._update_timer = threading.Timer(0.1, delayed_update)
        self._update_timer.start()
