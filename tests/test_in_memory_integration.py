from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sententia.__main__ import main
from sententia.index import Index
from sententia.storage import Storage


class TestInMemoryIntegration:
    """Integration tests verifying the full flow of main() -> Index() in both modes."""

    @patch("uvicorn.run")
    @patch("sententia.llm.openai.provider.httpx")
    def test_full_flow_in_memory(self, mock_httpx, mock_run, tmp_path):
        """main() without --index-path creates Index with index_path=None and search works."""
        (tmp_path / "doc.md").write_text("# Doc\nSome content here.", encoding="utf-8")

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_httpx.post.return_value = mock_response

        with patch("sententia.index.Index", wraps=Index) as index_spy:
            main(
                [
                    str(tmp_path),
                    "--llm-protocol",
                    "ollama",
                    "--llm-url",
                    "http://localhost:11434",
                    "--llm-model",
                    "llama3",
                ]
            )

            index_spy.assert_called_once()
            call_args = index_spy.call_args
            assert call_args[0][1] is None

    @patch("uvicorn.run")
    @patch("sententia.llm.openai.provider.httpx")
    def test_full_flow_persistent(self, mock_httpx, mock_run, tmp_path):
        """main() with --index-path creates the index file on disk."""
        (tmp_path / "doc.md").write_text("# Doc\nPersistent content.", encoding="utf-8")
        index_file = tmp_path / "test.faiss"

        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "test"}}]}
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_httpx.post.return_value = mock_response

        main(
            [
                str(tmp_path),
                "--index-path",
                str(index_file),
                "--llm-protocol",
                "ollama",
                "--llm-url",
                "http://localhost:11434",
                "--llm-model",
                "llama3",
            ]
        )

        assert index_file.exists()

    def test_in_memory_save_after_search_raises(self, tmp_path: Path) -> None:
        """Index(storage) without index_path: search works, then save() raises ValueError."""
        (tmp_path / "doc.md").write_text("# Doc\nContent to search for.", encoding="utf-8")

        storage = Storage(str(tmp_path))
        index = Index(storage)

        results = index.search("content")
        assert len(results) > 0

        with pytest.raises(ValueError, match="in-memory"):
            index.save()
