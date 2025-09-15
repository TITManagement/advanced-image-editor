#!/usr/bin/env python3
"""
カーブエディタウィジェット - Curve Editor Widget

0-255範囲のガンマ補正カーブを2次元グラフで編集するためのUIコンポーネント
"""

import tkinter as tk
import customtkinter as ctk
import numpy as np
from typing import List, Tuple, Callable, Optional
from scipy.interpolate import interp1d


class CurveEditor(ctk.CTkFrame):
    """
    ガンマ補正用カーブエディタ
    
    機能:
    - 縦軸: 出力濃度 (0-255)
    - 横軸: 入力濃度 (0-255)
    - マウス操作で制御点の追加・移動・削除
    - スプライン補間による滑らかな曲線
    - リアルタイムでLUT (Look-Up Table) を生成
    """
    
    def __init__(self, parent, width: int = 300, height: int = 300, 
                 on_curve_change: Optional[Callable] = None):
        super().__init__(parent)
        
        self.width = width
        self.height = height
        self.on_curve_change = on_curve_change
        
        # 制御点リスト [(x, y), ...] ここでx, yは0-255の範囲
        self.control_points = [(0, 0), (255, 255)]  # デフォルトは線形（y=x）
        
        # マウス操作用変数
        self.selected_point = None
        self.point_radius = 8
        self.grid_color = "#404040"
        self.curve_color = "#00ff00"
        self.point_color = "#ff0000"
        self.selected_point_color = "#ffff00"
        
        # パフォーマンス最適化用変数
        self.update_timer = None
        self.debounce_delay = 100  # ミリ秒
        self.is_dragging = False
        
        self._setup_ui()
        self._update_curve()
    
    def _setup_ui(self):
        """UIセットアップ"""
        # ラベル
        self.label = ctk.CTkLabel(self, text="ガンマ補正カーブ")
        self.label.pack(pady=(0, 5))
        
        # キャンバス
        self.canvas = tk.Canvas(
            self, 
            width=self.width, 
            height=self.height,
            bg="#2b2b2b",
            highlightthickness=1,
            highlightbackground="#565b5e"
        )
        self.canvas.pack(pady=5)
        
        # マウスイベントバインド
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Button-3>", self._on_right_click)  # 右クリック（削除用）
        
        # リセットボタン
        self.reset_button = ctk.CTkButton(
            self, 
            text="リセット", 
            width=80,
            command=self._reset_curve
        )
        self.reset_button.pack(pady=5)
        
        # 現在の値表示
        self.info_label = ctk.CTkLabel(self, text="制御点: 2個")
        self.info_label.pack()
    
    def _canvas_to_curve(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """キャンバス座標をカーブ座標(0-255)に変換"""
        curve_x = int((canvas_x / self.width) * 255)
        curve_y = int(255 - (canvas_y / self.height) * 255)  # Y軸は反転
        curve_x = max(0, min(255, curve_x))
        curve_y = max(0, min(255, curve_y))
        return curve_x, curve_y
    
    def _curve_to_canvas(self, curve_x: int, curve_y: int) -> Tuple[int, int]:
        """カーブ座標(0-255)をキャンバス座標に変換"""
        canvas_x = int((curve_x / 255) * self.width)
        canvas_y = int(self.height - (curve_y / 255) * self.height)  # Y軸は反転
        return canvas_x, canvas_y
    
    def _draw_grid(self):
        """グリッドを描画"""
        self.canvas.delete("grid")
        
        # 縦線
        for i in range(1, 4):  # 64, 128, 192の位置
            x = int((i * 64 / 255) * self.width)
            self.canvas.create_line(
                x, 0, x, self.height, 
                fill=self.grid_color, 
                width=1, 
                tags="grid"
            )
        
        # 横線
        for i in range(1, 4):  # 64, 128, 192の位置
            y = int(self.height - (i * 64 / 255) * self.height)
            self.canvas.create_line(
                0, y, self.width, y, 
                fill=self.grid_color, 
                width=1, 
                tags="grid"
            )
        
        # 枠線
        self.canvas.create_rectangle(
            0, 0, self.width, self.height, 
            outline="#565b5e", 
            width=2, 
            tags="grid"
        )
    
    def _draw_curve(self):
        """カーブを描画"""
        self.canvas.delete("curve")
        
        if len(self.control_points) < 2:
            return
        
        # 制御点をX座標でソート
        sorted_points = sorted(self.control_points, key=lambda p: p[0])
        
        # スプライン補間で滑らかな曲線を生成
        x_points = [p[0] for p in sorted_points]
        y_points = [p[1] for p in sorted_points]
        
        # 補間用のx値（0-255の範囲で細かく）
        x_interp = np.linspace(0, 255, 256)
        
        try:
            if len(sorted_points) == 2:
                # 2点の場合は線形補間
                y_interp = np.interp(x_interp, x_points, y_points)
            else:
                # 3点以上の場合はスプライン補間
                # cubic補間でエラーが出る場合はlinearにフォールバック
                try:
                    f = interp1d(x_points, y_points, kind='cubic', 
                               bounds_error=False, fill_value='extrapolate')
                    y_interp = f(x_interp)
                except ValueError:
                    # cubic補間が失敗した場合は線形補間
                    f = interp1d(x_points, y_points, kind='linear', 
                               bounds_error=False, fill_value='extrapolate')
                    y_interp = f(x_interp)
                
                y_interp = np.clip(y_interp, 0, 255)  # 0-255の範囲に制限
            
            # キャンバス座標に変換して描画
            canvas_points = []
            for i in range(len(x_interp)):
                canvas_x, canvas_y = self._curve_to_canvas(int(x_interp[i]), int(y_interp[i]))
                canvas_points.extend([canvas_x, canvas_y])
            
            if len(canvas_points) >= 4:
                self.canvas.create_line(
                    canvas_points,
                    fill=self.curve_color,
                    width=2,
                    smooth=True,
                    tags="curve"
                )
                
        except Exception as e:
            print(f"⚠️ カーブ描画エラー: {e}")
            # エラーの場合は直線で接続
            canvas_points = []
            for point in sorted_points:
                canvas_x, canvas_y = self._curve_to_canvas(point[0], point[1])
                canvas_points.extend([canvas_x, canvas_y])
            
            if len(canvas_points) >= 4:
                self.canvas.create_line(
                    canvas_points,
                    fill=self.curve_color,
                    width=2,
                    tags="curve"
                )
    
    def _draw_control_points(self):
        """制御点を描画"""
        self.canvas.delete("control_points")
        
        for i, (x, y) in enumerate(self.control_points):
            canvas_x, canvas_y = self._curve_to_canvas(x, y)
            
            color = self.selected_point_color if i == self.selected_point else self.point_color
            
            self.canvas.create_oval(
                canvas_x - self.point_radius, canvas_y - self.point_radius,
                canvas_x + self.point_radius, canvas_y + self.point_radius,
                fill=color,
                outline="white",
                width=2,
                tags="control_points"
            )
            
            # 座標表示
            self.canvas.create_text(
                canvas_x, canvas_y - self.point_radius - 15,
                text=f"({x},{y})",
                fill="white",
                font=("Arial", 8),
                tags="control_points"
            )
    
    def _update_curve(self):
        """カーブ全体を更新"""
        self._draw_grid()
        self._draw_curve()
        self._draw_control_points()
        
        # 情報更新
        self.info_label.configure(text=f"制御点: {len(self.control_points)}個")
    
    def _schedule_callback_update(self):
        """コールバック更新をスケジュール（デバウンス処理）"""
        # 既存のタイマーをキャンセル
        if self.update_timer:
            self.after_cancel(self.update_timer)
        
        # 新しいタイマーをセット
        self.update_timer = self.after(self.debounce_delay, self._execute_callback)
    
    def _execute_callback(self):
        """実際のコールバック実行"""
        self.update_timer = None
        if self.on_curve_change:
            self.on_curve_change(self.get_lut())
    
    def _find_point_at(self, canvas_x: int, canvas_y: int) -> Optional[int]:
        """指定座標にある制御点のインデックスを返す"""
        for i, (x, y) in enumerate(self.control_points):
            point_canvas_x, point_canvas_y = self._curve_to_canvas(x, y)
            distance = ((canvas_x - point_canvas_x) ** 2 + (canvas_y - point_canvas_y) ** 2) ** 0.5
            if distance <= self.point_radius:
                return i
        return None
    
    def _on_click(self, event):
        """マウスクリック処理"""
        self.selected_point = self._find_point_at(event.x, event.y)
        self.is_dragging = True
        
        if self.selected_point is None:
            # 新しい制御点を追加
            curve_x, curve_y = self._canvas_to_curve(event.x, event.y)
            self.control_points.append((curve_x, curve_y))
            self.selected_point = len(self.control_points) - 1
            print(f"📍 制御点追加: ({curve_x}, {curve_y})")
        
        self._update_curve()
        # ドラッグ中はコールバックを遅延
        self._schedule_callback_update()
    
    def _on_drag(self, event):
        """マウスドラッグ処理"""
        if self.selected_point is not None and self.is_dragging:
            curve_x, curve_y = self._canvas_to_curve(event.x, event.y)
            
            # 端点の場合はX座標を固定
            if self.selected_point == 0:
                curve_x = 0
            elif self.selected_point == len(self.control_points) - 1:
                curve_x = 255
            
            self.control_points[self.selected_point] = (curve_x, curve_y)
            self._update_curve()
            # ドラッグ中はコールバックを遅延（頻繁な更新を防ぐ）
            self._schedule_callback_update()
    
    def _on_release(self, event):
        """マウスリリース処理"""
        if self.is_dragging:
            self.is_dragging = False
            self.selected_point = None
            self._update_curve()
            # リリース時は即座にコールバック実行
            if self.update_timer:
                self.after_cancel(self.update_timer)
                self.update_timer = None
            self._execute_callback()
    
    def _on_double_click(self, event):
        """ダブルクリック処理（制御点追加の代替）"""
        curve_x, curve_y = self._canvas_to_curve(event.x, event.y)
        
        # 既存の点に近すぎる場合は追加しない
        for x, y in self.control_points:
            if abs(x - curve_x) < 10 and abs(y - curve_y) < 10:
                return
        
        self.control_points.append((curve_x, curve_y))
        print(f"📍 制御点追加（ダブルクリック）: ({curve_x}, {curve_y})")
        self._update_curve()
    
    def _on_right_click(self, event):
        """右クリック処理（制御点削除）"""
        point_index = self._find_point_at(event.x, event.y)
        
        if point_index is not None and len(self.control_points) > 2:
            # 端点（最初と最後）は削除しない
            if point_index != 0 and point_index != len(self.control_points) - 1:
                removed_point = self.control_points.pop(point_index)
                print(f"🗑️ 制御点削除: {removed_point}")
                self._update_curve()
                # 削除時は即座にコールバック実行
                self._execute_callback()
    
    def _reset_curve(self):
        """カーブをリセット（線形に戻す）"""
        self.control_points = [(0, 0), (255, 255)]
        self.selected_point = None
        self.is_dragging = False
        print("🔄 カーブリセット: 線形曲線に戻しました")
        self._update_curve()
        # リセット時は即座にコールバック実行
        self._execute_callback()
    
    def get_lut(self) -> np.ndarray:
        """現在のカーブからLUT（ルックアップテーブル）を生成"""
        try:
            # 制御点をX座標でソート
            sorted_points = sorted(self.control_points, key=lambda p: p[0])
            x_points = [p[0] for p in sorted_points]
            y_points = [p[1] for p in sorted_points]
            
            # 0-255の範囲でLUTを生成
            x_values = np.arange(256)
            
            if len(sorted_points) == 2:
                # 2点の場合は線形補間
                lut = np.interp(x_values, x_points, y_points)
            else:
                # 3点以上の場合はスプライン補間
                try:
                    f = interp1d(x_points, y_points, kind='cubic',
                               bounds_error=False, fill_value='extrapolate')
                    lut = f(x_values)
                except ValueError:
                    # cubic補間が失敗した場合は線形補間
                    f = interp1d(x_points, y_points, kind='linear',
                               bounds_error=False, fill_value='extrapolate')
                    lut = f(x_values)
            
            # 0-255の範囲にクリップ
            lut = np.clip(lut, 0, 255).astype(np.uint8)
            return lut
            
        except Exception as e:
            print(f"❌ LUT生成エラー: {e}")
            # エラーの場合は線形LUTを返す
            return np.arange(256, dtype=np.uint8)
    
    def set_curve(self, control_points: List[Tuple[int, int]]):
        """外部からカーブを設定"""
        if len(control_points) >= 2:
            self.control_points = control_points.copy()
            self.selected_point = None
            self._update_curve()
    
    def get_curve(self) -> List[Tuple[int, int]]:
        """現在のカーブの制御点を取得"""
        return self.control_points.copy()


# テスト用のサンプルアプリケーション
if __name__ == "__main__":
    def on_curve_changed(lut):
        print(f"📊 LUT更新: 入力0→出力{lut[0]}, 入力128→出力{lut[128]}, 入力255→出力{lut[255]}")
    
    root = ctk.CTk()
    root.title("カーブエディタ テスト")
    root.geometry("400x500")
    
    curve_editor = CurveEditor(root, on_curve_change=on_curve_changed)
    curve_editor.pack(padx=20, pady=20)
    
    root.mainloop()