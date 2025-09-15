#!/usr/bin/env python3
"""
画像解析プラグイン - Image Analysis Plugin

フーリエ変換、ウェーブレット変換、特徴点検出、ヒストグラム解析などの高度な画像解析機能を提供
"""

import numpy as np
import cv2
from PIL import Image
import customtkinter as ctk
from typing import Dict, Any

# matplotlib（オプション機能：グラフ描画）
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
    print("✅ matplotlib ライブラリ利用可能 - グラフ描画機能が有効です")
except ImportError:
    print("ℹ️ matplotlib未インストール - グラフ描画機能は無効（基本機能は利用可能）")
    print("   追加機能を利用したい場合：pip install matplotlib")
    MATPLOTLIB_AVAILABLE = False

# 相対インポートでcore moduleを使用
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin_base import ImageProcessorPlugin, PluginUIHelper


class ImageAnalysisPlugin(ImageProcessorPlugin):
    """画像解析プラグイン（旧：高度処理プラグイン）"""
    
    def __init__(self):
        super().__init__("image_analysis", "2.0.0")
        self.analysis_type = "none"
        self.show_histogram = False
        self.current_analysis_result = None
        
        # 個別機能の状態追跡
        self.applied_histogram = False
        self.applied_features = None
        self.applied_frequency = None
        self.applied_blur_detection = False
        self.applied_noise_analysis = False
        
        # 画像バックアップシステム
        self.backup_image = None           # 処理前の画像をバックアップ
        self.features_backup = None        # 特徴点検出処理前のバックアップ
        self.frequency_backup = None       # 周波数解析処理前のバックアップ
        self.blur_backup = None            # ブラー検出処理前のバックアップ
        self.noise_backup = None           # ノイズ解析処理前のバックアップ
        self.histogram_backup = None       # ヒストグラム表示処理前のバックアップ
        
    def get_display_name(self) -> str:
        return "画像解析"
    
    def get_description(self) -> str:
        return "フーリエ変換、特徴点検出、ヒストグラム解析などの高度な画像解析機能を提供します"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """画像解析UIを作成"""
        
        # ヒストグラム解析セクション
        histogram_frame = ctk.CTkFrame(parent)
        histogram_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(histogram_frame, text="ヒストグラム解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # ヒストグラム表示セクション
        histogram_section = ctk.CTkFrame(histogram_frame)
        histogram_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['histogram'] = PluginUIHelper.create_button(
            histogram_section,
            text="ヒストグラム表示",
            command=self._show_histogram_analysis,
            width=120
        )
        self._buttons['histogram'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_histogram'] = PluginUIHelper.create_button(
            histogram_section,
            text="🔄 取消",
            command=self._undo_histogram,
            width=60
        )
        self._buttons['undo_histogram'].pack(side="left")
        self._buttons['undo_histogram'].configure(state="disabled")
        
        # 特徴点検出セクション
        feature_frame = ctk.CTkFrame(parent)
        feature_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(feature_frame, text="特徴点検出", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 特徴点検出ボタン群
        feature_buttons_frame = ctk.CTkFrame(feature_frame)
        feature_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        # SIFT特徴点セクション
        sift_section = ctk.CTkFrame(feature_buttons_frame)
        sift_section.pack(fill="x", pady=3)
        
        self._buttons['sift'] = PluginUIHelper.create_button(
            sift_section,
            text="SIFT特徴点",
            command=lambda: self._apply_feature_detection("sift"),
            width=100
        )
        self._buttons['sift'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_sift'] = PluginUIHelper.create_button(
            sift_section,
            text="🔄 取消",
            command=lambda: self._undo_features("sift"),
            width=60
        )
        self._buttons['undo_sift'].pack(side="left")
        self._buttons['undo_sift'].configure(state="disabled")
        
        # ORB特徴点セクション
        orb_section = ctk.CTkFrame(feature_buttons_frame)
        orb_section.pack(fill="x", pady=3)
        
        self._buttons['orb'] = PluginUIHelper.create_button(
            orb_section,
            text="ORB特徴点",
            command=lambda: self._apply_feature_detection("orb"),
            width=100
        )
        self._buttons['orb'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_orb'] = PluginUIHelper.create_button(
            orb_section,
            text="🔄 取消",
            command=lambda: self._undo_features("orb"),
            width=60
        )
        self._buttons['undo_orb'].pack(side="left")
        self._buttons['undo_orb'].configure(state="disabled")
        
        # 周波数解析セクション
        frequency_frame = ctk.CTkFrame(parent)
        frequency_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(frequency_frame, text="周波数解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 周波数解析ボタン群
        freq_buttons_frame = ctk.CTkFrame(frequency_frame)
        freq_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        # フーリエ変換セクション
        fft_section = ctk.CTkFrame(freq_buttons_frame)
        fft_section.pack(fill="x", pady=3)
        
        self._buttons['fft'] = PluginUIHelper.create_button(
            fft_section,
            text="フーリエ変換",
            command=lambda: self._apply_frequency_analysis("fft"),
            width=100
        )
        self._buttons['fft'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_fft'] = PluginUIHelper.create_button(
            fft_section,
            text="🔄 取消",
            command=lambda: self._undo_frequency("fft"),
            width=60
        )
        self._buttons['undo_fft'].pack(side="left")
        self._buttons['undo_fft'].configure(state="disabled")
        
        # DCT変換セクション
        dct_section = ctk.CTkFrame(freq_buttons_frame)
        dct_section.pack(fill="x", pady=3)
        
        self._buttons['dct'] = PluginUIHelper.create_button(
            dct_section,
            text="DCT変換",
            command=lambda: self._apply_frequency_analysis("dct"),
            width=100
        )
        self._buttons['dct'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_dct'] = PluginUIHelper.create_button(
            dct_section,
            text="🔄 取消",
            command=lambda: self._undo_frequency("dct"),
            width=60
        )
        self._buttons['undo_dct'].pack(side="left")
        self._buttons['undo_dct'].configure(state="disabled")
        
        # 画像品質解析セクション
        quality_frame = ctk.CTkFrame(parent)
        quality_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(quality_frame, text="画像品質解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # ブラー検出セクション
        blur_section = ctk.CTkFrame(quality_frame)
        blur_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['blur_detect'] = PluginUIHelper.create_button(
            blur_section,
            text="ブラー検出",
            command=self._detect_blur,
            width=100
        )
        self._buttons['blur_detect'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_blur'] = PluginUIHelper.create_button(
            blur_section,
            text="🔄 取消",
            command=self._undo_blur,
            width=60
        )
        self._buttons['undo_blur'].pack(side="left")
        self._buttons['undo_blur'].configure(state="disabled")
        
        # ノイズ解析セクション
        noise_section = ctk.CTkFrame(quality_frame)
        noise_section.pack(fill="x", padx=5, pady=3)
        
        self._buttons['noise_detect'] = PluginUIHelper.create_button(
            noise_section,
            text="ノイズ解析",
            command=self._analyze_noise,
            width=100
        )
        self._buttons['noise_detect'].pack(side="left", padx=(0, 5))
        
        self._buttons['undo_noise'] = PluginUIHelper.create_button(
            noise_section,
            text="🔄 取消",
            command=self._undo_noise,
            width=60
        )
        self._buttons['undo_noise'].pack(side="left")
        self._buttons['undo_noise'].configure(state="disabled")
    
    def _show_histogram_analysis(self) -> None:
        """ヒストグラム解析を表示"""
        self.applied_histogram = True
        print("📊 ヒストグラム解析実行")
        
        # undoボタンを有効化
        self._enable_undo_button("undo_histogram")
        
        if hasattr(self, 'histogram_callback'):
            self.histogram_callback()
    
    def _undo_histogram(self) -> None:
        """ヒストグラム表示のundo"""
        print("🔄 ヒストグラム表示取消")
        
        # 状態をリセット
        self.applied_histogram = False
        
        # undoボタンを無効化
        self._disable_undo_button("undo_histogram")
        
        # コールバックがあれば実行
        if hasattr(self, 'undo_histogram_callback'):
            self.undo_histogram_callback()
    
    def _apply_feature_detection(self, feature_type: str) -> None:
        """特徴点検出実行"""
        self.analysis_type = feature_type
        self.applied_features = feature_type
        print(f"🎯 特徴点検出実行: {feature_type}")
        
        # undoボタンを有効化
        self._enable_undo_button(f"undo_{feature_type}")
        
        if hasattr(self, 'feature_callback'):
            self.feature_callback(feature_type)
    
    def _apply_frequency_analysis(self, analysis_type: str) -> None:
        """周波数解析実行"""
        self.analysis_type = analysis_type
        self.applied_frequency = analysis_type
        print(f"📊 周波数解析実行: {analysis_type}")
        
        # undoボタンを有効化
        self._enable_undo_button(f"undo_{analysis_type}")
        
        if hasattr(self, 'frequency_callback'):
            self.frequency_callback(analysis_type)
    
    def _detect_blur(self) -> None:
        """ブラー検出実行"""
        self.applied_blur_detection = True
        print("🔍 ブラー検出実行")
        
        # undoボタンを有効化
        self._enable_undo_button("undo_blur")
        
        if hasattr(self, 'blur_callback'):
            self.blur_callback()
    
    def _analyze_noise(self) -> None:
        """ノイズ解析実行"""
        self.applied_noise_analysis = True
        print("📈 ノイズ解析実行")
        
        # undoボタンを有効化
        self._enable_undo_button("undo_noise")
        
        if hasattr(self, 'noise_callback'):
            self.noise_callback()
    
    def _enable_undo_button(self, button_name: str) -> None:
        """undoボタンを有効化"""
        if button_name in self._buttons:
            self._buttons[button_name].configure(state="normal")
    
    def _disable_undo_button(self, button_name: str) -> None:
        """undoボタンを無効化"""
        if button_name in self._buttons:
            self._buttons[button_name].configure(state="disabled")
    
    def _undo_features(self, feature_type: str) -> None:
        """特徴点検出のundo"""
        print(f"🔄 特徴点検出取消: {feature_type}")
        
        # 状態をリセット
        self.applied_features = None
        self.analysis_type = "none"
        
        # undoボタンを無効化
        self._disable_undo_button(f"undo_{feature_type}")
        
        # コールバックがあれば実行
        if hasattr(self, 'undo_features_callback'):
            self.undo_features_callback(feature_type)
    
    def _undo_frequency(self, analysis_type: str) -> None:
        """周波数解析のundo"""
        print(f"🔄 周波数解析取消: {analysis_type}")
        
        # 状態をリセット
        self.applied_frequency = None
        self.analysis_type = "none"
        
        # undoボタンを無効化
        self._disable_undo_button(f"undo_{analysis_type}")
        
        # コールバックがあれば実行
        if hasattr(self, 'undo_frequency_callback'):
            self.undo_frequency_callback(analysis_type)
    
    def _undo_blur(self) -> None:
        """ブラー検出のundo"""
        print(f"🔄 ブラー検出取消")
        
        # 状態をリセット
        self.applied_blur_detection = False
        
        # undoボタンを無効化
        self._disable_undo_button("undo_blur")
        
        # コールバックがあれば実行
        if hasattr(self, 'undo_blur_callback'):
            self.undo_blur_callback()
    
    def _undo_noise(self) -> None:
        """ノイズ解析のundo"""
        print(f"🔄 ノイズ解析取消")
        
        # 状態をリセット
        self.applied_noise_analysis = False
        
        # undoボタンを無効化
        self._disable_undo_button("undo_noise")
        
        # コールバックがあれば実行
        if hasattr(self, 'undo_noise_callback'):
            self.undo_noise_callback()
    
    def set_histogram_callback(self, callback):
        """ヒストグラム解析用のコールバックを設定"""
        self.histogram_callback = callback
    
    def set_feature_callback(self, callback):
        """特徴点検出用のコールバックを設定"""
        self.feature_callback = callback
    
    def set_frequency_callback(self, callback):
        """周波数解析用のコールバックを設定"""
        self.frequency_callback = callback
    
    def set_blur_callback(self, callback):
        """ブラー検出用のコールバックを設定"""
        self.blur_callback = callback
    
    def set_noise_callback(self, callback):
        """ノイズ解析用のコールバックを設定"""
        self.noise_callback = callback
    
    def set_undo_features_callback(self, callback):
        """特徴点検出undo用のコールバックを設定"""
        self.undo_features_callback = callback
    
    def set_undo_frequency_callback(self, callback):
        """周波数解析undo用のコールバックを設定"""
        self.undo_frequency_callback = callback
    
    def set_undo_blur_callback(self, callback):
        """ブラー検出undo用のコールバックを設定"""
        self.undo_blur_callback = callback
    
    def set_undo_noise_callback(self, callback):
        """ノイズ解析undo用のコールバックを設定"""
        self.undo_noise_callback = callback
    
    def set_undo_histogram_callback(self, callback):
        """ヒストグラム表示undo用のコールバックを設定"""
        self.undo_histogram_callback = callback
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """画像解析を適用（通常の処理では使用しない）"""
        # 画像解析は特殊なボタン操作で実行されるため、通常の処理では何もしない
        return image
    
    def apply_feature_detection(self, image: Image.Image, feature_type: str) -> Image.Image:
        """特徴点検出を適用"""
        try:
            print(f"🎯 特徴点検出開始: {feature_type}")
            
            # OpenCVフォーマットに変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            if feature_type == "sift":
                # SIFT特徴点検出
                try:
                    sift = cv2.SIFT_create()
                    keypoints, _ = sift.detectAndCompute(gray_image, None)
                except:
                    # OpenCVのバージョンによっては異なるAPI
                    sift = cv2.xfeatures2d.SIFT_create()
                    keypoints, _ = sift.detectAndCompute(gray_image, None)
                
            elif feature_type == "orb":
                # ORB特徴点検出
                orb = cv2.ORB_create()
                keypoints, _ = orb.detectAndCompute(gray_image, None)
            else:
                keypoints = []
            
            # 特徴点を画像に描画
            result_image = cv_image.copy()
            result_image = cv2.drawKeypoints(result_image, keypoints, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            
            # PIL形式に戻す
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            
            print(f"✅ 特徴点検出完了: {len(keypoints)}個の特徴点を検出")
            return final_image
            
        except Exception as e:
            print(f"❌ 特徴点検出エラー ({feature_type}): {e}")
            return image
    
    def apply_frequency_analysis(self, image: Image.Image, analysis_type: str) -> Image.Image:
        """周波数解析を適用"""
        try:
            print(f"🔬 周波数解析開始: {analysis_type}")
            
            # グレースケールに変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            if analysis_type == "fft":
                # フーリエ変換
                f_transform = np.fft.fft2(gray_image)
                f_shift = np.fft.fftshift(f_transform)
                magnitude_spectrum = np.log(np.abs(f_shift) + 1)
                
                # 正規化
                magnitude_spectrum = (magnitude_spectrum - magnitude_spectrum.min()) / (magnitude_spectrum.max() - magnitude_spectrum.min()) * 255
                
            elif analysis_type == "dct":
                # DCT変換（2D DCT）
                # OpenCVのdctは1D用なので、scipyまたは手動実装を使用
                try:
                    # NumPyを使った簡易2D DCT実装
                    from scipy.fft import dct
                    # 各行と各列に対してDCTを適用
                    dct_result = dct(dct(gray_image.T, norm='ortho').T, norm='ortho')
                except ImportError:
                    # scipyが利用できない場合、フーリエ変換の実部を使用
                    f_transform = np.fft.fft2(gray_image)
                    dct_result = np.real(f_transform)
                
                magnitude_spectrum = np.log(np.abs(dct_result) + 1)
                
                # 正規化
                magnitude_spectrum = (magnitude_spectrum - magnitude_spectrum.min()) / (magnitude_spectrum.max() - magnitude_spectrum.min()) * 255
            else:
                magnitude_spectrum = gray_image
            
            # RGB形式に変換
            result_rgb = cv2.cvtColor(magnitude_spectrum.astype(np.uint8), cv2.COLOR_GRAY2RGB)
            result_image = Image.fromarray(result_rgb)
            
            print(f"✅ 周波数解析完了: {analysis_type}")
            return result_image
            
        except Exception as e:
            print(f"❌ 周波数解析エラー ({analysis_type}): {e}")
            return image
    
    def detect_blur(self, image: Image.Image) -> Image.Image:
        """ブラー検出を実行"""
        try:
            print("� ブラー検出開始")
            
            # グレースケールに変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Laplacianフィルタでブラー検出
            laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            
            # ブラーレベルの判定
            if laplacian_var < 100:
                blur_level = "高"
                color = (255, 0, 0)  # 赤
            elif laplacian_var < 500:
                blur_level = "中"
                color = (255, 255, 0)  # 黄
            else:
                blur_level = "低"
                color = (0, 255, 0)  # 緑
            
            # 結果を画像に描画
            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result_image, f"Blur Level: {blur_level} ({laplacian_var:.1f})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # PIL形式に戻す
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            
            print(f"✅ ブラー検出完了: レベル{blur_level} (分散: {laplacian_var:.1f})")
            return final_image
            
        except Exception as e:
            print(f"❌ ブラー検出エラー: {e}")
            return image
    
    def analyze_noise(self, image: Image.Image) -> Image.Image:
        """ノイズ解析を実行"""
        try:
            print("📈 ノイズ解析開始")
            
            # グレースケールに変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # ノイズレベルの推定（標準偏差ベース）
            noise_level = np.std(gray_image)
            
            # ノイズレベルの判定
            if noise_level > 50:
                noise_status = "高"
                color = (255, 0, 0)  # 赤
            elif noise_level > 25:
                noise_status = "中"
                color = (255, 255, 0)  # 黄
            else:
                noise_status = "低"
                color = (0, 255, 0)  # 緑
            
            # 結果を画像に描画
            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result_image, f"Noise Level: {noise_status} ({noise_level:.1f})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # PIL形式に戻す
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            
            print(f"✅ ノイズ解析完了: レベル{noise_status} (標準偏差: {noise_level:.1f})")
            return final_image
            
        except Exception as e:
            print(f"❌ ノイズ解析エラー: {e}")
            return image
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'analysis_type': self.analysis_type,
            'show_histogram': self.show_histogram
        }