#!/usr/bin/env python3
"""
Advanced Image Editor - Plugin System Version
プラグインシステム対応版画像編集アプリケーション

## 概要

プラグインシステムを採用した高度な画像編集アプリケーションです。
モジュラー設計により、各機能は独立したプラグインとして実装されており、
優れた保守性・拡張性・可読性を実現しています。

4つの専門プラグイン（基本調整・濃度調整・フィルター処理・画像解析）により、
基本的な画像補正から高度な画像解析まで幅広い画像編集機能を提供します。

【実行方法】
cd <本リポジトリのクローン先ディレクトリ>
# macOS/Linux: .venv/bin/python src/main_plugin.py
# Windows: .venv\\Scripts\\python.exe src\\main_plugin.py

【詳細ドキュメント】
プラグインの作成方法・API仕様・トラブルシューティングは README.md を参照してください。

【作成者】GitHub Copilot + プラグインシステム設計
【バージョン】Plugin System 1.0.0
【最終更新】2025年9月15日
"""

try:
    import tkinter as tk
    import customtkinter as ctk
    from PIL import Image, ImageTk
    import cv2
    import numpy as np
    from tkinter import filedialog, messagebox
    import os
    import sys
    print("✅ 必要なライブラリのインポートが完了しました")
except ImportError as e:
    print(f"❌ ライブラリのインポートエラー: {e}")
    print("📦 以下のコマンドでライブラリをインストールしてください:")
    print("pip install customtkinter opencv-python numpy pillow")
    sys.exit(1)

# gui_frameworkライブラリのインポート（オプション）
try:
    from gui_framework.core import FontManager, StyleManager, ImageUtils
    from gui_framework.widgets import ScalableLabel, StyledButton
    from gui_framework.widgets.dialogs import MessageDialog, TaskRunner
    print("✅ gui_framework ライブラリのインポートが完了しました")
    GUI_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ gui_framework インポート警告: {e}")
    print("📦 基本機能のみで動作します。gui_frameworkなしで継続...")
    GUI_FRAMEWORK_AVAILABLE = False
    
    # gui_frameworkが利用できない場合の代替クラス
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


class AdvancedImageEditorPluginVersion(ctk.CTk):
    """
    プラグインシステム対応版 Advanced Image Editor
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
        
        print("✅ Advanced Image Editor (Plugin Version) が起動しました")
        
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
        """プラグイン用のタブビューをセットアップ"""
        # タブ定義
        plugin_tabs = {
            "basic_adjustment": "🎯 基本調整",
            "density_adjustment": "🌈 濃度調整", 
            "filter_processing": "🌀 フィルター",
            "image_analysis": "🔬 画像解析"
        }
        
        # UIクラスでタブを作成
        self.plugin_frames = self.ui.setup_plugin_tabs(plugin_tabs)
    
    def setup_plugins(self):
        """プラグインを登録・初期化"""
        print("🔌 プラグインを登録中...")
        
        # 基本調整プラグイン
        basic_plugin = BasicAdjustmentPlugin()
        basic_plugin.set_parameter_change_callback(self.on_plugin_parameter_change)
        self.plugin_manager.register_plugin(basic_plugin)
        
        # 濃度調整プラグイン
        density_plugin = DensityAdjustmentPlugin()
        density_plugin.set_parameter_change_callback(self.on_plugin_parameter_change)
        density_plugin.set_histogram_callback(self.apply_histogram_equalization)
        density_plugin.set_threshold_callback(self.apply_binary_threshold)
        self.plugin_manager.register_plugin(density_plugin)
        
        # フィルター処理プラグイン
        filter_plugin = FilterProcessingPlugin()
        filter_plugin.set_parameter_change_callback(self.on_plugin_parameter_change)
        filter_plugin.set_special_filter_callback(self.apply_special_filter)
        filter_plugin.set_morphology_callback(self.apply_morphology_operation)
        filter_plugin.set_contour_callback(self.apply_contour_detection)
        self.plugin_manager.register_plugin(filter_plugin)
        
        # 画像解析プラグイン（旧：高度処理プラグイン）
        analysis_plugin = ImageAnalysisPlugin()
        analysis_plugin.set_histogram_callback(self.show_histogram_analysis)
        analysis_plugin.set_feature_callback(self.apply_feature_detection)
        analysis_plugin.set_frequency_callback(self.apply_frequency_analysis)
        analysis_plugin.set_blur_callback(self.detect_blur)
        analysis_plugin.set_noise_callback(self.analyze_noise)
        self.plugin_manager.register_plugin(analysis_plugin)
        
        print(f"✅ {len(self.plugin_manager.plugins)}個のプラグインが登録されました")
    
    def create_plugin_tabs(self):
        """プラグイン用のタブとUIを作成"""
        for plugin_name, frame in self.plugin_frames.items():
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if plugin:
                # プラグインUIを作成
                plugin.create_ui(frame)
    
    def on_plugin_parameter_change(self):
        """プラグインパラメータ変更時の処理"""
        if self.image_editor.has_image():
            self.apply_all_adjustments()
    
    def on_image_loaded(self):
        """画像読み込み完了時の処理"""
        print("🔄 新しい画像読み込み: 全プラグインを初期化中...")
        self.reset_all_plugins()
        print("✅ 全プラグイン初期化完了")
    
    def apply_all_adjustments(self):
        """全プラグインの調整を適用"""
        try:
            if not self.image_editor.has_image():
                print("⚠️ 画像が読み込まれていません")
                return
            
            print("🔄 全プラグイン処理開始...")
            
            # 元画像から開始
            adjusted_image = self.image_editor.get_original_image()
            if not adjusted_image:
                print("❌ 元画像が取得できません")
                return
            print(f"📸 元画像サイズ: {adjusted_image.size}")
            
            # 有効な全プラグインで順次処理
            enabled_plugins = self.plugin_manager.get_enabled_plugins()
            print(f"🔌 有効プラグイン数: {len(enabled_plugins)}")
            
            for i, plugin in enumerate(enabled_plugins, 1):
                plugin_params = plugin.get_parameters()
                print(f"🎛️ プラグイン{i}: {plugin.get_display_name()}")
                print(f"   パラメータ: {plugin_params}")
                
                # パラメータに変更があるかチェック
                has_changes = any(
                    (isinstance(v, (int, float)) and v != 0) or 
                    (isinstance(v, str) and v != "none") 
                    for v in plugin_params.values()
                )
                
                if has_changes:
                    adjusted_image = plugin.process_image(adjusted_image)
                    print(f"   ✅ 処理適用: {plugin.get_display_name()}")
                else:
                    print(f"   ⏭️ スキップ: {plugin.get_display_name()} (変更なし)")
            
            # 処理済み画像を表示
            self.image_editor.update_current_image(adjusted_image)
            
            print("✅ 全プラグイン処理完了")
            
        except Exception as e:
            print(f"❌ プラグイン処理エラー: {e}")
            import traceback
            traceback.print_exc()
            MessageDialog.show_error(self, "エラー", f"画像処理エラー: {e}")
    
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
            print(f"❌ ヒストグラム均等化エラー: {e}")
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
                # 基底クラスのapply_special_filterメソッドを使用
                filtered_image = filter_plugin.apply_special_filter(current_image, filter_type)
                self.image_editor.update_current_image(filtered_image)
                self.image_editor.status_label.configure(text=f"✨ {filter_type}フィルターを適用しました")
                print(f"✅ 特殊フィルター適用完了: {filter_type}")
            else:
                print("❌ フィルタープラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ 特殊フィルターエラー: {e}")
            MessageDialog.show_error(self, "エラー", f"フィルター処理エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_binary_threshold(self):
        """2値化を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # 濃度調整プラグインから2値化を実行
            density_plugin = self.plugin_manager.get_plugin('density_adjustment')
            if density_plugin and hasattr(density_plugin, 'apply_binary_threshold'):
                apply_method = getattr(density_plugin, 'apply_binary_threshold')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="📐 2値化を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 濃度調整プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ 2値化エラー: {e}")
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
                apply_method = getattr(filter_plugin, 'apply_morphology_operation')
                processed_image = apply_method(current_image, operation)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text=f"🔧 {operation}演算を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ フィルター処理プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ モルフォロジー演算エラー: {e}")
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
                apply_method = getattr(filter_plugin, 'apply_contour_detection')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="🎯 輪郭検出を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ フィルター処理プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ 輪郭検出エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"輪郭検出エラー: {e}")
    
    def show_histogram_analysis(self):
        """ヒストグラム解析を表示"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # 簡易ヒストグラム解析を実行（詳細な解析は今後実装）
            self.image_editor.status_label.configure(text="📊 ヒストグラム解析機能（実装予定）")
            print("📊 ヒストグラム解析機能が実行されました（実装予定）")
                
        except Exception as e:
            print(f"❌ ヒストグラム解析エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"ヒストグラム解析エラー: {e}")
    
    def apply_feature_detection(self, feature_type: str):
        """特徴点検出を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # 画像解析プラグインから特徴点検出を実行
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'apply_feature_detection'):
                apply_method = getattr(analysis_plugin, 'apply_feature_detection')
                processed_image = apply_method(current_image, feature_type)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text=f"🎯 {feature_type}特徴点検出を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ 特徴点検出エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"特徴点検出エラー: {e}")
    
    def apply_frequency_analysis(self, analysis_type: str):
        """周波数解析を適用"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # 画像解析プラグインから周波数解析を実行
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'apply_frequency_analysis'):
                apply_method = getattr(analysis_plugin, 'apply_frequency_analysis')
                processed_image = apply_method(current_image, analysis_type)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text=f"🔬 {analysis_type}解析を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ 周波数解析エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"周波数解析エラー: {e}")
    
    def detect_blur(self):
        """ブラー検出を実行"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # 画像解析プラグインからブラー検出を実行
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'detect_blur'):
                apply_method = getattr(analysis_plugin, 'detect_blur')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="🔍 ブラー検出を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ ブラー検出エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"ブラー検出エラー: {e}")
    
    def analyze_noise(self):
        """ノイズ解析を実行"""
        try:
            current_image = self.image_editor.get_current_image()
            if not current_image:
                self.image_editor.status_label.configure(text="❌ 画像が読み込まれていません")
                return
            
            # 画像解析プラグインからノイズ解析を実行
            analysis_plugin = self.plugin_manager.get_plugin('image_analysis')
            if analysis_plugin and hasattr(analysis_plugin, 'analyze_noise'):
                apply_method = getattr(analysis_plugin, 'analyze_noise')
                processed_image = apply_method(current_image)
                self.image_editor.update_current_image(processed_image)
                self.image_editor.display_image(processed_image)
                self.image_editor.status_label.configure(text="📈 ノイズ解析を適用しました")
            else:
                self.image_editor.status_label.configure(text="❌ 画像解析プラグインが見つかりません")
                
        except Exception as e:
            print(f"❌ ノイズ解析エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"ノイズ解析エラー: {e}")
    
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
            print("🔧 全プラグインリセット開始...")
            
            # 全プラグインのパラメータをリセット
            for plugin in self.plugin_manager.get_all_plugins():
                if hasattr(plugin, 'reset_parameters'):
                    plugin.reset_parameters()
                    print(f"   🔄 {plugin.get_display_name()}: パラメータリセット完了")
            
            # 元画像を表示（プラグイン処理を適用しない状態）
            if self.image_editor.has_image():
                self.image_editor.reset_to_original()
                print("   📸 元画像を表示")
            
            self.image_editor.status_label.configure(text="🔧 全プラグインをリセットしました")
            print("✅ 全プラグインリセット完了")
            
        except Exception as e:
            print(f"❌ プラグインリセットエラー: {e}")
            MessageDialog.show_error(self, "エラー", f"リセットエラー: {e}")
            import traceback
            traceback.print_exc()


def main():
    """メイン関数"""
    try:
        print("🎨 Advanced Image Editor (Plugin Version) を起動中...")
        
        # CustomTkinterの外観設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # アプリケーション起動
        app = AdvancedImageEditorPluginVersion()
        app.mainloop()
        
    except Exception as e:
        print(f"❌ アプリケーションの起動に失敗しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()