#!/usr/bin/env python3
"""
画像解析プラグイン - Image Analysis Plugin
フーリエ変換、ウェーブレット変換、特徴点検出、ヒストグラム解析などの高度な画像解析機能を提供
"""


import cv2
from packaging import version
if version.parse(cv2.__version__) < version.parse("4.8.0"):
    raise ImportError(f"OpenCVのバージョンが古いです: {cv2.__version__}。4.8.0以上をインストールしてください。")
import numpy as np
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
    """
    画像解析プラグイン (ImageAnalysisPlugin)
    --------------------------------------------------
    設計方針:
    - 外部APIはパブリックメソッド (アンダースコアなし) として公開し、外部から呼び出し可能にする。
    - 内部処理はプライベートメソッド (先頭にアンダースコア) とし、クラス内部からのみ利用する。
    - 命名規則: パブリックAPIは分かりやすい英語名、プライベートは _ で始める。
    - コールバック設定やUI生成など、外部連携はパブリックAPIで提供。
    - 画像解析処理やイベントハンドラはプライベートで隠蔽。
    - すべてのメソッド・属性に利用意図をコメント・docstringで明示。
    - セクションごとにコメントで区切り、機能追加・削除時の保守性を高める。

    推奨メソッド並び順:
    1. 初期化・基本情報
        - __init__, get_description, get_display_name, get_parameters, set_image, get_os_font
    2. コールバック設定（外部API）
        - set_display_image_callback, set_histogram_callback, set_feature_callback, set_frequency_callback, set_blur_callback, set_noise_callback, set_undo_features_callback, set_undo_frequency_callback, set_undo_blur_callback, set_undo_noise_callback, set_undo_histogram_callback
    3. UI生成・操作（外部API）
        - setup_ui, create_ui
    4. 画像解析API（外部API）
        - apply_feature_detection, analyze_noise, detect_blur, apply_frequency_analysis, process_image
    5. イベントハンドラ・内部処理（プライベート）
        - _show_histogram_analysis, _undo_histogram, _show_rgb_histogram, _undo_rgb_histogram, _apply_feature_detection, _undo_features, _apply_frequency_analysis, _undo_frequency, _analyze_noise, _undo_noise, _on_blur_button, _undo_blur, _on_sift_button, _on_orb_button, _enable_undo_button, _disable_undo_button, など
    """

    # --- 基本情報・初期化 ---

    def __init__(self, name="image_analysis"):
        super().__init__(name)
        self.image = None
        self.analysis_type = None
        self.show_histogram = False
        # コールバック属性の初期化
        self.display_image_callback = None
        self.histogram_callback = None
        self.feature_callback = None
        self.frequency_callback = None
        self.blur_callback = None
        self.noise_callback = None
        self.undo_features_callback = None
        self.undo_frequency_callback = None
        self.undo_blur_callback = None
        self.undo_noise_callback = None
        self.undo_histogram_callback = None
        self.undo_rgb_histogram_callback = None

    def _enable_undo_button(self, key):
        """指定したUndoボタンを有効化する"""
        if hasattr(self, '_buttons') and key in self._buttons:
            self._buttons[key].configure(state="normal")

    def _disable_undo_button(self, key):
        """指定したUndoボタンを無効化する"""
        if hasattr(self, '_buttons') and key in self._buttons:
            self._buttons[key].configure(state="disabled")


    def get_description(self) -> str:
        """プラグインの説明文を返す"""
        return "高度な画像解析（ヒストグラム・特徴点・周波数・ノイズ・ブラー）を提供するプラグインです。"

    def get_display_name(self) -> str:
        """プラグインの表示名を返す"""
        return "画像解析プラグイン"

    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータを取得"""
        return {
            'analysis_type': self.analysis_type,
            'show_histogram': self.show_histogram
        }

    def set_image(self, image: Image.Image):
        """解析対象画像をセット"""
        self.image = image

    def get_os_font(self, size=11):
        import platform
        os_name = platform.system()
        if os_name == "Darwin":
            return ("Hiragino Sans", size)
        elif os_name == "Windows":
            return ("Meiryo", size)
        else:
            return ("Noto Sans CJK JP", size)

    # --- ヒストグラム解析 ---
    def set_histogram_callback(self, callback):
        """ヒストグラム解析用のコールバックを設定"""
        self.histogram_callback = callback

    def _show_histogram_analysis(self):
        """ヒストグラム解析ボタン押下時の処理"""
        if self.image is not None:
            img_array = np.array(self.image)
            # グレースケール化
            if img_array.ndim == 3:
                img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img_array
            # ヒストグラム計算
            hist = cv2.calcHist([img_gray], [0], None, [256], [0,256])
            hist_img = np.full((100, 256, 3), 255, np.uint8)
            cv2.normalize(hist, hist, 0, 100, cv2.NORM_MINMAX)
            for x, y in enumerate(hist):
                cv2.line(hist_img, (x, 100), (x, 100-int(y)), (0,0,0), 1)
            result = Image.fromarray(hist_img)
            if self.display_image_callback:
                self.display_image_callback(result)
            self._enable_undo_button('undo_histogram')
        else:
            print("self.image is None, ヒストグラム解析スキップ")

    def _undo_histogram(self):
        print("[DEBUG] ヒストグラム解析取消ボタン押下")
        if self.display_image_callback and self.image is not None:
            self.display_image_callback(self.image)
        self._disable_undo_button('undo_histogram')

    def _show_rgb_histogram(self):
        """RGBヒストグラム解析ボタン押下時の処理"""
        if self.image is not None:
            img_array = np.array(self.image)
            hist_img = np.full((100, 256, 3), 255, np.uint8)
            colors = [(255,0,0), (0,255,0), (0,0,255)]
            for i, col in enumerate(colors):
                hist = cv2.calcHist([img_array], [i], None, [256], [0,256])
                cv2.normalize(hist, hist, 0, 100, cv2.NORM_MINMAX)
                for x, y in enumerate(hist):
                    cv2.line(hist_img, (x, 100), (x, 100-int(y)), col, 1)
            result = Image.fromarray(hist_img)
            if self.display_image_callback:
                self.display_image_callback(result)
            self._enable_undo_button('undo_rgb_histogram')
        else:
            print("self.image is None, RGBヒストグラム解析スキップ")

    def _undo_rgb_histogram(self):
        if MATPLOTLIB_AVAILABLE:
            import matplotlib.pyplot as plt
            plt.close("RGBヒストグラム解析")
        # コールバックが設定されていれば呼ぶ、なければ標準処理（元画像表示）
        if self.undo_rgb_histogram_callback and callable(self.undo_rgb_histogram_callback):
            self.undo_rgb_histogram_callback()
        elif self.display_image_callback and self.image is not None:
            if self.display_image_callback:
                self.display_image_callback(self.image)
        self._disable_undo_button('undo_rgb_histogram')

    # --- 周波数解析 ---
    def set_frequency_callback(self, callback):
        """周波数解析用のコールバックを設定"""
        self.frequency_callback = callback

    def apply_frequency_analysis(self, image: Image.Image, analysis_type: str) -> Image.Image:
        """
        DCT/FFT解析を実行し、結果画像を返す
        analysis_type: 'dct' or 'fft'
        """
        try:
            print(f"📈 周波数解析開始: {analysis_type}")
            img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            if analysis_type == 'dct':
                # DCT
                img_float = np.float32(img_gray) / 255.0
                dct = cv2.dct(img_float)
                dct_log = np.log(np.abs(dct) + 1e-5)
                dct_norm = cv2.normalize(dct_log, None, 0, 255, cv2.NORM_MINMAX)
                dct_img = np.uint8(dct_norm)
                result = cv2.cvtColor(dct_img, cv2.COLOR_GRAY2RGB)
                print("✅ DCT解析完了")
                return Image.fromarray(result)
            elif analysis_type == 'fft':
                # FFT
                f = np.fft.fft2(img_gray)
                fshift = np.fft.fftshift(f)
                magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-5)
                mag_norm = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
                mag_img = np.uint8(mag_norm)
                result = cv2.cvtColor(mag_img, cv2.COLOR_GRAY2RGB)
                print("✅ FFT解析完了")
                return Image.fromarray(result)
            else:
                print(f"未対応の解析種別: {analysis_type}")
                return image
        except Exception as e:
            print(f"❌ 周波数解析エラー: {e}")
            return image

    def _run_frequency_analysis(self, analysis_type):
        pass

    def _display_result_image(self, img: Image.Image):
        pass

    def _apply_frequency_analysis(self, analysis_type):
        # DCT/FFT解析ボタン押下時
        if self.image is not None:
            result_img = self.apply_frequency_analysis(self.image, analysis_type)
            if self.display_image_callback:
                self.display_image_callback(result_img)
        else:
            print("self.image is None, 処理をスキップ")
        # 解析種別ごとに取消ボタン有効化
        if analysis_type == "dct":
            self._enable_undo_button('undo_dct')
        elif analysis_type == "fft":
            self._enable_undo_button('undo_fft')

    def _undo_frequency(self, analysis_type):
        # DCT/FFT取消ボタン押下時
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        # 解析種別ごとに取消ボタン無効化
        if analysis_type == "dct":
            self._disable_undo_button('undo_dct')
        elif analysis_type == "fft":
            self._disable_undo_button('undo_fft')
        else:
            # 旧仕様の一括取消（未使用）
            self._disable_undo_button('undo_frequency')

    # --- ノイズ解析 ---
    def set_noise_callback(self, callback):
        """ノイズ解析用のコールバックを設定"""
        self.noise_callback = callback

    def analyze_noise(self, image: Image.Image) -> Image.Image:
        """ノイズ解析を実行"""
        try:
            print("📈 ノイズ解析開始")
            # グレースケールに変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            # ノイズレベルの推定（標準偏差ベース）
            noise_level = np.std(np.array(gray_image, dtype=np.float32))
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

    def _analyze_noise(self):
        print("[DEBUG] ノイズ解析ボタン押下")
        if self.image is not None:
            result_img = self.analyze_noise(self.image)
            if hasattr(self, 'display_image_callback'):
                if self.display_image_callback:
                    self.display_image_callback(result_img)
            self._enable_undo_button('undo_noise')
        else:
            print("self.image is None, 処理をスキップ")

    def _undo_noise(self):
        print("[DEBUG] ノイズ解析取消ボタン押下")
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        self._disable_undo_button('undo_noise')

    # --- ブラー解析 ---
    def set_blur_callback(self, callback):
        """ブラー検出用のコールバックを設定"""
        self.blur_callback = callback

    def detect_blur(self, image: Image.Image) -> Image.Image:
        """
        ブラー（ぼかし）解析を実行するパブリックAPI
        画像のブラー度合いを判定し、結果を画像上に描画して返す
        """
        try:
            print("📈 ブラー解析開始")
            # グレースケール変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            # ラプラシアンでブラー度判定
            laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            if laplacian_var < 50:
                blur_status = "強"
                color = (255, 0, 0)  # 赤
            elif laplacian_var < 150:
                blur_status = "中"
                color = (255, 255, 0)  # 黄
            else:
                blur_status = "弱"
                color = (0, 255, 0)  # 緑
            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result_image, f"Blur Level: {blur_status} ({laplacian_var:.1f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            print(f"✅ ブラー解析完了: レベル{blur_status} (ラプラシアン分散: {laplacian_var:.1f})")
            return final_image
        except Exception as e:
            print(f"❌ ブラー解析エラー: {e}")
            return image

    def _on_blur_button(self):
        """
        ブラー解析ボタン押下時のイベントハンドラ（内部用）
        外部API detect_blur() を呼び出し、結果画像を表示
        """
        print("[DEBUG] ブラー解析ボタン押下")
        if self.image is not None:
            result_img = self.detect_blur(self.image)
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_blur')
        else:
            print("self.image is None, 処理をスキップ")

    def _undo_blur(self):
        print("[DEBUG] ブラー解析取消ボタン押下")
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        self._disable_undo_button('undo_blur')

    # --- 特徴点検出 ---
    def set_feature_callback(self, callback):
        """特徴点検出用のコールバックを設定"""
        self.feature_callback = callback

    def apply_feature_detection(self, image: Image.Image, feature_type: str) -> Image.Image:
        """特徴点検出を適用"""
        print(f"[DEBUG] apply_feature_detection called: image={type(image)}, feature_type={feature_type}")
        print(f"🎯 特徴点検出開始: {feature_type}")
        # OpenCVフォーマットに変換
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        keypoints = []
        if feature_type == "sift":
            sift = None
            if hasattr(cv2, "SIFT_create"):
                try:
                    sift = cv2.SIFT_create()
                except Exception as e:
                    print(f"SIFT_create失敗: {e}")
            elif hasattr(cv2, "xfeatures2d") and hasattr(cv2.xfeatures2d, "SIFT_create"):
                try:
                    sift = cv2.xfeatures2d.SIFT_create()
                except Exception as e:
                    print(f"xfeatures2d.SIFT_create失敗: {e}")
            if sift:
                try:
                    keypoints = sift.detect(gray_image, None)
                except Exception as e:
                    print(f"SIFT検出エラー: {e}")
            else:
                print("SIFTが利用できません (opencv-contrib-python>=4.8.0が必要)")
        elif feature_type == "orb":
            orb = None
            if hasattr(cv2, "ORB_create"):
                try:
                    orb = cv2.ORB_create()
                except Exception as e:
                    print(f"ORB_create失敗: {e}")
            elif hasattr(cv2, "xfeatures2d") and hasattr(cv2.xfeatures2d, "ORB_create"):
                try:
                    orb = cv2.xfeatures2d.ORB_create()
                except Exception as e:
                    print(f"xfeatures2d.ORB_create失敗: {e}")
            if orb:
                try:
                    keypoints = orb.detect(gray_image, None)
                except Exception as e:
                    print(f"ORB検出エラー: {e}")
            else:
                print("ORBが利用できません (opencv-contrib-python>=4.8.0が必要)")
        print(f"[DEBUG] 検出特徴点数: {len(keypoints)}")
        if not keypoints:
            print("[WARNING] 特徴点が検出されませんでした。画像やパラメータをご確認ください。")
        # 特徴点描画（SIFTは緑、ORBは青）
        if keypoints:
            draw_color = (0, 255, 0) if feature_type == "sift" else (255, 0, 0)
            result_img = np.array(image.convert("RGB"))
            for kp in keypoints:
                if hasattr(kp, "pt") and hasattr(kp, "size"):
                    x, y = int(kp.pt[0]), int(kp.pt[1])
                    radius = int(max(10, kp.size / 2))
                    cv2.circle(result_img, (x, y), radius, draw_color, thickness=2)
            result_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result_rgb)
        else:
            print("特徴点が検出されませんでした")
            return image

    def _apply_feature_detection(self, feature_type):
        # コールバックが設定されていれば優先して呼ぶ
        if hasattr(self, "feature_callback") and callable(self.feature_callback):
            self.feature_callback(feature_type)
        else:
            # 標準処理（特徴点検出）
            if self.image is not None:
                result_img = self.apply_feature_detection(self.image, feature_type)
                if hasattr(self, 'display_image_callback'):
                    self.display_image_callback(result_img)
                self._enable_undo_button(f'undo_{feature_type}')
            else:
                print(f"画像がありません: {feature_type}")

    def _undo_features(self, feature_type):
        print(f"[DEBUG] 取消ボタン押下: {feature_type}")
        # 元画像に戻す
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        # ボタンを無効化
        if feature_type == "sift":
            self._buttons['undo_sift'].configure(state="disabled")
        elif feature_type == "orb":
            self._buttons['undo_orb'].configure(state="disabled")

    def _on_sift_button(self):
        print("[DEBUG] SIFTボタン押下")
        print(f"[DEBUG] self.image type: {type(self.image)}, is None: {self.image is None}")
        if self.image is not None:
            result_img = self.apply_feature_detection(self.image, "sift")
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_sift')
        else:
            print("[DEBUG] self.image is None, 処理をスキップ")

    def _on_orb_button(self):
        print("[DEBUG] ORBボタン押下")
        print(f"[DEBUG] self.image type: {type(self.image)}, is None: {self.image is None}")
        if self.image is not None:
            result_img = self.apply_feature_detection(self.image, "orb")
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_orb')
        else:
            print("[DEBUG] self.image is None, 処理をスキップ")

    # --- UI生成 ---
    def setup_ui(self, parent):
        """UI生成（main_plugin.pyから呼び出される）"""
        self.create_ui(parent)

    # --- Undoボタン制御 ---


    # --- 汎用API ---
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """画像解析を適用（通常の処理では使用しない）"""
        # 画像解析は特殊なボタン操作で実行されるため、通常の処理では何もしない
        return image
    def _undo_rgb_histogram(self):
        if MATPLOTLIB_AVAILABLE:
            import matplotlib.pyplot as plt
            plt.close("RGBヒストグラム解析")
        # コールバックが設定されていれば呼ぶ、なければ標準処理（元画像表示）
        if hasattr(self, "undo_rgb_histogram_callback") and callable(self.undo_rgb_histogram_callback):
            self.undo_rgb_histogram_callback()
        elif hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        self._disable_undo_button('undo_rgb_histogram')
    def _apply_feature_detection(self, feature_type):
        # コールバックが設定されていれば優先して呼ぶ
        if hasattr(self, "feature_callback") and callable(self.feature_callback):
            self.feature_callback(feature_type)
        else:
            # 標準処理（特徴点検出）
            if self.image is not None:
                result_img = self.apply_feature_detection(self.image, feature_type)
                if hasattr(self, 'display_image_callback'):
                    self.display_image_callback(result_img)
                self._enable_undo_button(f'undo_{feature_type}')
            else:
                print(f"画像がありません: {feature_type}")
    def _undo_features(self, feature_type):
        print(f"[DEBUG] 取消ボタン押下: {feature_type}")
        # 元画像に戻す
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        # ボタンを無効化
        if feature_type == "sift":
            self._buttons['undo_sift'].configure(state="disabled")
        elif feature_type == "orb":
            self._buttons['undo_orb'].configure(state="disabled")
    def _apply_frequency_analysis(self, analysis_type):
        # DCT/FFT解析ボタン押下時
        # コールバックは analysis_type のみ渡す
        if hasattr(self, "frequency_callback") and callable(self.frequency_callback):
            self.frequency_callback(analysis_type)
        else:
            print(f"周波数解析({analysis_type})を実行（仮実装）")
        # 解析種別ごとに取消ボタン有効化
        if analysis_type == "dct":
            self._enable_undo_button('undo_dct')
        elif analysis_type == "fft":
            self._enable_undo_button('undo_fft')

    def _undo_frequency(self, analysis_type):
        # DCT/FFT取消ボタン押下時
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        # 解析種別ごとに取消ボタン無効化
        if analysis_type == "dct":
            self._disable_undo_button('undo_dct')
        elif analysis_type == "fft":
            self._disable_undo_button('undo_fft')
        else:
            # 旧仕様の一括取消（未使用）
            self._disable_undo_button('undo_frequency')
    def _analyze_noise(self):
        print("[DEBUG] ノイズ解析ボタン押下")
        if self.image is not None:
            result_img = self.analyze_noise(self.image)
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_noise')
        else:
            print("self.image is None, 処理をスキップ")

    def _on_blur_button(self):
        """
        ブラー解析ボタン押下時のイベントハンドラ（内部用）
        外部API detect_blur() を呼び出し、結果画像を表示
        """
        print("[DEBUG] ブラー解析ボタン押下")
        if self.image is not None:
            result_img = self.detect_blur(self.image)
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_blur')
        else:
            print("self.image is None, 処理をスキップ")

    def detect_blur(self, image: Image.Image) -> Image.Image:
        """
        ブラー（ぼかし）解析を実行するパブリックAPI
        画像のブラー度合いを判定し、結果を画像上に描画して返す
        """
        try:
            print("📈 ブラー解析開始")
            # グレースケール変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            # ラプラシアンでブラー度判定
            laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            if laplacian_var < 50:
                blur_status = "強"
                color = (255, 0, 0)  # 赤
            elif laplacian_var < 150:
                blur_status = "中"
                color = (255, 255, 0)  # 黄
            else:
                blur_status = "弱"
                color = (0, 255, 0)  # 緑
            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result_image, f"Blur Level: {blur_status} ({laplacian_var:.1f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            print(f"✅ ブラー解析完了: レベル{blur_status} (ラプラシアン分散: {laplacian_var:.1f})")
            return final_image
        except Exception as e:
            print(f"❌ ブラー解析エラー: {e}")
            return image

    def create_ui(self, parent):
        # --- 周波数解析（DCT/FFT） ---
        ctk.CTkLabel(parent, text="周波数解析", font=self.get_os_font(11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_dct = ctk.CTkFrame(parent)
        row_dct.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['dct'] = ctk.CTkButton(row_dct, text="DCT解析", command=lambda: self._apply_frequency_analysis("dct"))
        self._buttons['dct'].pack(side="left", padx=(0, 5))
        self._buttons['undo_dct'] = ctk.CTkButton(row_dct, text="🔄 取消", command=lambda: self._undo_frequency("dct"))
        self._buttons['undo_dct'].pack(side="left", padx=(0, 5))
        self._buttons['undo_dct'].configure(state="disabled")
        row_fft = ctk.CTkFrame(parent)
        row_fft.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['fft'] = ctk.CTkButton(row_fft, text="FFT解析", command=lambda: self._apply_frequency_analysis("fft"))
        self._buttons['fft'].pack(side="left", padx=(0, 5))
        self._buttons['undo_fft'] = ctk.CTkButton(row_fft, text="🔄 取消", command=lambda: self._undo_frequency("fft"))
        self._buttons['undo_fft'].pack(side="left", padx=(0, 5))
        self._buttons['undo_fft'].configure(state="disabled")

        # --- ヒストグラム解析 ---
        ctk.CTkLabel(parent, text="ヒストグラム解析", font=self.get_os_font(11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_hist = ctk.CTkFrame(parent)
        row_hist.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['histogram'] = ctk.CTkButton(row_hist, text="ヒストグラム解析", command=self._show_histogram_analysis)
        self._buttons['histogram'].pack(side="left", padx=(0, 5))
        self._buttons['undo_histogram'] = ctk.CTkButton(row_hist, text="🔄 取消", command=self._undo_histogram)
        self._buttons['undo_histogram'].pack(side="left", padx=(0, 5))
        self._buttons['undo_histogram'].configure(state="disabled")

        # --- RGBヒストグラム解析 ---
        ctk.CTkLabel(parent, text="RGBヒストグラム解析", font=self.get_os_font(11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_rgb = ctk.CTkFrame(parent)
        row_rgb.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['rgb_histogram'] = ctk.CTkButton(row_rgb, text="RGBヒストグラム", command=self._show_rgb_histogram)
        self._buttons['rgb_histogram'].pack(side="left", padx=(0, 5))
        self._buttons['undo_rgb_histogram'] = ctk.CTkButton(row_rgb, text="🔄 取消", command=self._undo_rgb_histogram)
        self._buttons['undo_rgb_histogram'].pack(side="left", padx=(0, 5))
        self._buttons['undo_rgb_histogram'].configure(state="disabled")

        # --- ノイズ解析 ---
        ctk.CTkLabel(parent, text="ノイズ解析", font=self.get_os_font(11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_noise = ctk.CTkFrame(parent)
        row_noise.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['noise'] = ctk.CTkButton(row_noise, text="ノイズ解析", command=self._analyze_noise)
        self._buttons['noise'].pack(side="left", padx=(0, 5))
        self._buttons['undo_noise'] = ctk.CTkButton(row_noise, text="🔄 取消", command=self._undo_noise)
        self._buttons['undo_noise'].pack(side="left", padx=(0, 5))
        self._buttons['undo_noise'].configure(state="disabled")

        # --- ブラー解析 ---
        ctk.CTkLabel(parent, text="ブラー解析", font=self.get_os_font(11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_blur = ctk.CTkFrame(parent)
        row_blur.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['blur'] = ctk.CTkButton(row_blur, text="ブラー解析", command=self._on_blur_button)
        self._buttons['blur'].pack(side="left", padx=(0, 5))
        self._buttons['undo_blur'] = ctk.CTkButton(row_blur, text="🔄 取消", command=self._undo_blur)
        self._buttons['undo_blur'].pack(side="left", padx=(0, 5))
        self._buttons['undo_blur'].configure(state="disabled")

        # --- 特徴点検出 ---
        ctk.CTkLabel(parent, text="特徴点検出", font=self.get_os_font(11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_sift = ctk.CTkFrame(parent)
        row_sift.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['sift'] = ctk.CTkButton(row_sift, text="SIFT特徴点", command=lambda: self._on_sift_button())
        self._buttons['sift'].pack(side="left", padx=(0, 5))
        self._buttons['undo_sift'] = ctk.CTkButton(row_sift, text="🔄 取消", command=lambda: (print("[DEBUG] 取消SIFTクリック"), self._undo_features("sift")))
        self._buttons['undo_sift'].pack(side="left", padx=(0, 5))
        self._buttons['undo_sift'].configure(state="disabled")
        row_orb = ctk.CTkFrame(parent)
        row_orb.pack(side="top", fill="x", padx=5, pady=2)
        self._buttons['orb'] = ctk.CTkButton(row_orb, text="ORB特徴点", command=lambda: self._on_orb_button())
        self._buttons['orb'].pack(side="left", padx=(0, 5))
        self._buttons['undo_orb'] = ctk.CTkButton(row_orb, text="🔄 取消", command=lambda: (print("[DEBUG] 取消ORBクリック"), self._undo_features("orb")))
        self._buttons['undo_orb'].pack(side="left", padx=(0, 5))
        self._buttons['undo_orb'].configure(state="disabled")

    def set_display_image_callback(self, callback):
        """画像表示用コールバックを設定"""
        self.display_image_callback = callback

    def _on_sift_button(self):
        print("[DEBUG] SIFTボタン押下")
        print(f"[DEBUG] self.image type: {type(self.image)}, is None: {self.image is None}")
        if self.image is not None:
            result_img = self.apply_feature_detection(self.image, "sift")
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_sift')
        else:
            print("[DEBUG] self.image is None, 処理をスキップ")

    def _on_orb_button(self):
        print("[DEBUG] ORBボタン押下")
        print(f"[DEBUG] self.image type: {type(self.image)}, is None: {self.image is None}")
        if self.image is not None:
            result_img = self.apply_feature_detection(self.image, "orb")
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._enable_undo_button('undo_orb')
        else:
            print("[DEBUG] self.image is None, 処理をスキップ")
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
        print(f"[DEBUG] apply_feature_detection called: image={type(image)}, feature_type={feature_type}")
        print(f"🎯 特徴点検出開始: {feature_type}")
        # OpenCVフォーマットに変換
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        keypoints = []
        if feature_type == "sift":
            try:
                if hasattr(cv2, "SIFT_create"):
                    sift = cv2.SIFT_create()
                elif hasattr(cv2, "xfeatures2d") and hasattr(cv2.xfeatures2d, "SIFT_create"):
                    sift = cv2.xfeatures2d.SIFT_create()
                else:
                    print("SIFTが利用できません (opencv-contrib-python>=4.8.0が必要)")
                    return image
                keypoints = sift.detect(gray_image, None)
            except Exception as e:
                print(f"SIFT検出エラー: {e}")
                return image
        elif feature_type == "orb":
            try:
                if hasattr(cv2, "ORB_create"):
                    orb = cv2.ORB_create()
                elif hasattr(cv2, "xfeatures2d") and hasattr(cv2.xfeatures2d, "ORB_create"):
                    orb = cv2.xfeatures2d.ORB_create()
                else:
                    print("ORBが利用できません (opencv-contrib-python>=4.8.0が必要)")
                    return image
                keypoints = orb.detect(gray_image, None)
            except Exception as e:
                print(f"ORB検出エラー: {e}")
                return image
        # 特徴点数を表示
        print(f"[DEBUG] 検出特徴点数: {len(keypoints)}")
        if not keypoints:
            print("[WARNING] 特徴点が検出されませんでした。画像やパラメータをご確認ください。")
        # 特徴点描画（SIFTは緑、ORBは青）
        if keypoints:
            draw_color = (0, 255, 0) if feature_type == "sift" else (255, 0, 0)
            result_img = np.array(image.convert("RGB"))
            for kp in keypoints:
                if hasattr(kp, "pt") and hasattr(kp, "size"):
                    x, y = int(kp.pt[0]), int(kp.pt[1])
                    radius = int(max(10, kp.size / 2))
                    cv2.circle(result_img, (x, y), radius, draw_color, thickness=2)
            result_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result_rgb)
        else:
            print("特徴点が検出されませんでした")
            return image


    def analyze_noise(self, image: Image.Image) -> Image.Image:
        """ノイズ解析を実行"""
        try:
            print("📈 ノイズ解析開始")
            
            # グレースケールに変換
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # ノイズレベルの推定（標準偏差ベース）
            noise_level = np.std(np.array(gray_image, dtype=np.float32))
            
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
    def setup_ui(self, parent):
        """UI生成（main_plugin.pyから呼び出される）"""
        self.create_ui(parent)
    
    def _undo_noise(self):
        print("[DEBUG] ノイズ解析取消ボタン押下")
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        self._disable_undo_button('undo_noise')

    def _undo_blur(self):
        print("[DEBUG] ブラー解析取消ボタン押下")
        if hasattr(self, 'display_image_callback') and self.image is not None:
            self.display_image_callback(self.image)
        self._disable_undo_button('undo_blur')