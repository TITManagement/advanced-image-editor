#!/usr/bin/env bash
set -euo pipefail

INTERNAL_PYPI="/Users/tinoue/Development.local/internal-PyPI"

echo "[1/4] ビルド中..."
python -m build

echo "[2/4] 共通ディレクトリを確認中: $INTERNAL_PYPI"
mkdir -p "$INTERNAL_PYPI"

echo "[3/4] dist/.whl をコピー中..."
# wheelファイル名を変更せず、そのままコピー
for whl in dist/*.whl; do
    cp "$whl" "$INTERNAL_PYPI/"
done

echo "[4/4] 依存を取得して共通ディレクトリへ追加中..."
pip download . --only-binary :all: -d "$INTERNAL_PYPI"

echo "✅ 完了: $INTERNAL_PYPI に最新版を集約しました。"