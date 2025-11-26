# AWS カスタマーサポートエージェント

Strands Agent を使用して構築され、AgentCore Runtime にデプロイされた、従来のアカウントマネージャーの代替となる AI 搭載カスタマーサポートエージェントです。

## 機能

- **ナレッジ統合**: GitHub wiki から AWS ドキュメントを検索
- **会話メモリ**: AgentCore Memory を使用して顧客コンテキストを保存
- **サーバーレスデプロイ**: 自動スケーリング機能付きの AgentCore Runtime で実行
- **ワンクリックデプロイ**: 簡単セットアップ用の CloudFormation テンプレート

## クイックスタート

### 前提条件

- 適切な権限で設定された AWS CLI
- `uv` パッケージマネージャー付きの Python 3.11+
- Docker（ローカル開発用）

### ワンクリックデプロイ

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=aws-support-agent&templateURL=https://raw.githubusercontent.com/aws-samples/personal-account-manager/main/infrastructure/cloudformation/deployment-stack.yaml)

または CLI 経由でデプロイ：

```bash
./infrastructure/scripts/deploy.sh your-email@example.com
```

### ローカル開発

1. **環境セットアップ**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

2. **テスト実行**:
   ```bash
   uv run pytest tests/
   uv run ruff check
   ```

3. **ローカルテスト**:
   ```bash
   uv run python -c "
   from src.agent.support_agent import SupportAgent
   from src.knowledge.wiki_source import WikiKnowledgeSource
   from src.config.settings import Settings
   
   wiki = WikiKnowledgeSource(Settings.WIKI_REPO_URL, Settings.WIKI_LOCAL_PATH)
   agent = SupportAgent(Settings.MODEL_NAME, wiki, Settings.SYSTEM_PROMPT)
   print(agent.search_wiki_files('lambda'))
   "
   ```

## アーキテクチャ

- **SupportAgent**: すべてのナレッジソースの検索/取得ロジックを持つ Strands Agent
- **WikiKnowledgeSource**: GitHub wiki リポジトリのファイル I/O 操作
- **AgentCore Memory**: 会話履歴と顧客事実抽出
- **Amazon Bedrock**: プロンプトキャッシュ機能付きの Converse API 経由の Claude Sonnet 4

## プロジェクト構造

```
├── src/
│   ├── agent/          # Strands Agent 実装
│   ├── knowledge/      # ナレッジソースクラス
│   └── config/         # 設定管理
├── infrastructure/     # CloudFormation とデプロイスクリプト
├── tests/             # ユニットテストと統合テスト
└── data/              # ローカル wiki リポジトリ
```

## 設定

`src/config/settings.py` の主要設定：

- `WIKI_REPO_URL`: GitHub wiki リポジトリ
- `MODEL_NAME`: Bedrock モデル識別子
- `MEMORY_ID`: AgentCore Memory リソース ID
- `SYSTEM_PROMPT`: エージェント動作指示

## 開発ガイドライン

`.amazonq/rules/project.md` のコーディング標準に従ってください：

- すべての Python 操作に `uv run` を使用
- すべての関数に型ヒントが必要
- 文字列フォーマットには f-strings を使用
- `pytest` でテスト、`ruff` でフォーマット

## デプロイ

CloudFormation スタックが作成するもの：

- コンテナオーケストレーション用の AgentCore Runtime
- セマンティック戦略付きの AgentCore Memory
- コンテナイメージ用の ECR リポジトリ
- 自動デプロイ用の CodeBuild プロジェクト
- デプロイステータス用の SNS 通知

## コスト最適化

- **リクエスト課金**: AgentCore Runtime でアイドルコストなし
- **プロンプトキャッシュ**: Bedrock トークンコストを削減
- **ファイルベース検索**: フェーズ1でベクターデータベースコストなし
- **マネージドサービス**: 最小限のインフラオーバーヘッド

## サポート

問題や質問については：

1. [GitHub Issues](https://github.com/aws-samples/personal-account-manager/issues) を確認
2. [設計ドキュメント](spec/design.md) をレビュー
3. 開発チームに連絡

## ライセンス

このプロジェクトは MIT-0 ライセンスの下でライセンスされています。詳細は LICENSE ファイルを参照してください。
