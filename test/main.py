import random
import btncon

import js

async def btn_click(event) -> None:

    btn = btncon.ButtonController()
    await btn.send_trigger()

    secs = random.randint(1, 10)
    await btn.sleep(secs)

    if bool(random.getrandbits(1)):
        js.btn_success()
    else:
        js.btn_failure()
