#!/usr/bin/env python3

import argparse
import configparser
import os
import shutil
from string import Template
import tempfile
import time

DESCRIPTION = """Change the theme of xfce4 and xfce4-terminal, and taskwarrior"""


def run():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('brightness', type=str,
                        choices=['dark', 'light'],
                        help='choose how the desktop should look like')

    # set themes
    args = parser.parse_args()
    if args.brightness == 'light':
        xfce4_style = 'Adwaita'
        xfce4_terminal_colorscheme = 'marv-light'
        task_theme = 'light-256'
        polybar_colors = {'background': '#f6f5f4', 'foreground': '#222', 'icon': '#666',
                          'border_top_color': '#b2aca6'}
    elif args.brightness == 'dark':
        xfce4_style = 'Adwaita-dark'
        xfce4_terminal_colorscheme = 'marv-dark'
        task_theme = 'dark-256'
        polybar_colors = {'background': '#353535', 'foreground': '#eee', 'icon': '#888',
                          'border_top_color': '#252525'}

    # change xfce4 style
    change_xfce4_style(xfce4_style)

    # change xfce4-terminal colorscheme
    change_xfce4_terminal_colorscheme(xfce4_terminal_colorscheme)

    # change taskwarrior theme
    change_taskwarrior_theme(task_theme)

    # change polybar colors
    change_polybar_colors(polybar_colors)

    time.sleep(0.2)


def change_xfce4_style(style):
    """changes xfce4 style"""
    # does not work with subprocess.run() for some reason
    os.system("xfconf-query -c xsettings -p /Net/ThemeName -s '{}'".format(style))
    os.system("xfce4-panel -r")
    os.system("pkill xfwm4")


def change_xfce4_terminal_colorscheme(colorscheme):
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


def change_taskwarrior_theme(theme):
    """changes theme of taskwarrior
    ~/.taskrc-theme must be included in .taskrc"""

    os_file = f"/usr/share/doc/task/rc/{theme}.theme"
    taskrc_theme_file = os.path.expanduser("~/.taskrc-theme")

    # check if scheme is available
    if not os.path.isfile(os_file):
        raise ValueError(f"file {os_file} not found")

    with open(taskrc_theme_file, 'w') as f:
        f.write(f"include {os_file}\n")


def change_polybar_colors(polybar_colors):
    """changes colors in .config/polybar/config.pytemplate
       and saves them to .config/polybar/config."""
    template_file = os.path.expanduser("~/.config/polybar/config.pytemplate")
    config_file = os.path.expanduser("~/.polybar-config")
    random_string = next(tempfile._get_candidate_names())
    temp_file = os.path.expanduser(f"/tmp/polybar-config-{random_string}")
    # open template file
    with open(template_file, 'r') as f:
        config = f.read()
    # apply config
    config = Template(config).substitute(polybar_colors)
    # write config to temp file
    with open(temp_file, 'w') as f:
        f.write(config)
    # atomic change
    shutil.move(temp_file, config_file)


if __name__ == '__main__':
    run()
