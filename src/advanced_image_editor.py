"""
Advanced Image Editor
高度画像編集アプリケーション

## 概要

プラグインシステムを採用した高度な画像編集アプリケーションです。
モジュラー設計により、各機能は独立したプラグインとして実装されており、
優れた保守性・拡張性・可読性を実現しています。

4つの専門プラグイン（基本調整・濃度調整・フィルター処理・画像解析）により、
基本的な画像補正から高度な画像解析まで幅広い画像編集機能を提供します。

【実行方法】
cd <本リポジトリのクローン先ディレクトリ>
# macOS/Linux: .venv/bin/python src/advanced_image_editor.py
# Windows: .venv\\Scripts\\python.exe src\\advanced_image_editor.py

【詳細ドキュメント】
プラグインの作成方法・API仕様・トラブルシューティングは README.md を参照してください。

【作成者】GitHub Copilot + プラグインシステム設計
【バージョン】Advanced Image Editor 1.0.0
【最終更新】2025年10月3日
"""
import sys
sys.path.append('/Users/tinoue/Development.local/lib-image_toolkit')
#!/usr/bin/env python3
import sys
sys.path.append('/Users/tinoue/Development.local/lib-image_toolkit')

try:
    import tkinter as tk
    import customtkinter as ctk
    from PIL import Image, ImageTk
    import cv2
    import numpy as np
    from tkinter import filedialog, messagebox
    import os
    import sys
    import argparse
    print("✅ 必要なライブラリのインポートが完了しました")
except ImportError as e:
    print(f"❌ ライブラリのインポートエラー: {e}")
    print("📦 以下のコマンドでライブラリをインストールしてください:")
    print("pip install customtkinter opencv-python numpy pillow")
    sys.exit(1)

# ログシステムのインポート
from core.logging import (
    LogLevel, 
    set_log_level, 
    get_log_level,
    debug_print, 
    info_print, 
    warning_print, 
    error_print, 
    critical_print
)

# GUI framework（オプション機能：高度なUI）
try:
    from gui_framework.widgets.dialogs import MessageDialog
    print("✅ gui_framework ライブラリ利用可能 - 高度なダイアログ機能が有効です")
except ImportError:
    print("ℹ️ gui_framework未インストール - 標準ダイアログを使用（基本機能は利用可能）")
    # フォールバック用の基本MessageDialog
    from tkinter import messagebox
    class MessageDialog:
        @staticmethod
        def show_error(parent, title, message):
            messagebox.showerror(title, message)
        
        @staticmethod
        def show_warning(parent, title, message):
            messagebox.showwarning(title, message)
        
        @staticmethod
        def show_info(parent, title, message):
            messagebox.showinfo(title, message)

# プラグインシステムのインポート
try:
    from core.plugin_base import PluginManager
    from plugins.basic import BasicAdjustmentPlugin
    from plugins.density import DensityAdjustmentPlugin
    from plugins.filters import FilterProcessingPlugin
    from plugins.analysis import ImageAnalysisPlugin
    from plugins.analysis.histogram_analysis_plugin import HistogramAnalysisPlugin
    print("✅ プラグインシステムのインポートが完了しました")
except ImportError as e:
    print(f"❌ プラグインシステムインポートエラー: {e}")
    print("📦 プラグインディレクトリが正しく配置されているか確認してください")
    # より詳細なエラー情報
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 新しいモジュール構造のインポート
try:
    from editor import ImageEditor
    from ui import MainWindowUI
    from utils import ImageUtils as IUtils
    print("✅ 新しいモジュール構造のインポートが完了しました")
except ImportError as e:
    print(f"❌ モジュール構造インポートエラー: {e}")
    print("📦 editor, ui, utils ディレクトリが正しく配置されているか確認してください")
    sys.exit(1)


class AdvancedImageEditor(ctk.CTk):
    """
    Advanced Image Editor - プラグインシステム対応高度画像編集アプリケーション
    """
    
    def __init__(self):
        super().__init__()
        
        # プラグインマネージャーの初期化
        self.plugin_manager = PluginManager()
        
        # UIセットアップ
        self.ui = MainWindowUI(self)
        
        # 画像エディターセットアップ
        self.image_editor = ImageEditor(
            canvas_widget=self.ui.get_canvas(),
            status_label=self.ui.get_status_label()
        )
        
        # 画像読み込み完了時のコールバックを設定
        self.image_editor.set_image_loaded_callback(self.on_image_loaded)
        
        # プラグインセットアップ
        self.setup_plugins()
        
        # プラグインタブのセットアップ
        self.setup_plugin_tabs()
        
        # プラグインUIの作成
        self.create_plugin_tabs()
        
        # コントロールボタンのセットアップ
        self.setup_control_buttons()
        
        info_print("Advanced Image Editor が起動しました")
        
        # デフォルト画像を読み込み
        self.image_editor.load_default_image()
    
    def setup_control_buttons(self):
        """操作ボタンのセットアップ"""
        callbacks = {
            'load_image': self.load_image,
            'save_image': self.save_image,
            'reset_to_original': self.reset_to_original,
            'reset_all_plugins': self.reset_all_plugins
        }
        self.ui.setup_control_buttons(callbacks)
    
    def setup_plugin_tabs(self):
        """プラグイン用のタブビューをセットアップ（各タブにUI部品を生成）"""
        plugin_tabs = {
            "basic_adjustment": "🎯 基本調整",
            "density_adjustment": "🌈 濃度調整", 
            "filter_processing": "🌀 フィルター",
            "image_analysis": "🔬 画像解析"
        }
        self.plugin_frames = self.ui.setup_plugin_tabs(plugin_tabs)

        # 各プラグインのUI部品生成（analysis_plugin.py方式）
        # プラグインインスタンスはsetup_pluginsで生成済みと仮定
        # self.plugin_instancesはsetup_pluginsで作成する
        if hasattr(self, 'plugin_instances'):
            # 基本調整 (create_plugin_tabsで既にsetup_ui経由で作成済み)
            # 濃度調整
            if 'density_adjustment' in self.plugin_instances:
                print('[LOG] 濃度調整タブのUI部品表示トリガ: create_ui を呼び出します')
                self.plugin_instances['density_adjustment'].create_ui(self.plugin_frames['density_adjustment'])
            # フィルター
            if 'filter_processing' in self.plugin_instances:
                self.plugin_instances['filter_processing'].create_ui(self.plugin_frames['filter_processing'])
            # 画像解析（ここではUI生成しない）
    

    def setup_plugins(self):
        """プラグインを登録・初期化（UI生成→コールバック登録・検証の順に分離）"""
        info_print("プラグインを登録中...")
        plugin_configs = [
            {
                'name': 'basic_adjustment',
                'class': BasicAdjustmentPlugin,
                'callbacks': {
                    'parameter_change': self.on_plugin_parameter_change,
                }
            },
            {
                'name': 'density_adjustment',
                'class': DensityAdjustmentPlugin,
                'callbacks': {
                    'parameter_change': self.on_plugin_parameter_change,
                    'histogram': self.apply_histogram_equalization,
                    'threshold': self.apply_binary_threshold,
                }
            },
            {
                'name': 'filter_processing',
                'class': FilterProcessingPlugin,
                'callbacks': {
                    'parameter_change': self.on_plugin_parameter_change,
                    'special_filter': self.apply_special_filter,
                    'morphology': self.apply_morphology_operation,
                    'contour': self.apply_contour_detection,
                    'undo_special_filter': self.undo_special_filter,
                    'undo_morphology': self.undo_morphology_operation,
                    'undo_contour': self.undo_contour_detection,
                }
            },
            {
                'name': 'histogram_analysis',
                'class': HistogramAnalysisPlugin,
                'callbacks': {}
            },
            {
                'name': 'image_analysis',
                'class': ImageAnalysisPlugin,
                'callbacks': {
                    'histogram': self.show_histogram_analysis,
                    'feature': self.apply_feature_detection,
                    'frequency': self.apply_frequency_analysis,
                    'blur': self.detect_blur,
                    'noise': self.analyze_noise,
                    'undo_features': self.undo_feature_detection,
                    'undo_frequency': self.undo_frequency_analysis,
                    'undo_blur': self.undo_blur_detection,
                    'undo_noise': self.undo_noise_analysis,
                    'undo_histogram': self.undo_histogram_analysis,
                }
            }
        ]

        # プラグインインスタンス生成・UI生成
        plugin_instances = {}
        histogram_plugin_instance = None
        for config in plugin_configs:
            plugin_name = config['name']
            plugin_class = config['class']
            try:
                plugin_instance = plugin_class()
                plugin_instances[plugin_name] = plugin_instance
                self.plugin_manager.register_plugin(plugin_instance)
                debug_print(f"   ✅ {plugin_name} プラグインインスタンス生成・登録完了")
                if plugin_name == 'histogram_analysis':
                    histogram_plugin_instance = plugin_instance
                # 濃度調整プラグインには画像表示コールバックを設定
                if plugin_name == 'density_adjustment' and hasattr(self.image_editor, 'update_current_image'):
                    if hasattr(plugin_instance, 'set_update_image_callback'):
                        plugin_instance.set_update_image_callback(self.image_editor.update_current_image)
                        debug_print("   ✓ density_adjustment: update_image_callback 設定完了")
            except Exception as e:
                error_print(f"{plugin_name} プラグインインスタンス生成失敗: {e}")
                continue

        # UI生成（create_plugin_tabsで各フレームにUI生成済み）
        # コールバック登録・検証
        for config in plugin_configs:
            plugin_name = config['name']
            plugin_instance = plugin_instances.get(plugin_name)
            callbacks = config.get('callbacks', {})
            if not plugin_instance:
                continue
            try:
                self._setup_plugin_callbacks(plugin_instance, callbacks, plugin_name)
            except Exception as e:
                error_print(f"{plugin_name} コールバック登録失敗: {e}")
                continue

        # ImageAnalysisPluginにHistogramAnalysisPluginのshow_histogramを必ずコールバック登録
        image_analysis_plugin = plugin_instances.get('image_analysis')
        if image_analysis_plugin and histogram_plugin_instance:
            if hasattr(image_analysis_plugin, 'set_rgb_histogram_callback'):
                image_analysis_plugin.set_rgb_histogram_callback(histogram_plugin_instance.show_histogram)
                debug_print(f"[KISS] set_rgb_histogram_callback: {image_analysis_plugin.rgb_histogram_callback}")
                if image_analysis_plugin.rgb_histogram_callback is None:
                    error_print("[ERROR] set_rgb_histogram_callbackにNoneが渡されました。コールバック設定を確認してください。")

        # ImageAnalysisPluginに画像表示コールバックを登録
        image_analysis_plugin = plugin_instances.get('image_analysis')
        if image_analysis_plugin:
            if hasattr(self, 'image_editor'):
                image_analysis_plugin.set_display_image_callback(self.image_editor.update_current_image)

        info_print(f"{len(self.plugin_manager.plugins)}個のプラグインが登録されました")
        print("[DEBUG] plugin_manager.plugins:", self.plugin_manager.plugins)
        # ここでインスタンスを保存
        self.plugin_instances = plugin_instances
        
    def _register_plugins_from_config(self, plugin_configs):
        """プラグイン設定から一括登録（メンテナンス性向上）"""
        successful_plugins = 0
        failed_plugins = []
        
        histogram_plugin_instance = None
        for config in plugin_configs:
            try:
                plugin_name = config['name']
                plugin_class = config['class']
                callbacks = config.get('callbacks', {})

                debug_print(f"   🔌 {plugin_name} プラグインを初期化中...")

                # プラグインインスタンス作成
                plugin_instance = plugin_class()

                # HistogramAnalysisPluginのインスタンスを保存
                if plugin_name == 'histogram_analysis':
                    histogram_plugin_instance = plugin_instance

                # コールバック設定
                self._setup_plugin_callbacks(plugin_instance, callbacks, plugin_name)

                # ImageAnalysisPluginにHistogramAnalysisPluginのshow_histogramを渡す
                if plugin_name == 'image_analysis' and histogram_plugin_instance:
                    if hasattr(plugin_instance, 'set_rgb_histogram_callback'):
                        plugin_instance.set_rgb_histogram_callback(histogram_plugin_instance.show_histogram)

                # プラグインマネージャーに登録
                self.plugin_manager.register_plugin(plugin_instance)

                successful_plugins += 1
                debug_print(f"   ✅ {plugin_name} プラグイン登録完了")

            except Exception as e:
                failed_plugins.append({'name': plugin_name, 'error': str(e)})
                error_print(f"{plugin_name} プラグイン登録失敗: {e}")
                # プラグイン単体の失敗はアプリ全体を止めない
                continue
        
        # 結果サマリー
        if failed_plugins:
            warning_print(f"{len(failed_plugins)}個のプラグインで問題が発生しましたが、アプリは継続実行されます")
            for failed in failed_plugins:
                warning_print(f"- {failed['name']}: {failed['error']}")
        debug_print(f"プラグイン登録結果: 成功={successful_plugins}, 失敗={len(failed_plugins)}")
        print("[DEBUG] plugin_manager.plugins.keys():", self.plugin_manager.plugins.keys())
    
    def _setup_plugin_callbacks(self, plugin_instance, callbacks, plugin_name):
        """プラグインのコールバック設定（設定漏れ防止）"""
        # コールバック設定のマッピング
        callback_methods = {
            'parameter_change': 'set_parameter_change_callback',
            'histogram': 'set_histogram_callback',
            'threshold': 'set_threshold_callback',
            'special_filter': 'set_special_filter_callback',
            'morphology': 'set_morphology_callback',
            'contour': 'set_contour_callback',
            'feature': 'set_feature_callback',
            'frequency': 'set_frequency_callback',
            'blur': 'set_blur_callback',
            'noise': 'set_noise_callback',
            'undo_special_filter': 'set_undo_special_filter_callback',
            'undo_morphology': 'set_undo_morphology_callback',
            'undo_contour': 'set_undo_contour_callback',
            'undo_features': 'set_undo_features_callback',
            'undo_frequency': 'set_undo_frequency_callback',
            'undo_blur': 'set_undo_blur_callback',
            'undo_noise': 'set_undo_noise_callback',
            'undo_histogram': 'set_undo_histogram_callback',
        }

        # histogram_analysisプラグインには画像取得コールバックを必ず渡す
        if plugin_name == 'histogram_analysis' and hasattr(plugin_instance, 'set_histogram_callback'):
            def get_current_image():
                # ImageEditorから現在の画像を取得
                if hasattr(self, 'image_editor'):
                    img = self.image_editor.get_current_image()
                    print(f"[DEBUG] get_current_image called, img={img}")
                    return img
                print("[DEBUG] get_current_image: image_editor not found")
                return None
            plugin_instance.set_histogram_callback(get_current_image)
        
        # 各コールバックを設定
        for callback_key, callback_function in callbacks.items():
            if callback_key in callback_methods:
                method_name = callback_methods[callback_key]
                if hasattr(plugin_instance, method_name):
                    try:
                        getattr(plugin_instance, method_name)(callback_function)
                        debug_print(f"     ✓ {callback_key} コールバック設定完了")
                    except Exception as e:
                        warning_print(f"{callback_key} コールバック設定失敗: {e}")
                else:
                    warning_print(f"{plugin_name}: {method_name} メソッドが見つかりません")
            else:
                warning_print(f"未知のコールバック設定: {callback_key}")
        
        # 設定検証（必要なコールバックがすべて設定されているかチェック）
        self._validate_plugin_configuration(plugin_instance, callbacks, plugin_name)
    
    def _validate_plugin_configuration(self, plugin_instance, callbacks, plugin_name):
        """プラグイン設定の検証（設定漏れ検出）"""
        # プラグインタイプ別の必須コールバック定義
        required_callbacks = {
            'basic_adjustment': ['parameter_change'],
            'density_adjustment': ['parameter_change', 'histogram', 'threshold'],
            'filter_processing': [
                'parameter_change', 'special_filter', 'morphology', 'contour',
                'undo_special_filter', 'undo_morphology', 'undo_contour'
            ],
            'image_analysis': [
                'histogram', 'feature', 'frequency', 'blur', 'noise',
                'undo_features', 'undo_frequency', 'undo_blur', 'undo_noise', 'undo_histogram'
            ]
        }
        
        if plugin_name in required_callbacks:
            required = set(required_callbacks[plugin_name])
            configured = set(callbacks.keys())
            
            missing = required - configured
            if missing:
                warning_print(f"{plugin_name}: 未設定のコールバック = {missing}")
            else:
                debug_print(f"{plugin_name}: 全必須コールバック設定完了")
        else:
            debug_print(f"{plugin_name}: 検証定義がありません（カスタムプラグインの可能性）")
    
    def create_plugin_tabs(self):
        """プラグイン用のタブとUIを作成"""
        # 画像解析タブのフレームにサブプラグインUIを必ず生成
        image_analysis_frame = self.plugin_frames.get("image_analysis")
        histogram_plugin = self.plugin_manager.get_plugin("histogram_analysis")
        image_analysis_plugin = self.plugin_manager.get_plugin("image_analysis")
        if image_analysis_frame:
            # HistogramAnalysisPluginのUI生成は不要。ImageAnalysisPlugin側で集中管理。
            if image_analysis_plugin:
                try:
                    print(f"[DEBUG] image_analysis_plugin.setup_ui呼び出し: {image_analysis_plugin}, frame={image_analysis_frame}")
                    image_analysis_plugin.setup_ui(image_analysis_frame)
                except Exception as e:
                    print(f"[ERROR] 画像解析プラグインのUI生成で例外: {e}")
                    import traceback
                    traceback.print_exc()

        # 他のタブは従来通り
        for plugin_name, frame in self.plugin_frames.items():
            if plugin_name == "image_analysis":
                continue
            plugin = self.plugin_manager.get_plugin(plugin_name)
            print(f"[DEBUG] create_plugin_tabs: plugin_name={plugin_name}, plugin={plugin}, frame={frame}")
            if plugin:
                try:
                    print(f"[DEBUG] {plugin_name} setup_ui呼び出し: {plugin}, frame={frame}")
                    plugin.setup_ui(frame)
                except Exception as e:
                    print(f"[ERROR] プラグイン '{plugin_name}' のUI生成で例外: {e}")
                    import traceback
                    traceback.print_exc()
    
    def on_plugin_parameter_change(self):
        """プラグインパラメータ変更時の処理"""
        if self.image_editor.has_image():
            self.apply_all_adjustments()
    
    def on_image_loaded(self):
        """画像読み込み完了時の処理"""
        info_print("新しい画像読み込み: 全プラグインを初期化中...")
        self.reset_all_plugins()
        # 画像解析プラグインに画像をセット
        image_analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
        density_plugin = self.plugin_manager.get_plugin('density_adjustment')
        current_image = self.image_editor.get_current_image()
        if image_analysis_plugin and current_image:
            image_analysis_plugin.set_image(current_image)
        if density_plugin and current_image:
            density_plugin.set_image(current_image)
        debug_print("全プラグイン初期化完了")
    
    def apply_all_adjustments(self):
        """全プラグインの調整を適用"""
        try:
            if not self.image_editor.has_image():
                warning_print("画像が読み込まれていません")
                return
            
            debug_print("全プラグイン処理開始...")
            
            # 元画像から開始
            adjusted_image = self.image_editor.get_original_image()
            if not adjusted_image:
                error_print("元画像が取得できません")
                return
            debug_print(f"元画像サイズ: {adjusted_image.size}")
            
            # 画像解析プラグインに画像をセット
            image_analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if image_analysis_plugin:
                image_analysis_plugin.set_image(adjusted_image)
            
            # 有効な全プラグインで順次処理
            enabled_plugins = self.plugin_manager.get_enabled_plugins()
            debug_print(f"有効プラグイン数: {len(enabled_plugins)}")
            
            for i, plugin in enumerate(enabled_plugins, 1):
                plugin_params = plugin.get_parameters()
                debug_print(f"🎛️ プラグイン{i}: {plugin.get_display_name()}")
                debug_print(f"   パラメータ: {plugin_params}")
                
                # パラメータに変更があるかチェック
                has_changes = any(
                    (isinstance(v, (int, float)) and v != 0) or 
                    (isinstance(v, str) and v != "none") 
                    for v in plugin_params.values()
                )
                
                if has_changes:
                    adjusted_image = plugin.process_image(adjusted_image)
                    debug_print(f"   ✅ 処理適用: {plugin.get_display_name()}")
                else:
                    debug_print(f"   ⏭️ スキップ: {plugin.get_display_name()} (変更なし)")
            
            # 処理済み画像を表示
            self.image_editor.update_current_image(adjusted_image)
            
            debug_print("✅ 全プラグイン処理完了")
            
        except Exception as e:
            error_print(f"プラグイン処理エラー: {e}")
            import traceback
            traceback.print_exc()
            MessageDialog.show_error(self, "エラー", f"画像処理エラー: {e}")
    
    def undo_special_filter(self, filter_type: str):
        """特殊フィルターのundo処理"""
        try:
            debug_print(f"🔄 特殊フィルター取消: {filter_type}")
            
            # フィルタープラグインのバックアップから復元
            filter_plugin = self.plugin_manager.get_plugin("filter_processing")
            if filter_plugin and hasattr(filter_plugin, 'special_filter_backup') and filter_plugin.special_filter_backup:
                # バックアップから復元
                self.image_editor.update_current_image(filter_plugin.special_filter_backup)
                filter_plugin.special_filter_backup = None  # バックアップをクリア
                self.image_editor.status_label.configure(text=f"🔄 {filter_type}フィルターを取り消しました")
                debug_print(f"✅ 特殊フィルター取消完了: {filter_type}")
            else:
                # バックアップがない場合は全体を再処理
                debug_print("⚠️ バックアップがないため全体を再処理")
                self.apply_all_adjustments()
                self.image_editor.status_label.configure(text="🔄 フィルターを取り消しました（全体再処理）")
                
        except Exception as e:
            error_print(f"特殊フィルター取消エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"フィルター取消エラー: {e}")
    
    def undo_morphology_operation(self):
        """モルフォロジー演算のundo処理"""
        try:
            debug_print("🔄 モルフォロジー演算取消")
            
            # フィルタープラグインのバックアップから復元
            filter_plugin = self.plugin_manager.get_plugin("filter_processing")
            if filter_plugin and hasattr(filter_plugin, 'morphology_backup') and filter_plugin.morphology_backup:
                # バックアップから復元
                self.image_editor.update_current_image(filter_plugin.morphology_backup)
                filter_plugin.morphology_backup = None  # バックアップをクリア
                self.image_editor.status_label.configure(text="🔄 モルフォロジー演算を取り消しました")
                debug_print("✅ モルフォロジー演算取消完了")
            else:
                # バックアップがない場合は全体を再処理
                debug_print("⚠️ バックアップがないため全体を再処理")
                self.apply_all_adjustments()
                self.image_editor.status_label.configure(text="🔄 モルフォロジー演算を取り消しました（全体再処理）")
                
        except Exception as e:
            debug_print(f"❌ モルフォロジー演算取消エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"モルフォロジー演算取消エラー: {e}")
    
    def undo_contour_detection(self):
        """輪郭検出のundo処理"""
        try:
            debug_print("🔄 輪郭検出取消")
            
            # フィルタープラグインのバックアップから復元
            filter_plugin = self.plugin_manager.get_plugin("filter_processing")
            if filter_plugin and hasattr(filter_plugin, 'contour_backup') and filter_plugin.contour_backup:
                # バックアップから復元
                self.image_editor.update_current_image(filter_plugin.contour_backup)
                filter_plugin.contour_backup = None  # バックアップをクリア
                self.image_editor.status_label.configure(text="🔄 輪郭検出を取り消しました")
                debug_print("✅ 輪郭検出取消完了")
            else:
                # バックアップがない場合は全体を再処理
                debug_print("⚠️ バックアップがないため全体を再処理")
                self.apply_all_adjustments()
                self.image_editor.status_label.configure(text="🔄 輪郭検出を取り消しました（全体再処理）")
                
        except Exception as e:
            debug_print(f"❌ 輪郭検出取消エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"輪郭検出取消エラー: {e}")
    
    def apply_histogram_equalization(self):
        """ヒストグラム均等化を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                return
            
            # ImageUtilsクラスを使用してヒストグラム均等化
            equalized_image = IUtils.apply_histogram_equalization(current_image)
            self.image_editor.update_current_image(equalized_image)
            self.image_editor.status_label.configure(text="📊 ヒストグラム均等化を適用しました")
                
        except Exception as e:
            debug_print(f"❌ ヒストグラム均等化エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"ヒストグラム均等化エラー: {e}")
    
    def apply_special_filter(self, filter_type: str):
        """特殊フィルターを適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                return
            
            # フィルタープラグインを取得
            filter_plugin = self.plugin_manager.get_plugin("filter_processing")
            if filter_plugin:
                # 処理前の画像をバックアップ
                filter_plugin.special_filter_backup = current_image.copy()
                
                # 基底クラスのapply_special_filterメソッドを使用
                filtered_image = filter_plugin.apply_special_filter(current_image, filter_type)
                self.image_editor.update_current_image(filtered_image)
                self.image_editor.status_label.configure(text=f"✨ {filter_type}フィルターを適用しました")
                debug_print(f"✅ 特殊フィルター適用完了: {filter_type}")
            else:
                debug_print("❌ フィルタープラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ 特殊フィルターエラー: {e}")
            MessageDialog.show_error(self, "エラー", f"フィルター処理エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_binary_threshold(self):
        """2値化を適用"""
        print("[DEBUG] plugin_manager.plugins.keys():", self.plugin_manager.plugins.keys())
        density_plugin = self.plugin_manager.get_plugin('density_adjustment')
        print("[DEBUG] density_plugin:", density_plugin)
        print("[DEBUG] hasattr(apply_binary_threshold):", hasattr(density_plugin, 'apply_binary_threshold'))
        print("[DEBUG] type(density_plugin):", type(density_plugin))
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            # 濃度調整プラグインから2値化を実行
            if density_plugin and hasattr(density_plugin, 'apply_binary_threshold'):
                apply_method = getattr(density_plugin, 'apply_binary_threshold')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="📐 2値化を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 濃度調整プラグインが見つかりません")
        except Exception as e:
            debug_print(f"❌ 2値化エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"2値化エラー: {e}")
    
    def apply_morphology_operation(self, operation: str):
        """モルフォロジー演算を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # フィルター処理プラグインからモルフォロジー演算を実行
            filter_plugin = self.plugin_manager.get_plugin('filter_processing')
            if filter_plugin and hasattr(filter_plugin, 'apply_morphology_operation'):
                # 処理前の画像をバックアップ
                filter_plugin.morphology_backup = current_image.copy()
                
                apply_method = getattr(filter_plugin, 'apply_morphology_operation')
                processed_image = apply_method(current_image, operation)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text=f"🔧 {operation}演算を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ フィルター処理プラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ モルフォロジー演算エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"モルフォロジー演算エラー: {e}")
    
    def apply_contour_detection(self):
        """輪郭検出を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # フィルター処理プラグインから輪郭検出を実行
            filter_plugin = self.plugin_manager.get_plugin('filter_processing')
            if filter_plugin and hasattr(filter_plugin, 'apply_contour_detection'):
                # 処理前の画像をバックアップ
                filter_plugin.contour_backup = current_image.copy()
                
                apply_method = getattr(filter_plugin, 'apply_contour_detection')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="🎯 輪郭検出を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ フィルター処理プラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ 輪郭検出エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"輪郭検出エラー: {e}")
    
    def show_histogram_analysis(self):
        """ヒストグラム解析を表示"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # バックアップを保存
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin:
                analysis_plugin.histogram_backup = current_image.copy()
            
            # OpenCVでヒストグラム計算（matplotlibなしで基本統計を表示）
            cv_image = cv2.cvtColor(np.array(current_image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 基本統計情報を計算
            mean_val = np.mean(gray_image)
            std_val = np.std(gray_image)
            min_val = np.min(gray_image)
            max_val = np.max(gray_image)
            
            # ヒストグラム計算（binの数を256に設定）
            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
            
            # 最頻値（ピーク）を計算
            peak_idx = np.argmax(hist)
            peak_value = hist[peak_idx][0]
            
            # 結果を画像に描画
            result_image = cv_image.copy()
            
            # 統計情報をテキストで表示
            stats_text = [
                f"Mean: {mean_val:.1f}",
                f"Std: {std_val:.1f}",
                f"Range: {min_val}-{max_val}",
                f"Peak: {peak_idx} ({peak_value:.0f})"
            ]
            
            # テキストを画像に描画
            y_offset = 30
            for i, text in enumerate(stats_text):
                cv2.putText(result_image, text, (10, y_offset + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # PIL形式に戻して表示
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            
            self.image_editor.update_current_image(final_image)
            self.image_editor.display_image(final_image)
            self.image_editor.status_label.configure(text="📊 ヒストグラム解析を表示しました")
            debug_print(f"📊 ヒストグラム解析完了: 平均={mean_val:.1f}, 標準偏差={std_val:.1f}")
                
        except Exception as e:
            debug_print(f"❌ ヒストグラム解析エラー: {e}")
            self.image_editor.status_label.configure(text="❌ ヒストグラム解析でエラーが発生しました")
    
    def apply_feature_detection(self, feature_type: str):
        """特徴点検出を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # バックアップを保存
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin:
                analysis_plugin.features_backup = current_image.copy()
            
            # 画像解析プラグインから特徴点検出を実行
            if analysis_plugin and hasattr(analysis_plugin, 'apply_feature_detection'):
                apply_method = getattr(analysis_plugin, 'apply_feature_detection')
                processed_image = apply_method(current_image, feature_type)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text=f"🎯 {feature_type}特徴点検出を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ 特徴点検出エラー: {e}")
    
    def apply_frequency_analysis(self, analysis_type: str):
        """周波数解析を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # バックアップを保存
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin:
                analysis_plugin.frequency_backup = current_image.copy()
            
            # 画像解析プラグインから周波数解析を実行
            if analysis_plugin and hasattr(analysis_plugin, 'apply_frequency_analysis'):
                apply_method = getattr(analysis_plugin, 'apply_frequency_analysis')
                processed_image = apply_method(current_image, analysis_type)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text=f"🔬 {analysis_type}解析を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ 周波数解析エラー: {e}")
    
    def detect_blur(self):
        """ブラー検出を実行"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # バックアップを保存
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin:
                analysis_plugin.blur_backup = current_image.copy()
            
            # 画像解析プラグインからブラー検出を実行
            if analysis_plugin and hasattr(analysis_plugin, 'detect_blur'):
                apply_method = getattr(analysis_plugin, 'detect_blur')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="🔍 ブラー検出を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ ブラー検出エラー: {e}")
    
    def analyze_noise(self):
        """ノイズ解析を実行"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # バックアップを保存
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin:
                analysis_plugin.noise_backup = current_image.copy()
            
            # 画像解析プラグインからノイズ解析を実行
            if analysis_plugin and hasattr(analysis_plugin, 'analyze_noise'):
                apply_method = getattr(analysis_plugin, 'analyze_noise')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="📈 ノイズ解析を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            debug_print(f"❌ ノイズ解析エラー: {e}")
    
    # 画像解析Undo機能
    def undo_feature_detection(self, feature_type: str):
        """特徴点検出のundo"""
        try:
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'features_backup') and analysis_plugin.features_backup:
                self.image_editor.update_current_image(analysis_plugin.features_backup)
                self.image_editor.display_image(analysis_plugin.features_backup)
                analysis_plugin.features_backup = None
                self.image_editor.status_label.configure(text=f"🔄 {feature_type}特徴点検出を取り消しました")
            else:
                self.image_editor.status_label.configure(text="❌ 取り消し可能な特徴点検出がありません")
        except Exception as e:
            debug_print(f"❌ 特徴点検出undo エラー: {e}")
    
    def undo_frequency_analysis(self, analysis_type: str):
        """周波数解析のundo"""
        try:
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'frequency_backup') and analysis_plugin.frequency_backup:
                self.image_editor.update_current_image(analysis_plugin.frequency_backup)
                self.image_editor.display_image(analysis_plugin.frequency_backup)
                analysis_plugin.frequency_backup = None
                self.image_editor.status_label.configure(text=f"🔄 {analysis_type}解析を取り消しました")
            else:
                self.image_editor.status_label.configure(text="❌ 取り消し可能な周波数解析がありません")
        except Exception as e:
            debug_print(f"❌ 周波数解析undo エラー: {e}")
    
    def undo_blur_detection(self):
        """ブラー検出のundo"""
        try:
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'blur_backup') and analysis_plugin.blur_backup:
                self.image_editor.update_current_image(analysis_plugin.blur_backup)
                self.image_editor.display_image(analysis_plugin.blur_backup)
                analysis_plugin.blur_backup = None
                self.image_editor.status_label.configure(text="🔄 ブラー検出を取り消しました")
            else:
                self.image_editor.status_label.configure(text="❌ 取り消し可能なブラー検出がありません")
        except Exception as e:
            debug_print(f"❌ ブラー検出undo エラー: {e}")
    
    def undo_noise_analysis(self):
        """ノイズ解析のundo"""
        try:
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'noise_backup') and analysis_plugin.noise_backup:
                self.image_editor.update_current_image(analysis_plugin.noise_backup)
                self.image_editor.display_image(analysis_plugin.noise_backup)
                analysis_plugin.noise_backup = None
                self.image_editor.status_label.configure(text="🔄 ノイズ解析を取り消しました")
            else:
                self.image_editor.status_label.configure(text="❌ 取り消し可能なノイズ解析がありません")
        except Exception as e:
            debug_print(f"❌ ノイズ解析undo エラー: {e}")
    
    def undo_histogram_analysis(self):
        """ヒストグラム解析のundo"""
        try:
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'histogram_backup') and analysis_plugin.histogram_backup:
                self.image_editor.update_current_image(analysis_plugin.histogram_backup)
                self.image_editor.display_image(analysis_plugin.histogram_backup)
                analysis_plugin.histogram_backup = None
                self.image_editor.status_label.configure(text="🔄 ヒストグラム解析を取り消しました")
            else:
                self.image_editor.status_label.configure(text="❌ 取り消し可能なヒストグラム解析がありません")
        except Exception as e:
            debug_print(f"❌ ヒストグラム解析undo エラー: {e}")
    
    # 画像操作メソッド（ImageEditorクラスに委譲）
    def load_image(self):
        """画像を読み込み"""
        self.image_editor.load_image(parent_window=self)
    
    def save_image(self):
        """画像を保存"""
        self.image_editor.save_image(parent_window=self)
    
    def reset_to_original(self):
        """元画像に復元"""
        if self.image_editor.reset_to_original():
            # 全プラグインもリセット
            self.reset_all_plugins()
    
    def reset_all_plugins(self):
        """全プラグインをリセット"""
        try:
            debug_print("🔧 全プラグインリセット開始...")
            
            # 全プラグインのパラメータをリセット
            for plugin in self.plugin_manager.get_all_plugins():
                if hasattr(plugin, 'reset_parameters'):
                    plugin.reset_parameters()
                    debug_print(f"   🔄 {plugin.get_display_name()}: パラメータリセット完了")
            
            # 元画像を表示（プラグイン処理を適用しない状態）
            if self.image_editor.has_image():
                self.image_editor.reset_to_original()
                debug_print("   📸 元画像を表示")
            
            self.image_editor.status_label.configure(text="🔧 全プラグインをリセットしました")
            debug_print("✅ 全プラグインリセット完了")
            
        except Exception as e:
            debug_print(f"❌ プラグインリセットエラー: {e}")
            MessageDialog.show_error(self, "エラー", f"リセットエラー: {e}")
            import traceback
            traceback.print_exc()


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(description='Advanced Image Editor - 高度画像編集アプリケーション')
    
    # ログレベル指定オプション
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       default='INFO', help='ログレベルを指定 (デフォルト: INFO)')
    
    # 下位互換性のため--debugオプションも残す
    parser.add_argument('--debug', action='store_true', 
                       help='デバッグモードで起動（--log-level DEBUGと同等）')
    
    return parser.parse_args()


def main():
    """メイン関数"""
    try:
        # コマンドライン引数解析
        args = parse_arguments()
        
        # ログレベル設定
        if args.debug:
            # --debugオプションが指定された場合はDEBUGレベルに設定
            set_log_level(LogLevel.DEBUG)
        else:
            # --log-levelオプションの値を使用
            level_mapping = {
                'DEBUG': LogLevel.DEBUG,
                'INFO': LogLevel.INFO,
                'WARNING': LogLevel.WARNING,
                'ERROR': LogLevel.ERROR,
                'CRITICAL': LogLevel.CRITICAL
            }
            set_log_level(level_mapping[args.log_level])
        
        info_print("🎨 Advanced Image Editor を起動中...")
        debug_print(f"ログレベル設定: {get_log_level().name}")
        
        # CustomTkinterの外観設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # アプリケーション起動
        app = AdvancedImageEditor()
        app.mainloop()
        
    except Exception as e:
        critical_print(f"アプリケーションの起動に失敗しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()