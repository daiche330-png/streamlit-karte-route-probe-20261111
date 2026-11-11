# Community Cloud 最小API試験の結果（2026-11-11）

## 試験対象

- 公開アプリ https://karte-routes-20261111.streamlit.app/
- 専用公開リポジトリ https://github.com/daiche330-png/streamlit-karte-route-probe-20261111
- 配備コード `e66c6a8`、枝 `codex/minimal-route-probe`。追加したGETルートはhealthとechoの2つだけ。
- Streamlit 1.66.1。CloudログでPython 3.12.16、Starlette 1.10.0、uvicorn 0.54.0を確認。
- ブラウザーでタイトルとStreamlit版の表示を確認した後に外部curlを実行した。休止画面ではなく、実行中のアプリ画面を確認した。
- 実際の選手データ、APIキー、Drive、ポータルの認証処理は含まない。echoには依頼された架空の3見出しだけを送った。
- curlに `-L` を付けず、Cookieも指定していない。各要求は独立したcurlプロセスで実行。
- 既存の `feat/karte-readonly-api` はこの試験でpushしていない。

## 指定されたルート直下のcurl結果

日時はUTC。本文は先頭200文字までをJSON文字列として表示し、改行は `\n` と記した。

| 要求 | UTC | HTTP | Content-Type | Location | 本文の先頭200文字 |
|---|---|---|---|---|---|
| `https://karte-routes-20261111.streamlit.app/api/karte/v1/health` | 2026-11-11T02:03:41.386547+00:00 | 303 | `text/html; charset=utf-8` | `https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fkarte-routes-20261111.streamlit.app%2Fapi%2Fkarte%2Fv1%2Fhealth` | `"<a href=\"https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fkarte-routes-20261111.streamlit.app%2Fapi%2Fkarte%2Fv1%2Fhealth\">See Other</a>.\n\n"` |
| `https://karte-routes-20261111.streamlit.app/api/karte/v1/echo` | 2026-11-11T02:03:41.833440+00:00 | 303 | `text/html; charset=utf-8` | `https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fkarte-routes-20261111.streamlit.app%2Fapi%2Fkarte%2Fv1%2Fecho` | `"<a href=\"https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fkarte-routes-20261111.streamlit.app%2Fapi%2Fkarte%2Fv1%2Fecho\">See Other</a>.\n\n"` |
| `https://karte-routes-20261111.streamlit.app/_stcore/health` | 2026-11-11T02:03:42.210761+00:00 | 303 | `text/html; charset=utf-8` | `https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fkarte-routes-20261111.streamlit.app%2F_stcore%2Fhealth` | `"<a href=\"https://share.streamlit.io/-/auth/app?redirect_uri=https%3A%2F%2Fkarte-routes-20261111.streamlit.app%2F_stcore%2Fhealth\">See Other</a>.\n\n"` |

3件とも303でCloud側の認証用URLへ転送された。今回のcurlはその転送を追跡していない。echoがJSONに到達しなかったため、この経路での見出し受信は未確認。

## 補足比較としてアプリの `/~/+/` 配下を直接呼んだ結果

この比較は指定されたルート直下の試験とは別に行った。要求見出しと転送を追跡しない条件は同じ。

| 要求 | UTC | HTTP | Content-Type | Location | 本文の先頭200文字 |
|---|---|---|---|---|---|
| `https://karte-routes-20261111.streamlit.app/~/+/api/karte/v1/health` | 2026-11-11T02:09:54.583938+00:00 | 200 | `application/json` | なし | `"{\"ok\":true}"` |
| `https://karte-routes-20261111.streamlit.app/~/+/api/karte/v1/echo` | 2026-11-11T02:09:55.141860+00:00 | 200 | `application/json` | なし | `"{\"authorization_present\":false,\"if_match_present\":false,\"range_present\":true}"` |
| `https://karte-routes-20261111.streamlit.app/~/+/_stcore/health` | 2026-11-11T02:09:55.471515+00:00 | 200 | `text/plain; charset=utf-8` | なし | `"ok"` |

## 見出しの到達

| 経路 | Authorization | If-Match | Range |
|---|---|---|---|
| 指定の `/api/karte/v1/echo` | 未確認（303） | 未確認（303） | 未確認（303） |
| 補足の `/~/+/api/karte/v1/echo` | false | false | true |
| 同じ最小コードのローカルASGI対照 | true | true | true |

ローカル対照ではhealthは200 application/jsonで `{"ok":true}`、echoも200 application/jsonで3つすべてtrueだった。Cloudへのcurlは3つの見出しを明示的に指定し、Locationのない200を受け取ったが、echoが受信したAuthorizationとIf-Matchの存在はfalseだった。どの中継コンポーネントが削除したかはこの試験では特定していない。

## 条件付きの追加試験

| 追加項目 | 実施状況 | 理由・観測結果 |
|---|---|---|
| 8MiB断片の206とContent-Range | 未実施 | 指定のhealth/echoがJSON200になる前提を満たさなかったため、ルートを追加していない |
| 30分放置後のAPI | 未実施 | 同じ前提を満たさなかったため。休止後の返りを推測しない |
| 実際の休止後のAPI | 未確認 | 実際の休止状態での測定を行っていない |

公式文書では無通信12時間で休止するとされている。30分経過だけで休止したと扱わない。 https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app

## カルテ側に渡す判断材料

起動済みの試験環境でも、指定の公開ルートは303だった。補足のアプリ配下では独自ルートのJSON200を確認できたが、Bearer認証とIf-Matchに必要な見出しが届かなかった。提示された「JSON200かつ見出しが届く」という継続検討条件は満たしていない。

この結果は当該最小アプリと記載日時の観測。前回ポータルの500が発生する内部機構すべてを断定するものではない。今回、単純なJSON200のルートはアプリ配下で通ること、見出しが届かないことを個別に確認した。

再実行用コマンドはREADMEと `probe_http.py` を参照。生のHTTP応答・測定JSON・起動画面はローカル成果物のresultsフォルダーに保存した。応答に含まれうるCookieを公開リポジトリへ掲載しないため、生の応答はgit管理対象外とした。
