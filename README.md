# Minimal Community Cloud custom-route probe

A separate synthetic-only experiment requested on 2026-11-11.

- Entrypoint `streamlit_app.py` uses `st.App` with exactly two custom GET routes.
- `/api/karte/v1/health` returns JSON `{"ok": true}` with status 200.
- `/api/karte/v1/echo` returns only booleans indicating presence of Authorization, If-Match and Range headers. Header values are never returned or stored.
- Streamlit is pinned to 1.66.1 to match the original portal experiment.
- No secrets, credentials, external data stores, authentication middleware, portal code or athlete data.
- Deployment is a new public Community Cloud app. Open its page once before testing.

## External checks

Run the following without `-L`, without a browser cookie jar, and without real credentials. Replace APP with the test app hostname.

```sh
curl -i https://APP.streamlit.app/api/karte/v1/health
curl -i -H 'Authorization: Bearer test-test-test' -H 'If-Match: "e1"' -H 'Range: bytes=0-9' https://APP.streamlit.app/api/karte/v1/echo
curl -i https://APP.streamlit.app/_stcore/health
```

Preserve raw response headers and body. Record UTC time, status, Content-Type, Location and first 200 decoded body characters. Test the app iframe prefix separately as a supplementary comparison, keeping it distinct from the requested root URLs.

Only after the requested checks succeed, add an 8MiB synthetic 206 endpoint and test Content-Range. An idle period is not evidence of hibernation. Record actual app state independently.
