#!/usr/bin/env python3
"""Read-only MCP stdio bridge for the reference memory adapter.

Design invariants:
- disabled unless MEMORY_BRIDGE_ENABLED=1
- no network request when disabled
- client credential only from environment
"""
from __future__ import annotations
import json, os, sys, urllib.error, urllib.request

ADAPTER = os.environ.get("MEMORY_ADAPTER_URL", "http://127.0.0.1:18081").rstrip("/")
TOKEN = os.environ.get("MEMORY_CLIENT_TOKEN", "")
ENABLED = os.environ.get("MEMORY_BRIDGE_ENABLED", "0") == "1"
DISABLED_MESSAGE = "memory bridge is disabled; set MEMORY_BRIDGE_ENABLED=1 after reviewing the read-only policy"


def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def recall(args):
    if not ENABLED:
        return {"content": [{"type": "text", "text": json.dumps(
            {"status": "disabled", "message": DISABLED_MESSAGE}, ensure_ascii=False)}],
            "isError": False}
    body = json.dumps({"query": args.get("query", ""), "limit": min(int(args.get("limit", 5)), 5)},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ADAPTER + "/v1/recall", data=body, method="POST",
        headers={"content-type": "application/json", "x-client-token": TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read().decode("utf-8")
    except Exception as e:
        if isinstance(e, (urllib.error.URLError, ConnectionError, TimeoutError)):
            msg = "memory service is unavailable; start it and retry"
        else:
            msg = f"adapter error: {type(e).__name__}"
        return {"content": [{"type": "text", "text": json.dumps(
            {"status": "service_down", "message": msg}, ensure_ascii=False)}], "isError": True}
    try:
        payload = json.loads(data)
    except Exception:
        return {"content": [{"type": "text", "text": json.dumps(
            {"status": "service_down", "message": "adapter returned non-JSON"}, ensure_ascii=False)}], "isError": True}
    items = payload.get("items") if isinstance(payload, dict) else None
    if items == []:
        result = {"status": "no_match", "conclusion": "no matching memory", "record_id": None,
                  "provenance": None, "score": None, "low_relevance": False, "data": payload}
    elif isinstance(items, list):
        top = items[0] if items else {}
        result = {"status": "ok", "conclusion": top.get("content", ""),
                  "record_id": top.get("record_id") or top.get("id"),
                  "provenance": top.get("provenance"), "score": top.get("score"),
                  "low_relevance": bool(payload.get("low_relevance") or top.get("low_relevance")),
                  "no_direct_answer": bool(payload.get("no_direct_answer") or top.get("no_direct_answer")),
                  "data": payload}
    else:
        return {"content": [{"type": "text", "text": json.dumps(
            {"status": "service_down", "message": "adapter response missing items"}, ensure_ascii=False)}], "isError": True}
    return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "isError": False}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        mid = msg.get("id")
        method = msg.get("method")
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                "serverInfo": {"name": "memory-governance-bridge", "version": "0.1.0"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": [{
                "name": "recall_memory", "description": "Read-only memory recall.",
                "inputSchema": {"type": "object", "properties": {
                    "query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 5}},
                    "required": ["query"], "additionalProperties": False}}]}})
        elif method == "tools/call":
            params = msg.get("params") or {}
            if params.get("name") != "recall_memory":
                send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "unknown tool"}})
            else:
                send({"jsonrpc": "2.0", "id": mid, "result": recall(params.get("arguments") or {})})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        elif mid is not None:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}})


if __name__ == "__main__":
    main()
