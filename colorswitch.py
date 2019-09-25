#!/usr/bin/env python3

import argparse
import configparser
import os
import shutil
import tempfile
import time

DESCRIPTION = """Change the xfce4-terminal colorscheme"""

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('colorscheme', type=str,
                    help='a xfce4-terminal colorscheme')


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    if len(hex) != 6:
        raise ValueError("Can only deal with colors in form #XXXXXX")
    return tuple(int(hex[2*i:2*i+2], 16) for i in range(3))


def chane_xfce4_terminal_colorscheme(colorscheme):
    """changes colorscheme and returns bg_brightness
    bg_brightness is 'dark' or 'light'"""

    os_file = f"/usr/share/xfce4/terminal/colorschemes/{colorscheme}.theme"
    user_file = os.path.expanduser("~/.local/share/xfce4/terminal/"
                                   f"colorschemes/{colorscheme}.theme")
    rc_file = os.path.expanduser("~/.config/xfce4/terminal/terminalrc")
    random_string = next(tempfile._get_candidate_names())
    rc_temp = os.path.expanduser(f"/tmp/terminalrc_{random_string}")

    # check if scheme is available
    if os.path.isfile(os_file):
        scheme_file = os_file
    elif os.path.isfile(user_file):
        scheme_file = user_file
    else:
        raise ValueError(f"colorscheme {colorscheme} not found")

    term_conf = configparser.ConfigParser(interpolation=None)
    term_conf.optionxform = str
    term_conf.read(rc_file)

    scheme_conf = configparser.ConfigParser(interpolation=None)
    scheme_conf.optionxform = str
    scheme_conf.read(scheme_file)
    for key, value in dict(scheme_conf['Scheme']).items():
        if not key.startswith('Name'):
            term_conf['Configuration'][key] = value

    with open(rc_temp, 'w') as f:
        term_conf.write(f, space_around_delimiters=False)

    shutil.move(rc_temp, rc_file)

    # compare foreground and background brightness
    foreground = hex_to_rgb(term_conf['Configuration']['ColorForeground'])
    background = hex_to_rgb(term_conf['Configuration']['ColorBackground'])
    if sum(foreground) > sum(background):
        bg_brightness = 'dark'
    else:
        bg_brightness = 'light'
    return bg_brightness

def change_taskwarrior_colorscheme(colorscheme):
    """changes colorscheme of taskwarrior
    ~/.taskrc-colorscheme must be included in .taskrc"""

    os_file = f"/usr/share/doc/task/rc/{colorscheme}.theme"
    taskrc_colorscheme_file = os.path.expanduser("~/.taskrc-colorscheme")

    # check if scheme is available
    if not os.path.isfile(os_file):
        raise ValueError(f"file {os_file} not found")

    with open(taskrc_colorscheme_file, 'w') as f:
        f.write(f"include {os_file}\n")

if __name__ == '__main__':
    args = parser.parse_args()
    bg_brightness = chane_xfce4_terminal_colorscheme(args.colorscheme)

    if bg_brightness == 'light':
        task_colorscheme = 'light-256'
    elif bg_brightness == 'dark':
        task_colorscheme = 'dark-256'
    change_taskwarrior_colorscheme(task_colorscheme)

    time.sleep(0.2)
