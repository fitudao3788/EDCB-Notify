# EDCBNotify

EDCB の録画情報を監視し、Discord Webhook経由で通知を送信するPythonアプリケーションです。

## 概要

EDCBNotifyは、EDCB の録画記録ファイル (RecInfo.txt) を監視し、新しい録画完了情報を検出すると、Discord Webhook を通じてリアルタイムで通知を送信します。

**主な機能:**
- EDCB RecInfo.txt ファイルの自動監視
- Discord Webhook 統合による通知配信
- 録画状態の詳細情報表示（番組名、日時、チャンネル、ドロップ数）
- 録画状態に応じた色分け表示
  - ✅ 正常完了（青）
  - ⚠️ 警告・エラー（黄・赤）

## インストール

### 前提条件
- Python 3.14以上
- Docker/Docker Compose (オプション)

### ローカルセットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/fitudao3788/EDCB-Notify.git
cd EDCB-Notify
```

2. 環境変数ファイルを作成
```bash
cp .env.example .env
```

3. `.env`ファイルを編集して、以下の設定を行います:
```env
EDCB_RECINFO_PATH=/EDCB/Setting/RecInfo.txt
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

4. 依存パッケージをインストール

[uv](https://github.com/astral-sh/uv)を使用:
```bash
uv sync
```

5. アプリケーションを実行
```bash
uv run python main.py
```

## Docker での実行

### Docker Compose を使用 (推奨)

1. docker-compose ファイルを作成
```bash
cp docker-compose.example.yml docker-compose.yml
```

2. `docker-compose.yml`を編集して、環境変数を設定

3. コンテナを起動
```bash
docker-compose up -d
```

### Docker でビルド・実行

```bash
docker build -t edcb-notify .
docker run -d \
  --name edcb-notify \
  -e EDCB_RECINFO_PATH=/EDCB/Setting/RecInfo.txt \
  -e DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL \
  -v /EDCB:/EDCB \
  -e TZ=Asia/Tokyo \
  edcb-notify
```

## 環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `EDCB_RECINFO_PATH` | EDCB の RecInfo.txt ファイルパス | `/EDCB/Setting/RecInfo.txt` |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | `https://discord.com/api/webhooks/...` |

## 設定例

### `.env.example`

```env
EDCB_RECINFO_PATH=/EDCB/Setting/RecInfo.txt
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
```

### `docker-compose.example.yml`

```yaml
services:
  edcb_notify:
    build: .
    container_name: edcb-notify
    restart: always
    environment:
      - TZ=Asia/Tokyo
      - EDCB_RECINFO_FILE=/app/RecInfo.txt
      - DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
    volumes:
      - /EDCB:/EDCB
```

## 通知フォーマット

Discord に送信される通知の例:

**タイトル:** 番組名  
**説明:** 放送日時 (例: `2024/01/01(月) 20:00～21:00`)  
**フィールド:**
- チャンネル: チャンネル名
- 録画状態: 完了/警告/エラー
- ドロップ: フレームドロップ数

**色分け:**
- 🔵 青 (`#3498db`): 正常完了、ドロップなし
- 🟡 黄 (`#f1c40f`): 部分的に録画、またはドロップあり
- 🔴 赤 (`#e74c3c`): エラーまたは異常終了

## 依存パッケージ

- **httpx** (>=0.28.1): HTTP クライアント（Webhook送信用）
- **loguru** (>=0.7.3): ロギングライブラリ
- **python-dotenv** (>=1.2.2): 環境変数管理

詳細は `pyproject.toml` を参照してください。

## トラブルシューティング

### 通知が送信されない
- `EDCB_RECINFO_PATH` が正しいことを確認
- `DISCORD_WEBHOOK_URL` が有効なことを確認
- アプリケーションログを確認: `docker logs edcb-notify`

### ファイルパスが見つからない
- EDCB がインストールされているか確認
- RecInfo.txt ファイルが存在するか確認
- Docker で実行する場合、ボリュームマウントが正しいか確認

## ライセンス

このプロジェクトは [Apache License 2.0](LICENSE) の下でライセンスされています。

## 作者

fitudao3788

## 参考資料

- [EDCB](https://github.com/xtne6f/EDCB) - 公式リポジトリ
- [Discord Webhooks Documentation](https://discord.com/developers/docs/resources/webhook)
