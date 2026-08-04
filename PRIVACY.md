# Privacy

This plugin sends data directly from the user's Dify workspace to the Shisa AI API in order to provide the selected model service.

Depending on the model used, transmitted data may include:

- LLM prompts, conversation messages, and generation parameters
- Audio uploaded for speech recognition
- Text and voice selections submitted for speech synthesis

The plugin does not intentionally store this content itself. Processing by Shisa AI is governed by the Shisa AI privacy policy and terms available from [platform.shisa.ai](https://platform.shisa.ai/).

API credentials are supplied by the user through Dify's credential configuration and are used only to authenticate requests to the Shisa AI API.
