import badge
import wifi
import appglue
import ugfx
import dialogs
import time
import urequests as requests

engelsystem_url = "https://volunteer.sha2017.org/?p=shifts_json_export&key={}"

api_key = ""
shifts = []

def prompt_api_key():
    global api_key
    api_key = dialogs.prompt_text("Your engelsystem api key")
    badge.nvs_set_str("engel", "key", api_key)

def load_shifts():
    global shift_list
    global api_key
    r = requests.get(engelsystem_url.format(api_key))
    return r.json()

def list_shifts():
    global shift_list
    shift_list = ugfx.List(0,0,ugfx.width(),ugfx.height())
    shifts = load_shifts()
    for shift in s:
        shift_list.add_item("{}, {}".format(shift['name'], shift["Name"]))
    ugfx.flush(ugfx.LUT_NORMAL)
    ugfx.input_attach(ugfx.JOY_UP, lambda pushed: ugfx.flush() if pushed else False)
	ugfx.input_attach(ugfx.JOY_DOWN, lambda pushed: ugfx.flush() if pushed else False)

def main():
    global api_key
    api_key = badge.nvs_get_str("engel", "key", "")
    if not api_key:
        prompt_api_key()

    ugfx.clear(ugfx.BLACK)
    ugfx.flush()
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()

    list_shifts()

ugfx.input_attach(ugfx.BTN_B, appglue.home)
ugfx.input_attach(ugfx.BTN_SELECT, prompt_api_key)
wifi.init()
time.sleep(3)
main()

***
