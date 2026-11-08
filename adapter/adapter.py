#!/usr/bin/env python3
"""Read-only adapter: token-bound identity, result normalization, observe-mode markers."""
from __future__ import annotations
import argparse, json, os, re, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def post(base, path, body, headers, timeout=30):
    req = urllib.request.Request(base.rstrip("/") + path,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"), method="POST",
        headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


class JsonlIndex:
    def __init__(self, directory):
        self.dir = Path(directory); self.records = {}; self.lock = threading.Lock(); self.refresh()

    def refresh(self):
        with self.lock:
            for path in sorted(self.dir.glob("*.jsonl")):
                for line in path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if obj.get("id"):
                        self.records[obj["id"]] = obj
        return self

    def get(self, rid):
        return self.records.get(rid)


class Adapter:
    def __init__(self, upstream, data_dir, clients, policy):
        self.upstream = upstream; self.data_dir = Path(data_dir)
        self.policy = json.loads(Path(policy).read_text(encoding="utf-8"))
        self.clients = json.loads(Path(clients).read_text(encoding="utf-8"))
        self.l1 = JsonlIndex(self.data_dir / "records")
        self.l0 = JsonlIndex(self.data_dir / "conversations")
        self.headers = {
            "Authorization": "Bearer " + os.environ.get("MEMORY_CORE_API_KEY", ""),
            "x-tdai-service-id": os.environ.get("MEMORY_SERVICE_ID", "default"),
            "x-tdai-user-key": os.environ.get("MEMORY_CORE_USER_KEY", ""),
        }

    def hydrate(self, items):
        out = []
        for it in items:
            rid = it.get("id"); rec = self.l1.get(rid)
            sources = rec.get("source_message_ids", []) if rec else []
            found = {s: self.l0.get(s) for s in sources}
            prov = "message_level" if rec and sources and all(found.values()) else ("broken" if sources else "missing")
            x = dict(it); x["record_id"] = rid; x["source_message_ids"] = sources
            x["sources"] = [{"id": s, "exists": bool(found[s]), "role": (found[s] or {}).get("role"),
                             "summary": ((found[s] or {}).get("content") or "")[:120]} for s in sources]
            x["provenance"] = prov
            out.append(x)
        return out

    def core(self, text, terms):
        s = (text or "").lower()
        for t in sorted((x for x in terms if x), key=len, reverse=True):
            s = s.replace(str(t).lower(), " ")
        stop = {"a", "an", "the", "is", "are", "was", "were", "what", "which", "who",
                "whom", "whose", "of", "to", "in", "on", "for", "and", "or", "please",
                "about", "does", "do", "did", "this", "that", "it", "be", "with"}
        words = [w for w in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]+", s) if w not in stop]
        return " ".join(words)

    def grams(self, text):
        g = set()
        for token in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]+", text):
            if re.fullmatch(r"[a-z0-9_]+", token):
                g.add(token)
            else:
                g.update(token[i:i + 2] for i in range(max(0, len(token) - 1)))
        return g

    def apply(self, items, query, binding):
        floor = float(self.policy.get("relevance_floor", 0.0))
        direct = self.policy.get("direct_answer", {}) or {}
        threshold = float(direct.get("answer_threshold", 0.34))
        terms = direct.get("project_terms", []) or []
        qgrams = self.grams(self.core(query, terms))
        for it in items:
            try:
                score = float(it.get("score", 0) or 0)
            except Exception:
                score = 0.0
            match = len(qgrams & self.grams(self.core(it.get("content") or "", terms))) / len(qgrams) if qgrams else 0.0
            it["score"] = score
            it["answer_match"] = round(match, 4)
            it["no_direct_answer"] = bool(match < threshold)
            it["low_relevance"] = bool(score < floor)
        return {"relevance_floor": floor, "answer_threshold": threshold,
                "no_direct_answer": not any(not x.get("no_direct_answer") for x in items),
                "low_relevance": bool(items and all(x.get("low_relevance") for x in items))}

    def search(self, body, binding):
        st, r = post(self.upstream, "/v3/atomic/search", {
            "query": body.get("query", ""), "limit": min(int(body.get("limit", 5)), 5),
            "team_id": binding["team_id"], "agent_id": binding["agent_id"], "user_id": binding["user_id"]},
            self.headers)
        items = (r.get("data") or {}).get("items", []) if r.get("code") == 0 else []
        hydrated = self.hydrate(items)
        rel = self.apply(hydrated, body.get("query", ""), binding)
        return {"client": binding["client"], "project": binding["project"],
                "requested_identity_ignored": bool(body.get("team_id") or body.get("user_id") or body.get("agent_id")),
                "relevance_floor": rel["relevance_floor"], "answer_threshold": rel["answer_threshold"],
                "no_direct_answer": rel["no_direct_answer"], "low_relevance": rel["low_relevance"],
                "items": hydrated, "error": None if r.get("code") == 0 else r}


def handler(ad):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, obj):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status); self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(data))); self.end_headers(); self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                return self.reply(200, {"ok": True, "mode": "read-only", "clients": len(ad.clients)})
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            n = int(self.headers.get("content-length", "0"))
            try:
                body = json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception:
                return self.reply(400, {"error": "invalid json"})
            if self.path in ("/v1/write", "/v1/remember", "/v1/capture"):
                return self.reply(405, {"error": "read_only"})
            if self.path != "/v1/recall":
                return self.reply(404, {"error": "not found"})
            token = self.headers.get("x-client-token", "")
            binding = ad.clients.get(token)
            if not binding:
                return self.reply(401, {"error": "invalid client token"})
            try:
                return self.reply(200, ad.search(body, binding))
            except Exception as e:
                return self.reply(502, {"error": type(e).__name__})

    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", default=os.environ.get("MEMORY_CORE_URL", "http://127.0.0.1:18080"))
    ap.add_argument("--data-dir", default=os.environ.get("MEMORY_DATA_DIR", "examples/data"))
    ap.add_argument("--clients", default=os.environ.get("MEMORY_CLIENTS", "examples/clients.example.json"))
    ap.add_argument("--policy", default=os.environ.get("MEMORY_POLICY", "examples/policy.example.json"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("MEMORY_ADAPTER_PORT", "18081")))
    a = ap.parse_args()
    ad = Adapter(a.upstream, a.data_dir, a.clients, a.policy)
    ThreadingHTTPServer(("127.0.0.1", a.port), handler(ad)).serve_forever()


if __name__ == "__main__":
    main()
