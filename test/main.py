import random
import btncon

import js
import pyscript

btn = btncon.ButtonController()

def btn_click(event) -> None:
    pyscript.display("Sending Trigger")

    btn.send_trigger()

    pyscript.display("Sent Trigger")

    secs = random.randint(1, 10)
    btn.sleep(secs)

    pyscript.display(f"Waited {secs} seconds")

    if bool(random.getrandbits(1)):
        js.btn_success()
    else:
        js.btn_failure()

    pyscript.display("Changed button")
