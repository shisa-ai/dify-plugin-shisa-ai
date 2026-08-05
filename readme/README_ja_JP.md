# Shisa AI Difyモデルプロバイダー

Shisa AIのLLM、音声認識（ASR）、音声合成（TTS）をDifyから直接利用するためのモデルプロバイダープラグインです。

## 対応機能

- Shisa V2.1 Flash / Pro LLM
- Shisa ASR（任意のモデル認証ASRデフォルトに対応）
- Shisa TTS（Dify標準連携ではMP3）
- Difyが対応する画面での動的な音声一覧取得

翻訳APIは、Difyに標準の翻訳モデルインターフェースがないため、別リポジトリの [Shisa AI Tools](https://github.com/shisa-ai/dify-plugin-shisa-ai-tools) から提供します。

APIキーは [Shisa Platform](https://platform.shisa.ai/) で取得してください。料金、利用上限、モデル提供状況などの最新情報は、[Shisa Platform](https://platform.shisa.ai/) と [公式ドキュメント](https://docs.shisa.ai/) を確認してください。

Dify Workflow内の音声ファイルは後続ノードへ渡る前に完了データとしてバッファされるため、ワークフロー内でのプログレッシブ再生を保証するものではありません。

## Shisa ASRモデル設定

Difyの「Config model」画面で、APIキー、APIベースURL、言語、ホットワード、temperature、`top_p`、frequency penalty、repetition penalty、VADを含むShisa ASR専用モデル認証を設定できます。Difyが呼び出しごとにこれらを送るのではなく、プラグインが選択されたモデル認証の明示的な値だけをASRリクエストへ追加します。

> **注意:** これはモデル単位の設定であり、Chatflowパラメーターではありません。Dify標準マイクはワークスペースのデフォルト音声認識モデルを使うため、選択したShisa ASRモデル認証を使う全アプリに同じ値が適用されます。空欄では値を送らず、Shisa APIデフォルトを使用します。

アプリまたはノードごとに変更する場合は、別のShisa AI Toolsプラグインの「音声を文字起こし」を使用してください。
