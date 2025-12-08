import unittest
from unittest.mock import patch, mock_open, MagicMock
import time
import json

import maintenance_report

class TestMaintenanceReport(unittest.TestCase):

    @patch("subprocess.check_output")
    def test_get_cpu_temp_vcgencmd(self, mock_subproc):
        mock_subproc.return_value = b"temp=48.0'C\n"
        temp = maintenance_report.get_cpu_temp()
        self.assertEqual(temp, 48.0)

    @patch("psutil.sensors_temperatures")
    @patch("subprocess.check_output", side_effect=Exception("vcgencmd not found"))
    def test_get_cpu_temp_fallback(self, mock_subproc, mock_sensors):
        mock_sensors.return_value = {"cpu_thermal": [MagicMock(current=55.5)]}
        temp = maintenance_report.get_cpu_temp()
        self.assertEqual(temp, 55.5)

    @patch("psutil.boot_time", return_value=time.time() - 100)
    def test_get_uptime(self, mock_boot):
        uptime = maintenance_report.get_uptime()
        self.assertAlmostEqual(uptime, 100, delta=1)

    @patch("subprocess.check_output")
    def test_get_smart_status_ok(self, mock_subproc):
        mock_subproc.return_value = b"SMART overall-health self-assessment test result: PASSED"
        status = maintenance_report.get_smart_status()
        self.assertEqual(status, "OK")

    @patch("subprocess.check_output")
    def test_get_smart_status_warning(self, mock_subproc):
        mock_subproc.return_value = b"SMART overall-health test result: FAILED"
        status = maintenance_report.get_smart_status()
        self.assertEqual(status, "WARNING")

    @patch("subprocess.check_output", side_effect=Exception("smartctl missing"))
    def test_get_smart_status_unknown(self, mock_subproc):
        status = maintenance_report.get_smart_status()
        self.assertEqual(status, "UNKNOWN")

    @patch("maintenance_report.push_to_gateway")
    @patch("psutil.disk_usage")
    @patch("psutil.virtual_memory")
    @patch("psutil.cpu_percent")
    @patch("maintenance_report.get_smart_status", return_value="OK")
    @patch("maintenance_report.get_uptime", return_value=123)
    @patch("maintenance_report.get_cpu_temp", return_value=40.0)
    @patch("builtins.open", new_callable=mock_open)
    def test_main(
        self,
        mock_file,
        mock_temp,
        mock_uptime,
        mock_smart,
        mock_cpu_percent,
        mock_vm,
        mock_disk,
        mock_push
    ):
        mock_cpu_percent.return_value = 20.0
        mock_vm.return_value.percent = 50.0
        mock_disk.return_value.percent = 75.0

        maintenance_report.main()

        # Verify the JSON was written
        mock_file.assert_called_once()
        handle = mock_file()
        written_line = handle.write.call_args[0][0]
        data = json.loads(written_line)

        self.assertEqual(data["cpu_temp"], 40.0)
        self.assertEqual(data["cpu_usage"], 20.0)
        self.assertEqual(data["mem_usage"], 50.0)
        self.assertEqual(data["disk_usage"], 75.0)
        self.assertEqual(data["uptime"], 123)
        self.assertEqual(data["smart_status"], "OK")

        # Prometheus push was called
        mock_push.assert_called_once()


if __name__ == "__main__":
    unittest.main()
