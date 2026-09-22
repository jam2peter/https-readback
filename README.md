# HTTPS Readback

A small, dependency-free validation primitive for checking whether a deployed
public web target is present or absent over HTTPS and recording reproducible
evidence.

> Status: `v0.1-beta`

HTTPS Readback returns:

- HTTP status;
- SHA-256 of the response body;
- response size in bytes;
- normalized target;
- PASS/FAIL against an explicit expectation.

It deliberately fixes the request to a configured HTTPS base URL plus an
allowlisted logical target. It is not a generic URL fetcher.

## GitHub Action

```yaml
- uses: jam2peter/https-readback@v0
  with:
    base-url: https://example.com/
    target: apps/my-app
    expectation: present
```

Outputs:

- `http-code`
- `body-sha256`
- `body-bytes`

## CLI

```bash
python3 scripts/readback.py \
  --base-url https://example.com/ \
  --target apps/my-app \
  --expectation present \
  --allowed-root apps \
  --allowed-root projects
```

`present` requires HTTP 200. `absent` requires anything other than HTTP 200.

## Issue workflow

A reusable template is included for:

```text
/https-readback present apps/my-app
/https-readback absent projects/old-site
```

## Security model

- HTTPS only;
- no arbitrary scheme;
- no userinfo credentials in URL;
- target must be `<allowlisted-root>/<slug>`;
- no query/fragment supplied by the target;
- fixed base host;
- sanitized evidence only;
- no secrets required.

See [Security](docs/SECURITY.md).

## Development

```bash
python3 -m py_compile scripts/readback.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## License

MIT
