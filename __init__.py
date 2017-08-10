import badge, wifi, appglue, ugfx, dialogs, time

from angelshifts.service import *

api_key = ""
shifts = []

def nothing(pressed):
    ugfx.flush()


def prompt_api_key():
    global api_key
    api_key = dialogs.prompt_text("Your engelsystem api key")
    badge.nvs_set_str("engel", "key", api_key)

def show_shift_list():
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()
    global shift_list
    global shifts
    shift_list = ugfx.List(0,0,ugfx.width(),ugfx.height())
    if not shifts:
        shifts = get_shifts(api_key)
    for shift in shifts:
        shift_list.add_item("{} - {}, {}".format(generate_timedelta_text(int(shift['start']), int(shift['end'])), shift['name'], shift["Name"]))
    ugfx.flush(ugfx.LUT_NORMAL)
    ugfx.input_attach(ugfx.JOY_UP, nothing)
    ugfx.input_attach(ugfx.JOY_DOWN, nothing)
    ugfx.input_attach(ugfx.JOY_LEFT, nothing)
    ugfx.input_attach(ugfx.JOY_RIGHT, nothing)
    ugfx.input_attach(ugfx.BTN_A, lambda pressed: show_shift_detail() if pressed else None)
    ugfx.input_attach(ugfx.BTN_B, lambda pressed: appglue.home() if pressed else None)


def show_shift_detail():
    global shifts
    global shift_list
    shift_list.visible(False)
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()
    i = shift_list.selected_index()
    title = shifts[i]["name"]
    title_height = 20 if ugfx.get_string_width(title, "PermanentMarker22") <= ugfx.width() else 60
    title = ugfx.string_box(0, 0, ugfx.width(), title_height, title, "PermanentMarker22", ugfx.BLACK, ugfx.justifyCenter)
    location = ugfx.string(0, title_height + 5, "Location: " + shifts[i]["Name"], "Roboto_Regular18", ugfx.BLACK)
    description = ugfx.string_box(0, title_height + 25, ugfx.width(), 40, "Description: " + shifts[i]["title"], "Roboto_Regular12", ugfx.BLACK, ugfx.justifyLeft)
    time = ugfx.string(0, ugfx.height()-20, "Time: " + generate_timedelta_text(int(shifts[i]["start"]), int(shifts[i]["end"])), "Roboto_Regular18", ugfx.BLACK)
    ugfx.flush()
    ugfx.input_attach(ugfx.BTN_B, lambda pressed: show_shift_list() if pressed else None)


def main():
    print("> Main")
    global api_key

    ugfx.init()
    ugfx.input_init()

    ugfx.clear(ugfx.BLACK)
    ugfx.flush()
    ugfx.clear(ugfx.WHITE)
    ugfx.flush()

    ugfx.input_attach(ugfx.BTN_B, appglue.home)
    ugfx.input_attach(ugfx.BTN_SELECT, prompt_api_key)
    wifi.init()
    while not wifi.sta_if.isconnected():
        time.sleep(0.1)
        pass

    api_key = badge.nvs_get_str("engel", "key", "")
    if not api_key:
        prompt_api_key()

    show_shift_list()

print("Name= ", __name__)
main()
