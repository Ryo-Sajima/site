import base64
import zlib
import js
import random
import json
import asyncio
import pyscript


print("BTNCON")


class ButtonController:
    def __init__(self) -> None:
        query_key = self.__get_query_key()

        api_dev_key, api_user_key, divisor_int, remainder_int = self.__get_keys(query_key)

        self.__request_url = "https://pastebin.com/api/api_post.php"
        self.__base_data = {"api_dev_key": api_dev_key,
                            "api_user_key": api_user_key
                            }

        self.__divisor_int = divisor_int
        self.__remainder_int = remainder_int

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

    async def __create_paste(self) -> None:
        while True:
            dividend = random.randint(self.__remainder_int + 1, self.__divisor_int)
            if dividend % self.__remainder_int != 0:
                break

        paste_int = self.__divisor_int * dividend + self.__remainder_int

        paste_bytes = paste_int.to_bytes(16, "big")

        paste_a85_bytes = base64.a85encode(paste_bytes)

        paste_a85_str = paste_a85_bytes.decode()

        post_data = self.__base_data.copy()
        post_data["api_option"] = "paste"
        post_data["api_paste_code"] = paste_a85_str
        post_data["api_paste_private"] = "1"
        post_data["api_paste_expire_date"] = "10M"
        pyscript.display((self.__request_url, post_data))

        body = json.dumps(post_data)

        response = await js.fetch(self.__request_url, {"method": "POST", "headers": "{}", "mode": "no-cors", "body": body})
        text = await response.text()
        print(text)

        # res = await pyodide.http.pyfetch(self.__request_url, method="POST", headers={}, body=post_data)

        # print(res)
        # pyscript.display(res)

        # status = res.status

        # text = res.text

        # print(status, text)

    async def send_trigger(self):
        await self.__create_paste()

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)
