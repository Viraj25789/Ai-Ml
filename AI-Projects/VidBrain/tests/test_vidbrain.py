
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from utils.extract_vid_id import extract_video_id
from utils import transcript as transcript_module


class VideoIdTests(unittest.TestCase):

    def test_standard_youtube_url(self):
        self.assertEqual(
            extract_video_id(
                "https://www.youtube.com/watch?v=YimMzb0mHkI"
            ),
            "YimMzb0mHkI",
        )

    def test_short_youtube_url(self):
        self.assertEqual(
            extract_video_id("https://youtu.be/YimMzb0mHkI"),
            "YimMzb0mHkI",
        )

    def test_shorts_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/shorts/YimMzb0mHkI"),
            "YimMzb0mHkI",
        )

    def test_embed_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/embed/YimMzb0mHkI"),
            "YimMzb0mHkI",
        )

    def test_live_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/live/YimMzb0mHkI"),
            "YimMzb0mHkI",
        )

    def test_invalid_url(self):
        self.assertIsNone(
            extract_video_id("https://example.com/video")
        )

    def test_empty_url(self):
        self.assertIsNone(extract_video_id(""))

    def test_invalid_video_id(self):
        self.assertIsNone(
            extract_video_id("https://youtu.be/invalid")
        )


class TranscriptTests(unittest.TestCase):

    def test_invalid_video_id_raises_error(self):
        with self.assertRaises(ValueError):
            transcript_module.get_youtube_transcript("invalid")

    @patch.object(transcript_module, "YouTubeTranscriptApi")
    @patch.object(transcript_module, "_select_best_transcript")
    def test_transcript_is_combined(
        self, mock_select, mock_api_class
    ):
        fake_transcript = SimpleNamespace(
            fetch=lambda: [
                {"text": "Python is easy."},
                {"text": "Learn it step by step."},
            ]
        )

        mock_select.return_value = fake_transcript
        mock_api_class.return_value.list.return_value = []

        result = transcript_module.get_youtube_transcript(
            "YimMzb0mHkI"
        )

        self.assertEqual(
            result,
            "Python is easy. Learn it step by step.",
        )

    @patch.object(transcript_module, "YouTubeTranscriptApi")
    @patch.object(transcript_module, "_select_best_transcript")
    def test_empty_transcript_returns_none(
        self, mock_select, mock_api_class
    ):
        fake_transcript = SimpleNamespace(
            fetch=lambda: [
                {"text": ""},
                {"text": "   "},
            ]
        )

        mock_select.return_value = fake_transcript
        mock_api_class.return_value.list.return_value = []

        result = transcript_module.get_youtube_transcript(
            "YimMzb0mHkI"
        )

        self.assertIsNone(result)

    @patch.object(transcript_module, "YouTubeTranscriptApi")
    def test_youtube_connection_error(
        self, mock_api_class
    ):
        mock_api_class.return_value.list.side_effect = Exception(
            "Connection failed"
        )

        with self.assertRaises(RuntimeError):
            transcript_module.get_youtube_transcript(
                "YimMzb0mHkI"
            )


if __name__ == "__main__":
    unittest.main()
