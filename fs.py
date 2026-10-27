#!/usr/bin/env python3
"""Savdo Daftari Firestore helper (REST, no SDK needed).

Usage:
  python3 fs.py list <collection> [limit]            -> JSON {id: doc}
  python3 fs.py get <collection> <id>                -> JSON doc or null
  python3 fs.py set <collection> <id> '<json>'       -> create/replace
  python3 fs.py update <collection> <id> '<json>'    -> merge fields
  python3 fs.py setfile <collection> <id> <file.json>
  python3 fs.py batch <file.json>   file = [{"col":..,"id":..,"data":{..},"merge":true}, ...]
  python3 fs.py query <collection> <field> <op> <value_json> [limit]   op: EQUAL, LESS_THAN, GREATER_THAN_OR_EQUAL ...
"""
import json, sys, urllib.request, urllib.parse

PROJECT = "savdo-daftari-574fe"
API_KEY = "AIzaSyCKaesQUGHlDZ1HExG9yrK0Tk4ExV_ChCo"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"


def _req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + "key=" + API_KEY, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "null")


def enc(v):
    if v is None: return {"nullValue": None}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, list): return {"arrayValue": {"values": [enc(x) for x in v]}}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: enc(x) for k, x in v.items()}}}
    return {"stringValue": str(v)}


def dec(v):
    if "nullValue" in v: return None
    if "booleanValue" in v: return v["booleanValue"]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return v["doubleValue"]
    if "stringValue" in v: return v["stringValue"]
    if "timestampValue" in v: return v["timestampValue"]
    if "arrayValue" in v: return [dec(x) for x in v["arrayValue"].get("values", [])]
    if "mapValue" in v: return {k: dec(x) for k, x in v["mapValue"].get("fields", {}).items()}
    return None


def doc_to_py(d):
    return {k: dec(v) for k, v in d.get("fields", {}).items()}


def doc_id(d):
    return d["name"].rsplit("/", 1)[1]


def list_col(col, limit=1000):
    out, token = {}, None
    while True:
        url = f"{BASE}/{col}?pageSize={min(limit, 300)}" + (f"&pageToken={token}" if token else "")
        r = _req("GET", url)
        for d in r.get("documents", []):
            out[doc_id(d)] = doc_to_py(d)
        token = r.get("nextPageToken")
        if not token or len(out) >= limit: break
    return out


def get(col, did):
    try:
        return doc_to_py(_req("GET", f"{BASE}/{col}/{urllib.parse.quote(did, safe='')}"))
    except urllib.error.HTTPError as e:
        if e.code == 404: return None
        raise


def set_doc(col, did, data, merge=False):
    url = f"{BASE}/{col}/{urllib.parse.quote(did, safe='')}"
    if merge:
        url += "?" + "&".join("updateMask.fieldPaths=" + urllib.parse.quote(k, safe="") for k in data)
    return doc_id(_req("PATCH", url, {"fields": {k: enc(v) for k, v in data.items()}}))


def batch(items):
    writes = []
    for it in items:
        w = {"update": {"name": f"projects/{PROJECT}/databases/(default)/documents/{it['col']}/{it['id']}",
                        "fields": {k: enc(v) for k, v in it["data"].items()}}}
        if it.get("merge"):
            w["updateMask"] = {"fieldPaths": list(it["data"].keys())}
        writes.append(w)
    n = 0
    for i in range(0, len(writes), 400):
        _req("POST", f"{BASE}:commit", {"writes": writes[i:i + 400]})
        n += len(writes[i:i + 400])
    return n


def query(col, field, op, value, limit=1000):
    body = {"structuredQuery": {"from": [{"collectionId": col}],
            "where": {"fieldFilter": {"field": {"fieldPath": field}, "op": op, "value": enc(value)}},
            "limit": limit}}
    r = _req("POST", f"{BASE}:runQuery", body)
    return {doc_id(x["document"]): doc_to_py(x["document"]) for x in r if "document" in x}


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else ""
    if cmd == "list": print(json.dumps(list_col(a[1], int(a[2]) if len(a) > 2 else 1000), ensure_ascii=False))
    elif cmd == "get": print(json.dumps(get(a[1], a[2]), ensure_ascii=False))
    elif cmd == "set": print(set_doc(a[1], a[2], json.loads(a[3])))
    elif cmd == "update": print(set_doc(a[1], a[2], json.loads(a[3]), merge=True))
    elif cmd == "setfile": print(set_doc(a[1], a[2], json.load(open(a[3]))))
    elif cmd == "batch": print(batch(json.load(open(a[1]))))
    elif cmd == "query": print(json.dumps(query(a[1], a[2], a[3], json.loads(a[4]), int(a[5]) if len(a) > 5 else 1000), ensure_ascii=False))
    else: print(__doc__)
