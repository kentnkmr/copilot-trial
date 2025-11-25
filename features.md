# Pomodoro Timer — Features

このファイルは、FastAPI + HTML/CSS/Vanilla JavaScript で開発するポモドーロタイマーアプリに必要な機能を洗い出し、優先度別（MVP / 推奨 / 任意）に整理したものです。

---

## 優先度キー
- 必須 (MVP) — まず実装するコア機能。
- 推奨 (Short-term) — MVP の次に必要/価値の高い機能。
- 任意 (Long-term / Optional) — 将来的に追加で価値がある機能。

---

## 必須 (MVP)
1. Timer Core (純粋ロジック)
   - 機能: start / pause / resume / stop / skip のロジック、残り時間計算
   - 実装ポイント: timeProvider を注入できるように抽象化、単体テスト可能

2. フロント UI（静的）
   - 機能: タイマー表示（大きな残り時間）、操作ボタン（開始/一時停止/停止/スキップ）、設定パネル、履歴領域
   - 実装ポイント: アクセシビリティ・キーボード操作を最低限サポート

3. 設定保存（local-first）
   - 機能: ポモドーロ時間、短休憩/長休憩の分数、サウンド/通知トグルを保存
   - 実装ポイント: localStorage または IndexedDB に保存、リロードで復元

4. 履歴保存（ローカル）
   - 機能: 完了/中断したセッションをローカルに保存して一覧表示
   - 実装ポイント: スキーマは簡素（セッションID, type, start_ts, end_ts, status, meta）

5. タブ間同期（同一ブラウザ）
   - 機能: BroadcastChannel（または localStorage イベント）を使った同一ブラウザのタブ間の状態共有
   - 実装ポイント: 片方で操作すると即座に他タブに反映されること

6. FastAPI サーバ（最小API）
   - 機能: /api/v1/settings, /api/v1/sessions, /api/v1/history の CRUD 実装（サーバ永続化はオプション）
   - 実装ポイント: app factory, DI を使ってテスト時に差し替え可能に

7. テスト基盤
   - 機能: Python 側 (pytest/pytest-asyncio)、フロント側 (vitest/jest)、E2E (Playwright) を整備
   - 実装ポイント: Timer Core と各サービスのユニットテストを優先

8. 開発ドキュメント / 起動手順
   - 機能: README、architecture.md、簡単なローカル起動スクリプト（Docker/venv）の整備

---

## 推奨 (Short-term)
1. WebSocket 同期（サーバ経由）
   - 機能: /ws/timer による start/pause/resume/stop のリアルタイム中継
   - 実装ポイント: 認証は MVP では不要、device_token による匿名識別をオプションで実装可能

2. PWA 対応（Service Worker）
   - 機能: オフライン時に静的コンテンツを表示、ホーム画面追加、基本的なキャッシュ戦略
   - 実装ポイント: オフラインでもタイマーはローカルで動作し続ける

3. Notification / Sound
   - 機能: 終了時のブラウザ通知（Notification API）・サウンドアラート
   - 実装ポイント: 権限ハンドリング、フォールバックの処理

4. UI/UX 改良
   - 機能: ダークモード、滑らかなアニメーション、高コントラスト対応
   - 実装ポイント: ARIA 属性、キーボードショートカット、レスポンシブ

5. IndexedDB を利用したローカルDB
   - 機能: 大きな履歴や複雑なクエリを扱うための保存層
   - 実装ポイント: idb ライブラリなどを活用して簡潔に実装

6. フロントの分割とテスト容易化
   - 機能: Timer Core と DOM 更新層を分離してユニットテストを充実させる

---

## 任意 (Long-term / Optional)
1. Cross-device persistent sync
   - 機能: 複数デバイスでセッションを同期（device_token で匿名同期、またはオプションのユーザーアカウント）
   - 実装ポイント: サーバ側の保存、WebSocket + room management、Conflict 解決戦略

2. アナリティクス / ダッシュボード
   - 機能: 集中時間の統計、習慣分析、CSV/JSON エクスポート

3. セーブ/ロード/テンプレート
   - 機能: カスタムサイクルのテンプレート保存と復元

4. チーム機能 / 共有
   - 機能: チームで同期して共同でセッションを運用する機能（将来的な拡張）

---

## 非機能要件・運用要点
- セキュリティ: HTTPS を必須にし、WebSocket の無認証使用時はリスクを考慮（rate-limiting等）
- テストしやすさ: DI、Clock 抽象化、Repository パターンの徹底
- CI/CD: Unit → Integration → E2E の順でパイプライン構築
- 可観測性: ログ整備、Sentry などの導入オプション

---

## 初期イテレーションの推奨タスク順
1. Timer Core の実装 + 単体テスト
2. シンプルなフロント UI（操作と表示） + localStorage 保存
3. タブ間同期（BroadcastChannel） + ローカル履歴保存
4. FastAPI の最小 REST API（settings / sessions / history） + server-side tests
5. WebSocket / PWA / Notifications を順次追加

---

この `features.md` をベースに GitHub Issues / 開発チケットに分割できます。必要なら、各項目のチケットテンプレートと見積もりも作成できます。