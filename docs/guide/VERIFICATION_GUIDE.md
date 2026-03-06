# 🔍 検証ガイド（現行実装対応）

| 項目 | 内容 |
| --- | --- |
| 文書ID | `LAB-AUTOMATION-MODULE-ADVANCED-IMAGE-EDITOR-DOCS-GUIDE-VERIFICATION-GUIDE` |
| 作成日 | `2026-03-01` |
| 作成者 | `Takaya Inoue` |
| 最終更新日 | `2026-03-01` |
| 最終更新者 | `Takaya Inoue (with Codex)` |
| 版数 | `v1.0` |
| 状態 | `運用中` |


このドキュメントは、現在の `advanced-image-editor` 実装に合わせた検証手順です。  
対象は **GUI/プラグイン中心** で、`contracts/` や `data/db/` など未実装モジュールは扱いません。

## 0. 前提

- 実行場所: `lab_automation_module/advanced-image-editor`
- Python: 3.9 以上
- 仮想環境: `.venv_aid`（本リポジトリ運用）

```bash
cd /Users/tinoue/Development.local/app/AiLab/lab_automation_module/advanced-image-editor
source .venv_aid/bin/activate
python --version
```

依存の再導入が必要な場合:

```bash
python -m pip install -e .
```

## 1. クイック検証（1-2分）

### 1-1. 主要ライブラリ import

```bash
python -c "import customtkinter, cv2, numpy, PIL, matplotlib, torch, torchvision; print('✅ 主要ライブラリ正常')"
```

### 1-2. アプリ起動オプション確認（GUI非起動）

```bash
python src/advanced_image_editor.py --help
```

### 1-3. プラグイン自動検出確認

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

from core.plugin_base import PluginManager

manager = PluginManager()
discovered = manager.discover_plugins()
plugins = manager.get_all_plugins()

print(f"✅ discover_plugins: {len(discovered)}件 -> {discovered}")
print(f"✅ get_all_plugins: {len(plugins)}件")
for p in plugins:
    print(f" - {p.name}: {p.get_display_name()}")
PY
```

期待値（目安）:
- `basic_adjustment`
- `density_adjustment`
- `filter_processing`
- `image_analysis`

## 2. 非GUIスモークテスト（プラグイン処理）

`PIL.Image` をメモリ上で生成し、主要APIがエラーなく動くことを確認します。

```bash
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

import numpy as np
from PIL import Image

from plugins.basic.basic_plugin import BasicAdjustmentPlugin
from plugins.density.density_plugin import DensityAdjustmentPlugin
from plugins.filters.filters_plugin import FilterProcessingPlugin
from plugins.analysis.analysis_plugin import ImageAnalysisPlugin

img = Image.fromarray(np.full((128, 128, 3), 127, dtype=np.uint8))

basic = BasicAdjustmentPlugin()
out_basic = basic.process_image(img)
print(f"✅ basic.process_image: {out_basic.size}")

density = DensityAdjustmentPlugin()
out_density = density.process_image(img)
out_bin = density.apply_binary_threshold(img)
print(f"✅ density.process_image: {out_density.size}")
print(f"✅ density.apply_binary_threshold: {out_bin.size}")

filt = FilterProcessingPlugin()
out_filter = filt.process_image(img)
print(f"✅ filters.process_image: {out_filter.size}")

analysis = ImageAnalysisPlugin()
out_analysis = analysis.process_image(img)
print(f"✅ analysis.process_image: {out_analysis.size}")
PY
```

## 3. GUI手動検証（重要）

## 3-1. 起動

```bash
python src/advanced_image_editor.py --debug
```

確認ポイント:
- 起動時にクラッシュしない
- 4タブ（基本調整 / 濃度調整 / フィルター処理 / 画像解析）が表示される
- 画像読み込み後にプレビュー更新が機能する

## 3-2. 基本調整タブ

1. 明度・コントラスト・彩度スライダーを操作
2. 画像がリアルタイムで変化することを確認
3. リセットで元に戻ることを確認

## 3-3. 濃度調整タブ（今回の重点）

1. `2値化実行` を押す  
2. `2値化調整` スライダーを動かす  
3. 閾値変更に応じて二値画像が更新されることを確認  
4. `取消` で2値化前画像に戻ることを確認  
5. `全リセット` 後、2値化取消ボタンが無効化されることを確認

## 3-4. フィルター処理タブ

1. ブラー/シャープのスライダー操作で変化すること
2. 特殊フィルター（例: エンボス、エッジ）が適用できること
3. 取消ボタンが有効/無効を正しく遷移すること

## 3-5. 画像解析タブ

1. ヒストグラム表示が実行できること
2. SIFT/ORB等の解析ボタンがエラーなく応答すること
3. 取消系ボタンで元画像へ戻せること

## 4. 回帰チェック（最低限）

ドキュメント更新やコード変更後は、最低限以下を再実行:

```bash
python src/advanced_image_editor.py --help
python - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))
from core.plugin_base import PluginManager
m = PluginManager()
print("plugins:", m.discover_plugins())
PY
```

## 5. よくある問題

1. `ModuleNotFoundError`
- 仮想環境が未有効化の可能性
- `source .venv_aid/bin/activate`
- `python -m pip install -e .`

2. `tkinter` / GUI起動エラー
- macOS/Linux の Python ビルドに Tk が不足している可能性
- 別Python（pyenv等）や OS パッケージで Tk 対応版を利用

3. OpenCV関連エラー
- `opencv-python` / `opencv-contrib-python` の不整合
- `pyproject.toml` に合わせて再インストール

## 6. 補足

- 旧手順で使っていた `src/main_plugin.py`、`contracts.*`、`data.db.*` は現行構成では対象外です。
- `scripts/comprehensive_verification.py` には旧前提の記述が残るため、利用前に現行構成へ更新してください。
