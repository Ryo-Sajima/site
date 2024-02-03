import btncon

import js
import pyscript

print("MAIN")

async def btn_click(event) -> None:
    btn = btncon.ButtonController()

    await btn.send_trigger()



    if not await btn.send_ok():
        js.btn_failure()
        return

    while True:
        await btn.sleep(10)
        is_done = await btn.check_done()

        if is_done:
            break

    js.btn_success()
