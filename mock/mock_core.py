#!/usr/bin/env python3
"""Tiny mock memory core for the reference demo. No production behavior."""
from __future__ import annotations
import json, pathlib, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECORDS = ROOT / "examples" / "data" / "records"


def load():
    out = []
    for p in RECORDS.glob("*.jsonl"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


class H(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"ok": True, "service": "mock-memory-core"})
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/v3/atomic/search":
            return self.reply(404, {"error": "not found"})
        n = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(n).decode("utf-8"))
        q = body.get("query", "")
        terms = [t for t in re.split(r"\s+", q.lower()) if t]
        items = []
        for r in load():
            text = (r.get("content") or "").lower()
            score = sum(1 for t in terms if t and t in text) / max(1, len(terms))
            items.append({"id": r["id"], "content": r["content"], "type": r.get("type", "episodic"),
                          "score": round(0.55 + 0.35 * score, 4), "record_id": r["id"]})
        items.sort(key=lambda x: x["score"], reverse=True)
        self.reply(200, {"code": 0, "data": {"items": items[:min(int(body.get("limit", 5)), 5)]}})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 18080), H).serve_forever()
