"""
画像エディター機能モジュール
画像の読み込み、保存、表示処理を担当
"""

import os
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk

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


class ImageEditor:
    """画像エディターのコア機能を提供するクラス"""
    
    def __init__(self, canvas_widget, status_label):
        """
        初期化
        
        Args:
            canvas_widget: 画像を表示するキャンバスウィジェット
            status_label: ステータス表示用ラベル
        """
        self.canvas = canvas_widget
        self.status_label = status_label
        self.current_image = None
        self.original_image = None
        self.on_image_loaded_callback = None
    
    def load_image(self, parent_window=None):
        """
        ファイルダイアログから画像を読み込み
        
        Args:
            parent_window: 親ウィンドウ（エラーダイアログの親として使用）
        
        Returns:
            bool: 読み込み成功時True、失敗時False
        """
        try:
            file_path = filedialog.askopenfilename(
                title="画像ファイルを選択",
                filetypes=[
                    ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                    ("すべてのファイル", "*.*")
                ]
            )
            
            if file_path:
                image = Image.open(file_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                self.original_image = image.copy()
                self.current_image = image.copy()
                self.display_image(image)
                self.status_label.configure(text=f"✅ 画像読み込み: {os.path.basename(file_path)}")
                print(f"✅ 画像読み込み: {file_path}")
                
                # 画像読み込み完了コールバックを実行
                if self.on_image_loaded_callback:
                    self.on_image_loaded_callback()
                
                return True
                
        except Exception as e:
            print(f"❌ 画像読み込みエラー: {e}")
            if parent_window:
                MessageDialog.show_error(parent_window, "エラー", f"画像読み込みエラー: {e}")
            return False
    
    def load_default_image(self):
        """
        デフォルト画像を読み込み
        
        Returns:
            bool: 読み込み成功時True、失敗時False
        """
        try:
            # 現在のスクリプトディレクトリを基準にした相対パス
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # デフォルト画像パスを探索（クロスプラットフォーム対応）
            default_paths = [
                os.path.join(script_dir, "SampleImage", "IMG_1307.jpeg"),
                os.path.join(script_dir, "SampleImage", "IMG_1308.jpeg"),
                # フォールバック用：プロジェクトルートからの相対パス
                os.path.join("SampleImage", "IMG_1307.jpeg"),
                os.path.join("SampleImage", "IMG_1308.jpeg")
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    image = Image.open(path)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    self.original_image = image.copy()
                    self.current_image = image.copy()
                    self.display_image(image)
                    self.status_label.configure(text=f"✅ デフォルト画像読み込み: {os.path.basename(path)}")
                    print(f"✅ デフォルト画像読み込み: {path}")
                    
                    # 画像読み込み完了コールバックを実行
                    if self.on_image_loaded_callback:
                        self.on_image_loaded_callback()
                    
                    return True
            
            print("ℹ️ デフォルト画像が見つかりませんでした")
            return False
            
        except Exception as e:
            print(f"⚠️ デフォルト画像読み込み警告: {e}")
            return False
    
    def save_image(self, parent_window=None):
        """
        画像を保存
        
        Args:
            parent_window: 親ウィンドウ（ダイアログの親として使用）
        
        Returns:
            bool: 保存成功時True、失敗時False
        """
        try:
            if not self.current_image:
                if parent_window:
                    MessageDialog.show_warning(parent_window, "警告", "保存する画像がありません")
                return False
            
            file_path = filedialog.asksaveasfilename(
                title="画像を保存",
                defaultextension=".jpg",
                filetypes=[
                    ("JPEG", "*.jpg"),
                    ("PNG", "*.png"),
                    ("BMP", "*.bmp"),
                    ("TIFF", "*.tiff")
                ]
            )
            
            if file_path:
                self.current_image.save(file_path)
                self.status_label.configure(text=f"💾 画像保存完了: {os.path.basename(file_path)}")
                print(f"✅ 画像保存: {file_path}")
                return True
                
        except Exception as e:
            print(f"❌ 画像保存エラー: {e}")
            if parent_window:
                MessageDialog.show_error(parent_window, "エラー", f"画像保存エラー: {e}")
            return False
    
    def display_image(self, image: Image.Image):
        """
        画像をキャンバスに表示
        
        Args:
            image: 表示する画像（PIL.Image.Image）
        """
        try:
            if not image:
                return
            
            # キャンバスサイズを取得
            self.canvas.update()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # キャンバスサイズが未確定の場合は少し待ってからリトライ
                self.canvas.after(100, lambda: self.display_image(image))
                return
            
            # 画像をキャンバスサイズに合わせてリサイズ
            img_width, img_height = image.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # PhotoImageに変換
            self.photo = ImageTk.PhotoImage(resized_image)
            
            # キャンバスをクリアして新しい画像を描画
            self.canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.canvas.create_image(x, y, anchor="nw", image=self.photo)
            
        except Exception as e:
            print(f"❌ 画像表示エラー: {e}")
    
    def update_current_image(self, new_image: Image.Image):
        """
        現在の画像を更新して表示
        
        Args:
            new_image: 新しい画像（PIL.Image.Image）
        """
        if new_image:
            self.current_image = new_image.copy()
            self.display_image(new_image)
    
    def reset_to_original(self):
        """
        オリジナル画像に戻す
        
        Returns:
            bool: リセット成功時True、失敗時False
        """
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.display_image(self.current_image)
            return True
        return False
    
    def get_current_image(self):
        """
        現在の画像を取得
        
        Returns:
            PIL.Image.Image: 現在の画像、なければNone
        """
        return self.current_image.copy() if self.current_image else None
    
    def get_original_image(self):
        """
        オリジナル画像を取得
        
        Returns:
            PIL.Image.Image: オリジナル画像、なければNone
        """
        return self.original_image.copy() if self.original_image else None
    
    def has_image(self):
        """
        画像が読み込まれているかチェック
        
        Returns:
            bool: 画像が読み込まれている場合True
        """
        return self.current_image is not None
    
    def set_image_loaded_callback(self, callback):
        """
        画像読み込み完了時のコールバックを設定
        
        Args:
            callback: 画像読み込み完了時に呼び出される関数
        """
        self.on_image_loaded_callback = callback
