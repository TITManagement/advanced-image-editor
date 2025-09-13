"""
メインウィンドウのUI構築機能
"""

import tkinter as tk
import customtkinter as ctk


class MainWindowUI:
    """メインウィンドウのUI構築を担当するクラス"""
    
    def __init__(self, parent_window):
        """
        初期化
        
        Args:
            parent_window: 親ウィンドウ（通常はmain_plugin.pyのメインクラス）
        """
        self.parent = parent_window
        self.setup_window_properties()
        self.setup_main_layout()
        self.setup_canvas()
        self.setup_status_bar()
    
    def setup_window_properties(self):
        """ウィンドウの基本プロパティ設定"""
        self.parent.title("🎨 Advanced Image Editor - Plugin System")
        self.parent.geometry("1400x900")
    
    def setup_main_layout(self):
        """メインレイアウトの構築"""
        # グリッド設定
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        
        # 左パネル（プラグインUI）
        self.left_panel = ctk.CTkFrame(self.parent, width=280)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.left_panel.grid_propagate(False)
        
        # 右パネル（画像表示エリア）
        self.right_panel = ctk.CTkFrame(self.parent)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)
    
    def setup_canvas(self):
        """画像表示キャンバスの設定"""
        self.canvas = tk.Canvas(self.right_panel, bg="gray25")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    
    def setup_control_buttons(self, callbacks):
        """
        操作ボタンのセットアップ
        
        Args:
            callbacks: ボタンのコールバック関数辞書
                {
                    'load_image': function,
                    'save_image': function, 
                    'reset_to_original': function,
                    'reset_all_plugins': function
                }
        """
        button_frame = ctk.CTkFrame(self.right_panel)
        button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # 画像読み込みボタン
        load_btn = ctk.CTkButton(
            button_frame,
            text="📁 画像を開く",
            command=callbacks.get('load_image'),
            font=("Arial", 12)
        )
        load_btn.pack(side="left", padx=5, pady=5)
        
        # 画像保存ボタン
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 保存",
            command=callbacks.get('save_image'),
            font=("Arial", 12)
        )
        save_btn.pack(side="left", padx=5, pady=5)
        
        # 元画像復元ボタン
        reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄 元画像復元",
            command=callbacks.get('reset_to_original'),
            font=("Arial", 12)
        )
        reset_btn.pack(side="left", padx=5, pady=5)
        
        # 全プラグインリセットボタン
        reset_all_btn = ctk.CTkButton(
            button_frame,
            text="🔧 全リセット",
            command=callbacks.get('reset_all_plugins'),
            font=("Arial", 12)
        )
        reset_all_btn.pack(side="left", padx=5, pady=5)
    
    def setup_status_bar(self):
        """ステータスバーの設定"""
        self.status_label = ctk.CTkLabel(
            self.parent, 
            text="🎯 プラグインシステム版画像エディター起動完了", 
            font=("Arial", 12)
        )
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
    
    def setup_plugin_tabs(self, tab_definitions):
        """
        プラグイン用のタブビューをセットアップ
        
        Args:
            tab_definitions: タブ定義辞書 {plugin_name: tab_display_name}
        """
        # タブビュー作成
        self.tab_view = ctk.CTkTabview(self.left_panel, width=250, height=600)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # タブ作成
        self.plugin_frames = {}
        for plugin_name, tab_name in tab_definitions.items():
            # タブを追加
            self.tab_view.add(tab_name)
            
            # タブ内のフレームを取得して保存
            tab_frame = self.tab_view.tab(tab_name)
            
            # スクロール可能なフレームを作成
            scrollable_frame = ctk.CTkScrollableFrame(tab_frame, width=220, height=550)
            scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            self.plugin_frames[plugin_name] = scrollable_frame
        
        return self.plugin_frames
    
    def get_canvas(self):
        """キャンバスウィジェットを取得"""
        return self.canvas
    
    def get_status_label(self):
        """ステータスラベルウィジェットを取得"""
        return self.status_label
    
    def get_left_panel(self):
        """左パネルウィジェットを取得"""
        return self.left_panel
    
    def get_right_panel(self):
        """右パネルウィジェットを取得"""
        return self.right_panel