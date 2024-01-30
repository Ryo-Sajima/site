import asyncio
import random

import js


async def btn_click(event) -> None:
    print("btn_click")
    secs = random.randint(1, 10)
    await asyncio.sleep(secs)

    if bool(random.getrandbits(1)):
        js.btn_success()
    else:
        js.btn_failure()
