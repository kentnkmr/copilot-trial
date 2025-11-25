# Pomodoro Timer — Architecture

このドキュメントは、このプロジェクトで作成するポモドーロタイマーWebアプリのアーキテクチャ案をまとめたものです。

主な実装スタック: FastAPI (backend)、HTML/CSS/Vanilla JavaScript (frontend)

---

## 1. 目的
- シンプルで信頼できるポモドーロタイマーをWebブラウザで提供する。
- 単一ページで動く軽量なフロントエンドと、必要に応じたリアルタイム同期・永続化を持つバックエンドを提供。
- テストしやすい構造と、PWA / multi-device 同期を視野に入れた拡張性を重視。

---

## 2. ハイレベル構成

- クライアント (ブラウザ)
  - UI: index.html, styles.css, app.js
  - タイマーのコアロジックは "Timer Core" モジュールに抽象化（時間依存ロジックは timeProvider を注入）
  - 状態保存: localStorage / IndexedDB（設定や未完了セッション）
  - タブ間同期: BroadcastChannel
  - リアルタイム: WebSocket （オプション：複数デバイス同期）
  - PWA対応: Service Worker + Push Notification（将来）

- サーバー (FastAPI)
  - REST API: 設定・履歴・セッション管理
  - WebSocket: リアルタイム更新と複数クライアントの同期
  - DB: 開発は SQLite、運用は PostgreSQL 想定
  - 認証: 本プロジェクトのMVPではユーザー認証機能を持たせず、local-first（デバイス単位で完結）な設計とします。将来的に複数デバイス同期やサーバ側永続化が必要になった場合は、匿名デバイス・トークンやオプションでのユーザーアカウントを追加検討します。

- インフラ / 開発ワークフロー
  - Docker / docker-compose（ローカル開発）
  - CI: GitHub Actions（lint, unit tests, integration tests）
  - デプロイ: Render / Railway / Fly / GCP Run など

---

## 3. 詳細設計

### 3.1 API（骨子）
REST (JSON) エンドポイント例
- GET  /api/v1/settings            — ユーザやローカルの設定を取得
- PUT  /api/v1/settings            — 設定を保存
- POST /api/v1/sessions            — セッション開始（start）
- PATCH /api/v1/sessions/{id}      — 状態更新（pause/resume/stop/skip）
- GET  /api/v1/history             — 完了したセッションの一覧

WebSocket
- /ws/timer[?session_id=...]      — タイマーイベント同期用
- メッセージ種別: start, pause, resume, stop, tick-sync, session-updated
- メッセージは UTC epoch millisecond を含めて送る（クライアントは完全な時刻ベースで同期）

### 3.2 データモデル
-- (本設計ではユーザーアカウントを含めません。)
- settings
  - id, device_token (nullable), pomodoro_minutes, short_break_minutes, long_break_minutes, cycles_to_long_break

- sessions
  - id, device_token (nullable), session_type (pomodoro/short/long), start_ts, end_ts, paused_intervals (json), status

- events/history
  - id, session_id, event_type, timestamp, meta (json)

※ 本設計では MVP 段階でユーザーアカウントを導入しません。すべての操作はクライアント側（localStorage / IndexedDB）で完結する "local-first" を優先します。サーバで永続化や複数デバイス間の同期を行う場合は、device_token ベースでオプション実装とし、ユーザーアカウントは将来の拡張機能とします。

### 3.3 タイマーの同期設計（高信頼）
- クライアント主導 + 時刻ベースの同期
  - セッション開始時に start_ts を決める（UTC epoch ms）。サーバ保存・通知は start_ts を含む。
  - クライアントは end_ts（= start_ts + duration）と現在時刻との差分から残り時間を算出。これによりドリフトを回避。
- 複数端末/タブ
  - タブ内：BroadcastChannel で変更をブロードキャスト
  - 複数デバイス/他端末: WebSocket 経由でサーバにイベントを送信し、サーバは room/presence を通じて他端末へ中継

---

## 4. テスト性を高めるための設計指針
- 副作用の分離: DB・通知・外部IOは Adapter/Repository 層に隔離
- 依存注入: FastAPI の Depends / app factory で依存を差し替え可能に
- 時刻を抽象化: Clock/TimeProvider を導入しテストで FakeClock を使う
- WebSocket / PubSub 層も抽象化し InMemory Stub を用意する

テストツール
- Python: pytest + pytest-asyncio, httpx AsyncClient, freezegun（または独自 FakeClock）
- Frontend: vitest/jest（unit）、@testing-library/dom（DOM）、Playwright（E2E）

---

## 5. セキュリティ・運用メモ
- 通信は TLS（HTTPS）を必須にする
-- WebSocket / server-side features: MVP は認証なし（or 匿名 device_token を利用）で動作可能。ただし、サーバに保存されたユーザーデータやクロスデバイス同期を提供する場合は、認証と安全なトークン管理の導入を推奨します。
- DB マイグレは Alembic を利用

---

## 6. MVP ロードマップ（推奨）
- Phase 1: Minimal working product
  - FastAPI + static frontend (HTML/CSS/Vanilla JS)
  - localStorage 保存、設定編集、基本タイマー（start/pause/stop）
  - unit tests for Timer core and server services

- Phase 2: Real-time & PWA
  - WebSocket を用いたマルチタブ/マルチデバイス同期
  - BroadcastChannel / Service Worker（PWA） + Push Notifications

-- Phase 3: Optional — cross-device sync
  - 端末間での永続同期が必要なら、device_token やオプションでのユーザーアカウントを実装してクロスデバイス同期を実現します。

- Phase 4: Analytics / Team features (optional)

---

## 7. 推奨ディレクトリ構成
```
/ (project root)
├─ app/
│  ├─ main.py
│  ├─ api/v1/                      # REST handlers
│  ├─ ws.py                        # websocket handlers
│  ├─ services/                    # business logic (Clock-injectable)
│  ├─ repositories/                 # DB adapters
│  └─ db.py                        # DB session factory
├─ frontend/
│  ├─ index.html
│  ├─ styles.css
│  └─ app.js                        # Timer core + UI
├─ tests/
├─ Dockerfile
├─ docker-compose.yml
└─ architecture.md
```

---

## 8. 次の実務的アクション
1. small-scope: `Timer Core` の純粋関数実装とテストを作る（単体テスト化が最も効果的）
2. app factory を作り、Repository と Clock を DI 可能にする
3. 軽量の動作する MVP を作り E2E シナリオを追加する

---

このドキュメントを基に、サンプル実装（FastAPI + simple frontend）で scaffold を作ることができます。要望があれば次に実装スキャフォールディングを作成します。
