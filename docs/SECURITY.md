# Security

HTTPS Readback is intentionally not a generic URL fetcher.

The base URL must be absolute HTTPS, may not contain userinfo credentials,
query strings or fragments, and stays fixed for every logical target.

Targets are exactly:

```text
<allowlisted-root>/<slug>
```

This prevents Issue input from selecting an arbitrary host or protocol.

The action requires no secret. Output is limited to status, SHA-256 and byte
count; response bodies are not printed.
