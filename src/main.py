#!/usr/bin/env python3
"""
ImageEditor - 高度な画像編集アプリケーション

image_gui_templateライブラリを使用した新規プロジェクト
"""

import sys
from pathlib import Path

# ライブラリからインポート
try:
    from apps.gui_image_processor import ImageProcessorApp
    import customtkinter as ctk
except ImportError as e:
    print(f"❌ ライブラリのインポートエラー: {e}")
    print("💡 image_gui_templateライブラリがインストールされていることを確認してください")
    print("📦 インストール方法: pip install -e /Users/tinoue/Development.local/lib/image_gui_template")
    sys.exit(1)

class ImageEditor(ImageProcessorApp):
    """
    ImageProcessorAppを継承した独自の画像編集アプリケーション
    """
    
    def __init__(self):
        super().__init__()
        self.title("ImageEditor - Professional Image Editor")
        self.setup_custom_features()
    
    def setup_custom_features(self):
        """独自機能の追加"""
        # ここに独自の機能を追加
        pass

def main():
    """メイン実行関数"""
    print("🎨 ImageEditor を起動中...")
    
    try:
        # CustomTkinter設定
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # アプリケーション起動
        app = ImageEditor()
        print("✅ ImageEditor が起動しました")
        app.mainloop()
        
    except Exception as e:
        print(f"❌ アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
