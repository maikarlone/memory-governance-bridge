#!/usr/bin/env python3
"""Offline tests for the reference bridge and adapter."""
import importlib.util
import pathlib
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BridgeTests(unittest.TestCase):
    def test_disabled_by_default_and_no_network(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            mod = load(ROOT / "bridge" / "memory_bridge.py", "test_bridge_disabled")
            with mock.patch("urllib.request.urlopen") as urlopen:
                result = mod.recall({"query": "anything", "limit": 3})
                payload = __import__("json").loads(result["content"][0]["text"])
                self.assertEqual(payload["status"], "disabled")
                urlopen.assert_not_called()

    def _enabled_bridge(self, payload):
        with mock.patch.dict("os.environ", {"MEMORY_BRIDGE_ENABLED": "1",
                                             "MEMORY_CLIENT_TOKEN": "demo"}, clear=True):
            mod = load(ROOT / "bridge" / "memory_bridge.py", "test_bridge_enabled")

        class Resp:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return __import__("json").dumps(payload).encode()

        with mock.patch("urllib.request.urlopen", return_value=Resp()):
            return mod.recall({"query": "q", "limit": 3})

    def test_no_direct_answer_status(self):
        result = self._enabled_bridge({
            "no_direct_answer": True, "low_relevance": False,
            "items": [{"id": "m1", "content": "adjacent", "score": 0.9}]})
        payload = __import__("json").loads(result["content"][0]["text"])
        self.assertEqual(payload["status"], "no_direct_answer")
        self.assertIsNone(payload["conclusion"])
        self.assertIsNone(payload["record_id"])
        self.assertEqual(payload["data"]["items"][0]["content"], "adjacent")

    def test_low_relevance_status(self):
        result = self._enabled_bridge({
            "no_direct_answer": False, "low_relevance": True,
            "items": [{"id": "m1", "content": "weak", "score": 0.1}]})
        payload = __import__("json").loads(result["content"][0]["text"])
        self.assertEqual(payload["status"], "low_relevance")
        self.assertIsNone(payload["conclusion"])
        self.assertIsNone(payload["record_id"])


class AdapterTests(unittest.TestCase):
    def setUp(self):
        mod = load(ROOT / "adapter" / "adapter.py", "test_adapter")
        self.adapter = mod.Adapter(
            "http://127.0.0.1:18080",
            ROOT / "examples" / "data",
            ROOT / "examples" / "clients.example.json",
            ROOT / "examples" / "policy.example.json",
        )

    def test_hashed_client_lookup(self):
        self.assertEqual(self.adapter.lookup_client("demo-desktop-token")["client"], "desktop-agent")
        self.assertIsNone(self.adapter.lookup_client("wrong-token"))

    def apply(self, query, content, score=0.9):
        items = [{"id": "m_example_001", "content": content, "score": score}]
        return self.adapter.apply(items, query, {"project": "example-project"})

    def test_positive_direct_answer(self):
        rel = self.apply("What is the sample project codename?", "The sample project codename is SMP.")
        self.assertFalse(rel["no_direct_answer"])

    def test_negative_office_address(self):
        rel = self.apply("What is the sample project office address?", "The sample project codename is SMP.")
        self.assertTrue(rel["no_direct_answer"])

    def test_low_relevance_marker(self):
        rel = self.apply("What is the sample project codename?", "unrelated", score=0.1)
        self.assertTrue(rel["low_relevance"])


if __name__ == "__main__":
    unittest.main()
