import unittest
from unittest.mock import patch, MagicMock, mock_open
import time
import os
import backup_data


class TestBackupData(unittest.TestCase):

    @patch("os.makedirs")
    def test_ensure_dir(self, mock_makedirs):
        backup_data.ensure_dir("/test/path")
        mock_makedirs.assert_called_once_with("/test/path", exist_ok=True)

    @patch("subprocess.run")
    @patch("os.path.exists", return_value=True)
    @patch("backup_data.datetime")
    def test_create_backup(self, mock_datetime, mock_exists, mock_run):
        mock_datetime.now.return_value.strftime.return_value = "20250101_120000"

        backup_data.create_backup()

        expected_backup_path = os.path.join(backup_data.BACKUP_DIR, "backup_20250101_120000.tar.gz")
        expected_cmd = ["tar", "-czf", expected_backup_path] + backup_data.SOURCE_DIRS

        mock_run.assert_called_once_with(expected_cmd, check=True)

    @patch("os.remove")
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("os.path.getmtime")
    @patch("os.listdir")
    def test_cleanup_old_backups(
        self, mock_listdir, mock_getmtime, mock_isdir, mock_isfile, mock_remove
    ):
        mock_listdir.return_value = ["old.tar.gz", "new.tar.gz"]

        old_time = time.time() - (20 * 86400)
        new_time = time.time() - (1 * 86400)

        mock_getmtime.side_effect = [old_time, new_time]

        backup_data.cleanup_old_backups()

        mock_remove.assert_called_once_with(os.path.join(backup_data.BACKUP_DIR, "old.tar.gz"))

    @patch("backup_data.cleanup_old_backups")
    @patch("backup_data.create_backup")
    @patch("backup_data.ensure_dir")
    def test_main(self, mock_ensure, mock_backup, mock_cleanup):
        backup_data.main()
        mock_ensure.assert_called_once_with(backup_data.BACKUP_DIR)
        mock_backup.assert_called_once()
        mock_cleanup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
