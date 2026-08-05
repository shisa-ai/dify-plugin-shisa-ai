# Shisa AI Difyモデルプロバイダー

Shisa AIのLLM、音声認識（ASR）、音声合成（TTS）をDifyから直接利用するためのモデルプロバイダープラグインです。

## 対応機能

- Shisa V2.1 Flash / Pro LLM
- Shisa ASR（任意のワークスペース全体デフォルトに対応）
- Shisa TTS（Dify標準連携ではMP3）
- Difyが対応する画面での動的な音声一覧取得

翻訳APIは、Difyに標準の翻訳モデルインターフェースがないため、別リポジトリの [Shisa AI Tools](https://github.com/shisa-ai/dify-plugin-shisa-ai-tools) から提供します。

APIキーは [Shisa Platform](https://platform.shisa.ai/) で取得してください。料金、利用上限、モデル提供状況などの最新情報は、[Shisa Platform](https://platform.shisa.ai/) と [公式ドキュメント](https://docs.shisa.ai/) を確認してください。

Dify Workflow内の音声ファイルは後続ノードへ渡る前に完了データとしてバッファされるため、ワークフロー内でのプログレッシブ再生を保証するものではありません。

## ASRのワークスペース全体デフォルト

プロバイダー設定では、言語、ホットワード、temperature、`top_p`、frequency penalty、repetition penalty、VADを任意で設定できます。Difyが呼び出しごとにこれらを送るのではなく、プラグインが明示的に設定された値だけをASRリクエストへ追加します。

> **注意:** これらはワークスペース全体のプロバイダーデフォルトです。このShisa ASRを使うワークスペース内の全アプリに影響し、個別Chatflowだけには限定されません。空欄ではその値を送らず、Shisa APIのデフォルトを使用します。

アプリまたはノードごとに変更する場合は、別のShisa AI Toolsプラグインの「音声を文字起こし」を使用してください。
