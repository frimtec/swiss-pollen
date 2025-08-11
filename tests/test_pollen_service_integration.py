import unittest

from swiss_pollen import PollenService, EXPECTED_DATA_VERSION


class TestPollenServiceIntegration(unittest.TestCase):
    def test_backend_version_is_expected(self):
        result = PollenService.load()

        self.assertEqual(
            EXPECTED_DATA_VERSION,
            result.backend_version,
            msg=f"Unexpected backend version from real service: {result.backend_version}"
        )

if __name__ == "__main__":
    unittest.main()
