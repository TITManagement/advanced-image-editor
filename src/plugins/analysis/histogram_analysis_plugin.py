"""
UI生成時のボタンイベント紐付け例 (analysis_plugin.py等で):
    undo_btn = ctk.CTkButton(frame, text="取消", command=histogram_plugin.undo_histogram)
    histogram_plugin.set_undo_button(undo_btn)
"""
 # ctk未使用のため削除
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HistogramAnalysisPlugin:
    def __init__(self):
        self.name = "histogram_analysis"
        self._buttons = {}
        self.histogram_canvas = None
        self.histogram_callback = None
        self.frame = None  # 描画先Frameを保持

    def get_parameters(self):
        """パラメータ取得 (ヒストグラム解析は空dictでOK)"""
        return {}

    def is_enabled(self):
        """プラグインが有効かどうか (常にTrue)"""
        return True

    def set_frame(self, frame):
        """描画先Frameを外部からセット"""
        self.frame = frame

    def set_histogram_callback(self, callback):
        """ヒストグラム描画用画像取得コールバックを設定"""
        self.histogram_callback = callback

    def get_display_name(self):
        return "ヒストグラム解析"



    def show_histogram(self):
        print("[DEBUG] show_histogram called")
        if self.histogram_callback:
            print(f"[DEBUG] histogram_callback: {self.histogram_callback}")
            img = self.histogram_callback()
            print(f"[DEBUG] histogram_callback result: {type(img)} {img}")
        else:
            img = None
            print("[DEBUG] histogram_callback is None")
        if img is None:
            print("[DEBUG] img is None. No image to show histogram.")
            return False
        if not isinstance(img, Image.Image):
            print(f"[DEBUG] img is not PIL.Image.Image: {type(img)}")
            return False
        print(f"[DEBUG] img.mode: {getattr(img, 'mode', None)}")
        arr = np.array(img)
        print(f"[DEBUG] arr.shape: {arr.shape}")
        plt.figure(figsize=(4,2))
        try:
            plt.hist(arr[...,0].ravel(), bins=256, color='r', alpha=0.5, label='R')
            plt.hist(arr[...,1].ravel(), bins=256, color='g', alpha=0.5, label='G')
            plt.hist(arr[...,2].ravel(), bins=256, color='b', alpha=0.5, label='B')
        except (ValueError, TypeError) as e:
            print(f"[DEBUG] Exception in plt.hist: {e}")
            plt.close()
            return False
        plt.legend()
        plt.tight_layout()
        if not hasattr(self, 'frame') or self.frame is None:
            print("[DEBUG] self.frame is not set. Cannot display histogram.")
            plt.close()
            return False
        if self.histogram_canvas:
            print("[DEBUG] Destroying previous histogram_canvas")
            widget = self.histogram_canvas.get_tk_widget()
            widget.pack_forget()
            widget.destroy()
            self.histogram_canvas = None
        fig = plt.gcf()
        print(f"[DEBUG] FigureCanvasTkAgg master: {self.frame}")
        self.histogram_canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.histogram_canvas.draw()
        self.histogram_canvas.get_tk_widget().pack(fill="x", padx=5, pady=5)
        plt.close(fig)
        self._buttons['undo_histogram'].configure(state="normal")
        return True

    def undo_histogram(self):
        print("[DEBUG] undo_histogram called (取消ボタンイベント)")
        if self.histogram_canvas:
            widget = self.histogram_canvas.get_tk_widget()
            print(f"[DEBUG] histogram_canvas widget: {widget}")
            widget.pack_forget()
            widget.destroy()
            self.histogram_canvas = None
        else:
            print("[DEBUG] histogram_canvas is None")
        self._buttons['undo_histogram'].configure(state="disabled")
