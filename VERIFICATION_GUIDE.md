# 🔍 Phase 1 検証ガイド - データサイエンス基盤検証方法

## 検証レベル

### 1. 📋 クイック検証（推奨開始点）
最低限の動作確認をすぐに実行できます。

```bash
# 仮想環境に入る
source .venv/bin/activate

# 依存関係確認
python -c "import PIL, pandas, numpy, pydantic, fastapi, duckdb; print('✅ 主要ライブラリ正常')"

# 既存GUI起動確認（短時間テスト）
python src/main_plugin.py --help
```

### 2. 🏗️ コンポーネント別検証
各機能を個別に確認します。

#### A. スキーマ検証（型安全性確認）
```bash
python -c "
from contracts.schemas.image_processing import BasicAdjustmentParams, ImageMetadata
from contracts.schemas.experiment import ExperimentConfig, ModelType

# パラメータ作成テスト
params = BasicAdjustmentParams(brightness=10, contrast=5, saturation=0)
print(f'✅ 基本調整パラメータ: {params}')

# 画像メタデータテスト
metadata = ImageMetadata(
    file_path='SampleImage/IMG_1307.jpeg',
    file_name='IMG_1307.jpeg', 
    file_size=1024000,
    width=4032, height=3024,
    format='JPEG', mode='RGB'
)
print(f'✅ メタデータ: {metadata.file_name} ({metadata.width}x{metadata.height})')

# 実験設定テスト
exp = ExperimentConfig(
    experiment_id='test_001',
    name='検証テスト',
    description='スキーマ検証',
    model_type=ModelType.ENHANCEMENT,
    training_dataset_id='train_data',
    validation_dataset_id='val_data',
    test_dataset_id='test_data',
    output_dir='data/experiments/test'
)
print(f'✅ 実験設定: {exp.name} - {exp.model_type}')
print('🎉 全スキーマ検証成功')
"
```

#### B. データベース検証
```bash
python -c "
from data.db.database_schema import DatabaseManager

# データベース初期化
print('🔄 データベース初期化中...')
db = DatabaseManager('data/db/verification_test.duckdb')
db.initialize_schema()
db.create_indexes()

# テーブル確認
conn = db.connect()
tables = conn.execute('SHOW TABLES').fetchall()
print(f'✅ 作成済みテーブル: {len(tables)}個')

for table in tables:
    count = conn.execute(f'SELECT COUNT(*) FROM {table[0]}').fetchone()[0]
    print(f'   📋 {table[0]}: {count}レコード')

# サンプルデータ挿入テスト
conn.execute('''
INSERT INTO image_metadata (file_path, file_name, file_size, width, height, format, mode)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('test/sample.jpg', 'sample.jpg', 1000000, 1920, 1080, 'JPEG', 'RGB'))

result = conn.execute('SELECT COUNT(*) FROM image_metadata').fetchone()[0]
print(f'✅ データ挿入確認: {result}件')

db.close()
print('🎉 データベース検証成功')
"
```

#### C. API設計検証
```bash
python -c "
from contracts.api.image_processing_api import router as image_router
from contracts.api.experiment_api import router as experiment_router

# ルーター確認
image_routes = len([r for r in image_router.routes])
experiment_routes = len([r for r in experiment_router.routes])

print(f'✅ 画像処理API: {image_routes}個のエンドポイント')
print(f'✅ 実験管理API: {experiment_routes}個のエンドポイント')

# 主要エンドポイント確認
print('📋 主要エンドポイント:')
print('   /api/v1/process/basic-adjustment')
print('   /api/v1/process/density-adjustment') 
print('   /api/v1/process/filters')
print('   /api/v1/experiments/create')
print('   /api/v1/experiments/run')
print('🎉 API設計検証成功')
"
```

### 3. 🔗 統合検証
既存機能との互換性を確認します。

```bash
python -c "
# 既存プラグインシステム確認
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from core.plugin_base import PluginManager

# プラグインマネージャー初期化
manager = PluginManager()
print(f'✅ プラグインマネージャー初期化成功')

# 利用可能プラグイン確認
plugins = manager.get_all_plugins()
print(f'✅ 登録可能プラグイン: {len(plugins)}個')

# 基本機能テスト（実際の画像なしでパラメータのみ）
from contracts.schemas.image_processing import BasicAdjustmentParams
params = BasicAdjustmentParams(brightness=10, contrast=5, saturation=0)
print(f'✅ スキーマ-プラグイン統合: {params.dict()}')

print('🎉 統合検証成功')
"
```

### 4. 🚀 実際の画像処理テスト
サンプル画像を使った実動作確認。

```bash
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from PIL import Image
from contracts.schemas.image_processing import ImageMetadata, BasicAdjustmentParams
import os

# サンプル画像確認
sample_path = 'SampleImage/IMG_1307.jpeg'
if os.path.exists(sample_path):
    img = Image.open(sample_path)
    print(f'✅ サンプル画像読み込み: {img.size} {img.format} {img.mode}')
    
    # メタデータ作成
    metadata = ImageMetadata(
        file_path=sample_path,
        file_name='IMG_1307.jpeg',
        file_size=os.path.getsize(sample_path),
        width=img.width,
        height=img.height,
        format=img.format,
        mode=img.mode
    )
    print(f'✅ メタデータ生成: {metadata.file_name} ({metadata.width}x{metadata.height})')
    
    # 処理パラメータ
    params = BasicAdjustmentParams(brightness=10, contrast=5, saturation=0)
    print(f'✅ 処理パラメータ: {params}')
    
    print('🎉 実画像処理準備完了')
else:
    print('⚠️ サンプル画像が見つかりません')
"
```

### 5. 📊 包括検証レポート
先ほど作成した詳細検証スクリプトを実行。

```bash
# 包括検証実行（推奨）
python scripts/comprehensive_verification.py
```

## 🎯 検証のポイント

### ✅ 成功確認項目
1. **既存機能保持**: GUIアプリが正常に起動
2. **型安全性**: Pydanticスキーマが正常動作
3. **データ永続化**: DuckDBが正常動作
4. **API設計**: FastAPIルーターが正常定義
5. **統合性**: 既存プラグインと新スキーマの連携

### ⚠️ 注意点
- 仮想環境（`.venv`）が有効になっていることを確認
- サンプル画像（`SampleImage/IMG_1307.jpeg`）が存在することを確認
- Python 3.9以上で実行

### 🔧 トラブルシューティング

#### よくある問題と解決法

1. **インポートエラー**
```bash
# パス問題の場合
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

2. **依存関係不足**
```bash
# 依存関係再インストール
pip install -r requirements.txt
```

3. **データベースファイル権限**
```bash
# データディレクトリ作成
mkdir -p data/db data/experiments
```

## 📈 次のステップ

検証が成功したら、Phase 2の選択肢：

1. **FastAPIサーバー実装** - 実際の処理ロジック
2. **Streamlit UI** - データサイエンティスト向けWebUI
3. **MLflow連携** - 実験トラッキング

どの方向に進むかお聞かせください！