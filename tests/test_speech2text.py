import unittest

from models.speech2text.speech2text import ShisaAISpeech2TextModel


class TranscriptNormalizationTests(unittest.TestCase):
    def test_exact_music_marker_becomes_empty(self):
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript("[Music]"), "")
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript(" [MUSIC] "), "")

    def test_other_transcripts_are_preserved_after_trimming(self):
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript(" music "), "music")
        self.assertEqual(ShisaAISpeech2TextModel._normalize_transcript("[Music] hello"), "[Music] hello")


if __name__ == "__main__":
    unittest.main()
