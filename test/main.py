import asyncio
import random
import btncon

import js

btn = btncon.ButtonController()

async def btn_click(event) -> None:
    btn.send_trigger()

    secs = random.randint(1, 10)
    await asyncio.sleep(secs)

    if bool(random.getrandbits(1)):
        js.btn_success()
    else:
        js.btn_failure()
