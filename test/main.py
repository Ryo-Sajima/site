import base64
import json

import js
import pyodide.http
import pyweb.pydom

query_params = js.location.search
query_set = js.URLSearchParams.new(query_params)
query_dict = dict(query_set)
try:
    print(query_dict["text"])
except KeyError:
    print("Error")


async def get_sha(owner, repo, path, headers) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    method = "GET"
    headers["Content-Type"] = "application/json"

    res = await pyodide.http.pyfetch(url, method=method, headers=headers)

    data = await res.json()

    sha = data["sha"]

    return sha


async def put_request(owner, repo, path, body, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    method = "PUT"
    headers["Content-Type"] = "application/json"
    body_str = json.dumps(body)

    res = await pyodide.http.pyfetch(url, method=method, headers=headers, body=body_str)

    status = res.status

    data = await res.json()

    print(data)

    return status, data


# 入力の度に呼び出す関数
async def get_text(event) -> None:
    # リクエストのヘッダー情報
    headers = {"Authorization": "token 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", "X-GitHub-Api-Version": "2022-11-28"}

    sha = await get_sha("Ryo-Sajima", "storage", "test.txt", headers)

    text = pyweb.pydom["#text_area"].value[0]
    text_bytes = text.encode()
    text_b64_bytes = base64.b64encode(text_bytes)
    text_b64 = text_b64_bytes.decode()

    # リクエストのデータ
    data = {"message": "test commit", "content": text_b64, "sha": sha}

    # リクエストの実行
    status, response = await put_request("Ryo-Sajima", "storage", "test.txt", data, headers)

    if status == 200:
        status_des = "OK"
    elif status == 201:
        status_des = "Created"
    elif status == 404:
        status_des = "Resource not found"
    elif status == 409:
        status_des = "Conflict"
    elif status == 422:
        status_des = "Validation failed, or the endpoint has been spammed."
    else:
        status_des = str(status)

    status_str = f"{status} ({status_des})"

    pyweb.pydom["#status"].html = status_str
