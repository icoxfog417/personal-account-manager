# Genu（ジェニュー）完全ガイド - 第8章：デプロイとカスタマイズ

## 8.1 デプロイ方法の選択

Genuを自身の環境にデプロイするには、2つの方法があります。

### 8.1.1 AWS CDKを使用したデプロイ（推奨）

**特徴**：
- ソースコードから直接デプロイ
- 最新機能にすぐ追従可能
- 柔軟なカスタマイズが可能
- Knowledge Bases for Amazon Bedrockに対応
- ダッシュボード機能が利用可能

**推奨する場合**：
- 本番環境での利用
- カスタマイズが必要な場合
- 最新機能を使いたい場合
- ソースコードを確認・修正したい場合

**必要な環境**：
- Node.js（18.x以上）
- AWS CLI
- Git
- 適切なAWS権限

### 8.1.2 AWS CloudFormationを使用したデプロイ（非推奨）

**特徴**：
- 数クリックで簡単に構築
- 設定項目が少ない
- バージョンが遅れている場合がある

**推奨する場合**：
- 検証目的
- すぐに試したい場合
- カスタマイズ不要の場合

**注意**：
CloudFormationを使用する場合、CDKを使用した場合に比べて、構築するアプリケーションのバージョンが遅れている場合があります。業務で利用する環境として構築する際は、AWS CDKを使用することを推奨します。

## 8.2 AWS CDKによるデプロイ手順

### 8.2.1 事前準備

#### AWSアカウントへのログイン

適切な権限を持つIAMユーザーでAWSマネジメントコンソールにログインします。

**必要な権限**：
- Amazon Bedrock（モデルアクセス）
- Amazon S3
- Amazon CloudFront
- AWS Lambda
- Amazon Cognito
- Amazon CloudFormation
- IAM
- Amazon CloudWatch

#### Bedrockモデルへのアクセス有効化

1. Bedrockコンソールを開く
2. 「モデルアクセス」を選択
3. 使用するモデルのアクセスをリクエスト
4. 承認を待つ（数分〜数十分）

**推奨モデル**：
- Anthropic Claude 3.5 Sonnet v2
- Anthropic Claude 3.5 Haiku
- Amazon Nova Pro
- Amazon Nova Lite
- Amazon Nova Canvas（画像生成）
- Stability AI Stable Diffusion XL（画像生成）

### 8.2.2 開発環境のセットアップ

#### AWS Code Editorの使用（推奨）

1. **SageMakerコンソールを開く**
2. **Code Editorを起動**
   - 起動には数分かかります
3. **ターミナルを開く**
   - Command + Shift + P（Windows: Ctrl + Shift + P）
   - 「Terminal: Create New Terminal」を実行

#### ローカル環境の使用

必要なツールをインストール：
- Node.js 18.x以上
- AWS CLI
- Git

### 8.2.3 ソースコードの取得

```bash
cd ~
git clone https://github.com/aws-samples/generative-ai-use-cases.git
cd generative-ai-use-cases
```

### 8.2.4 依存関係のインストール

```bash
npm ci
```

数分かかる場合があります。

### 8.2.5 設定ファイルの編集

#### cdk.jsonの編集

`packages/cdk/cdk.json`ファイルを開いて設定を変更します。

**基本設定**：
```json
{
  "app": "npx ts-node --prefer-ts-exts bin/generative-ai-use-cases.ts",
  "context": {
    "ragEnabled": false,
    "ragKnowledgeBaseEnabled": false,
    "modelIds": [
      "anthropic.claude-3-5-sonnet-20241022-v2:0",
      "anthropic.claude-3-5-haiku-20241022-v1:0",
      "amazon.nova-pro-v1:0",
      "amazon.nova-lite-v1:0"
    ],
    "imageGenerationModelIds": [
      "amazon.nova-canvas-v1:0"
    ]
  }
}
```

#### RAG機能の有効化

**Amazon Kendraを使用する場合**：
```json
"ragEnabled": true
```

**Knowledge Basesを使用する場合**：
```json
"ragKnowledgeBaseEnabled": true
```

### 8.2.6 CDK Bootstrap

初回のみ実行が必要です。

```bash
cd ~/generative-ai-use-cases
npx -w packages/cdk cdk bootstrap
```

Bootstrap処理により、以下が作成されます：
- S3バケット（アセット管理用）
- IAMロール（デプロイ用）
- その他の必要なリソース

### 8.2.7 デプロイの実行

```bash
cd ~/generative-ai-use-cases
npm -w packages/cdk run -- cdk deploy --require-approval never --all
```

デプロイには10-20分ほどかかります。

**デプロイ完了時の出力例**：
```bash
✅ GenerativeAiUseCasesStack

✨ Deployment time: 765.71s

Outputs:
GenerativeAiUseCasesStack.WebUrl = https://xxxx.cloudfront.net
GenerativeAiUseCasesStack.UserPoolId = ap-northeast-1_xxxx
GenerativeAiUseCasesStack.UserPoolClientId = xxxx

✨ Total time: 815.93s
```

**WebURLをメモ**してください。これがアプリケーションのURLです。

### 8.2.8 アプリケーションURLの確認

後からURLを確認する場合：

```bash
aws cloudformation describe-stacks \
  --stack-name GenerativeAiUseCasesStack \
  --query 'Stacks[].Outputs[?OutputKey==`WebUrl`].OutputValue' \
  --output text
```

## 8.3 モデルのカスタマイズ

### 8.3.1 使用するモデルの変更

`packages/cdk/cdk.json`を編集して、使用するモデルを変更できます。

#### テキスト生成モデル

```json
"modelIds": [
  "anthropic.claude-sonnet-4-20250514-v1:0",
  "anthropic.claude-3-7-sonnet-20250219-v1:0",
  "anthropic.claude-3-5-haiku-20241022-v1:0",
  "amazon.nova-premier-v1:0",
  "amazon.nova-pro-v1:0",
  "amazon.nova-lite-v1:0",
  "amazon.nova-micro-v1:0"
]
```

#### 画像生成モデル

```json
"imageGenerationModelIds": [
  "amazon.nova-canvas-v1:0",
  "stability.stable-diffusion-xl-v1"
]
```

#### 音声モデル

```json
"speechToSpeechModelIds": [
  "amazon.nova-sonic-v1:0"
]
```

**注意**：
- Bedrockで使用したいモデルを事前に有効化する必要があります
- モデルIDは正確に記述してください
- サポートされているモデルのリストは公式ドキュメントを参照

### 8.3.2 サポートされているモデル

**Claudeシリーズ**：
- Claude Sonnet 4
- Claude 3.7 Sonnet
- Claude 3.5 Sonnet v2
- Claude 3.5 Haiku

**Amazon Novaシリーズ**：
- Nova Premier
- Nova Pro
- Nova Lite
- Nova Micro
- Nova Canvas（画像生成）
- Nova Reel（動画生成）
- Nova Sonic（音声）

**その他**：
- Stability AI Stable Diffusion XL（画像生成）

最新のサポート状況は[公式GitHubリポジトリ](https://github.com/aws-samples/generative-ai-use-cases)を参照してください。

### 8.3.3 デフォルトモデルの設定

ユーザーが最初に選択されるモデルを指定できます。

```json
"defaultModel": "anthropic.claude-3-5-sonnet-20241022-v2:0"
```

## 8.4 その他のカスタマイズ

### 8.4.1 リージョンの変更

デフォルトは東京リージョン（ap-northeast-1）ですが、変更可能です。

**cdk.jsonでの指定**：
```json
"region": "us-east-1"
```

または、AWS CLIのデフォルトリージョンを使用：
```bash
export AWS_DEFAULT_REGION=us-east-1
```

### 8.4.2 コスト最適化の設定

#### Knowledge Basesの冗長化設定

```json
"knowledgeBaseStandby": false
```

`false`に設定することで、OpenSearch Serverlessの冗長化を無効にし、コストを削減できます。

**注意**：本番環境では冗長化を有効（`true`）にすることを推奨します。

#### モデルの選択

コストを抑える場合は、より安価なモデルを選択：
- Claude 3.5 Haiku（高速・低価格）
- Amazon Nova Lite（軽量・低価格）

### 8.4.3 カスタムドメインの設定

CloudFrontのデフォルトURLではなく、独自ドメインを使用できます。

**手順**：
1. Route 53でドメインを管理
2. ACMで証明書を取得
3. cdk.jsonでドメイン設定を追加
4. デプロイ

詳細は公式ドキュメントを参照してください。

## 8.5 更新とメンテナンス

### 8.5.1 アプリケーションの更新

最新バージョンにアップデートする手順：

```bash
cd ~/generative-ai-use-cases
git pull origin main
npm ci
npm -w packages/cdk run -- cdk deploy --require-approval never --all
```

### 8.5.2 設定変更の反映

cdk.jsonを変更した後、デプロイを実行して変更を反映：

```bash
npm -w packages/cdk run -- cdk deploy --require-approval never --all
```

### 8.5.3 ログの確認

#### CloudWatch Logs

Lambda関数のログはCloudWatch Logsで確認できます。

```bash
aws logs tail /aws/lambda/GenerativeAiUseCasesStack-XXX --follow
```

#### アクセスログ

CloudFrontのアクセスログを有効化することで、ユーザーのアクセスパターンを分析できます。

### 8.5.4 モニタリング

#### CloudWatchダッシュボード

主要なメトリクスを監視：
- Lambda実行回数
- エラー率
- レスポンスタイム
- Cognito認証数

#### コストモニタリング

AWS Cost Explorerで以下をモニタリング：
- Bedrockの利用料金
- CloudFrontのデータ転送量
- Lambda実行コスト
- RAG（Kendra/OpenSearch）のコスト

## 8.6 トラブルシューティング

### 8.6.1 デプロイエラー

**エラー**: `Unable to resolve AWS account`

**解決策**：
```bash
aws configure
# または
export AWS_PROFILE=your-profile-name
```

**エラー**: `Model access denied`

**解決策**：
Bedrockコンソールでモデルアクセスを有効化

### 8.6.2 アプリケーションエラー

**問題**: ログイン後に真っ白な画面

**解決策**：
1. ブラウザのキャッシュをクリア
2. シークレットモードで試す
3. CloudFrontのキャッシュを無効化

**問題**: RAG機能が動作しない

**解決策**：
1. Kendra/Knowledge Basesが正しくデプロイされているか確認
2. データソースが同期されているか確認
3. IAM権限を確認

### 8.6.3 パフォーマンス問題

**問題**: 応答が遅い

**解決策**：
1. より高速なモデルを使用（Haiku、Nova Lite）
2. Lambdaのメモリを増やす
3. リージョンをユーザーに近い場所に変更

## 8.7 リソースの削除

使用を終了する場合、リソースを削除して課金を停止します。

### 8.7.1 CDKを使用した削除

```bash
cd ~/generative-ai-use-cases
npm -w packages/cdk run -- cdk destroy --all
```

確認プロンプトで`y`を入力します。

### 8.7.2 手動での確認

以下のリソースが削除されたことを確認：
- CloudFormationスタック
- S3バケット（場合によっては手動削除が必要）
- CloudWatch Logs
- Cognito User Pool

### 8.7.3 コストの確認

削除後、数日間はCost Explorerでコストが発生していないことを確認してください。

## まとめ

第8章では、Genuのデプロイ方法、カスタマイズ、更新、トラブルシューティング、リソース削除について説明しました。これらの知識を活用することで、Genuを安全かつ効率的に運用できます。次章では、セキュリティとアクセス制御について詳しく解説します。
