import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from subscope.normalize import extract_hosts, in_scope, normalize_domain


class NormalizeTests(unittest.TestCase):
    def test_normalize_domain_strips_scheme_port_and_wildcard(self):
        self.assertEqual(normalize_domain("https://*.WWW.Example.com:443/path"), "www.example.com")

    def test_in_scope_uses_label_boundary(self):
        self.assertTrue(in_scope("a.example.com", "example.com"))
        self.assertFalse(in_scope("badexample.com", "example.com"))

    def test_extract_hosts_filters_scope_and_wildcards(self):
        text = "Found *.api.example.com and badexample.com plus www.example.com."
        self.assertEqual(extract_hosts(text, "example.com"), {"api.example.com", "www.example.com"})


if __name__ == "__main__":
    unittest.main()
