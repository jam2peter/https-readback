#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

ROOT_RE=re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SLUG_RE=re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


@dataclass(frozen=True)
class Evidence:
    url: str
    http_code: int
    body_sha256: str
    body_bytes: int
    expectation: str
    passed: bool


def resolve_url(base_url: str, target: str, allowed_roots: list[str]) -> str:
    base=urllib.parse.urlsplit(base_url)
    if base.scheme!="https" or not base.hostname:
        raise ValueError("base-url must be absolute HTTPS")
    if base.username or base.password:
        raise ValueError("base-url userinfo is not allowed")
    if base.query or base.fragment:
        raise ValueError("base-url query/fragment is not allowed")
    if not all(ROOT_RE.fullmatch(x) for x in allowed_roots):
        raise ValueError("allowed root invalid")
    parts=target.split("/")
    if len(parts)!=2 or not ROOT_RE.fullmatch(parts[0]) or not SLUG_RE.fullmatch(parts[1]):
        raise ValueError("target must match <root>/<slug>")
    if parts[0] not in allowed_roots:
        raise ValueError("target root is not allowlisted")
    prefix=base.path.rstrip("/")
    path=f"{prefix}/{parts[0]}/{parts[1]}/"
    return urllib.parse.urlunsplit(("https",base.netloc,path,"",""))


def fetch(url: str, timeout: int=30, max_bytes: int=8*1024*1024) -> tuple[int,bytes]:
    request=urllib.request.Request(url,method="GET",headers={"User-Agent":"HTTPS-Readback/0.1"})
    try:
        with urllib.request.urlopen(request,timeout=timeout) as response:
            body=response.read(max_bytes+1)
            if len(body)>max_bytes:
                raise ValueError("response exceeds max-bytes")
            return response.status,body
    except urllib.error.HTTPError as exc:
        body=exc.read(max_bytes+1)
        if len(body)>max_bytes:
            raise ValueError("response exceeds max-bytes")
        return exc.code,body
    except urllib.error.URLError:
        return 0,b""


def check(
    base_url: str,
    target: str,
    expectation: str,
    allowed_roots: list[str],
    *,
    timeout: int=30,
    max_bytes: int=8*1024*1024,
) -> Evidence:
    if expectation not in {"present","absent"}:
        raise ValueError("expectation must be present or absent")
    url=resolve_url(base_url,target,allowed_roots)
    code,body=fetch(url,timeout=timeout,max_bytes=max_bytes)
    passed=(code==200) if expectation=="present" else (code!=200)
    return Evidence(
        url=url,
        http_code=code,
        body_sha256=hashlib.sha256(body).hexdigest(),
        body_bytes=len(body),
        expectation=expectation,
        passed=passed,
    )


def write_output(key: str, value: object) -> None:
    import os
    path=os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path,"a",encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--base-url",required=True)
    parser.add_argument("--target",required=True)
    parser.add_argument("--expectation",choices=["present","absent"],required=True)
    parser.add_argument("--allowed-root",action="append",dest="roots",required=True)
    parser.add_argument("--timeout",type=int,default=30)
    parser.add_argument("--max-bytes",type=int,default=8*1024*1024)
    args=parser.parse_args()
    try:
        evidence=check(
            args.base_url,args.target,args.expectation,args.roots,
            timeout=args.timeout,max_bytes=args.max_bytes
        )
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}")

    payload={
        "ok":evidence.passed,
        "expectation":evidence.expectation,
        "target":args.target,
        "http_code":evidence.http_code,
        "body_sha256":evidence.body_sha256,
        "body_bytes":evidence.body_bytes,
    }
    print(json.dumps(payload,separators=(",",":"),sort_keys=True))
    print(f"HTTPS_READBACK_HTTP={evidence.http_code}")
    print(f"HTTPS_READBACK_SHA256={evidence.body_sha256}")
    print(f"HTTPS_READBACK_BYTES={evidence.body_bytes}")
    write_output("http_code",evidence.http_code)
    write_output("body_sha256",evidence.body_sha256)
    write_output("body_bytes",evidence.body_bytes)
    return 0 if evidence.passed else 2


if __name__=="__main__":
    raise SystemExit(main())
