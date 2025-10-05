#!/usr/bin/env python3
"""
UniversalPluginBase - 画像解析タブリファクタリング版

元の619行 → 150行に削減
"""

import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Union
from PIL import Image
import json
import os

from .plugin_base import ImageProcessorPlugin, PluginUIHelper
from utils.smart_slider import SmartSlider


class UniversalPluginBase(ImageProcessorPlugin, ABC):
    """UniversalPluginBase - シンプルなプラグイン基盤"""

    def __init__(self, plugin_id: str, version: str = "1.0.0"):
        super().__init__(plugin_id, version)
        
        # 基本属性
        self.image = None
        self.update_image_callback = None
        self._parameters = {}
        self._sliders = {}
        self._labels = {}
        self._buttons = {}
        
        # 設定読み込み
        self._config = self._load_config()
        
        # パラメータ初期化
        for param_name, param_config in self._config.get('parameters', {}).items():
            default_value = param_config.get('default', 0)
            self._parameters[param_name] = default_value
            setattr(self, param_name, default_value)
        
        # UI更新フラグ
        self._updating_ui = False

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        try:
            plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(plugin_dir, "plugins", f"{self.name}_universal", "plugin.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ 設定読み込みエラー: {e}")
        return {}

    def get_display_name(self) -> str:
        """表示名"""
        return self._config.get('display_name', self.name)

    def get_description(self) -> str:
        """説明"""
        return self._config.get('description', '')

    def set_image(self, image: Image.Image):
        """処理対象画像をセット"""
        self.image = image

    def set_update_image_callback(self, callback: Callable):
        """画像更新コールバックをセット"""
        self.update_image_callback = callback

    def setup_ui(self, parent: ctk.CTkFrame) -> None:
        """UI生成"""
        print(f"[DEBUG] {self.name} UniversalPluginBase.setup_ui開始")
        self.create_ui(parent)
        print(f"[DEBUG] {self.name} UI生成完了: plugin_type={self._config.get('plugin_type')}, buttons={list(self._buttons.keys())}")

    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """UI生成（完全自動）"""
        self._create_automatic_ui(parent)

    def _create_automatic_ui(self, parent: ctk.CTkFrame) -> None:
        """パラメータ設定に基づく自動UI生成"""
        plugin_type = self._config.get('plugin_type', '')
        
        # プラグイン種別に応じた専用機能（先に実行 - ガンマカーブエディタを最上部に）
        if plugin_type == 'density':
            self._create_density_features_top(parent)
        
        parameters = self._config.get('parameters', {})
        
        # パラメータスライダー生成
        for param_name, param_config in parameters.items():
            if isinstance(param_config, dict) and 'range' in param_config:
                # filters プラグインの場合、morph_kernel_size は後でモルフォロジー演算セクションに配置
                if plugin_type == 'filters' and param_name == 'morph_kernel_size':
                    continue
                
                # Universal プラグインの主要パラメータは1行レイアウト
                use_horizontal = (
                    (plugin_type == 'basic' and param_name in ['brightness', 'contrast', 'saturation']) or
                    (plugin_type == 'density' and param_name in ['shadow', 'highlight', 'temperature', 'threshold']) or
                    (plugin_type == 'filters' and param_name in ['blur_strength', 'sharpen_strength'])
                )
                
                slider, label = SmartSlider.create(
                    parent=parent,
                    text=param_config.get('label', param_name),
                    from_=param_config['range'][0],
                    to=param_config['range'][1],
                    default_value=param_config.get('default', 0),
                    command=lambda value, name=param_name: self._on_parameter_change(name, value),
                    value_format=param_config.get('format', "{:.0f}"),
                    value_type=param_config.get('type', int),
                    horizontal_layout=use_horizontal
                )
                self._sliders[param_name] = slider
                self._labels[param_name] = label

        # その他の専用機能（スライダー後）
        if plugin_type == 'analysis':
            self._create_analysis_features(parent)
        elif plugin_type == 'filters':
            self._create_analysis_features(parent)  # filters も analysis_features と同じ処理
        elif plugin_type == 'basic':
            self._create_basic_features(parent)
        elif plugin_type == 'density':
            self._create_density_features_bottom(parent)

        # リセットボタン
        if self._parameters:
            self._create_reset_button(parent)
            
        # プリセット機能（最後に配置）
        self._create_presets(parent)

    def _create_analysis_features(self, parent: ctk.CTkFrame):
        """画像解析専用機能"""
        # 新形式のspecial_buttonsを優先、旧形式analysis_featuresもサポート
        special_buttons = self._config.get('special_buttons', {})
        analysis_features = self._config.get('analysis_features', {})
        
        # カテゴリごとにボタンをグループ化
        categories = {}
        for button_name, button_config in special_buttons.items():
            category = button_config.get('category', 'その他')
            if category not in categories:
                categories[category] = []
            categories[category].append((button_name, button_config.get('display_name', button_name)))
        
        # 旧形式との互換性
        if analysis_features and not special_buttons:
            if 'dct' in analysis_features or 'fft' in analysis_features:
                categories['周波数解析'] = []
                if 'dct' in analysis_features:
                    categories['周波数解析'].append(('dct', 'DCT解析'))
                if 'fft' in analysis_features:
                    categories['周波数解析'].append(('fft', 'FFT解析'))
        
        # カテゴリごとにUI生成
        for category, buttons in categories.items():
            if buttons:
                ctk.CTkLabel(parent, text=category, font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
                
                # モルフォロジー演算の場合、カーネルサイズスライダーを先に配置
                if category == "モルフォロジー演算" and hasattr(self, '_config'):
                    parameters = self._config.get('parameters', {})
                    if 'morph_kernel_size' in parameters:
                        param_config = parameters['morph_kernel_size']
                        if isinstance(param_config, dict) and 'range' in param_config:
                            slider, label = SmartSlider.create(
                                parent=parent,
                                text=param_config.get('label', 'morph_kernel_size'),
                                from_=param_config['range'][0],
                                to=param_config['range'][1],
                                default_value=param_config.get('default', 0),
                                command=lambda value, name='morph_kernel_size': self._on_parameter_change(name, value),
                                value_format=param_config.get('format', "{:.0f}"),
                                value_type=param_config.get('type', int)
                            )
                            self._sliders['morph_kernel_size'] = slider
                            self._labels['morph_kernel_size'] = label
                
                for button_name, display_name in buttons:
                    self._create_analysis_button(parent, button_name, display_name)

    def _create_analysis_button(self, parent: ctk.CTkFrame, button_name: str, display_name: str):
        """解析ボタンを作成"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", padx=5, pady=2)
        
        self._buttons[button_name] = PluginUIHelper.create_button(
            button_frame, 
            text=display_name, 
            command=lambda: self._execute_analysis(button_name)
        )
        self._buttons[button_name].pack(side="left", padx=(0, 5))
        
        self._buttons[f'undo_{button_name}'] = PluginUIHelper.create_button(
            button_frame, 
            text="🔄 取消", 
            command=lambda: self._undo_analysis(button_name)
        )
        self._buttons[f'undo_{button_name}'].pack(side="left", padx=(0, 5))
        self._buttons[f'undo_{button_name}'].configure(state="disabled")

    def _execute_analysis(self, analysis_type: str):
        """解析実行"""
        if not hasattr(self, 'image') or not self.image:
            print("❌ 画像が読み込まれていません")
            return
        
        # 派生クラスのapply_filterメソッドを呼び出し
        if hasattr(self, 'apply_filter'):
            result_image = self.apply_filter(self.image, analysis_type)
            if result_image and hasattr(self, 'update_image_callback') and self.update_image_callback:
                self.update_image_callback(result_image)
        
        # undoボタンを有効化
        if f'undo_{analysis_type}' in self._buttons:
            self._buttons[f'undo_{analysis_type}'].configure(state="normal")

    def _undo_analysis(self, analysis_type: str):
        """解析取消"""
        print(f"解析取消: {analysis_type}")
        if hasattr(self, 'image') and self.image and hasattr(self, 'update_image_callback') and self.update_image_callback:
            self.update_image_callback(self.image)
        if f'undo_{analysis_type}' in self._buttons:
            self._buttons[f'undo_{analysis_type}'].configure(state="disabled")

    def _create_reset_button(self, parent: ctk.CTkFrame):
        """リセットボタン生成"""
        ctk.CTkLabel(parent, text="一括操作", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        reset_frame = ctk.CTkFrame(parent)
        reset_frame.pack(fill="x", padx=5, pady=2)
        self._buttons['reset'] = PluginUIHelper.create_button(reset_frame, text="全リセット", command=self.reset_parameters)
        self._buttons['reset'].pack(side="left", padx=2)

    def _on_parameter_change(self, param_name: str, value: Union[int, float]):
        """パラメータ変更処理"""
        if self._updating_ui:
            return

        if param_name in self._parameters:
            self._parameters[param_name] = value
            setattr(self, param_name, value)
            print(f"[DEBUG] _on_parameter_change: {param_name}={value}, parameters={self._parameters}")

        print(f"[DEBUG] _on_parameter_change: call _trigger_image_update")
        self._trigger_image_update()

    def _trigger_image_update(self):
        """画像更新"""
        print(f"[DEBUG] _trigger_image_update: image={self.image is not None}, update_image_callback={self.update_image_callback is not None}")
        if hasattr(self, 'image') and self.image and hasattr(self, 'update_image_callback') and self.update_image_callback:
            try:
                print(f"[DEBUG] _trigger_image_update: self._parameters={self._parameters}")
                processed = self.process_image(self.image, **self._parameters)
                self.update_image_callback(processed)
            except Exception as e:
                print(f"❌ 画像処理エラー: {e}")

    def reset_parameters(self) -> None:
        """パラメータリセット"""
        self._updating_ui = True
        
        for param_name, param_config in self._config.get('parameters', {}).items():
            default_value = param_config.get('default', 0)
            self._parameters[param_name] = default_value
            setattr(self, param_name, default_value)
            
            if param_name in self._sliders:
                self._sliders[param_name].set(default_value)
            if param_name in self._labels:
                self._labels[param_name].configure(text=f"{default_value}")
        
        self._updating_ui = False
        self._trigger_image_update()

    def _create_basic_features(self, parent: ctk.CTkFrame):
        """基本調整専用機能"""
        # RGB分析表示エリア
        rgb_analysis_frame = ctk.CTkFrame(parent)
        rgb_analysis_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(rgb_analysis_frame, text="RGB分析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(2, 0))
        
        rgb_controls = ctk.CTkFrame(rgb_analysis_frame)
        rgb_controls.pack(fill="x", padx=5, pady=2)
        
        # RGB分析表示切り替え
        self._rgb_analysis_var = ctk.BooleanVar(value=False)
        self._rgb_analysis_checkbox = ctk.CTkCheckBox(
            rgb_controls, text="RGB分析表示", variable=self._rgb_analysis_var,
            command=self._toggle_rgb_analysis
        )
        self._rgb_analysis_checkbox.pack(side="left", padx=5)
        
        # 分析実行ボタン
        self._buttons['analyze_rgb'] = PluginUIHelper.create_button(
            rgb_controls, text="分析実行", command=self._execute_rgb_analysis, width=80
        )
        self._buttons['analyze_rgb'].pack(side="left", padx=5)
        
        # RGB分析結果表示エリア
        rgb_results_frame = ctk.CTkFrame(rgb_analysis_frame)
        rgb_results_frame.pack(fill="x", padx=5, pady=(2, 5))
        
        self._rgb_results_label = ctk.CTkLabel(
            rgb_results_frame, 
            text="分析結果がここに表示されます",
            font=("Arial", 10),
            justify="left"
        )
        self._rgb_results_label.pack(padx=10, pady=5)

    def _create_density_features_top(self, parent: ctk.CTkFrame):
        """濃度調整専用機能 - 最上部（ガンマカーブエディタ）"""
        # 1. ガンマ補正カーブエディタ（最上部）
        try:
            from ui.curve_editor import CurveEditor
            # カーブエディタ自体が「ガンマ補正カーブ」ラベルを表示するため、重複ラベル削除
            self.gamma_curve_frame = ctk.CTkFrame(parent)
            self.gamma_curve_frame.pack(side="top", fill="x", padx=5, pady=2)
            self.curve_editor = CurveEditor(self.gamma_curve_frame)
            self.curve_editor.pack(fill="x", padx=5, pady=2)
            self.curve_editor.on_curve_change = self._on_curve_change
            print("✅ ガンマ補正カーブエディタを追加しました")
        except ImportError as e:
            print(f"⚠️ カーブエディタインポート警告: {e}")

    def _create_density_features_bottom(self, parent: ctk.CTkFrame):
        """濃度調整専用機能 - 下部（ボタン類）"""
        # 2. 2値化調整 + 実行ボタン（同じ行に配置）
        if 'threshold' in self._sliders:
            # 既存のthresholdスライダーがあるフレームに2値化実行ボタンを追加
            threshold_parent = self._sliders['threshold'].master
            self._buttons['binary'] = PluginUIHelper.create_button(
                threshold_parent,
                text="2値化実行", 
                command=self._on_apply_binary_threshold
            )
            self._buttons['binary'].pack(side="left", padx=5)
        
        # 3. ヒストグラム均等化セクション
        ctk.CTkLabel(parent, text="ヒストグラム均等化", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        hist_frame = ctk.CTkFrame(parent)
        hist_frame.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['histogram'] = PluginUIHelper.create_button(
            hist_frame,
            text="ヒストグラム均等化",
            command=self._on_histogram_equalization
        )
        self._buttons['histogram'].pack(side="left", padx=2)

    def _create_density_features(self, parent: ctk.CTkFrame):
        """濃度調整専用機能 - 後方互換性のため残す"""
        self._create_density_features_bottom(parent)

    # スタブメソッド
    def _toggle_rgb_analysis(self):
        """RGB分析表示の切り替え（派生クラスで実装）"""
        enabled = self._rgb_analysis_var.get()
        print(f"RGB分析表示: {'有効' if enabled else '無効'}")

    def _execute_rgb_analysis(self):
        """RGB分析を実行（派生クラスで実装）"""
        print("RGB分析を実行します")

    def _on_apply_binary_threshold(self):
        """2値化実行（派生クラスで実装）"""
        print("2値化実行ボタンがクリックされました")

    def _on_histogram_equalization(self):
        """ヒストグラム均等化（派生クラスで実装）"""
        print("ヒストグラム均等化ボタンがクリックされました")

    def _on_curve_change(self, lut=None):
        """カーブエディタの変更コールバック"""
        if hasattr(self, 'curve_editor') and hasattr(self, 'image') and self.image:
            try:
                # カーブエディタからデータを取得
                if lut is not None:
                    self.curve_data = lut
                elif hasattr(self.curve_editor, 'get_curve'):
                    self.curve_data = self.curve_editor.get_curve()
                
                # 画像を更新
                if hasattr(self, 'update_image_callback') and self.update_image_callback:
                    processed_image = self.process_image(self.image, **self._parameters)
                    if processed_image:
                        self.update_image_callback(processed_image)
            except Exception as e:
                print(f"カーブ変更処理エラー: {e}")

    def _create_presets(self, parent: ctk.CTkFrame):
        """プリセット機能の作成"""
        presets = self._config.get('presets', {})
        if not presets:
            return
            
        # プリセットセクション
        preset_label = ctk.CTkLabel(parent, text="プリセット", font=("Arial", 11, "bold"))
        preset_label.pack(anchor="w", padx=3, pady=(10, 0))
        
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill="x", padx=5, pady=2)
        
        # プリセット選択用のcombobox
        preset_names = list(presets.keys())
        self._preset_combo = ctk.CTkComboBox(
            preset_frame,
            values=preset_names,
            width=200,
            command=self._apply_preset
        )
        self._preset_combo.pack(side="left", padx=(5, 0))
        self._preset_combo.set("プリセットを選択")
        
        # 適用ボタン
        apply_btn = PluginUIHelper.create_button(
            preset_frame, 
            text="適用", 
            command=lambda: self._apply_current_preset()
        )
        apply_btn.pack(side="left", padx=(5, 0))

    def _apply_preset(self, preset_name: str):
        """プリセット選択時の処理"""
        if preset_name == "プリセットを選択":
            return
            
        presets = self._config.get('presets', {})
        if preset_name in presets:
            preset_values = presets[preset_name]
            # スライダー値を更新
            for param_name, value in preset_values.items():
                if param_name in self._sliders:
                    self._sliders[param_name].set(value)
                    self._parameters[param_name] = value
                    setattr(self, param_name, value)
            # 画像を即座に更新
            self._apply_current_preset()

    def _apply_current_preset(self):
        """現在のプリセット値で画像処理を実行"""
        if hasattr(self, 'image') and self.image and hasattr(self, 'update_image_callback') and self.update_image_callback:
            try:
                processed_image = self.process_image(self.image, **self._parameters)
                if processed_image:
                    self.update_image_callback(processed_image)
            except Exception as e:
                print(f"プリセット適用エラー: {e}")

    @abstractmethod
    def process_image(self, image: Image.Image, **parameters) -> Image.Image:
        """画像処理（派生クラスで実装）"""
        pass