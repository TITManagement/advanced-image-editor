#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Super Resolution Module
汎用超解像度処理モジュール - GIMP依存なし

This module provides super-resolution functionality that can be used
in any Python project without GIMP dependencies.
"""

import os
import sys
import warnings
import traceback
from pathlib import Path
from typing import Optional, Union, Tuple

import torch
from torch.autograd import Variable
import numpy as np
import cv2
from PIL import Image

warnings.filterwarnings("ignore")


class SuperResolution:
    """
    汎用超解像度処理クラス
    
    SRResNetモデルを使用して画像の超解像度処理を行います。
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        初期化
        
        Args:
            model_path: 学習済みモデルのパス (.pth ファイル)
            device: 使用デバイス ('cuda', 'cpu', None=自動選択)
        """
        self.model_path = model_path
        self.device = self._setup_device(device)
        self.model = None
        
    def _setup_device(self, device: Optional[str]) -> str:
        """デバイス設定"""
        if device is None:
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
        
    def load_model(self, model_path: Optional[str] = None) -> None:
        """
        モデルを読み込み
        
        Args:
            model_path: モデルファイルのパス
        """
        if model_path:
            self.model_path = model_path
            
        if not self.model_path or not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
        try:
            if self.device == "cuda":
                checkpoint = torch.load(self.model_path)
            else:
                checkpoint = torch.load(self.model_path, map_location=torch.device("cpu"))
                
            self.model = checkpoint["model"]
            
            if self.device == "cuda":
                self.model = self.model.cuda()
            else:
                self.model = self.model.cpu()
                
            self.model.eval()  # 評価モード
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """
        画像前処理
        
        Args:
            image: 入力画像 (H, W, C) BGR形式
            
        Returns:
            前処理済みテンソル
        """
        # BGR → RGB 変換
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        # float32に変換し正規化
        image = image.astype(np.float32) / 255.0
        
        # チャンネル順序変更: HWC → CHW
        image = image.transpose(2, 0, 1)
        
        # バッチ次元追加: CHW → BCHW
        image = image.reshape(1, image.shape[0], image.shape[1], image.shape[2])
        
        # PyTorchテンソルに変換
        tensor = torch.from_numpy(image).float()
        
        if self.device == "cuda":
            tensor = tensor.cuda()
            
        return Variable(tensor)
    
    def postprocess_image(self, tensor: torch.Tensor, target_scale: float = 4.0) -> np.ndarray:
        """
        画像後処理
        
        Args:
            tensor: モデル出力テンソル
            target_scale: 目標スケール倍率
            
        Returns:
            処理済み画像 (H, W, C) BGR形式
        """
        # CPU に移動
        output = tensor.cpu().data[0].numpy()
        
        # 正規化を戻す
        output = output * 255.0
        output = np.clip(output, 0.0, 255.0)
        
        # チャンネル順序変更: CHW → HWC
        output = output.transpose(1, 2, 0).astype(np.uint8)
        
        # スケール調整 (モデルは4倍固定のため)
        if target_scale != 4.0:
            scale_factor = target_scale / 4.0
            new_size = (int(output.shape[1] * scale_factor), 
                       int(output.shape[0] * scale_factor))
            output = cv2.resize(output, new_size, interpolation=cv2.INTER_CUBIC)
        
        # RGB → BGR 変換
        if len(output.shape) == 3 and output.shape[2] == 3:
            output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
            
        return output
    
    def enhance_image(self, 
                     image: np.ndarray, 
                     scale: float = 2.0,
                     use_patches: bool = True,
                     patch_size: int = 300) -> np.ndarray:
        """
        画像の超解像度処理
        
        Args:
            image: 入力画像 (H, W, C) BGR形式
            scale: 拡大倍率 (1.0 - 4.0)
            use_patches: パッチベース処理を使用するか
            patch_size: パッチサイズ（use_patches=Trueの場合）
            
        Returns:
            超解像度処理後の画像 (H, W, C) BGR形式
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        h, w = image.shape[:2]
        
        # 前処理
        input_tensor = self.preprocess_image(image)
        
        try:
            if use_patches and (w > patch_size or h > patch_size):
                # パッチベース処理
                output = self._process_with_patches(input_tensor, patch_size)
            else:
                # 全体処理
                with torch.no_grad():
                    output = self.model(input_tensor)
            
            # 後処理
            result = self.postprocess_image(output, scale)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Enhancement failed: {e}")
    
    def _process_with_patches(self, input_tensor: torch.Tensor, patch_size: int) -> torch.Tensor:
        """
        パッチベース処理
        
        Args:
            input_tensor: 入力テンソル (B, C, H, W)
            patch_size: パッチサイズ
            
        Returns:
            出力テンソル
        """
        _, _, h, w = input_tensor.shape
        
        # 出力画像の初期化 (4倍サイズ)
        output_h, output_w = h * 4, w * 4
        output = torch.zeros(1, 3, output_h, output_w, dtype=input_tensor.dtype, device=input_tensor.device)
        
        # パッチごとに処理
        for i in range(0, h, patch_size):
            i_end = min(i + patch_size, h)
            for j in range(0, w, patch_size):
                j_end = min(j + patch_size, w)
                
                # パッチ抽出
                patch = input_tensor[:, :, i:i_end, j:j_end]
                
                # 推論
                with torch.no_grad():
                    patch_output = self.model(patch)
                
                # 結果を出力画像に配置
                output[:, :, i*4:i_end*4, j*4:j_end*4] = patch_output
        
        return output
    
    def enhance_file(self,
                    input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    scale: float = 2.0,
                    use_patches: bool = True,
                    patch_size: int = 300) -> None:
        """
        ファイルから画像を読み込んで超解像度処理し保存
        
        Args:
            input_path: 入力画像パス
            output_path: 出力画像パス
            scale: 拡大倍率
            use_patches: パッチベース処理を使用するか
            patch_size: パッチサイズ
        """
        # 画像読み込み
        image = cv2.imread(str(input_path))
        if image is None:
            raise FileNotFoundError(f"Could not load image: {input_path}")
        
        # 超解像度処理
        enhanced = self.enhance_image(image, scale, use_patches, patch_size)
        
        # 保存
        success = cv2.imwrite(str(output_path), enhanced)
        if not success:
            raise RuntimeError(f"Failed to save image: {output_path}")


def create_super_resolution(model_path: str, device: Optional[str] = None) -> SuperResolution:
    """
    SuperResolutionインスタンスを作成し、モデルを読み込む
    
    Args:
        model_path: 学習済みモデルのパス
        device: 使用デバイス
        
    Returns:
        初期化済みのSuperResolutionインスタンス
    """
    sr = SuperResolution(model_path, device)
    sr.load_model()
    return sr


if __name__ == "__main__":
    # 使用例
    import argparse
    
    parser = argparse.ArgumentParser(description="Super Resolution Image Enhancement")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--model", required=True, help="Model file path (.pth)")
    parser.add_argument("--scale", type=float, default=2.0, help="Scale factor (1.0-4.0)")
    parser.add_argument("--device", choices=["cuda", "cpu"], help="Device to use")
    parser.add_argument("--no-patches", action="store_true", help="Disable patch-based processing")
    parser.add_argument("--patch-size", type=int, default=300, help="Patch size for processing")
    
    args = parser.parse_args()
    
    try:
        # SuperResolution初期化
        sr = create_super_resolution(args.model, args.device)
        
        # 処理実行
        sr.enhance_file(
            args.input, 
            args.output, 
            scale=args.scale,
            use_patches=not args.no_patches,
            patch_size=args.patch_size
        )
        
        print(f"Enhancement completed: {args.input} → {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)