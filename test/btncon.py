import base64
import zlib
import js
import random
import asyncio
import pyodide.http
import io
import urllib.parse
import json

print("BTNCON")

class ButtonController:
    def __init__(self) -> None:
        query_key = self.__get_query_key()

        api_dev_key, api_user_key, divisor_int, remainder_int = self.__get_keys(query_key)

        self.__request_url = "https://pastebin.com/api/api_post.php"
        self.__base_data = {"api_dev_key": api_dev_key, "api_user_key": api_user_key}

        self.__divisor_int = divisor_int
        self.__remainder_int = remainder_int
        self.__content = ""

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

    def my_open_url(self, url: str, data) -> io.StringIO:
        req = js.XMLHttpRequest.new()
        req.open("POST", url, False)  # means async=False
        req.setRequestHeader("Origin", "*")
        req.send(data)

        return io.StringIO(req.response)

    async def __create_paste(self) -> None:
        self.__content = ""

        while True:
            dividend = random.randint(self.__remainder_int + 1, self.__divisor_int)
            if dividend % self.__remainder_int != 0:
                break

        paste_int = self.__divisor_int * dividend + self.__remainder_int

        paste_bytes = paste_int.to_bytes(16, "big")

        paste_b64_bytes = base64.urlsafe_b64encode(paste_bytes)

        paste_code = paste_b64_bytes.decode()

        # data = self.__base_data.copy()
        # data["api_option"] = "paste"
        # data["api_paste_code"] = paste_code
        # data["api_paste_private"] = "1"
        # data["api_paste_expire_date"] = "10M"

        # req_data = urllib.parse.urlencode(data).encode("ascii")

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # req = urllib.request.Request(url=self.__request_url, data=req_data, method="POST")

        # with urllib.request.urlopen(req) as response:
        #     res_bytes = response.read()

        # res_text = res_bytes.decode()

        # self.__paste_url = self.my_open_url(self.__request_url, json.dumps(data))

        response = await pyodide.http.pyfetch("https://raw.githubusercontent.com/Ryo-Sajima/site/main/test/main.py", method="GET")



        # await asyncio.sleep(1)

        import pyscript

        # pyscript.display(response.status)

        self.__content = await response.text()
        pyscript.display(self.__content)

        # await asyncio.sleep(10)

    async def __check_paste(self):
        try:
            pyodide.http.open_url(self.__content)
        except:
            return True

        return False

    async def send_trigger(self):
        await self.__create_paste()

    async def send_ok(self):
        return bool(self.__content)

    async def check_done(self):
        return await self.__check_paste()

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)
