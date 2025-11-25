# Pomodoro Timer — Implementation Plan

この計画書は、ポモドーロタイマー Web アプリ（FastAPI + HTML/CSS/Vanilla JS）を段階的に実装するための、スプリント単位のロードマップ・タスク分割と受け入れ基準、見積り（目安）をまとめたものです。

目的：短期で安定した MVP を早期にリリースし、以降で価値の高い機能を優先して追加します。プロジェクトは "local-first" を原則とし、最初はユーザー認証を持たないシンプルな設計とします。

---

## 基本運用ルール（チーム向け）
- スプリント: 1週間（短期開発）または 2週間（落ち着いたペース）を推奨
- ブランチ: feature/<name> を作成 → PR → CI (lint + unit tests + integration tests) → レビュー → merge
- テスト方針: unit → integration → E2E (必要に応じて nightly)
- ドキュメント: 各完了チケットは簡易 README/手順を残す

---

## フェーズ / スプリント計画（優先順位付き）
以下は推奨の段階別計画です。各 sprint の中で複数の小チケット（2~8 時間相当）に分割してください。

### Sprint 0 — 準備（1 sprint, 1–3 日）
目的：環境と構成を整え、最初のスケルトンを用意する
タスク:
- プロジェクト初期化 (pyproject / package.json / Dockerfile / .gitignore)
- README に開発手順とローカル起動コマンドを追加
- CI（GitHub Actions）: lint + unit tests をセット
- App factory FastAPI の雛形と static ファイル配信
受け入れ基準:
- 開発者がローカルで app を起動できる
- CI が lint と unit tests を実行する
見積: 1–3 日

---

### Sprint 1 — Timer Core 実装とユニットテスト（1–2 週間）
目的：アプリの心臓部となるタイマーの純粋ロジックを提供し、テスト可能にする
タスク（小チケット）:
- Timer Core implementation (pure class/functions)
  - API: start(), pause(), resume(), stop(), skip(), getRemaining(now)
  - timeProvider injection (RealClock, FakeClock)
- Unit tests for Timer Core (pytest / vitest)
- Edge cases tests: pause/resume multiple times, long pauses, negative remaining times
受け入れ基準:
- Timer Core のユニットテストが安定して通る
- ドリフト補正ロジックが正しく動く
見積: 3–7 日

---

### Sprint 2 — シンプル UI とローカル保存（1–2 週間）
目的：ユーザーがブラウザでタイマーを簡単に使える最小 UI を作る
タスク:
- index.html, styles.css, app.js の最小 UI
  - 大きな残り時間表示、開始/一時停止/停止/スキップ
  - 設定パネル（pomodoro/short/long durations）
  - ローカル履歴表示領域
- localStorage または IndexedDB を使った設定 & 履歴保存
- BroadcastChannel を使ったタブ間同期
- フロントロジック単体テスト（Timer Core と DOM 層の分離）
受け入れ基準:
- UI で start → complete が動作
- 設定・履歴がリロードで保持される
- 複数タブで状態が同期される
見積: 1–2 週間

---

### Sprint 3 — サーバ API と永続化（1–2 週間）
目的：REST API のスケルトンを用意し、設定や履歴をサーバに保存するオプションを提供
タスク:
- SQLite + SQLModel/SQLAlchemy + Alembic migration のセットアップ
- REST endpoints: /api/v1/settings, /api/v1/sessions, /api/v1/history (CRUD)
- Repository layer + App factory + DI
- Server tests: unit + integration (pytest + httpx AsyncClient)
- Frontend optional integration: settings sync (client → server)
受け入れ基準:
- API が仕様どおり動作し、CI で integration tests が通る
見積: 1–2 週間

---

### Sprint 4 — リアルタイム同期（2 週間）
目的：複数クライアント間でタイマー操作をリアルタイムに同期させる
タスク:
- FastAPI WebSocket endpoint /ws/timer
- Message contract document (start / pause / resume / stop / tick-sync)
- Server-side pub/sub (in-process stub → optional Redis for scalability)
- Client-side WebSocket handler and event dispatch
- Tests for websocket handlers and message flows
受け入れ基準:
- クライアント A が start するとクライアント B にイベントが届き、UI が同期される
見積: 2 週間

---

### Sprint 5 — PWA / 通知 / UX 改善（1–2 週間）
目的：オフライン対応・通知でユーザー体験を向上させる
タスク:
- Service Worker (cache-first strategy for static assets)
- Notification API + sound support (権限フロー、フォールバック)
- Accessibility improvements (ARIA, keyboard navigation)
- Dark mode / responsive polish
受け入れ基準:
- オフラインでもアプリが起動・タイマーが動作する
- 完了時に通知/音が出る（権限がある場合）
見積: 1–2 週間

---

### Sprint 6 — Optional: Cross-device / Analytics / Export（2週間以上、任意）
目的：複数デバイス間で永続同期、分析やエクスポート機能を提供
タスク候補:
- device_token ベースで匿名デバイス同期または optional user accounts
- Cross-device synchronization logic & conflict resolution
- Analytics endpoints, lightweight dashboard
- Export/import (CSV/JSON)
受け入れ基準:
- 別デバイスで同じセッションが引き継がれる
見積: 要検討（scope 依存）

---

## チケット分割・優先順位の例
各スプリントはさらに 2–8 時間の小さなチケットに切り分けます。例:
- feat: timer-core start/pause/resume
- test: timer-core edgecases
- feat: ui timer component + styles
- chore: add CI job for integration tests
- feat: broadcastchannel sync
- feat: api sessions endpoint

---

## CI / テスト & Quality Gates
- 必須: lint, unit tests for core logic
- 推奨: integration tests for API (sqlite memory / test container)
- E2E: Playwright smoke tests for critical flows
- Gate: 各 PR は unit tests と lint をパスすること

---

## 最初の優先アクション（今すぐ着手）
1. Sprint 1 の Timer Core 実装と単体テストについて、最初の feature ブランチを切る
2. 並行して Sprint 2 の UI 基本スケルトン (index.html + app.js) を作る

---
