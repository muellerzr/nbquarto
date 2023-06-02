import subprocess
import tempfile
import unittest


class TestCLI(unittest.TestCase):
    def test_example_processor(self):
        """
        Test that the example processor works
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            args = [
                "--config_file",
                "tests/test_artifacts/single_processor.yaml",
                "--notebook_file",
                "tests/test_artifacts/test_example.ipynb",
                "--output_folder",
                tmpdir,
            ]
            subprocess.run(["nbquarto-process"] + args)
            with open(f"{tmpdir}/test_artifacts/test_example.qmd") as f:
                self.assertIn("# This code has been processed!", f.read())
