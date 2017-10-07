import ugfx, badge, wifi, time, utime, easyrtc

next_shift = None
wakeup_interval = 60000  # in miliseconds, to make sure the screen gets updated
update_interval = 300  # in seconds
wifi_tries = 50
notify_time = 600  # in seconds


def setup():
    global api_key
    print("setup")
    api_key = badge.nvs_get_str("engel", "key", "")

def loop():
    print("> angelshifts loop")
    last_update = int(badge.nvs_get_str("engel", "update", "0"))
    print("last update: ", last_update)
    if api_key:
        # Perform update if update_interval has passed
        if last_update + update_interval < easyrtc.time.time():
            print("angelshifts: updating...")
            wifi.init()
            tries = 0
            while not wifi.sta_if.isconnected():
                time.sleep(0.1)
                tries += 1
                if tries >= wifi_tries:
                    return wakeup_interval
            next_shift = get_next_shift(api_key)
            if next_shift:
                badge.nvs_set_str("engel", "shift_name", next_shift["name"])
                badge.nvs_set_str("engel", "shift_loc", next_shift["Name"])
                badge.nvs_set_str("engel", "shift_start", next_shift["start"])
                badge.nvs_set_str("engel", "shift_end", next_shift["end"])
                badge.nvs_set_u8("engel", "notified", 0)
            else:
                badge.nvs_set_str("engel", "shift_name", "")
            badge.nvs_set_str("engel", "update", str(easyrtc.time.time()))
        else:
            print("angelshifts: no update needed")

        # Notify about upcoming shift if it starts in less than notify_time
        if badge.nvs_get_str("engel", "shift_name", "") and not bool(badge.nvs_get_u8("engel", "notified")):
            start = int(badge.nvs_get_str("engel", "shift_start", ""))
            now = easyrtc.time.time()
            if start > now and start < now + notify_time:
                global notified
                badge.vibrator_init()
                badge.vibrator_activate(200)
                ugfx.string(0, 0, "NEXT SHIFT IN {} MINUTES!".format(notify_time // 60), "PermanentMarker22", ugfx.BLACK)
                ugfx.flush()


        return wakeup_interval
    else:
        print("no api key set up")
        return 0

def draw(y, sleep=False):
    print("> angelshifts draw")
    name = badge.nvs_get_str("engel", "shift_name", "")
    loc = badge.nvs_get_str("engel", "shift_loc", "")
    start = int(badge.nvs_get_str("engel", "shift_start", 0))
    end = int(badge.nvs_get_str("engel", "shift_end", 0))

    if name:
        time_text = generate_timedelta_text(start, end)
        ugfx.string(0, y-14, "{}: {} @ {}".format(time_text, name, loc), "Roboto_Regular12", ugfx.BLACK)
        # ugfx.flush()
        return 60000, 14
    else:
        return 120000, 0

## utils

# This is here because putting it in a seperate utils.py wouldn't work:
# When importing utils in service, __init__.py (and by this, the main app)
# is run. Unfortunately, there also is no way to find out in __init__.py
# if it's run as an app or merely imported :/
# Really unfortunate design oversight in the badge firmware

import easyrtc
import urequests as requests
engelsystem_url = "https://engel.hackover.de/?p=shifts_json_export&key={}"
show_shifts_in_past = False


def get_shifts(api_key):
    r = requests.get(engelsystem_url.format(api_key))
    all_shifts = r.json()
    now = easyrtc.time.time()
    return [s for s in all_shifts if show_shifts_in_past or int(s['end']) > now]

def get_next_shift(api_key):
    shifts = get_shifts(api_key)
    now = easyrtc.time.time()
    for shift in shifts:
        if int(shift['end']) > now:
            return shift

def make_timedelta_tuple(timedelta_int):
    t_tuple = utime.localtime(timedelta_int)
    differences = (1970, 1, 1, 0, 0, 0, 5, 0)
    timedelta = []
    for delta, dif in zip(t_tuple, differences):
        timedelta.append(delta - dif)
    return timedelta


def truncate_timedelta_text(timedelta_tuple):
    s = []
    units = ('y', 'm', 'd', 'h', 'min', 'sec')

    for delta, unit in zip(timedelta_tuple, units):
        if abs(delta) > 0:
            s.append(str(abs(delta)) + unit)
    return ' '.join(s[:2])


def generate_timedelta_text(start, end):
    now = easyrtc.time.time()
    if now < start:
        s = "in"
        delta = start - now
    elif now > start and now < end:
        s = "ends in"
        delta = end - now
    else:
        s = "ago"
        delta = now - end

    t = make_timedelta_tuple(delta)
    time_text = truncate_timedelta_text(t)
    if s != "ago":
        return s + " " + time_text
    else:
        return time_text + " " + s
