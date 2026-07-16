import asyncio
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from engine import Enumerator
from models import Candidate
from sources import Source


class StaticSource(Source):
    name = "static"

    async def enumerate(self, domain, http):
        return [
            Candidate("api.example.com", self.name),
            Candidate("badexample.com", self.name),
            Candidate("example.com", self.name),
        ]


class EngineTests(unittest.TestCase):
    def test_engine_deduplicates_and_filters_scope(self):
        findings, errors = asyncio.run(Enumerator(sources=[StaticSource()]).run("example.com"))
        self.assertEqual(errors, {})
        self.assertEqual([finding.host for finding in findings], ["api.example.com"])
        self.assertEqual(findings[0].sources, {"static"})


if __name__ == "__main__":
    unittest.main()
