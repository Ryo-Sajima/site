import asyncio
import base64
import json
import zlib

import js
import pyodide.ffi
import pyodide.http

print("BTNCON")

class ButtonController:
    def __init__(self) -> None:
        query_key = self.__get_query_key()

        auth = query_key

        # api_dev_key, api_user_key, divisor_int, remainder_int = self.__get_keys(query_key)

        owner = "Ryo-Sajima"
        repo = "storage"
        path = "test.txt"

        self.__request_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        self.__headers = {"Authorization": f"token {auth}", "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"}

    def __get_query_key(self) -> str:
        query_params = js.location.search
        query_set = js.URLSearchParams.new(query_params)
        query_dict = dict(query_set)
        try:
            return query_dict["key"]
        except KeyError:
            return ""

    def __get_keys(self, query_key) -> tuple:
        """コントローラーに必要なキーを取得する

        戻り値
        -------
        tuple
            api_dev_key, api_user_key, divisor_int, remainder_sha_hex
        """

        return self.__convert_b64_to_keys(query_key)

    def __convert_b64_to_keys(self, key_b64_str):
        key_b64_bytes = key_b64_str.encode()

        compressed_key_bytes = base64.urlsafe_b64decode(key_b64_bytes)

        key_bytes = zlib.decompress(compressed_key_bytes)
        key_text = key_bytes.decode()

        api_dev_hex, api_user_key, divisor_hex, remainder_hex = key_text.split("&")

        api_dev_bytes = bytes.fromhex(api_dev_hex)
        api_dev_key = api_dev_bytes.decode()

        divisor_int = int(divisor_hex, 16)

        remainder_int = int(remainder_hex, 16)

        return (api_dev_key, api_user_key, divisor_int, remainder_int)

    async def __get_data(self) -> dict:
        method = "GET"

        res = await pyodide.http.pyfetch(self.__request_url, method=method, headers=self.__headers)

        self.__status_sha = res.status

        data = await res.json()

        return data

    async def __store_sha(self):
        data = await self.__get_data()

        self.__sha = data["sha"]

        print(self.__sha)

    def __create_body(self, sha) -> dict:
        text = "test message"

        text_bytes = text.encode()
        text_b64_bytes = base64.b64encode(text_bytes)
        text_b64 = text_b64_bytes.decode()

        return {"message": "test commit", "content": text_b64, "sha": sha}

    async def __push_repo(self):
        method = "PUT"
        body = self.__create_body(self.__sha)
        body_str = json.dumps(body)

        res = await pyodide.http.pyfetch(self.__request_url, method=method, headers=self.__headers, body=body_str)

        self.__status_push = res.status

        self.__data = await res.json()

    async def __get_repo_content(self):
        data = await self.__get_data()

        content_b64 = data["content"]

        content_bytes = base64.b64decode(content_b64)

        content_raw = content_bytes.decode()

        return content_raw.strip()

    async def __check_repo(self):
        content = await self.__get_repo_content()

        return content == "ok"

    async def send_trigger(self):
        await self.__store_sha()
        await self.__push_repo()

    def is_send_ok(self):
        return self.__status_sha == 200 and self.__status_push == 200

    async def is_done(self):
        return await self.__check_repo()

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)
