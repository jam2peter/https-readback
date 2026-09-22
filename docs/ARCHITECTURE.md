# Architecture

```text
explicit expectation
  + fixed HTTPS base URL
  + allowlisted logical target
  -> GET
  -> HTTP status
  -> SHA-256(response body)
  -> byte count
  -> PASS/FAIL
```

The evidence tuple makes a readback reproducible without logging the response
body itself. The primitive is designed to run immediately after a deployment or
rollback.
