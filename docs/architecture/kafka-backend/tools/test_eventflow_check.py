"""Tests for eventflow_check.py: python3 -m unittest discover -s docs/architecture/kafka-backend/tools"""
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / "eventflow_check.py"
FIELDS = ["topic", "owner", "key", "partitions", "cleanup", "retention", "class", "data_class", "consumers", "note"]


def row(topic, owner, consumers, key="paymentId", cleanup="delete", retention="7d", data_class="pseudonymous"):
    return {"topic": topic, "owner": owner, "key": key, "partitions": "6", "cleanup": cleanup,
            "retention": retention, "class": "A-critical", "data_class": data_class, "consumers": consumers, "note": ""}


def run(rows):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    try:
        proc = subprocess.run([sys.executable, str(CHECK), f.name, "--strict"], capture_output=True, text=True)
    finally:
        Path(f.name).unlink()
    return proc.returncode, proc.stdout


class EventflowCheckTest(unittest.TestCase):
    def test_project_catalogue_passes(self):
        proc = subprocess.run([sys.executable, str(CHECK), str(HERE / "topics.csv"), "--strict"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_good_catalogue_passes(self):
        code, out = run([row("ev.payment.a.v1", "payments", "loyalty")])
        self.assertEqual(code, 0, out)

    def test_second_writer_fails_r1(self):
        code, out = run([row("ev.payment.a.v1", "payments", "loyalty"), row("ev.payment.a.v1", "invoicing", "loyalty")])
        self.assertEqual(code, 1)
        self.assertIn("R1 ev.payment.a.v1: declared twice", out)

    def test_personal_identifier_inside_key_fails_r3(self):
        for key in ["vin", "vehicleVin", "driver_phone", "ownerEmail", "nationalId", "msisdn", "licensePlate", "mobileNo", "homeAddress"]:
            code, out = run([row("ev.payment.a.v1", "payments", "loyalty", key=key)])
            self.assertEqual(code, 1, key)
            self.assertIn("R3", out)

    def test_reference_keys_pass_r3(self):
        for key in ["paymentId", "driverRef", "evseUid", "tariffUid", "companyId"]:
            code, out = run([row("ev.payment.a.v1", "payments", "loyalty", key=key)])
            self.assertEqual(code, 0, f"{key}: {out}")

    def test_undeclared_loop_fails_r7(self):
        code, out = run([row("ev.payment.a.v1", "payments", "loyalty"), row("ev.loyalty.b.v1", "loyalty", "payments")])
        self.assertEqual(code, 1)
        self.assertIn("R7 undeclared event loop: loyalty <-> payments", out)


if __name__ == "__main__":
    unittest.main()
