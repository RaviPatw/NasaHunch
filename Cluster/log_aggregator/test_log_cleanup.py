import unittest
from unittest.mock import patch, MagicMock, mock_open
import log_cleanup
import os

class TestLogCleanup(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=b"data")
    @patch("gzip.open")
    @patch("shutil.copyfileobj")
    @patch("os.remove")
    def test_compress_file(self, mock_remove, mock_copy, mock_gzip, mock_file):
        log_file = "/var/log/test.log"
        log_cleanup.compress_file(log_file)
        mock_file.assert_called_once_with(log_file, "rb")
        mock_gzip.assert_called_once_with(log_file + ".gz", "wb")
        mock_copy.assert_called_once()
        mock_remove.assert_called_once_with(log_file)

    @patch("log_cleanup.compress_file")
    @patch("os.path.getsize")
    @patch("os.path.getmtime")
    @patch("os.remove")
    @patch("os.walk")
    def test_cleanup_logs(self, mock_walk, mock_remove, mock_mtime, mock_size, mock_compress):
        mock_walk.return_value = [
            ("/var/log", [], ["old.log", "large.log", "skip.gz"])
        ]


        current_time = 1_700_000_000
        with patch("time.time", return_value=current_time):
            cutoff = current_time - (log_cleanup.MAX_DAYS * 86400)

            def mtime_side_effect(path):
                if "old.log" in path:
                    return cutoff - 10  
                else:
                    return cutoff + 10  

            mock_mtime.side_effect = mtime_side_effect
            mock_size.side_effect = lambda path: 100_000_000 if "large.log" in path else 1_000

            log_cleanup.cleanup_logs()

            mock_remove.assert_any_call("/var/log/old.log")
            mock_compress.assert_called_once_with("/var/log/large.log")
            self.assertNotIn(("/var/log/skip.gz"), [c[0][0] for c in mock_remove.call_args_list])

    @patch("os.walk", return_value=[])
    def test_cleanup_logs_empty(self, mock_walk):
        log_cleanup.cleanup_logs()  


if __name__ == "__main__":
    unittest.main()
