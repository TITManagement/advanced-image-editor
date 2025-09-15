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
    
    def __init__(self, parent, width: int = 255, height: int = 255, 
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
        
        # ドラッグ操作用変数
        self.is_dragging = False
        self.drag_start_pos = None  # ドラッグ開始時のマウス座標
        self.drag_start_point = None  # ドラッグ開始時の制御点座標
        self.click_threshold = 5  # クリックとドラッグを区別するピクセル距離
        
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
            highlightthickness=0,  # 境界線を除去
            bd=0  # ボーダーを除去
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
        """キャンバス座標をカーブ座標(0-255)に変換 - 完全1:1版"""
        # キャンバスサイズを動的に取得
        actual_width = self.canvas.winfo_width()
        actual_height = self.canvas.winfo_height()
        
        # キャンバスが初期化されていない場合は設定値を使用
        if actual_width <= 1 or actual_height <= 1:
            actual_width = self.width
            actual_height = self.height
        
        # 1:1マッピング（キャンバス座標 = カーブ値）
        curve_x = max(0, min(255, int(canvas_x)))
        curve_y = max(0, min(255, int(255 - canvas_y)))  # Y軸反転
        
        return curve_x, curve_y
    
    def _curve_to_canvas(self, curve_x: int, curve_y: int) -> Tuple[int, int]:
        """カーブ座標(0-255)をキャンバス座標に変換 - 完全1:1版"""
        # 1:1マッピング（カーブ値 = キャンバス座標）
        canvas_x = max(0, min(255, int(curve_x)))
        canvas_y = max(0, min(255, int(255 - curve_y)))  # Y軸反転
        
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
        self.drag_start_pos = (event.x, event.y)
        clicked_point = self._find_point_at(event.x, event.y)
        
        if clicked_point is None:
            # 新しい制御点を追加
            curve_x, curve_y = self._canvas_to_curve(event.x, event.y)
            self.control_points.append((curve_x, curve_y))
            print(f"📍 制御点追加: ({curve_x}, {curve_y})")
            self._update_curve()
            # 制御点追加時はドラッグを無効にする
            self.selected_point = None
            self.is_dragging = False
        else:
            # 既存の制御点を選択
            self.selected_point = clicked_point
            self.drag_start_point = self.control_points[self.selected_point]
            self.is_dragging = False  # ドラッグはまだ開始しない
            print(f"🎯 制御点選択: インデックス{self.selected_point}")
        
        self._schedule_callback_update()
    
    def _on_drag(self, event):
        """マウスドラッグ処理"""
        if (self.selected_point is not None and self.drag_start_pos is not None and 
            self.drag_start_point is not None):
            
            # マウス移動距離を計算
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]
            move_distance = (dx * dx + dy * dy) ** 0.5
            
            print(f"🖱️ ドラッグ: 現在位置({event.x}, {event.y}), 開始位置{self.drag_start_pos}, 移動量({dx}, {dy}), 距離={move_distance:.1f}")
            
            # 一定距離以上移動した場合にドラッグ開始
            if move_distance > self.click_threshold:
                if not self.is_dragging:
                    self.is_dragging = True
                    print(f"🚀 ドラッグ開始: 制御点{self.selected_point}, 元座標{self.drag_start_point}")
                
                # 🔧 新しいアプローチ: マウスの現在位置を直接カーブ座標に変換
                print(f"   現在のマウス位置を直接変換: ({event.x}, {event.y})")
                curve_x, curve_y = self._canvas_to_curve(event.x, event.y)
                print(f"   直接変換結果: ({curve_x}, {curve_y})")
                
                # 逆変換で確認
                back_canvas_x, back_canvas_y = self._curve_to_canvas(curve_x, curve_y)
                canvas_diff_x = abs(event.x - back_canvas_x)
                canvas_diff_y = abs(event.y - back_canvas_y)
                print(f"   逆変換確認: カーブ({curve_x}, {curve_y}) → キャンバス({back_canvas_x}, {back_canvas_y})")
                print(f"   往復変換誤差: X差={canvas_diff_x}, Y差={canvas_diff_y}")
                
                # 🔓 制約解除: すべての制御点でX、Y座標ともに自由に移動可能
                final_point = (curve_x, curve_y)
                
                if self.selected_point == 0:
                    print("   端点(開始): X、Y座標ともに自由に更新")
                elif self.selected_point == len(self.control_points) - 1:
                    print("   端点(終了): X、Y座標ともに自由に更新")
                else:
                    print("   中間点: X、Y座標ともに更新")
                
                # 制御点座標を更新
                old_point = self.control_points[self.selected_point]
                self.control_points[self.selected_point] = final_point
                print(f"   制御点更新: {old_point} → {self.control_points[self.selected_point]}")
                
                # 更新後の制御点を再度キャンバス座標に変換して確認
                final_canvas_x, final_canvas_y = self._curve_to_canvas(final_point[0], final_point[1])
                
                # すべての制御点でX、Y座標の両方を評価
                final_diff_x = abs(event.x - final_canvas_x)
                final_diff_y = abs(event.y - final_canvas_y)
                
                # 制御点タイプに関係なく、統一された評価ロジック
                point_type = "端点" if (self.selected_point == 0 or self.selected_point == len(self.control_points) - 1) else "中間点"
                print(f"   {point_type}確認: 制御点({final_point[0]}, {final_point[1]}) → 描画位置({final_canvas_x}, {final_canvas_y})")
                print(f"   マウス位置({event.x}, {event.y})との差: X差={final_diff_x}, Y差={final_diff_y}")
                
                if final_diff_x <= 1 and final_diff_y <= 1:
                    print(f"   ✅ {point_type}の座標ズレは許容範囲内")
                else:
                    print(f"   ⚠️ {point_type}の座標ズレが大きいです")
                
                self._update_curve()
                self._schedule_callback_update()
    
    def _on_release(self, event):
        """マウスリリース処理"""
        if self.is_dragging:
            # デバッグ情報：マウスリリース時の座標確認
            release_canvas_x, release_canvas_y = event.x, event.y
            release_curve_x, release_curve_y = self._canvas_to_curve(release_canvas_x, release_canvas_y)
            
            print(f"🖱️ マウスリリース: キャンバス座標({release_canvas_x}, {release_canvas_y}) → カーブ座標({release_curve_x}, {release_curve_y})")
            
            if self.selected_point is not None and 0 <= self.selected_point < len(self.control_points):
                actual_point = self.control_points[self.selected_point]
                
                # 🔓 制約解除: すべての制御点でX、Y座標ともに評価
                x_diff = abs(actual_point[0] - release_curve_x)
                y_diff = abs(actual_point[1] - release_curve_y)
                
                point_type = "端点" if (self.selected_point == 0 or self.selected_point == len(self.control_points) - 1) else "中間点"
                print(f"📍 {point_type}制御点: {actual_point}")
                print(f"📏 座標ズレ: X差={x_diff}, Y差={y_diff}")
                
                if x_diff <= 1 and y_diff <= 1:
                    print(f"✅ {point_type}の座標ズレは許容範囲内")
                else:
                    print(f"⚠️ {point_type}の座標ズレが大きいです")
            
            self.is_dragging = False
            self.selected_point = None
            self.drag_start_pos = None
            self.drag_start_point = None
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
        self.drag_start_pos = None
        self.drag_start_point = None
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
            self.is_dragging = False
            self.drag_start_pos = None
            self.drag_start_point = None
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