#!/usr/bin/env python3
"""Start the synthetic mock core only. No private data, no real service."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mock"))
from mock_core import H  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402

if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 18080), H).serve_forever()
