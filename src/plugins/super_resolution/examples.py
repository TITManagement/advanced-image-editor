#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super Resolution Usage Examples
使用例集
"""

import sys
import os
import cv2
import numpy as np

# モジュールのインポート
from super_resolution_standalone import SuperResolution, create_super_resolution


def example_basic_usage():
    """基本的な使用方法"""
    print("=== 基本的な使用方法 ===")
    
    # モデルパス（実際のパスに変更してください）
    model_path = "model_srresnet.pth"
    
    try:
        # SuperResolution初期化
        sr = SuperResolution()
        sr.load_model(model_path)
        
        # 画像読み込み
        input_image = cv2.imread("input.jpg")
        if input_image is None:
            print("画像ファイルが見つかりません: input.jpg")
            return
        
        # 超解像度処理
        enhanced = sr.enhance_image(input_image, scale=2.0)
        
        # 保存
        cv2.imwrite("output_basic.jpg", enhanced)
        print("処理完了: output_basic.jpg")
        
    except Exception as e:
        print(f"エラー: {e}")


def example_file_processing():
    """ファイル処理の例"""
    print("=== ファイル処理の例 ===")
    
    model_path = "model_srresnet.pth"
    
    try:
        # モデル付きで初期化
        sr = create_super_resolution(model_path)
        
        # ファイル処理
        sr.enhance_file(
            "input.jpg", 
            "output_file.jpg", 
            scale=3.0
        )
        print("ファイル処理完了: output_file.jpg")
        
    except Exception as e:
        print(f"エラー: {e}")


def example_batch_processing():
    """バッチ処理の例"""
    print("=== バッチ処理の例 ===")
    
    model_path = "model_srresnet.pth"
    input_dir = "input_images"
    output_dir = "output_images"
    
    try:
        # 出力ディレクトリ作成
        os.makedirs(output_dir, exist_ok=True)
        
        # SuperResolution初期化
        sr = create_super_resolution(model_path)
        
        # 入力ディレクトリの画像を処理
        if not os.path.exists(input_dir):
            print(f"入力ディレクトリが見つかりません: {input_dir}")
            return
            
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f"enhanced_{filename}")
                
                print(f"処理中: {filename}")
                sr.enhance_file(input_path, output_path, scale=2.0)
                
        print("バッチ処理完了")
        
    except Exception as e:
        print(f"エラー: {e}")


def example_memory_efficient():
    """メモリ効率的な処理の例"""
    print("=== メモリ効率的な処理の例 ===")
    
    model_path = "model_srresnet.pth"
    
    try:
        # CPU使用（メモリ節約）
        sr = SuperResolution(device="cpu")
        sr.load_model(model_path)
        
        # 大きな画像の処理
        image = cv2.imread("large_image.jpg")
        if image is None:
            print("大きな画像ファイルが見つかりません")
            return
            
        # 小さなパッチサイズでメモリ使用量を抑制
        enhanced = sr.enhance_image(
            image, 
            scale=2.0,
            use_patches=True,
            patch_size=200  # 小さなパッチサイズ
        )
        
        cv2.imwrite("output_memory_efficient.jpg", enhanced)
        print("メモリ効率処理完了")
        
    except Exception as e:
        print(f"エラー: {e}")


def example_high_performance():
    """高性能処理の例"""
    print("=== 高性能処理の例 ===")
    
    model_path = "model_srresnet.pth"
    
    try:
        # GPU使用（高速処理）
        sr = SuperResolution(device="cuda")
        sr.load_model(model_path)
        
        print(f"使用デバイス: {sr.device}")
        
        # 小さな画像は一括処理
        image = cv2.imread("small_image.jpg")
        if image is None:
            print("小さな画像ファイルが見つかりません")
            return
            
        enhanced = sr.enhance_image(
            image, 
            scale=4.0,          # 最大倍率
            use_patches=False   # 一括処理
        )
        
        cv2.imwrite("output_high_performance.jpg", enhanced)
        print("高性能処理完了")
        
    except Exception as e:
        print(f"エラー: {e}")


def example_custom_processing():
    """カスタム処理の例"""
    print("=== カスタム処理の例 ===")
    
    model_path = "model_srresnet.pth"
    
    try:
        sr = SuperResolution()
        sr.load_model(model_path)
        
        # 画像読み込み
        image = cv2.imread("input.jpg")
        if image is None:
            print("画像ファイルが見つかりません")
            return
        
        # 前処理：リサイズ
        height, width = image.shape[:2]
        if width > 1000:
            scale_factor = 1000 / width
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = cv2.resize(image, (new_width, new_height))
            print(f"入力画像リサイズ: {width}x{height} → {new_width}x{new_height}")
        
        # 超解像度処理
        enhanced = sr.enhance_image(image, scale=2.5)
        
        # 後処理：シャープネス調整
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel * 0.1)
        
        # 保存
        cv2.imwrite("output_custom.jpg", sharpened)
        print("カスタム処理完了")
        
    except Exception as e:
        print(f"エラー: {e}")


def example_comparison():
    """処理前後の比較"""
    print("=== 処理前後の比較 ===")
    
    model_path = "model_srresnet.pth"
    
    try:
        sr = create_super_resolution(model_path)
        
        # 元画像
        original = cv2.imread("input.jpg")
        if original is None:
            print("画像ファイルが見つかりません")
            return
        
        # 通常のリサイズ（比較用）
        height, width = original.shape[:2]
        bicubic = cv2.resize(original, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
        
        # 超解像度処理
        enhanced = sr.enhance_image(original, scale=2.0)
        
        # 比較画像作成（横並び）
        comparison = np.hstack([
            cv2.resize(original, (width*2, height*2)),  # 元画像（拡大）
            bicubic,                                    # バイキューブ補間
            enhanced                                    # 超解像度
        ])
        
        # ラベル追加
        cv2.putText(comparison, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.putText(comparison, "Bicubic", (width*2+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.putText(comparison, "Super Resolution", (width*4+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        cv2.imwrite("comparison.jpg", comparison)
        print("比較画像作成完了: comparison.jpg")
        
    except Exception as e:
        print(f"エラー: {e}")


def main():
    """使用例の実行"""
    print("Super Resolution Standalone - 使用例集")
    print("=" * 50)
    
    # 使用可能な例
    examples = {
        "1": ("基本的な使用方法", example_basic_usage),
        "2": ("ファイル処理", example_file_processing),
        "3": ("バッチ処理", example_batch_processing),
        "4": ("メモリ効率処理", example_memory_efficient),
        "5": ("高性能処理", example_high_performance),
        "6": ("カスタム処理", example_custom_processing),
        "7": ("処理前後の比較", example_comparison),
    }
    
    # メニュー表示
    print("実行する例を選択してください:")
    for key, (desc, _) in examples.items():
        print(f"{key}: {desc}")
    print("0: 全て実行")
    print("q: 終了")
    
    choice = input("\n選択: ").strip()
    
    if choice == "q":
        return
    elif choice == "0":
        # 全て実行
        for key, (desc, func) in examples.items():
            print(f"\n{desc}を実行中...")
            func()
    elif choice in examples:
        # 選択された例を実行
        desc, func = examples[choice]
        print(f"\n{desc}を実行中...")
        func()
    else:
        print("無効な選択です")


if __name__ == "__main__":
    main()