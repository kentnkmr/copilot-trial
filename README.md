# copilot-trial

[公式チュートリアル](https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0)を参照しつつ独自の拡張を行う

### 変更点

1. Flask を FastAPI に変更
## ローカル実行ガイド

下記コマンドでローカル環境の仮想環境を作成し、依存を入れて uvicorn でサーバを起動できます。

簡単に実行する方法（推奨）:

```bash
chmod +x ./scripts/run_dev.sh
./scripts/run_dev.sh
```

手動で行う場合:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

サーバはデフォルトで http://127.0.0.1:8000 に立ちます。API ドキュメントは http://127.0.0.1:8000/docs を参照してください。

テスト実行:

```bash
source .venv/bin/activate
python -m pytest -q
```
