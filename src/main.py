#!/usr/bin/env python3
"""
Advanced Image Editor - 高度な画像編集アプリケーション

【機能概要】
このファイルは、lib/gui_frameworkライブラリを使用したプロフェッショナルな画像編集アプリケーションです。

【主要機能】
■ パッケージ管理
  - gui_framework: pip install -e でインストール済み
  - 標準的なPythonパッケージとして利用
  ├ 実現: pyproject.toml + setuptools

■ UI コンポーネント
  - CustomTkinter ベースのモダンなGUI
  - FontManager: スケーラブルフォント管理
  - StyleManager: 統一されたスタイル管理  
  - ScalableLabel: 自動スケールラベル
  - StyledButton: 統一デザインボタン
  - TabLayout: タブベースレイアウト
  ├ 実現クラス: gui_framework.core.FontManager
  ├ 実現クラス: gui_framework.core.StyleManager
  ├ 実現クラス: gui_framework.widgets.ScalableLabel
  ├ 実現クラス: gui_framework.widgets.StyledButton
  └ 実現クラス: gui_framework.layouts.TabLayout

■ 画像処理機能
  - ImageUtils: 画像ファイル読み込み・保存
  - ファイルダイアログによる画像選択
  - PIL(Pillow)ベースの画像処理
  - エラーハンドリング付き画像操作
  ├ 実現クラス: gui_framework.core.ImageUtils
  └ 実現メソッド: AdvancedImageEditor.load_image(), save_image()

■ ダイアログシステム
  - MessageDialog: 情報・警告・エラー表示
  - TaskRunner: プログレス付き長時間処理
  - ProgressDialog: 進捗表示とキャンセル機能
  ├ 実現クラス: gui_framework.widgets.dialogs.MessageDialog
  ├ 実現クラス: gui_framework.widgets.dialogs.TaskRunner
  └ 実現メソッド: AdvancedImageEditor.process_image()

■ アプリケーション構成
  - AdvancedImageEditor(ctk.CTk): メインアプリケーションクラス
  - 1200x800ピクセルのウィンドウサイズ
  - タイトル、タブレイアウト、操作ボタン
  - ステータス表示機能
  ├ 実現クラス: AdvancedImageEditor(customtkinter.CTk)
  ├ 実現メソッド: AdvancedImageEditor.__init__()
  ├ 実現メソッド: AdvancedImageEditor.setup_ui()
  └ 実現属性: title_label, main_layout, button_frame, status_label

【技術仕様】
- 対応Python: 3.8+
- 依存ライブラリ: customtkinter 5.2+, Pillow 11.3+
- 実行方法: ./venv/bin/python src/main.py
- UI フレームワーク: CustomTkinter (tkinter問題回避)
  └ 実現: customtkinter.CTk継承, ctk.set_appearance_mode()

【アーキテクチャ】
- lib/gui_framework: 再利用可能UIコンポーネント
- 自動ライブラリ検出: 開発環境に依存しない配置
- モジュール設計: FontManager, StyleManager, ImageUtilsの分離
- エラーハンドリング: 堅牢な例外処理とユーザーフィードバック
  ├ 実現パッケージ: gui_framework.core.*, gui_framework.widgets.*
  ├ 実現関数: find_lib_path(), main()
  └ 実現機能: try-except文, MessageDialog.show_error()
"""

import sys
import os
from pathlib import Path

# libライブラリパスを追加
# libライブラリパスを相対パスで設定
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# gui_frameworkライブラリのパスを相対的に探索
potential_lib_paths = [
    os.path.join(project_root, "..", "..", "lib"),  # ../../lib
    os.path.join(project_root, "..", "lib"),        # ../lib
    os.path.join(project_root, "lib"),              # ./lib
]

lib_path = None
for path in potential_lib_paths:
    abs_path = os.path.abspath(path)
    gui_framework_path = os.path.join(abs_path, "gui_framework")
    if os.path.exists(gui_framework_path) and os.path.exists(os.path.join(gui_framework_path, "__init__.py")):
        lib_path = abs_path
        print(f"✅ gui_frameworkライブラリ発見: {path}")
        break

if lib_path and lib_path not in sys.path:
    sys.path.insert(0, lib_path)
elif lib_path is None:
    print("⚠️ gui_frameworkライブラリが見つかりません。基本機能のみで動作します。")

# 標準ライブラリからインポート
try:
    import customtkinter as ctk
    import cv2
    import numpy as np
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    
    # gui_frameworkライブラリからインポート
    from gui_framework.core import FontManager, StyleManager, ImageUtils
    from gui_framework.widgets import ScalableLabel, StyledButton
    from gui_framework.layouts import TabLayout
    from gui_framework.widgets.dialogs import MessageDialog, TaskRunner
    
    print("✅ 必要なライブラリのインポートが完了しました")
except ImportError as e:
    print(f"❌ ライブラリのインポートエラー: {e}")
    print("💡 必要なライブラリをインストールしてください:")
    print("   pip install customtkinter opencv-python numpy pillow")
    sys.exit(1)

class OpenCVImageProcessor:
    """OpenCVを使用した高度な画像処理クラス"""
    
    @staticmethod
    def pil_to_cv2(pil_image):
        """PIL画像をOpenCV形式に変換"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def cv2_to_pil(cv2_image):
        """OpenCV画像をPIL形式に変換"""
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def gaussian_blur(image, kernel_size=15, sigma=0):
        """ガウシアンブラー"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        if kernel_size % 2 == 0:
            kernel_size += 1  # カーネルサイズは奇数である必要がある
        blurred = cv2.GaussianBlur(cv2_img, (kernel_size, kernel_size), sigma)
        return OpenCVImageProcessor.cv2_to_pil(blurred)
    
    @staticmethod
    def edge_detection(image, threshold1=100, threshold2=200):
        """Cannyエッジ検出"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1, threshold2)
        # エッジをRGBに変換
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(edges_rgb)
    
    @staticmethod
    def morphological_operation(image, operation, kernel_size=5):
        """モルフォロジー演算"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        
        if operation == 'opening':
            result = cv2.morphologyEx(cv2_img, cv2.MORPH_OPEN, kernel)
        elif operation == 'closing':
            result = cv2.morphologyEx(cv2_img, cv2.MORPH_CLOSE, kernel)
        elif operation == 'gradient':
            result = cv2.morphologyEx(cv2_img, cv2.MORPH_GRADIENT, kernel)
        elif operation == 'tophat':
            result = cv2.morphologyEx(cv2_img, cv2.MORPH_TOPHAT, kernel)
        elif operation == 'blackhat':
            result = cv2.morphologyEx(cv2_img, cv2.MORPH_BLACKHAT, kernel)
        else:
            result = cv2_img
            
        return OpenCVImageProcessor.cv2_to_pil(result)
    
    @staticmethod
    def noise_reduction(image, h=10, templateWindowSize=7, searchWindowSize=21):
        """ノイズ除去（Non-local Means Denoising）"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        denoised = cv2.fastNlMeansDenoisingColored(cv2_img, None, h, h, templateWindowSize, searchWindowSize)
        return OpenCVImageProcessor.cv2_to_pil(denoised)
    
    @staticmethod
    def histogram_equalization(image):
        """ヒストグラム均等化"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        # YUVカラースペースに変換
        yuv = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2YUV)
        # Y成分（明度）にヒストグラム均等化を適用
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        # BGRカラースペースに戻す
        result = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        return OpenCVImageProcessor.cv2_to_pil(result)
    
    @staticmethod
    def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
        """バイラテラルフィルター（エッジ保持平滑化）"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        filtered = cv2.bilateralFilter(cv2_img, d, sigma_color, sigma_space)
        return OpenCVImageProcessor.cv2_to_pil(filtered)
    
    @staticmethod
    def unsharp_mask(image, amount=1.5, radius=1, threshold=0):
        """アンシャープマスク（シャープニング）"""
        cv2_img = OpenCVImageProcessor.pil_to_cv2(image)
        
        # ガウシアンブラーを適用
        blurred = cv2.GaussianBlur(cv2_img, (0, 0), radius)
        
        # アンシャープマスクを計算
        sharpened = cv2.addWeighted(cv2_img, 1 + amount, blurred, -amount, 0)
        
        return OpenCVImageProcessor.cv2_to_pil(sharpened)

class AdvancedImageEditor(ctk.CTk):
    """
    gui_frameworkライブラリを使用した高度な画像編集アプリケーション
    """
    
    def __init__(self):
        super().__init__()
        self.geometry("1200x800")
        self.title("Advanced Image Editor - Professional Studio")
        
        # マネージャーの初期化
        self.font_mgr = FontManager(base_size=14)
        self.style_mgr = StyleManager()
        
        # OpenCV処理インスタンスの初期化
        self.opencv_processor = OpenCVImageProcessor()
        
        # 画像管理
        self.current_image = None
        self.original_image = None  # 元画像のバックアップ
        self.image_path = None
        self.zoom_level = 1.0
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """UIの設定"""
        # タイトルラベル
        self.title_label = ScalableLabel(
            self, 
            text="Advanced Image Editor", 
            font_mgr=self.font_mgr, 
            style_mgr=self.style_mgr,
            font_key="title"
        )
        self.title_label.pack(pady=10)

        # メインフレーム（左右分割）
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=5)

        # 左側：ツールパネル (幅を拡張)
        self.left_panel = ctk.CTkFrame(self.main_frame, width=260)
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.pack_propagate(False)

        # 右側：画像表示エリア
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", expand=True, fill="both")

        # 画像キャンバス
        self.image_canvas = ctk.CTkCanvas(
            self.right_panel, 
            bg="gray20",
            highlightthickness=0
        )
        self.image_canvas.pack(expand=True, fill="both", padx=10, pady=10)

        # キャンバスイベントバインド
        self.image_canvas.bind("<Button-1>", self.on_canvas_click)
        self.image_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.image_canvas.bind("<MouseWheel>", self.on_canvas_scroll)

        # ツールパネルの設定
        self.setup_tool_panel()

        # ボタンフレーム
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=10, pady=5)

        # 画像読み込みボタン
        self.btn_load = StyledButton(
            self.button_frame, 
            text="画像を読み込む", 
            command=self.load_image,
            font_mgr=self.font_mgr, 
            style_mgr=self.style_mgr
        )
        self.btn_load.pack(side="left", padx=5, pady=5)

        # 画像保存ボタン
        self.btn_save = StyledButton(
            self.button_frame, 
            text="画像を保存", 
            command=self.save_image,
            font_mgr=self.font_mgr, 
            style_mgr=self.style_mgr
        )
        self.btn_save.pack(side="left", padx=5, pady=5)

        # 処理開始ボタン
        self.btn_process = StyledButton(
            self.button_frame, 
            text="処理実行", 
            command=self.process_image,
            font_mgr=self.font_mgr, 
            style_mgr=self.style_mgr
        )
        self.btn_process.pack(side="left", padx=5, pady=5)

        # ズームリセットボタン
        self.btn_zoom_reset = StyledButton(
            self.button_frame, 
            text="ズームリセット", 
            command=self.reset_zoom,
            font_mgr=self.font_mgr, 
            style_mgr=self.style_mgr
        )
        self.btn_zoom_reset.pack(side="left", padx=5, pady=5)

        # ステータスラベル
        self.status_label = ScalableLabel(
            self, 
            text="準備完了", 
            font_mgr=self.font_mgr, 
            style_mgr=self.style_mgr
        )
        self.status_label.pack(pady=5)
    
    def setup_tool_panel(self):
        """ツールパネルの設定 - タブベースの改良版"""
        # ツールタイトル
        tool_title = ScalableLabel(
            self.left_panel,
            text="編集ツール",
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr,
            font_key="subtitle"
        )
        tool_title.pack(pady=10)

        # タブビューの作成 (幅と高さを調整、スクロール可能)
        self.tool_tabview = ctk.CTkTabview(self.left_panel, width=240, height=650)
        self.tool_tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # タブの追加 (短縮名で文字切れを防止)
        self.tool_tabview.add("基本")
        self.tool_tabview.add("濃度") 
        self.tool_tabview.add("フィルタ")
        self.tool_tabview.add("高度")
        
        # 各タブの設定
        self.setup_basic_adjustment_tab()
        self.setup_density_editing_tab()
        self.setup_filter_tab()
        self.setup_advanced_tab()

    def setup_basic_adjustment_tab(self):
        """基本調整タブの設定"""
        tab = self.tool_tabview.tab("基本")
        
        # 明度調整
        brightness_frame = ctk.CTkFrame(tab)
        brightness_frame.pack(fill="x", padx=3, pady=3)
        
        brightness_label = ctk.CTkLabel(brightness_frame, text="明度", font=("Arial", 11, "bold"))
        brightness_label.pack(pady=2)
        
        self.brightness_slider = ctk.CTkSlider(
            brightness_frame, 
            from_=-100, 
            to=100, 
            number_of_steps=200,
            command=self.update_brightness
        )
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill="x", padx=3, pady=2)
        
        self.brightness_value_label = ctk.CTkLabel(brightness_frame, text="0", font=("Arial", 9))
        self.brightness_value_label.pack(pady=1)

        # コントラスト調整
        contrast_frame = ctk.CTkFrame(tab)
        contrast_frame.pack(fill="x", padx=3, pady=3)
        
        contrast_label = ctk.CTkLabel(contrast_frame, text="コントラスト", font=("Arial", 11, "bold"))
        contrast_label.pack(pady=2)
        
        self.contrast_slider = ctk.CTkSlider(
            contrast_frame, 
            from_=-100, 
            to=100, 
            number_of_steps=200,
            command=self.update_contrast
        )
        self.contrast_slider.set(0)
        self.contrast_slider.pack(fill="x", padx=3, pady=2)
        
        self.contrast_value_label = ctk.CTkLabel(contrast_frame, text="0", font=("Arial", 9))
        self.contrast_value_label.pack(pady=1)

        # 彩度調整
        saturation_frame = ctk.CTkFrame(tab)
        saturation_frame.pack(fill="x", padx=3, pady=3)
        
        saturation_label = ctk.CTkLabel(saturation_frame, text="彩度", font=("Arial", 11, "bold"))
        saturation_label.pack(pady=2)
        
        self.saturation_slider = ctk.CTkSlider(
            saturation_frame, 
            from_=-100, 
            to=100, 
            number_of_steps=200,
            command=self.update_saturation
        )
        self.saturation_slider.set(0)
        self.saturation_slider.pack(fill="x", padx=3, pady=2)
        
        self.saturation_value_label = ctk.CTkLabel(saturation_frame, text="0", font=("Arial", 9))
        self.saturation_value_label.pack(pady=1)

        # 回転ボタン
        rotation_frame = ctk.CTkFrame(tab)
        rotation_frame.pack(fill="x", padx=5, pady=5)
        
        rotation_label = ctk.CTkLabel(rotation_frame, text="回転", font=("Arial", 12, "bold"))
        rotation_label.pack(pady=3)
        
        rotation_btn_frame = ctk.CTkFrame(rotation_frame)
        rotation_btn_frame.pack(fill="x", padx=5, pady=3)
        
        btn_rotate_left = ctk.CTkButton(
            rotation_btn_frame,
            text="左90°",
            command=self.rotate_left,
            width=60,
            height=25
        )
        btn_rotate_left.pack(side="left", padx=2)
        
        btn_rotate_right = ctk.CTkButton(
            rotation_btn_frame,
            text="右90°",
            command=self.rotate_right,
            width=60,
            height=25
        )
        btn_rotate_right.pack(side="right", padx=2)

        # リセットボタン
        reset_frame = ctk.CTkFrame(tab)
        reset_frame.pack(fill="x", padx=5, pady=5)
        
        btn_reset_all = ctk.CTkButton(
            reset_frame,
            text="すべてリセット",
            command=self.reset_all_adjustments,
            width=120,
            height=30
        )
        btn_reset_all.pack(pady=5)
        
        btn_restore_original = ctk.CTkButton(
            reset_frame,
            text="元画像に戻す",
            command=self.restore_original_image,
            width=120,
            height=30
        )
        btn_restore_original.pack(pady=5)

    def setup_density_editing_tab(self):
        """濃度編集タブの設定"""
        tab = self.tool_tabview.tab("濃度")
        
        # ガンマ補正
        gamma_frame = ctk.CTkFrame(tab)
        gamma_frame.pack(fill="x", padx=5, pady=5)
        
        gamma_label = ctk.CTkLabel(gamma_frame, text="ガンマ補正", font=("Arial", 12, "bold"))
        gamma_label.pack(pady=3)
        
        self.gamma_slider = ctk.CTkSlider(
            gamma_frame, 
            from_=0.1, 
            to=3.0, 
            number_of_steps=58,
            command=self.update_gamma
        )
        self.gamma_slider.set(1.0)
        self.gamma_slider.pack(fill="x", padx=5, pady=3)
        
        self.gamma_value_label = ctk.CTkLabel(gamma_frame, text="1.0", font=("Arial", 10))
        self.gamma_value_label.pack(pady=2)

        # レベル調整（シャドウ）
        shadow_frame = ctk.CTkFrame(tab)
        shadow_frame.pack(fill="x", padx=5, pady=5)
        
        shadow_label = ctk.CTkLabel(shadow_frame, text="シャドウ", font=("Arial", 12, "bold"))
        shadow_label.pack(pady=3)
        
        self.shadow_slider = ctk.CTkSlider(
            shadow_frame, 
            from_=-100, 
            to=100, 
            number_of_steps=200,
            command=self.update_shadow
        )
        self.shadow_slider.set(0)
        self.shadow_slider.pack(fill="x", padx=5, pady=3)
        
        self.shadow_value_label = ctk.CTkLabel(shadow_frame, text="0", font=("Arial", 10))
        self.shadow_value_label.pack(pady=2)

        # レベル調整（ハイライト）
        highlight_frame = ctk.CTkFrame(tab)
        highlight_frame.pack(fill="x", padx=5, pady=5)
        
        highlight_label = ctk.CTkLabel(highlight_frame, text="ハイライト", font=("Arial", 12, "bold"))
        highlight_label.pack(pady=3)
        
        self.highlight_slider = ctk.CTkSlider(
            highlight_frame, 
            from_=-100, 
            to=100, 
            number_of_steps=200,
            command=self.update_highlight
        )
        self.highlight_slider.set(0)
        self.highlight_slider.pack(fill="x", padx=5, pady=3)
        
        self.highlight_value_label = ctk.CTkLabel(highlight_frame, text="0", font=("Arial", 10))
        self.highlight_value_label.pack(pady=2)

        # 色温度調整
        temperature_frame = ctk.CTkFrame(tab)
        temperature_frame.pack(fill="x", padx=5, pady=5)
        
        temperature_label = ctk.CTkLabel(temperature_frame, text="色温度", font=("Arial", 12, "bold"))
        temperature_label.pack(pady=3)
        
        self.temperature_slider = ctk.CTkSlider(
            temperature_frame, 
            from_=-100, 
            to=100, 
            number_of_steps=200,
            command=self.update_temperature
        )
        self.temperature_slider.set(0)
        self.temperature_slider.pack(fill="x", padx=5, pady=3)
        
        self.temperature_value_label = ctk.CTkLabel(temperature_frame, text="0", font=("Arial", 10))
        self.temperature_value_label.pack(pady=2)

        # ヒストグラム均等化ボタン
        histogram_frame = ctk.CTkFrame(tab)
        histogram_frame.pack(fill="x", padx=5, pady=5)
        
        btn_equalize = ctk.CTkButton(
            histogram_frame,
            text="ヒストグラム均等化",
            command=self.apply_histogram_equalization,
            width=140,
            height=30
        )
        btn_equalize.pack(pady=5)

    def setup_filter_tab(self):
        """フィルタータブの設定"""
        tab = self.tool_tabview.tab("フィルタ")
        
        # 基本フィルター
        basic_filter_frame = ctk.CTkFrame(tab)
        basic_filter_frame.pack(fill="x", padx=5, pady=5)
        
        basic_filter_label = ctk.CTkLabel(basic_filter_frame, text="基本フィルター", font=("Arial", 12, "bold"))
        basic_filter_label.pack(pady=3)
        
        # フィルターボタンのグリッド配置
        btn_frame = ctk.CTkFrame(basic_filter_frame)
        btn_frame.pack(fill="x", padx=5, pady=3)
        
        # ぼかし
        btn_blur = ctk.CTkButton(btn_frame, text="ぼかし", command=self.apply_blur_filter, width=60, height=25)
        btn_blur.grid(row=0, column=0, padx=2, pady=2)
        
        # シャープ
        btn_sharpen = ctk.CTkButton(btn_frame, text="シャープ", command=self.apply_sharpen_filter, width=60, height=25)
        btn_sharpen.grid(row=0, column=1, padx=2, pady=2)
        
        # エッジ検出
        btn_edge = ctk.CTkButton(btn_frame, text="エッジ", command=self.apply_edge_filter, width=60, height=25)
        btn_edge.grid(row=1, column=0, padx=2, pady=2)
        
        # エンボス
        btn_emboss = ctk.CTkButton(btn_frame, text="エンボス", command=self.apply_emboss_filter, width=60, height=25)
        btn_emboss.grid(row=1, column=1, padx=2, pady=2)

        # ぼかし強度調整
        blur_strength_frame = ctk.CTkFrame(tab)
        blur_strength_frame.pack(fill="x", padx=5, pady=5)
        
        blur_strength_label = ctk.CTkLabel(blur_strength_frame, text="ぼかし強度", font=("Arial", 12, "bold"))
        blur_strength_label.pack(pady=3)
        
        self.blur_strength_slider = ctk.CTkSlider(
            blur_strength_frame, 
            from_=1, 
            to=50, 
            number_of_steps=49,
            command=self.update_blur_strength
        )
        self.blur_strength_slider.set(5)
        self.blur_strength_slider.pack(fill="x", padx=5, pady=3)
        
        self.blur_strength_value_label = ctk.CTkLabel(blur_strength_frame, text="5", font=("Arial", 10))
        self.blur_strength_value_label.pack(pady=2)

    def setup_advanced_tab(self):
        """高度処理タブの設定"""
        tab = self.tool_tabview.tab("高度")
        
        # OpenCV高度フィルター
        opencv_filter_frame = ctk.CTkFrame(tab)
        opencv_filter_frame.pack(fill="x", padx=5, pady=5)
        
        opencv_filter_label = ctk.CTkLabel(opencv_filter_frame, text="OpenCV処理", font=("Arial", 12, "bold"))
        opencv_filter_label.pack(pady=3)
        
        # Cannyエッジ検出
        btn_canny = ctk.CTkButton(
            opencv_filter_frame,
            text="Canny エッジ",
            command=self.apply_canny_edge,
            width=120,
            height=25
        )
        btn_canny.pack(pady=2)
        
        # ノイズ除去
        btn_denoise = ctk.CTkButton(
            opencv_filter_frame,
            text="ノイズ除去",
            command=self.apply_denoise,
            width=120,
            height=25
        )
        btn_denoise.pack(pady=2)

        # モルフォロジー演算
        morphology_frame = ctk.CTkFrame(tab)
        morphology_frame.pack(fill="x", padx=5, pady=5)
        
        morphology_label = ctk.CTkLabel(morphology_frame, text="モルフォロジー", font=("Arial", 12, "bold"))
        morphology_label.pack(pady=3)
        
        # モルフォロジーボタン
        morph_btn_frame = ctk.CTkFrame(morphology_frame)
        morph_btn_frame.pack(fill="x", padx=5, pady=3)
        
        btn_opening = ctk.CTkButton(morph_btn_frame, text="開放", command=self.apply_opening, width=55, height=25)
        btn_opening.grid(row=0, column=0, padx=1, pady=2)
        
        btn_closing = ctk.CTkButton(morph_btn_frame, text="閉鎖", command=self.apply_closing, width=55, height=25)
        btn_closing.grid(row=0, column=1, padx=1, pady=2)
        
        btn_gradient = ctk.CTkButton(morph_btn_frame, text="勾配", command=self.apply_gradient, width=55, height=25)
        btn_gradient.grid(row=1, column=0, padx=1, pady=2)
        
        btn_top_hat = ctk.CTkButton(morph_btn_frame, text="トップハット", command=self.apply_top_hat, width=55, height=25)
        btn_top_hat.grid(row=1, column=1, padx=1, pady=2)

        # ズーム調整
        zoom_frame = ctk.CTkFrame(tab)
        zoom_frame.pack(fill="x", padx=5, pady=5)
        
        zoom_label = ctk.CTkLabel(zoom_frame, text="ズーム", font=("Arial", 12, "bold"))
        zoom_label.pack(pady=3)
        
        self.zoom_label = ctk.CTkLabel(zoom_frame, text="100%", font=("Arial", 10))
        self.zoom_label.pack(pady=2)

        # フィルターセクション
        filter_frame = ctk.CTkFrame(self.left_panel)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        filter_label = ctk.CTkLabel(filter_frame, text="フィルター")
        filter_label.pack(pady=5)
        
        # ぼかしフィルター
        btn_blur = StyledButton(
            filter_frame,
            text="ぼかし",
            command=self.apply_blur_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_blur.pack(fill="x", padx=5, pady=2)
        
        # シャープフィルター
        btn_sharpen = StyledButton(
            filter_frame,
            text="シャープ",
            command=self.apply_sharpen_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_sharpen.pack(fill="x", padx=5, pady=2)
        
        # エッジ検出フィルター
        btn_edge = StyledButton(
            filter_frame,
            text="エッジ検出",
            command=self.apply_edge_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_edge.pack(fill="x", padx=5, pady=2)
        
        # エンボスフィルター
        btn_emboss = StyledButton(
            filter_frame,
            text="エンボス",
            command=self.apply_emboss_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_emboss.pack(fill="x", padx=5, pady=2)
        
        # 輪郭フィルター
        btn_contour = StyledButton(
            filter_frame,
            text="輪郭",
            command=self.apply_contour_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_contour.pack(fill="x", padx=5, pady=2)
        
        # 詳細フィルター
        btn_detail = StyledButton(
            filter_frame,
            text="詳細強調",
            command=self.apply_detail_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_detail.pack(fill="x", padx=5, pady=2)

        # 高度なフィルター
        advanced_filter_frame = ctk.CTkFrame(self.left_panel)
        advanced_filter_frame.pack(fill="x", padx=10, pady=5)
        
        advanced_filter_label = ctk.CTkLabel(advanced_filter_frame, text="高度なフィルター")
        advanced_filter_label.pack(pady=5)
        
        # スムーズフィルター
        btn_smooth = StyledButton(
            advanced_filter_frame,
            text="スムーズ",
            command=self.apply_smooth_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_smooth.pack(fill="x", padx=5, pady=2)
        
        # 最大フィルター（膨張）
        btn_max = StyledButton(
            advanced_filter_frame,
            text="膨張",
            command=self.apply_max_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_max.pack(fill="x", padx=5, pady=2)
        
        # 最小フィルター（収縮）
        btn_min = StyledButton(
            advanced_filter_frame,
            text="収縮",
            command=self.apply_min_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_min.pack(fill="x", padx=5, pady=2)
        
        # モードフィルター
        btn_mode = StyledButton(
            advanced_filter_frame,
            text="ノイズ除去",
            command=self.apply_mode_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_mode.pack(fill="x", padx=5, pady=2)

        # OpenCV専用フィルター
        opencv_filter_frame = ctk.CTkFrame(self.left_panel)
        opencv_filter_frame.pack(fill="x", padx=10, pady=5)
        
        opencv_filter_label = ctk.CTkLabel(opencv_filter_frame, text="OpenCV高度フィルター")
        opencv_filter_label.pack(pady=5)
        
        # Cannyエッジ検出
        btn_canny = StyledButton(
            opencv_filter_frame,
            text="Cannyエッジ検出",
            command=self.apply_canny_edge,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_canny.pack(fill="x", padx=5, pady=2)
        
        # ノイズ除去
        btn_denoise = StyledButton(
            opencv_filter_frame,
            text="高度ノイズ除去",
            command=self.apply_noise_reduction,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_denoise.pack(fill="x", padx=5, pady=2)
        
        # ヒストグラム均等化
        btn_histogram = StyledButton(
            opencv_filter_frame,
            text="ヒストグラム均等化",
            command=self.apply_histogram_eq,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_histogram.pack(fill="x", padx=5, pady=2)
        
        # バイラテラルフィルター
        btn_bilateral = StyledButton(
            opencv_filter_frame,
            text="エッジ保持平滑化",
            command=self.apply_bilateral_filter,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_bilateral.pack(fill="x", padx=5, pady=2)
        
        # アンシャープマスク
        btn_unsharp = StyledButton(
            opencv_filter_frame,
            text="アンシャープマスク",
            command=self.apply_unsharp_mask,
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_unsharp.pack(fill="x", padx=5, pady=2)

        # モルフォロジー演算
        morphology_frame = ctk.CTkFrame(self.left_panel)
        morphology_frame.pack(fill="x", padx=10, pady=5)
        
        morphology_label = ctk.CTkLabel(morphology_frame, text="モルフォロジー演算")
        morphology_label.pack(pady=5)
        
        # オープニング
        btn_opening = StyledButton(
            morphology_frame,
            text="オープニング",
            command=lambda: self.apply_morphology('opening'),
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_opening.pack(fill="x", padx=5, pady=1)
        
        # クロージング
        btn_closing = StyledButton(
            morphology_frame,
            text="クロージング",
            command=lambda: self.apply_morphology('closing'),
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_closing.pack(fill="x", padx=5, pady=1)
        
        # グラディエント
        btn_gradient = StyledButton(
            morphology_frame,
            text="グラディエント",
            command=lambda: self.apply_morphology('gradient'),
            font_mgr=self.font_mgr,
            style_mgr=self.style_mgr
        )
        btn_gradient.pack(fill="x", padx=5, pady=1)

        # ぼかし強度スライダー
        blur_strength_frame = ctk.CTkFrame(self.left_panel)
        blur_strength_frame.pack(fill="x", padx=10, pady=5)
        
        blur_strength_label = ctk.CTkLabel(blur_strength_frame, text="ぼかし強度")
        blur_strength_label.pack(pady=5)
        
        self.blur_strength_slider = ctk.CTkSlider(
            blur_strength_frame, 
            from_=1, 
            to=50, 
            number_of_steps=49,
            command=self.update_blur_strength
        )
        self.blur_strength_slider.set(10)
        self.blur_strength_slider.pack(fill="x", padx=5, pady=5)

        # ズーム表示
        zoom_frame = ctk.CTkFrame(self.left_panel)
        zoom_frame.pack(fill="x", padx=10, pady=5)
        
        zoom_label = ctk.CTkLabel(zoom_frame, text="ズーム")
        zoom_label.pack(pady=5)
        
        self.zoom_label = ctk.CTkLabel(zoom_frame, text="100%")
        self.zoom_label.pack(pady=5)

    def on_canvas_click(self, event):
        """キャンバスクリック処理"""
        self.last_x = event.x
        self.last_y = event.y

    def on_canvas_drag(self, event):
        """キャンバスドラッグ処理（パン機能）"""
        if hasattr(self, 'last_x') and hasattr(self, 'last_y'):
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.canvas_offset_x += dx
            self.canvas_offset_y += dy
            self.last_x = event.x
            self.last_y = event.y
            self.update_canvas()

    def on_canvas_scroll(self, event):
        """キャンバススクロール処理（ズーム機能）"""
        if self.current_image:
            # ズーム倍率の調整
            zoom_factor = 1.1 if event.delta > 0 else 0.9
            new_zoom = self.zoom_level * zoom_factor
            
            # ズーム範囲制限
            if 0.1 <= new_zoom <= 10.0:
                self.zoom_level = new_zoom
                self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
                self.update_canvas()

    def reset_zoom(self):
        """ズームをリセット"""
        self.zoom_level = 1.0
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.zoom_label.configure(text="100%")
        self.update_canvas()
        self.status_label.configure(text="ズームをリセットしました")

    def update_brightness(self, value):
        """明度を更新"""
        if hasattr(self, 'brightness_value_label'):
            self.brightness_value_label.configure(text=f"{int(value)}")
        if self.current_image:
            self.apply_adjustments()
            self.status_label.configure(text=f"明度: {int(value)}")

    def update_contrast(self, value):
        """コントラストを更新"""
        if hasattr(self, 'contrast_value_label'):
            self.contrast_value_label.configure(text=f"{int(value)}")
        if self.current_image:
            self.apply_adjustments()
            self.status_label.configure(text=f"コントラスト: {int(value)}")

    def update_saturation(self, value):
        """彩度を更新"""
        if hasattr(self, 'saturation_value_label'):
            self.saturation_value_label.configure(text=f"{int(value)}")
        if self.current_image:
            self.apply_adjustments()
            self.status_label.configure(text=f"彩度: {int(value)}")

    # 新しい濃度編集機能
    def update_gamma(self, value):
        """ガンマ補正調整"""
        gamma_value = round(float(value), 2)
        print(f"🔍 ガンマ値更新: {gamma_value}")  # デバッグ出力
        if hasattr(self, 'gamma_value_label'):
            self.gamma_value_label.configure(text=f"{gamma_value}")
        if self.current_image:
            print(f"🎯 ガンマ調整適用中...")  # デバッグ出力
            # 即座にガンマ補正を適用
            self.apply_gamma_directly(gamma_value)
            self.status_label.configure(text=f"ガンマ: {gamma_value}")
    
    def apply_gamma_directly(self, gamma_value):
        """ガンマ補正を直接適用（シンプル版）"""
        try:
            if not self.current_image:
                return
            
            print(f"🔄 直接ガンマ補正開始: {gamma_value}")
            
            # PILでシンプルなガンマ補正
            if gamma_value != 1.0:
                # NumPy配列に変換
                img_array = np.array(self.current_image, dtype=np.float32)
                
                # ガンマ補正適用
                gamma_corrected = np.power(img_array / 255.0, 1.0 / gamma_value) * 255.0
                gamma_corrected = np.clip(gamma_corrected, 0, 255).astype(np.uint8)
                
                # PIL画像に戻す
                gamma_image = Image.fromarray(gamma_corrected)
                
                print(f"✅ ガンマ補正完了、表示更新中...")
                # 直接表示
                self.display_image(gamma_image)
            else:
                # ガンマ値が1.0の場合は元画像を表示
                self.display_image(self.current_image)
                
        except Exception as e:
            print(f"❌ ガンマ補正エラー: {e}")
            import traceback
            traceback.print_exc()

    def update_shadow(self, value):
        """シャドウ調整"""
        shadow_val = int(value)
        print(f"🔍 シャドウ値更新: {shadow_val}")
        if hasattr(self, 'shadow_value_label'):
            self.shadow_value_label.configure(text=f"{shadow_val}")
        if self.current_image:
            print(f"🌑 シャドウ調整適用中...")
            self.apply_shadow_highlight_directly()
            self.status_label.configure(text=f"シャドウ: {shadow_val}")

    def update_highlight(self, value):
        """ハイライト調整"""
        highlight_val = int(value)
        print(f"🔍 ハイライト値更新: {highlight_val}")
        if hasattr(self, 'highlight_value_label'):
            self.highlight_value_label.configure(text=f"{highlight_val}")
        if self.current_image:
            print(f"💡 ハイライト調整適用中...")
            self.apply_shadow_highlight_directly()
            self.status_label.configure(text=f"ハイライト: {highlight_val}")
    
    def apply_shadow_highlight_directly(self):
        """シャドウ/ハイライト調整を直接適用"""
        try:
            if not self.current_image:
                return
            
            shadow_val = self.shadow_slider.get() if hasattr(self, 'shadow_slider') else 0
            highlight_val = self.highlight_slider.get() if hasattr(self, 'highlight_slider') else 0
            
            print(f"🔄 シャドウ/ハイライト調整: シャドウ={shadow_val}, ハイライト={highlight_val}")
            
            if shadow_val == 0 and highlight_val == 0:
                self.display_image(self.current_image)
                return
            
            # NumPy配列に変換
            img_array = np.array(self.current_image, dtype=np.float32) / 255.0
            
            # シャドウ調整（暗部を明るく）
            if shadow_val != 0:
                shadow_factor = shadow_val / 100.0
                mask = img_array < 0.5  # 暗部マスク
                img_array = np.where(mask, 
                                   img_array + shadow_factor * (0.5 - img_array), 
                                   img_array)
            
            # ハイライト調整（明部を暗く）  
            if highlight_val != 0:
                highlight_factor = highlight_val / 100.0
                mask = img_array > 0.5  # 明部マスク
                img_array = np.where(mask,
                                   img_array - highlight_factor * (img_array - 0.5),
                                   img_array)
            
            # 0-255の範囲にクリップして戻す
            adjusted_array = np.clip(img_array * 255.0, 0, 255).astype(np.uint8)
            adjusted_image = Image.fromarray(adjusted_array)
            
            print(f"✅ シャドウ/ハイライト調整完了")
            self.display_image(adjusted_image)
            
        except Exception as e:
            print(f"❌ シャドウ/ハイライト調整エラー: {e}")
            import traceback
            traceback.print_exc()

    def update_temperature(self, value):
        """色温度調整"""
        temp_val = int(value)
        print(f"🔍 色温度値更新: {temp_val}")
        if hasattr(self, 'temperature_value_label'):
            self.temperature_value_label.configure(text=f"{temp_val}")
        if self.current_image:
            print(f"🌡️ 色温度調整適用中...")
            self.apply_temperature_directly(temp_val)
            self.status_label.configure(text=f"色温度: {temp_val}")
    
    def apply_temperature_directly(self, temp_val):
        """色温度調整を直接適用"""
        try:
            if not self.current_image or temp_val == 0:
                if temp_val == 0:
                    self.display_image(self.current_image)
                return
            
            print(f"🔄 色温度調整開始: {temp_val}")
            
            # NumPy配列に変換
            img_array = np.array(self.current_image, dtype=np.float32)
            
            # 色温度調整（簡易版）
            if temp_val > 0:  # 暖色系
                factor = temp_val / 100.0
                img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1.0 + factor * 0.3), 0, 255)  # 赤を強化
                img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1.0 - factor * 0.2), 0, 255)  # 青を弱化
            else:  # 寒色系
                factor = abs(temp_val) / 100.0
                img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1.0 - factor * 0.2), 0, 255)  # 赤を弱化
                img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1.0 + factor * 0.3), 0, 255)  # 青を強化
            
            # PIL画像に戻す
            temp_image = Image.fromarray(img_array.astype(np.uint8))
            
            print(f"✅ 色温度調整完了")
            self.display_image(temp_image)
            
        except Exception as e:
            print(f"❌ 色温度調整エラー: {e}")
            import traceback
            traceback.print_exc()

    def update_blur_strength(self, value):
        """ぼかし強度調整"""
        blur_value = int(value)
        if hasattr(self, 'blur_strength_value_label'):
            self.blur_strength_value_label.configure(text=f"{blur_value}")
        self.status_label.configure(text=f"ぼかし強度: {blur_value}")

    def apply_histogram_equalization(self):
        """ヒストグラム均等化"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            # PIL ImageをOpenCV形式に変換
            cv_image = self.opencv_processor.pil_to_cv2(self.current_image)
            
            # グレースケールに変換してヒストグラム均等化
            if len(cv_image.shape) == 3:
                # カラー画像の場合、LAB色空間でL(輝度)チャンネルのみ均等化
                lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
                lab[:,:,0] = cv2.equalizeHist(lab[:,:,0])
                cv_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            else:
                # グレースケール画像の場合
                cv_image = cv2.equalizeHist(cv_image)
            
            # OpenCV形式をPIL Imageに変換
            self.current_image = self.opencv_processor.cv2_to_pil(cv_image)
            self.apply_adjustments()
            self.status_label.configure(text="ヒストグラム均等化を適用しました")
            
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"ヒストグラム均等化エラー: {e}")
            print(f"❌ ヒストグラム均等化エラー: {e}")

    def rotate_left(self):
        """左に90度回転"""
        if self.current_image:
            self.current_image = self.current_image.rotate(90, expand=True)
            self.apply_adjustments()
            self.status_label.configure(text="左に90度回転しました")

    def rotate_right(self):
        """右に90度回転"""
        if self.current_image:
            self.current_image = self.current_image.rotate(-90, expand=True)
            self.apply_adjustments()
            self.status_label.configure(text="右に90度回転しました")

    def reset_all_adjustments(self):
        """すべての調整をリセット"""
        if self.current_image:
            # スライダーをリセット
            self.brightness_slider.set(0)
            self.contrast_slider.set(0)
            self.saturation_slider.set(0)
            
            # ズームもリセット
            self.reset_zoom()
            
            self.status_label.configure(text="すべての調整をリセットしました")

    def restore_original_image(self):
        """元画像に戻す"""
        if not self.original_image:
            MessageDialog.show_warning(self, "警告", "元画像がありません")
            return
        
        try:
            self.current_image = self.original_image.copy()
            
            # スライダーをリセット
            self.brightness_slider.set(0)
            self.contrast_slider.set(0)
            self.saturation_slider.set(0)
            
            # ズームもリセット
            self.reset_zoom()
            
            self.status_label.configure(text="元画像に戻しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"元画像復元エラー: {e}")

    def apply_blur_filter(self):
        """ぼかしフィルターを適用（OpenCV版）"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            strength = int(self.blur_strength_slider.get())
            # OpenCVのガウシアンブラーを使用
            filtered_image = OpenCVImageProcessor.gaussian_blur(self.current_image, kernel_size=strength)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text=f"ガウシアンブラーを適用しました (強度: {strength})")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"ぼかしフィルターエラー: {e}")

    def apply_sharpen_filter(self):
        """シャープフィルターを適用（OpenCV版）"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            # OpenCVのアンシャープマスクを使用
            filtered_image = OpenCVImageProcessor.unsharp_mask(self.current_image, amount=1.0, radius=1)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="シャープフィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"シャープフィルターエラー: {e}")

    def apply_edge_filter(self):
        """エッジ検出フィルターを適用（OpenCV版）"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            # OpenCVのCannyエッジ検出を使用
            filtered_image = OpenCVImageProcessor.edge_detection(self.current_image)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="Cannyエッジ検出を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"エッジ検出フィルターエラー: {e}")

    def apply_emboss_filter(self):
        """エンボスフィルターを適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.EMBOSS)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="エンボスフィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"エンボスフィルターエラー: {e}")

    def apply_contour_filter(self):
        """輪郭フィルターを適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.CONTOUR)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="輪郭フィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"輪郭フィルターエラー: {e}")

    def apply_detail_filter(self):
        """詳細強調フィルターを適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.DETAIL)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="詳細強調フィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"詳細強調フィルターエラー: {e}")

    def apply_smooth_filter(self):
        """スムーズフィルターを適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.SMOOTH)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="スムーズフィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"スムーズフィルターエラー: {e}")

    def apply_max_filter(self):
        """最大フィルター（膨張）を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.MaxFilter(size=3))
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="膨張フィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"膨張フィルターエラー: {e}")

    def apply_min_filter(self):
        """最小フィルター（収縮）を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.MinFilter(size=3))
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="収縮フィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"収縮フィルターエラー: {e}")

    def apply_mode_filter(self):
        """モードフィルター（ノイズ除去）を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = self.current_image.filter(ImageFilter.ModeFilter(size=3))
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="ノイズ除去フィルターを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"ノイズ除去フィルターエラー: {e}")

    # OpenCV専用フィルターメソッド
    def apply_canny_edge(self):
        """Cannyエッジ検出を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = OpenCVImageProcessor.edge_detection(self.current_image)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="Cannyエッジ検出を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"Cannyエッジ検出エラー: {e}")

    def apply_denoise(self):
        """ノイズ除去を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = OpenCVImageProcessor.noise_reduction(self.current_image)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="ノイズ除去を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"ノイズ除去エラー: {e}")

    def apply_noise_reduction(self):
        """高度ノイズ除去を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            # プログレスダイアログで処理実行（処理時間が長いため）
            def denoise_task(progress_dialog):
                progress_dialog.update_progress(25, "ノイズ除去処理中...")
                filtered_image = OpenCVImageProcessor.noise_reduction(self.current_image)
                progress_dialog.update_progress(100, "完了")
                return filtered_image
            
            result = TaskRunner.run_with_progress(
                parent=self,
                task_func=denoise_task,
                title="ノイズ除去処理",
                message="高度ノイズ除去を実行中..."
            )
            
            if result:
                self.current_image = result
                self.apply_adjustments()
                self.status_label.configure(text="高度ノイズ除去を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"ノイズ除去エラー: {e}")

    def apply_histogram_eq(self):
        """ヒストグラム均等化を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = OpenCVImageProcessor.histogram_equalization(self.current_image)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="ヒストグラム均等化を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"ヒストグラム均等化エラー: {e}")

    def apply_bilateral_filter(self):
        """バイラテラルフィルターを適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = OpenCVImageProcessor.bilateral_filter(self.current_image)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="エッジ保持平滑化を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"バイラテラルフィルターエラー: {e}")

    # モルフォロジー演算メソッド
    def apply_opening(self):
        """開放（Opening）演算を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            cv_image = self.opencv_processor.pil_to_cv2(self.current_image)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            opened = cv2.morphologyEx(cv_image, cv2.MORPH_OPEN, kernel)
            self.current_image = self.opencv_processor.cv2_to_pil(opened)
            self.apply_adjustments()
            self.status_label.configure(text="開放演算を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"開放演算エラー: {e}")

    def apply_closing(self):
        """閉鎖（Closing）演算を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            cv_image = self.opencv_processor.pil_to_cv2(self.current_image)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(cv_image, cv2.MORPH_CLOSE, kernel)
            self.current_image = self.opencv_processor.cv2_to_pil(closed)
            self.apply_adjustments()
            self.status_label.configure(text="閉鎖演算を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"閉鎖演算エラー: {e}")

    def apply_gradient(self):
        """勾配（Gradient）演算を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            cv_image = self.opencv_processor.pil_to_cv2(self.current_image)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            gradient = cv2.morphologyEx(cv_image, cv2.MORPH_GRADIENT, kernel)
            self.current_image = self.opencv_processor.cv2_to_pil(gradient)
            self.apply_adjustments()
            self.status_label.configure(text="勾配演算を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"勾配演算エラー: {e}")

    def apply_top_hat(self):
        """トップハット（Top Hat）演算を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            cv_image = self.opencv_processor.pil_to_cv2(self.current_image)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
            tophat = cv2.morphologyEx(cv_image, cv2.MORPH_TOPHAT, kernel)
            self.current_image = self.opencv_processor.cv2_to_pil(tophat)
            self.apply_adjustments()
            self.status_label.configure(text="トップハット演算を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"トップハット演算エラー: {e}")

    def apply_unsharp_mask(self):
        """アンシャープマスクを適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = OpenCVImageProcessor.unsharp_mask(self.current_image)
            self.current_image = filtered_image
            self.apply_adjustments()
            self.status_label.configure(text="アンシャープマスクを適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"アンシャープマスクエラー: {e}")

    def apply_morphology(self, operation):
        """モルフォロジー演算を適用"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "画像が読み込まれていません")
            return
        
        try:
            filtered_image = OpenCVImageProcessor.morphological_operation(self.current_image, operation)
            self.current_image = filtered_image
            self.apply_adjustments()
            operation_names = {
                'opening': 'オープニング',
                'closing': 'クロージング', 
                'gradient': 'グラディエント',
                'tophat': 'トップハット',
                'blackhat': 'ブラックハット'
            }
            self.status_label.configure(text=f"{operation_names.get(operation, operation)}を適用しました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"モルフォロジー演算エラー: {e}")

    def apply_adjustments(self):
        """明度・コントラスト調整を適用"""
        if not self.current_image:
            return
        
        try:
            print(f"🔄 調整適用開始...")  # デバッグ出力
            # 調整済み画像を取得
            adjusted_image = self.get_adjusted_image()
            if adjusted_image:
                print(f"✅ 調整済み画像取得完了")  # デバッグ出力
                # 調整済み画像を表示
                self.display_image(adjusted_image)
                print(f"✅ 画像表示完了")  # デバッグ出力
            else:
                print(f"❌ 調整済み画像取得失敗")  # デバッグ出力
            
        except Exception as e:
            print(f"❌ 調整エラー: {e}")  # エラーメッセージを詳細化

    def update_canvas(self):
        """キャンバスを更新"""
        if self.current_image:
            self.display_image(self.current_image)

    def display_image(self, image):
        """画像をキャンバスに表示"""
        try:
            import tkinter as tk
            
            # キャンバスクリア
            self.image_canvas.delete("all")
            
            # 画像サイズ取得
            img_width, img_height = image.size
            
            # ズーム適用
            display_width = int(img_width * self.zoom_level)
            display_height = int(img_height * self.zoom_level)
            
            # 画像リサイズ
            display_image = image.resize((display_width, display_height), resample=Image.Resampling.LANCZOS)
            
            # Tkinter用に変換
            self.photo_image = ImageTk.PhotoImage(display_image)
            
            # キャンバス中央に配置
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            x = (canvas_width // 2) + self.canvas_offset_x
            y = (canvas_height // 2) + self.canvas_offset_y
            
            # 画像をキャンバスに配置
            self.image_canvas.create_image(x, y, image=self.photo_image, anchor=tk.CENTER)
            
        except Exception as e:
            print(f"画像表示エラー: {e}")
            MessageDialog.show_error(self, "エラー", f"画像表示エラー: {e}")
    
    
    def load_image(self):
        """画像を読み込む"""
        try:
            path = ImageUtils.open_image_file()
            if path:
                image = ImageUtils.load_image(path)
                if image:
                    self.current_image = image
                    self.original_image = image.copy()  # 元画像を保存
                    self.image_path = path
                    
                    # スライダーをリセット
                    self.brightness_slider.set(0)
                    self.contrast_slider.set(0)
                    self.saturation_slider.set(0)
                    
                    # ズームをリセット
                    self.reset_zoom()
                    
                    # 画像を表示
                    self.display_image(image)
                    
                    self.status_label.configure(text=f"画像読み込み完了: {os.path.basename(path)}")
                    print(f"✅ 画像読み込み: {path}")
                    return image
                else:
                    MessageDialog.show_error(self, "エラー", "画像の読み込みに失敗しました")
            else:
                self.status_label.configure(text="画像読み込みをキャンセルしました")
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"画像読み込みエラー: {e}")
            print(f"❌ 画像読み込みエラー: {e}")
    
    def save_image(self):
        """画像を保存"""
        if not self.current_image:
            MessageDialog.show_warning(self, "警告", "保存する画像がありません")
            return
        
        try:
            # 調整を適用した画像を取得
            save_image = self.get_adjusted_image()
            if not save_image:
                MessageDialog.show_error(self, "エラー", "保存用画像の準備に失敗しました")
                return
            
            # ファイル保存ダイアログ
            from tkinter import filedialog
            filetypes = [
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All files", "*.*")
            ]
            path = filedialog.asksaveasfilename(
                title="画像を保存",
                filetypes=filetypes,
                defaultextension=".png"
            )
            
            if path:
                # ファイル拡張子に基づいて保存形式を決定
                file_ext = os.path.splitext(path)[1].lower()
                if file_ext in ['.jpg', '.jpeg']:
                    # JPEGの場合、RGBに変換（透明度を削除）
                    if save_image.mode in ('RGBA', 'LA'):
                        rgb_image = Image.new('RGB', save_image.size, (255, 255, 255))
                        rgb_image.paste(save_image, mask=save_image.split()[-1] if save_image.mode == 'RGBA' else None)
                        save_image = rgb_image
                    save_image.save(path, "JPEG", quality=95)
                elif file_ext == '.png':
                    save_image.save(path, "PNG")
                elif file_ext == '.bmp':
                    save_image.save(path, "BMP")
                elif file_ext in ['.tiff', '.tif']:
                    save_image.save(path, "TIFF")
                else:
                    save_image.save(path)
                
                self.status_label.configure(text=f"画像保存完了: {os.path.basename(path)}")
                MessageDialog.show_info(self, "完了", f"画像を保存しました:\n{path}")
            else:
                self.status_label.configure(text="画像保存をキャンセルしました")
                
        except Exception as e:
            MessageDialog.show_error(self, "エラー", f"画像保存エラー: {e}")
            print(f"❌ 画像保存エラー: {e}")

    def get_adjusted_image(self):
        """調整を適用した画像を取得"""
        if not self.current_image:
            return None
        
        try:
            print(f"🔍 調整開始: 元画像サイズ {self.current_image.size}")
            # 元画像から調整を適用
            adjusted_image = self.current_image.copy()
            
            # まず基本的なPIL調整を適用
            # 明度調整
            brightness_value = (self.brightness_slider.get() + 100) / 100.0
            if brightness_value != 1.0:
                print(f"🔆 明度調整: {brightness_value}")
                enhancer = ImageEnhance.Brightness(adjusted_image)
                adjusted_image = enhancer.enhance(brightness_value)
            
            # コントラスト調整
            contrast_value = (self.contrast_slider.get() + 100) / 100.0
            if contrast_value != 1.0:
                print(f"📊 コントラスト調整: {contrast_value}")
                enhancer = ImageEnhance.Contrast(adjusted_image)
                adjusted_image = enhancer.enhance(contrast_value)
            
            # 彩度調整
            saturation_value = (self.saturation_slider.get() + 100) / 100.0
            if saturation_value != 1.0:
                print(f"🌈 彩度調整: {saturation_value}")
                enhancer = ImageEnhance.Color(adjusted_image)
                adjusted_image = enhancer.enhance(saturation_value)
            
            # OpenCV形式に変換（高度な処理用）
            cv_image = None
            
            # ガンマ補正
            if hasattr(self, 'gamma_slider') and self.gamma_slider.get() != 1.0:
                print(f"🎯 ガンマ補正適用中: {self.gamma_slider.get()}")  # デバッグ出力
                if cv_image is None:
                    cv_image = self.opencv_processor.pil_to_cv2(adjusted_image)
                gamma = self.gamma_slider.get()
                # ガンマテーブル作成
                gamma_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)]).astype(np.uint8)
                cv_image = cv2.LUT(cv_image, gamma_table)
                print(f"✅ ガンマ補正完了: {gamma}")  # デバッグ出力
            
            # シャドウ/ハイライト調整
            if hasattr(self, 'shadow_slider') and hasattr(self, 'highlight_slider'):
                shadow_val = self.shadow_slider.get()
                highlight_val = self.highlight_slider.get()
                if shadow_val != 0 or highlight_val != 0:
                    if cv_image is None:
                        cv_image = self.opencv_processor.pil_to_cv2(adjusted_image)
                    # シャドウ/ハイライト調整実装
                    cv_image = self.apply_shadow_highlight_adjustment(cv_image, shadow_val, highlight_val)
            
            # 色温度調整
            if hasattr(self, 'temperature_slider') and self.temperature_slider.get() != 0:
                if cv_image is None:
                    cv_image = self.opencv_processor.pil_to_cv2(adjusted_image)
                temperature_val = self.temperature_slider.get()
                cv_image = self.apply_temperature_adjustment(cv_image, temperature_val)
            
            # OpenCV処理が行われた場合、PIL形式に戻す
            if cv_image is not None:
                print(f"🔄 OpenCV→PIL変換中...")
                adjusted_image = self.opencv_processor.cv2_to_pil(cv_image)
                print(f"✅ 変換完了")
            
            print(f"🎯 最終画像サイズ: {adjusted_image.size}")
            return adjusted_image
            
        except Exception as e:
            print(f"❌ 画像調整エラー: {e}")
            import traceback
            traceback.print_exc()
            return self.current_image

    def apply_shadow_highlight_adjustment(self, cv_image, shadow_val, highlight_val):
        """シャドウ/ハイライト調整"""
        try:
            # 画像を0-1の範囲に正規化
            img_float = cv_image.astype(np.float32) / 255.0
            
            # シャドウ調整（暗い部分を明るく）
            if shadow_val > 0:
                # 暗い部分のマスクを作成
                shadow_mask = 1.0 - img_float
                shadow_mask = np.power(shadow_mask, 3)  # 暗い部分を強調
                shadow_adjustment = shadow_val / 100.0
                img_float = img_float + shadow_mask * shadow_adjustment
            elif shadow_val < 0:
                # 暗い部分をより暗く
                shadow_mask = 1.0 - img_float
                shadow_mask = np.power(shadow_mask, 2)
                shadow_adjustment = abs(shadow_val) / 100.0
                img_float = img_float - shadow_mask * shadow_adjustment * 0.5
            
            # ハイライト調整（明るい部分を暗く/明るく）
            if highlight_val < 0:
                # 明るい部分を暗く
                highlight_mask = img_float
                highlight_mask = np.power(highlight_mask, 2)  # 明るい部分を強調
                highlight_adjustment = abs(highlight_val) / 100.0
                img_float = img_float - highlight_mask * highlight_adjustment * 0.5
            elif highlight_val > 0:
                # 明るい部分をより明るく
                highlight_mask = img_float
                highlight_mask = np.power(highlight_mask, 3)
                highlight_adjustment = highlight_val / 100.0
                img_float = img_float + highlight_mask * highlight_adjustment * 0.3
            
            # 0-255の範囲にクリップして戻す
            img_float = np.clip(img_float, 0.0, 1.0)
            return (img_float * 255).astype(np.uint8)
            
        except Exception as e:
            print(f"シャドウ/ハイライト調整エラー: {e}")
            return cv_image

    def apply_temperature_adjustment(self, cv_image, temperature_val):
        """色温度調整"""
        try:
            # 色温度調整の係数
            temp_factor = temperature_val / 100.0
            
            if temp_factor > 0:
                # 暖色系（赤/黄色を強調）
                cv_image[:, :, 0] = cv_image[:, :, 0] * (1 - temp_factor * 0.3)  # 青を減らす
                cv_image[:, :, 2] = cv_image[:, :, 2] * (1 + temp_factor * 0.2)  # 赤を増やす
            else:
                # 寒色系（青を強調）
                temp_factor = abs(temp_factor)
                cv_image[:, :, 0] = cv_image[:, :, 0] * (1 + temp_factor * 0.3)  # 青を増やす
                cv_image[:, :, 2] = cv_image[:, :, 2] * (1 - temp_factor * 0.2)  # 赤を減らす
            
            return np.clip(cv_image, 0, 255).astype(np.uint8)
            
        except Exception as e:
            print(f"色温度調整エラー: {e}")
            return cv_image
    
    def process_image(self):
        """画像処理を実行"""
        def long_task(progress_dialog):
            """長時間処理のサンプル"""
            import time
            for i in range(101):
                if progress_dialog.is_cancelled():
                    break
                progress_dialog.update_progress(i, f"処理中... {i}%")
                time.sleep(0.02)  # 処理のシミュレーション
        
        # プログレスダイアログで処理実行
        TaskRunner.run_with_progress(
            parent=self,
            task_func=long_task,
            title="画像処理中",
            message="画像を処理しています..."
        )
        self.status_label.configure(text="画像処理完了")

def main():
    """メイン実行関数"""
    print("🎨 Advanced Image Editor を起動中...")
    
    try:
        # CustomTkinter設定
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # アプリケーション起動
        app = AdvancedImageEditor()
        print("✅ Advanced Image Editor が起動しました")
        app.mainloop()
        
    except Exception as e:
        print(f"❌ アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
