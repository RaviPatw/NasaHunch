import unittest
from unittest.mock import patch, MagicMock, mock_open
import auto_mantain
import builtins


class TestAutoMaintian(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_log(self, mock_file):
        auto_mantain.log("Test message")
        mock_file.assert_called_once_with(auto_mantain.LOG_FILE, "a")
        handle = mock_file()
        written = handle.write.call_args[0][0]
        self.assertIn("Test message", written)

    @patch("auto_mantain.log")
    @patch("subprocess.run")
    def test_run_success(self, mock_run, mock_log):
        mock_run.return_value = MagicMock(
            stdout="OK",
            stderr="",
            returncode=0
        )
        code, out = auto_mantain.run(["echo", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "OK")

    @patch("auto_mantain.log")
    @patch("subprocess.run", side_effect=Exception("FAIL"))
    def test_run_exception(self, mock_run, mock_log):
        code, out = auto_mantain.run(["bad"])
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)

    @patch("auto_mantain.run", return_value=(0, "backup ok"))
    @patch("auto_mantain.log")
    def test_backup_etc_success(self, mock_log, mock_run):
        auto_mantain.backup_etc()
        mock_run.assert_called_once()

    @patch("auto_mantain.run", return_value=(1, "err"))
    @patch("auto_mantain.log")
    def test_backup_etc_failure(self, mock_log, mock_run):
        auto_mantain.backup_etc()
        mock_log.assert_any_call("WARNING: /etc backup failed, continuing anyway.")

    @patch("auto_mantain.run", return_value=(1, "failed"))
    @patch("auto_mantain.log")
    def test_update_package_lists_failure(self, mock_log, mock_run):
        auto_mantain.update_package_lists()
        mock_log.assert_any_call("ERROR: apt-get update failed.")

    @patch("auto_mantain.run", return_value=(0, "linux-image-6.1 installed\nother stuff"))
    @patch("auto_mantain.log")
    def test_upgrade_packages_kernel_update(self, mock_log, mock_run):
        kernel_updated = auto_mantain.upgrade_packages()
        self.assertTrue(kernel_updated)

    @patch("auto_mantain.run", return_value=(0, "nothing interesting"))
    @patch("auto_mantain.log")
    def test_upgrade_packages_no_kernel_update(self, mock_log, mock_run):
        kernel_updated = auto_mantain.upgrade_packages()
        self.assertFalse(kernel_updated)

    @patch("auto_mantain.run")
    @patch("auto_mantain.log")
    def test_cleanup(self, mock_log, mock_run):
        auto_mantain.cleanup()
        self.assertEqual(mock_run.call_count, 2)

    @patch("auto_mantain.run")
    @patch("auto_mantain.log")
    def test_reboot_system(self, mock_log, mock_run):
        auto_mantain.reboot_system()
        mock_run.assert_called_once_with(["systemctl", "reboot"])

    @patch("auto_mantain.reboot_system")
    @patch("auto_mantain.cleanup")
    @patch("auto_mantain.upgrade_packages", return_value=True)
    @patch("auto_mantain.update_package_lists")
    @patch("auto_mantain.backup_etc")
    @patch("auto_mantain.ensure_log_file")
    @patch("auto_mantain.time.sleep")  # prevent real sleep
    @patch("auto_mantain.log")
    def test_main_with_kernel_update(
        self, mock_log, mock_sleep, mock_ensure, mock_backup,
        mock_update, mock_upgrade, mock_cleanup, mock_reboot
    ):
        auto_mantain.main()
        mock_reboot.assert_called_once()

    @patch("auto_mantain.reboot_system")
    @patch("auto_mantain.cleanup")
    @patch("auto_mantain.upgrade_packages", return_value=False)
    @patch("auto_mantain.update_package_lists")
    @patch("auto_mantain.backup_etc")
    @patch("auto_mantain.ensure_log_file")
    @patch("auto_mantain.log")
    def test_main_no_kernel_update(
        self, mock_log, mock_ensure, mock_backup,
        mock_update, mock_upgrade, mock_cleanup, mock_reboot
    ):
        auto_mantain.main()
        mock_reboot.assert_not_called()


if __name__ == "__main__":
    unittest.main()
