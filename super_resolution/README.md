# Super Resolution Standalone Module

独立したSuperResolution処理モジュールです。GIMP依存なしで任意のPythonプロジェクトで使用できます。

## 機能

- SRResNetモデルによる画像超解像度処理
- GPU/CPU自動選択または手動指定
- パッチベース処理（メモリ効率化）
- 1.0〜4.0倍のスケール調整
- ファイル入出力対応
- コマンドライン実行対応

## 必要な環境

- Python 3.7+
- PyTorch
- OpenCV (cv2)
- NumPy
- PIL/Pillow

## インストール

```bash
pip install torch torchvision opencv-python numpy pillow
```

## 使用方法

### 1. 基本的な使用

```python
from super_resolution_standalone import SuperResolution

# 初期化
sr = SuperResolution()

# モデル読み込み
sr.load_model("path/to/model_srresnet.pth")

# 画像処理
import cv2
image = cv2.imread("input.jpg")
enhanced = sr.enhance_image(image, scale=2.0)
cv2.imwrite("output.jpg", enhanced)
```

### 2. ファイル処理

```python
from super_resolution_standalone import create_super_resolution

# モデル付きで初期化
sr = create_super_resolution("path/to/model_srresnet.pth")

# ファイル処理
sr.enhance_file("input.jpg", "output.jpg", scale=2.0)
```

### 3. コマンドライン使用

```bash
python super_resolution_standalone.py input.jpg output.jpg --model model_srresnet.pth --scale 2.0
```

#### コマンドラインオプション

- `--model`: 学習済みモデルファイル (.pth) **必須**
- `--scale`: 拡大倍率 (1.0-4.0) デフォルト: 2.0  
- `--device`: 使用デバイス (cuda/cpu) デフォルト: 自動選択
- `--no-patches`: パッチ処理を無効化
- `--patch-size`: パッチサイズ デフォルト: 300

### 4. 詳細設定

```python
sr = SuperResolution(device="cuda")  # GPU強制使用
sr.load_model("model.pth")

# 大きな画像はパッチ処理推奨
enhanced = sr.enhance_image(
    image, 
    scale=3.0,           # 3倍拡大
    use_patches=True,    # パッチ処理有効
    patch_size=512       # 512x512パッチ
)
```

## API リファレンス

### SuperResolution クラス

#### `__init__(model_path=None, device=None)`
- `model_path`: モデルファイルパス
- `device`: 使用デバイス ("cuda", "cpu", None=自動)

#### `load_model(model_path=None)`
モデルを読み込み

#### `enhance_image(image, scale=2.0, use_patches=True, patch_size=300)`
画像の超解像度処理
- `image`: 入力画像 (H,W,C) BGR形式のnumpy配列
- `scale`: 拡大倍率 (1.0-4.0)
- `use_patches`: パッチベース処理の使用
- `patch_size`: パッチサイズ

#### `enhance_file(input_path, output_path, scale=2.0, use_patches=True, patch_size=300)`
ファイルから画像を処理

### 便利関数

#### `create_super_resolution(model_path, device=None)`
モデル読み込み済みのインスタンスを作成

## パフォーマンス調整

### メモリ使用量を抑える
```python
# 小さなパッチサイズ
enhanced = sr.enhance_image(image, patch_size=200, use_patches=True)
```

### 処理速度を上げる
```python
# GPU使用 + パッチ処理なし（小さな画像の場合）
sr = SuperResolution(device="cuda")
enhanced = sr.enhance_image(image, use_patches=False)
```

## 注意事項

1. **モデルファイル**: 元のGIMP-MLの `model_srresnet.pth` が必要
2. **メモリ**: 大きな画像はパッチ処理を使用してください
3. **GPU**: CUDA対応GPUがある場合は自動で使用されます
4. **画像形式**: OpenCV読み込み可能な形式（JPEG, PNG等）

## トラブルシューティング

### OutOfMemoryError
```python
# パッチサイズを小さくする
sr.enhance_image(image, patch_size=100, use_patches=True)
```

### 処理が遅い
```python
# GPU使用を確認
sr = SuperResolution(device="cuda")
print(f"Using device: {sr.device}")
```

### モデル読み込みエラー
```python
# パスを確認
import os
print(os.path.exists("model_srresnet.pth"))
```

## 元のGIMPプラグインとの違い

| 項目 | GIMP版 | Standalone版 |
|------|--------|-------------|
| GIMP依存 | あり | なし |
| ファイルI/O | pickle経由 | 直接処理 |
| UI | GTK | プログラム/CLI |
| エラー処理 | ログファイル | 例外 |
| インポート | GIMP環境 | 標準Python |

## ライセンス

元のGIMP-MLプラグインと同じMITライセンス