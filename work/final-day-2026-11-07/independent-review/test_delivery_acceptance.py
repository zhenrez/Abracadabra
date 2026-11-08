"""Independent acceptance orchestration checks; no result files are mutated."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import run_delivery


class DeliveryAcceptanceTests(unittest.TestCase):
    def test_zero_collected_suite_cannot_count_as_passed_acceptance(self):
        completed=subprocess.CompletedProcess([],0,'','Ran 0 tests in 0.000s\n\nOK\n')
        argv=[sys.executable,'-B','-m','unittest','discover','-s','empty','-p','test_*.py','-v']
        with patch.object(run_delivery.subprocess,'run',return_value=completed),patch.object(run_delivery,'save'):
            with self.assertRaises(RuntimeError):run_delivery.command('required-unit-suite',argv)


if __name__=='__main__':unittest.main()
