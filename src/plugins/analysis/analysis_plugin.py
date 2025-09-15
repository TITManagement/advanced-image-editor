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

# matplotlib（オプション）
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_AVAILABLE = True
    print("✅ matplotlib ライブラリのインポートが完了しました")
except ImportError as e:
    print(f"⚠️ matplotlib インポート警告: {e}")
    print("📦 基本機能のみで動作します。matplotlibなしで継続...")
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
        
        # ヒストグラム表示ボタン
        self._buttons['histogram'] = PluginUIHelper.create_button(
            histogram_frame,
            text="ヒストグラム表示",
            command=self._show_histogram_analysis
        )
        
        # 特徴点検出セクション
        feature_frame = ctk.CTkFrame(parent)
        feature_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(feature_frame, text="特徴点検出", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 特徴点検出ボタン群
        feature_buttons_frame = ctk.CTkFrame(feature_frame)
        feature_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self._buttons['sift'] = PluginUIHelper.create_button(
            feature_buttons_frame,
            text="SIFT特徴点",
            command=lambda: self._apply_feature_detection("sift"),
            width=100
        )
        
        self._buttons['orb'] = PluginUIHelper.create_button(
            feature_buttons_frame,
            text="ORB特徴点",
            command=lambda: self._apply_feature_detection("orb"),
            width=100
        )
        
        # 周波数解析セクション
        frequency_frame = ctk.CTkFrame(parent)
        frequency_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(frequency_frame, text="周波数解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        # 周波数解析ボタン群
        freq_buttons_frame = ctk.CTkFrame(frequency_frame)
        freq_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self._buttons['fft'] = PluginUIHelper.create_button(
            freq_buttons_frame,
            text="フーリエ変換",
            command=lambda: self._apply_frequency_analysis("fft"),
            width=100
        )
        
        self._buttons['dct'] = PluginUIHelper.create_button(
            freq_buttons_frame,
            text="DCT変換",
            command=lambda: self._apply_frequency_analysis("dct"),
            width=100
        )
        
        # 画像品質解析セクション
        quality_frame = ctk.CTkFrame(parent)
        quality_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(quality_frame, text="画像品質解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        
        self._buttons['blur_detect'] = PluginUIHelper.create_button(
            quality_frame,
            text="ブラー検出",
            command=self._detect_blur
        )
        
        self._buttons['noise_detect'] = PluginUIHelper.create_button(
            quality_frame,
            text="ノイズ解析",
            command=self._analyze_noise
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent,
            text="リセット",
            command=self.reset_parameters
        )
    
    def _show_histogram_analysis(self) -> None:
        """ヒストグラム解析を表示"""
        print("📊 ヒストグラム解析実行")
        if hasattr(self, 'histogram_callback'):
            self.histogram_callback()
    
    def _apply_feature_detection(self, feature_type: str) -> None:
        """特徴点検出実行"""
        self.analysis_type = feature_type
        print(f"🎯 特徴点検出実行: {feature_type}")
        if hasattr(self, 'feature_callback'):
            self.feature_callback(feature_type)
    
    def _apply_frequency_analysis(self, analysis_type: str) -> None:
        """周波数解析実行"""
        self.analysis_type = analysis_type
        print(f"� 周波数解析実行: {analysis_type}")
        if hasattr(self, 'frequency_callback'):
            self.frequency_callback(analysis_type)
    
    def _detect_blur(self) -> None:
        """ブラー検出実行"""
        print("� ブラー検出実行")
        if hasattr(self, 'blur_callback'):
            self.blur_callback()
    
    def _analyze_noise(self) -> None:
        """ノイズ解析実行"""
        print("📈 ノイズ解析実行")
        if hasattr(self, 'noise_callback'):
            self.noise_callback()
    
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
                # DCT変換
                dct_result = cv2.dct(np.float32(gray_image))
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
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        print(f"🔄 画像解析パラメータリセット")
        super().reset_parameters()
        self.analysis_type = "none"
        self.show_histogram = False
        self.current_analysis_result = None
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'analysis_type': self.analysis_type,
            'show_histogram': self.show_histogram
        }