# Shisa AI Difyモデルプロバイダー

Shisa AIのLLM、音声認識（ASR）、音声合成（TTS）をDifyから直接利用するためのモデルプロバイダープラグインです。

## 対応機能

- Shisa V2.1 Flash / Pro LLM
- Shisa ASR
- Shisa TTS（Dify標準連携ではMP3）
- Difyが対応する画面での動的な音声一覧取得

翻訳APIは、Difyに標準の翻訳モデルインターフェースがないため、別リポジトリの [Shisa AI Tools](https://github.com/shisa-ai/dify-plugin-shisa-ai-tools) から提供します。

APIキーは [Shisa Platform](https://platform.shisa.ai/) で取得してください。料金、利用上限、モデル提供状況などの最新情報は、[Shisa Platform](https://platform.shisa.ai/) と [公式ドキュメント](https://docs.shisa.ai/) を確認してください。

Dify Workflow内の音声ファイルは後続ノードへ渡る前に完了データとしてバッファされるため、ワークフロー内でのプログレッシブ再生を保証するものではありません。
