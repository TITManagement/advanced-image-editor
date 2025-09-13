"""
画像処理ユーティリティ
画像変換、フォーマット処理などのヘルパー関数
"""

import cv2
import numpy as np
from PIL import Image


class ImageUtils:
    """画像処理ユーティリティクラス"""
    
    @staticmethod
    def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
        """
        PIL画像をOpenCV形式に変換
        
        Args:
            pil_image: PIL.Image.Image
        
        Returns:
            np.ndarray: OpenCV形式の画像 (BGR)
        """
        if pil_image.mode == 'RGB':
            # RGBをBGRに変換
            cv_image = np.array(pil_image)
            return cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        elif pil_image.mode == 'RGBA':
            # RGBAをBGRAに変換
            cv_image = np.array(pil_image)
            return cv2.cvtColor(cv_image, cv2.COLOR_RGBA2BGRA)
        else:
            # その他の形式はRGBに変換してからBGRに
            rgb_image = pil_image.convert('RGB')
            cv_image = np.array(rgb_image)
            return cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def cv2_to_pil(cv_image: np.ndarray) -> Image.Image:
        """
        OpenCV画像をPIL形式に変換
        
        Args:
            cv_image: OpenCV形式の画像 (BGR)
        
        Returns:
            PIL.Image.Image: PIL形式の画像
        """
        # BGRをRGBに変換
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    @staticmethod
    def ensure_rgb(image: Image.Image) -> Image.Image:
        """
        画像をRGB形式に変換（必要な場合）
        
        Args:
            image: PIL.Image.Image
        
        Returns:
            PIL.Image.Image: RGB形式の画像
        """
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image
    
    @staticmethod
    def resize_with_aspect_ratio(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """
        アスペクト比を保持してリサイズ
        
        Args:
            image: PIL.Image.Image
            max_width: 最大幅
            max_height: 最大高さ
        
        Returns:
            PIL.Image.Image: リサイズされた画像
        """
        width, height = image.size
        ratio = min(max_width / width, max_height / height)
        
        if ratio < 1:  # 縮小が必要な場合のみ
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def apply_brightness(image: Image.Image, brightness: int) -> Image.Image:
        """
        明度調整を適用
        
        Args:
            image: PIL.Image.Image
            brightness: 明度調整値 (-100 〜 +100)
        
        Returns:
            PIL.Image.Image: 明度調整された画像
        """
        if brightness == 0:
            return image
        
        cv_image = ImageUtils.pil_to_cv2(image)
        
        # 明度調整（HSVで実行）
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 明度チャンネルを調整
        brightness_factor = 1.0 + (brightness / 100.0)
        v = cv2.multiply(v, brightness_factor)
        v = np.clip(v, 0, 255).astype(np.uint8)
        
        hsv = cv2.merge([h, s, v])
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return ImageUtils.cv2_to_pil(adjusted)
    
    @staticmethod
    def apply_contrast(image: Image.Image, contrast: int) -> Image.Image:
        """
        コントラスト調整を適用
        
        Args:
            image: PIL.Image.Image
            contrast: コントラスト調整値 (-100 〜 +100)
        
        Returns:
            PIL.Image.Image: コントラスト調整された画像
        """
        if contrast == 0:
            return image
        
        cv_image = ImageUtils.pil_to_cv2(image)
        
        # コントラスト調整
        contrast_factor = 1.0 + (contrast / 100.0)
        adjusted = cv2.convertScaleAbs(cv_image, alpha=contrast_factor, beta=0)
        
        return ImageUtils.cv2_to_pil(adjusted)
    
    @staticmethod
    def apply_saturation(image: Image.Image, saturation: int) -> Image.Image:
        """
        彩度調整を適用
        
        Args:
            image: PIL.Image.Image
            saturation: 彩度調整値 (-100 〜 +100)
        
        Returns:
            PIL.Image.Image: 彩度調整された画像
        """
        if saturation == 0:
            return image
        
        cv_image = ImageUtils.pil_to_cv2(image)
        
        # 彩度調整（HSVで実行）
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 彩度チャンネルを調整
        saturation_factor = 1.0 + (saturation / 100.0)
        s = cv2.multiply(s, saturation_factor)
        s = np.clip(s, 0, 255).astype(np.uint8)
        
        hsv = cv2.merge([h, s, v])
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return ImageUtils.cv2_to_pil(adjusted)
    
    @staticmethod
    def apply_gamma_correction(image: Image.Image, gamma: float) -> Image.Image:
        """
        ガンマ補正を適用
        
        Args:
            image: PIL.Image.Image
            gamma: ガンマ値 (0.1 〜 3.0)
        
        Returns:
            PIL.Image.Image: ガンマ補正された画像
        """
        if gamma == 1.0:
            return image
        
        cv_image = ImageUtils.pil_to_cv2(image)
        
        # ガンマ補正テーブル作成
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        
        # ガンマ補正適用
        adjusted = cv2.LUT(cv_image, table)
        
        return ImageUtils.cv2_to_pil(adjusted)
    
    @staticmethod
    def apply_histogram_equalization(image: Image.Image) -> Image.Image:
        """
        ヒストグラム均等化を適用
        
        Args:
            image: PIL.Image.Image
        
        Returns:
            PIL.Image.Image: ヒストグラム均等化された画像
        """
        cv_image = ImageUtils.pil_to_cv2(image)
        
        # YUVに変換してY成分にヒストグラム均等化を適用
        yuv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2YUV)
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        adjusted = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        
        return ImageUtils.cv2_to_pil(adjusted)
    
    @staticmethod
    def apply_gaussian_blur(image: Image.Image, blur_strength: int) -> Image.Image:
        """
        ガウシアンブラーを適用
        
        Args:
            image: PIL.Image.Image
            blur_strength: ブラー強度 (0 〜 20)
        
        Returns:
            PIL.Image.Image: ブラーが適用された画像
        """
        if blur_strength == 0:
            return image
        
        cv_image = ImageUtils.pil_to_cv2(image)
        
        # カーネルサイズは奇数である必要がある
        kernel_size = blur_strength * 2 + 1
        blurred = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
        
        return ImageUtils.cv2_to_pil(blurred)
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """
        画像の基本情報を取得
        
        Args:
            image: PIL.Image.Image
        
        Returns:
            dict: 画像情報辞書
        """
        if not image:
            return {}
        
        return {
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'size_mb': (image.width * image.height * len(image.getbands())) / (1024 * 1024)
        }