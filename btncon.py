"""ボタン側の動作を行うためのライブラリ

使用例：
    >>> import btncon
    >>> btn = btncon.ButtonController()

    >>> await btn.send_trigger()

© 2024 Swimmy石神井公園校
"""

import asyncio
import base64
import hashlib
import hmac
import json
import time
import zlib

import js
import pyodide.ffi
import pyodide.http


class ButtonController:
    def __init__(self) -> None:
        try:
            query_key = self.__get_query_key()

            github_access_token, hmac_key, owner, repo, path = self.__get_keys(
                query_key
            )

            self.__hmac_key = hmac_key

            auth = f"token ghp_{github_access_token}"

            self.__request_url = (
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            )
            self.__headers = {
                "Authorization": auth,
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            }

            self.__ready = True

            js.ready()
        except:
            self.__ready = False

    def __get_query_key(self) -> str:
        """URLから「key」のクエリを取得

        戻り値
        -------
        str
            「key」のクエリ
        """

        query_params = js.location.search
        query_set = js.URLSearchParams.new(query_params)
        query_dict = dict(query_set)
        return query_dict["key"]

    def __get_keys(self, query_key: str) -> tuple:
        """コントローラーに必要なキーを取得する

        引数
        ----------
        query_key : str
            URLから「key」のクエリから取得したキー

        戻り値
        -------
        tuple
            github_access_token, hmac_key, owner, repo, path
        """
        return self.__convert_b64_to_keys(query_key)

    def __convert_b64_to_keys(self, key_b64_str: str) -> tuple:
        """Base 64に変換されている文字列キーをタプル型のキーに変換する

        引数
        ----------
        key_a85_str : str
            Ascii 85に変換されている文字列キー

        戻り値
        -------
        tuple
            github_access_token, hmac_key, owner, repo, path
        """

        # 鍵はBase 64で記されており、難読化されている。
        # まず、Base 64の文字列をバイト列に変換する
        # このバイト列は圧縮処理が施されているため、解凍する
        # そうすると、「&」で区切られた2つの文字列が出現する。
        # それぞれがgithub_access_token, hmac_key, owner, repo, pathに当たる
        # すべてb64（64進数）に変換されているため、hmac_key_b64はバイト列に戻す

        compressed_key_bytes = base64.urlsafe_b64decode(key_b64_str)

        key_bytes = zlib.decompress(compressed_key_bytes)

        key_text = key_bytes.decode()

        github_access_token, hmac_key_b64, owner, repo, path = key_text.split("&")

        hmac_key = base64.urlsafe_b64decode(hmac_key_b64)

        return (github_access_token, hmac_key, owner, repo, path)

    async def __get_data(self) -> dict:
        """該当のリポジトリのファイルの情報を入手する

        戻り値
        -------
        dict
            リポジトリのファイルの情報
        """

        res = await pyodide.http.pyfetch(
            self.__request_url, method="GET", headers=self.__headers
        )

        self.__status_sha = res.status

        data = await res.json()

        return data

    async def __store_sha(self) -> None:
        """該当レポジトリのファイルのSHA値を保持する"""
        data = await self.__get_data()

        self.__sha = data["sha"]

    def __create_body(self, sha: str) -> dict:
        """IoT機器に対して送る秘密の文字列を生成し、PUTリクエストをするBodyを生成する

        引数
        ----------
        sha : str
            書き換えを行う該当レポジトリのファイルのSHA値

        戻り値
        -------
        dict
            該当レポジトリに対してPUTリクエストをするBody
        """

        unix_now = int(time.time())
        unix_hmac = unix_now // 10

        unix_bytes = unix_hmac.to_bytes(4, "big")
        unix_hmac = hmac.new(self.__hmac_key, unix_bytes, hashlib.sha256)
        unix_hmac_bytes = unix_hmac.digest()
        unix_hmac_b64 = base64.b64encode(unix_hmac_bytes).decode()

        unix_hmac_b64_bytes = unix_hmac_b64.encode()
        unix_hmac_b64_bytes = base64.b64encode(unix_hmac_b64_bytes)
        unix_hmac_b64 = unix_hmac_b64_bytes.decode()

        commit_message = f"Button Commit on {unix_now}"

        return {"message": commit_message, "content": unix_hmac_b64, "sha": sha}

    async def __push_repo(self) -> None:
        """該当レポジトリに対してPUSHする"""
        method = "PUT"
        body = self.__create_body(self.__sha)
        body_str = json.dumps(body)

        res = await pyodide.http.pyfetch(
            self.__request_url, method=method, headers=self.__headers, body=body_str
        )

        self.__status_push = res.status

    async def __get_repo_content(self) -> str:
        """該当レポジトリのファイルのテキスト内容を取得する

        戻り値
        -------
        str
            該当レポジトリのファイルのテキスト内容
        """
        data = await self.__get_data()

        content_b64 = data["content"]

        content_bytes = base64.b64decode(content_b64)

        content_raw = content_bytes.decode()

        return content_raw.strip()

    async def __check_repo(self) -> bool:
        """該当レポジトリのファイルのテキストの内容により、受信に成功したかどうか確認する

        戻り値
        -------
        bool
            成功可否
        """
        content = await self.__get_repo_content()

        return content == "ok"

    async def send_trigger(self) -> None:
        """IoT機器に対してトリガーを送信する"""
        if self.__hmac_key is None:
            return

        await self.__store_sha()
        await self.__push_repo()

    def is_send_ok(self) -> bool:
        """IoT機器に対して信号の送信に成功したかどうか確認する

        戻り値
        -------
        bool
            成功可否
        """
        if self.__hmac_key is None:
            return False

        return self.__status_sha == 200 and self.__status_push == 200

    async def is_done(self) -> bool:
        """IoT機器側の動作が完了したかどうか確認する

        戻り値
        -------
        bool
            完了是非
        """
        if self.__hmac_key is None:
            return False

        return await self.__check_repo()

    async def sleep(self, seconds: int) -> None:
        """指定秒数待機する

        引数
        ----------
        seconds : int
            待機する秒数
        """
        await asyncio.sleep(seconds)

    def is_ready(self) -> bool:
        """信号送信の準備が完了したかどうか

        Returns
        -------
        bool
            準備完了是非
        """
        return self.__ready
