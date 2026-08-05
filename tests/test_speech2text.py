import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from dify_plugin.errors.model import CredentialsValidateFailedError, InvokeBadRequestError

from models.speech2text.speech2text import ShisaAISpeech2TextModel


class TranscriptNormalizationTests(unittest.TestCase):
    def test_exact_music_marker_becomes_empty(self):
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript("[Music]"), "")
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript(" [MUSIC] "), "")

    def test_other_transcripts_are_preserved_after_trimming(self):
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript(" music "), "music")
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript("[Music] hello"), "[Music] hello")


class ModelCredentialASRDefaultsTests(unittest.TestCase):
    def test_blank_defaults_are_not_sent(self):
        self.assertEqual(
            ShisaAISpeech2TextModel._model_asr_defaults(
                {
                    "asr_language": " ",
                    "asr_hotwords": "",
                    "asr_temperature": None,
                }
            ),
            {},
        )

    def test_all_documented_defaults_are_parsed(self):
        self.assertEqual(
            ShisaAISpeech2TextModel._model_asr_defaults(
                {
                    "asr_language": "ja",
                    "asr_hotwords": '["Shisa AI", "Shisa V2.1"]',
                    "asr_temperature": "0.0",
                    "asr_top_p": "0.85",
                    "asr_frequency_penalty": "0.5",
                    "asr_repetition_penalty": "1.05",
                    "asr_vad": "1",
                }
            ),
            {
                "language": "ja",
                "hotwords": ["Shisa AI", "Shisa V2.1"],
                "temperature": 0.0,
                "top_p": 0.85,
                "frequency_penalty": 0.5,
                "repetition_penalty": 1.05,
                "vad": 1,
            },
        )

    def test_hotwords_accept_newlines_and_commas(self):
        self.assertEqual(
            ShisaAISpeech2TextModel._parse_hotwords("Shisa AI\nDify, Shisa ASR"),
            ["Shisa AI", "Dify", "Shisa ASR"],
        )

    def test_invalid_values_fail_before_api_request(self):
        with self.assertRaises(InvokeBadRequestError):
            ShisaAISpeech2TextModel._model_asr_defaults(
                {"asr_temperature": "not-a-number"}
            )
        with self.assertRaises(InvokeBadRequestError):
            ShisaAISpeech2TextModel._parse_hotwords('["valid", 2]')

    def test_asr_defaults_are_in_model_credential_schema_only(self):
        provider = yaml.safe_load(Path("provider/shisa_ai.yaml").read_text(encoding="utf-8"))
        provider_forms = provider["provider_credential_schema"]["credential_form_schemas"]
        self.assertFalse(
            any(form["variable"].startswith("asr_") for form in provider_forms)
        )
        self.assertIn("customizable-model", provider["configurate_methods"])
        model_forms = provider["model_credential_schema"]["credential_form_schemas"]
        asr_forms = [form for form in model_forms if form["variable"].startswith("asr_")]
        self.assertEqual(len(asr_forms), 7)
        for form in asr_forms:
            self.assertFalse(form["required"])
            self.assertIn("MODEL CREDENTIAL", form["label"]["en_US"])
            self.assertIn("モデル認証", form["label"]["ja_JP"])

    def test_model_credential_validation_rejects_invalid_defaults(self):
        model_instance = object.__new__(ShisaAISpeech2TextModel)
        with self.assertRaises(CredentialsValidateFailedError):
            model_instance.validate_credentials(
                "shisa-asr", {"api_key": "test", "asr_vad": "not-an-integer"}
            )

    def test_invoke_merges_model_credential_defaults_into_request(self):
        response = Mock()
        response.json.return_value = {"text": "Shisa AI"}
        credentials = {
            "api_key": "test-key",
            "asr_language": "ja",
            "asr_hotwords": "Shisa AI,Dify",
        }
        with patch.object(ShisaAISpeech2TextModel, "_request", return_value=response) as request:
            model_instance = object.__new__(ShisaAISpeech2TextModel)
            result = model_instance._invoke(
                "shisa-asr", credentials, BytesIO(b"audio")
            )
        self.assertEqual(result, "Shisa AI")
        payload = request.call_args.args[1]
        self.assertEqual(payload["hotwords"], ["Shisa AI", "Dify"])
        self.assertEqual(payload["language"], "ja")
        self.assertTrue(payload["audio"])


if __name__ == "__main__":
    unittest.main()
