# Weather API

FastAPI で構築した天気情報 API です。[OpenWeatherMap](https://openweathermap.org/api) を利用して都市名から現在の天気を返します。

## 技術スタック

- Python 3.12 / FastAPI
- パッケージ管理: [uv](https://docs.astral.sh/uv/)
- フォーマット: black
- テスト: pytest
- コンテナ: Docker / docker-compose
- CI: GitHub Actions

## ディレクトリ構成

```
.
├── app/
│   ├── main.py           # FastAPI アプリケーション
│   ├── config.py         # 環境変数・設定
│   ├── schemas.py        # レスポンスモデル
│   ├── dependencies.py   # DI
│   ├── routers/          # エンドポイント
│   └── services/         # 外部 API 連携
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── Makefile
```

## セットアップ

### 前提

- [uv](https://docs.astral.sh/uv/getting-started/installation/) がインストール済みであること
- [OpenWeatherMap](https://home.openweathermap.org/api_keys) で API キーを取得していること

### ローカル開発

```bash
# 依存関係のインストール
make install

# 環境変数
cp .env.example .env
# .env に OPENWEATHER_API_KEY を設定

# pre-commit（任意）
make pre-commit
```

## 起動方法

### Docker Compose（推奨）

```bash
cp .env.example .env
# .env に OPENWEATHER_API_KEY を設定

make run
```

`http://localhost:8000` で API が起動します。Swagger UI は `http://localhost:8000/docs` です。

### ローカル（uv）

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## テスト方法

```bash
make test
```

フォーマット確認:

```bash
make lint
```

自動フォーマット:

```bash
make format
```

## API 実行例

### リクエスト

```bash
curl "http://localhost:8000/weather?city=osaka"
```

### レスポンス（例）

```json
{
  "city": "osaka",
  "temperature_celsius": 22.5,
  "description": "clear sky",
  "humidity": 65,
  "wind_speed_mps": 3.2
}
```

### エラー例

都市が見つからない場合（404）:

```bash
curl -i "http://localhost:8000/weather?city=not-a-real-city-xyz"
```

## 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `OPENWEATHER_API_KEY` | はい | OpenWeatherMap API キー |
| `OPENWEATHER_BASE_URL` | いいえ | API ベース URL（デフォルト: OpenWeatherMap v2.5） |

## Makefile コマンド

| コマンド | 説明 |
|----------|------|
| `make run` | docker-compose で起動 |
| `make test` | pytest 実行 |
| `make lint` | black チェック |
| `make format` | black でフォーマット |
| `make install` | 依存関係インストール |
| `make pre-commit` | pre-commit フック登録 |

## GitHub への段階的コミット例

```bash
git init
git add pyproject.toml uv.lock .gitignore .env.example
git commit -m "chore: initialize project with uv"

git add app/
git commit -m "feat: add weather API endpoint"

git add tests/ .github/
git commit -m "test: add pytest and GitHub Actions"

git add Dockerfile docker-compose.yml Makefile README.md .pre-commit-config.yaml
git commit -m "chore: add Docker, Makefile, and documentation"
```
