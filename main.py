# -*- coding: utf-8 -*-
import pygame
import datetime
import time
import os
import sys
import math
import threading
from pygame_controls import *
from forecaster import *
import location
import select
import socket

sock = None


def init_irw():
    global sock
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/var/run/lirc/lircd')
    sock.setblocking(0)


def next_ir_key():
    '''Get the next key pressed. Return keyname, updown.
    '''
    ready = select.select([sock], [], [], 0.1)
    if ready[0]:
        data = sock.recv(128)
        if not data:
            print('No data')
            return 0
    else:
        return 0
    data = data.strip().split()
    if int(data[1].decode()) == 1:
        return data[2].decode()


init_irw()

# from security import SecurityCamera
weather = Weather()

script_dir = os.path.dirname(os.path.realpath(__file__))

# security = SecurityCamera()
# t = threading.Thread(target=security.start)

# window will start at 0, 0
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
time_format = '%I:%M %p\n'
day_month = '%A, %h '
day_format = '%d'

days_to_display = 7

pygame.init()

display_info = pygame.display.Info()
time_game = pygame.time.Clock()

screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.NOFRAME | pygame.HWSURFACE)

# default_font = pygame.font.SysFont('C:\\WINDOWS\\Fonts\\comic.ttf', 250)
# fps_font = pygame.font.SysFont('Consolas', 12)
# username_font = pygame.font.SysFont('Consolas', 14)
# username_font.set_bold(True)

pygame.mouse.set_visible(False)

controller = PyGameControls()

lblTime = controller.create_label(screen, '', 0, 0, display_info.current_w, display_info.current_h / 2, [TS_HCENTER],
                                  ControlProperties('label', 'flat', text_color_normal=(241, 241, 241)))
lblTime.font.font_size = 160

forecast_width = int((display_info.current_w - 80) / days_to_display)
forecast_y = display_info.current_h / 2

forecast_list = list()

for i in range(0, days_to_display):
    current_x = (forecast_width * i) + (10 * (i + 1))
    lblHeader = controller.create_label(screen, 'Today' if i == 0 else datetime.datetime.strftime(
        datetime.datetime.now() + datetime.timedelta(days=i), '%A'), current_x, forecast_y, forecast_width, 35,
                                        [TS_HCENTER, TS_VCENTER],
                                        ControlProperties('label', 'flat', text_color_normal=(241, 241, 241),
                                                          border_color_normal=(0, 0, 0, 255),
                                                          px_border=2,
                                                          bk_color_normal=(16, 16, 16, 255)))
    # print(os.path.join(script_dir, 'Icons', weather.get_summary(i)['icon'] + '.png'))
    summary = weather.get_summary(i)

    pic_dimensions = forecast_width * 0.75
    lblBg = controller.create_label(screen, ' ', current_x, forecast_y + 36, forecast_width, pic_dimensions + 201,
                                        [TS_LEFT, TS_TOP],
                                        ControlProperties('label', 'flat', bk_color_normal=(16, 16, 16, 255),
                                                          px_border=2, border_color_normal=(0, 0, 0, 255)))
    picIcon = controller.create_pic(screen, os.path.join(script_dir, 'Icons', summary.icon + '.png'),
                                        current_x + ((forecast_width - pic_dimensions) / 2), forecast_y + 39,
                                        pic_dimensions, pic_dimensions,
                                        [IMS_REALSIZECONTROL],
                                        ControlProperties('picture', 'flat'))
    lblSummary = controller.create_label(screen, weather.weather_string(summary),
                                             current_x + 2, forecast_y + 40 + pic_dimensions, forecast_width, 198,
                                             [TS_LEFT, TS_TOP],
                                             ControlProperties('label', 'flat', text_color_normal=(241, 241, 241)))

    lblHeader.font.font_size = 26
    lblHeader.font.attribute = 'bold'
    lblSummary.font.font_size = 16
    forecast_list.append(dict(lblHeader=lblHeader, lblBg=lblBg, picIcon=picIcon, lblSummary=lblSummary))

current_day = datetime.datetime.strftime(datetime.datetime.now(), '%A')

key_timer = 0
key_string = ''
monitor_state = 1

while True:
    ir_key = next_ir_key()

    if ir_key:
        if ir_key == 'KEY_OK':
            if key_string == 'KEY_UP':
                if monitor_state:
                    subprocess.Popen("tvservice -o", shell=True, stdout=subprocess.PIPE)
                else:
                    subprocess.Popen("tvservice -p;sudo chvt 6;sudo chvt 7", shell=True, stdout=subprocess.PIPE)

                monitor_state = not monitor_state
            key_timer = 0
            key_string = ''
        else:
            key_string += ir_key
            key_timer = time.time()
    elif key_timer and time.time() - key_timer > 10000:
        print('Resetting key string')
        key_string = ''
        key_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type in (pygame.KEYUP, pygame.KEYDOWN):
            key = pygame.key.get_pressed()
            if key[pygame.K_ESCAPE] or (event.key == pygame.K_F4 and (key[pygame.K_LALT] or key[pygame.K_RALT])):
                pygame.quit()
                sys.exit()

    screen.fill(0x1F1F1F)

    now = datetime.datetime.now()
    new_time = datetime.datetime.strftime(now, time_format)
    day = datetime.datetime.strftime(now, day_format)

    if new_time[0] == '0':
        new_time = new_time[1:]

    if day[0] == '0':
        day = day[1:]

    now = new_time + datetime.datetime.strftime(now, day_month) + day

    if lblTime.text != now:
        lblTime.text = now

    if weather.minutes_since_update() > 20:
        weather.get_forecast()
        i = 0
        for x in forecast_list:
            summary = weather.get_summary(i)
            x['lblHeader'].text = 'Today' \
                if i == 0 \
                else datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=i), '%A')
            if x['lblSummary'].text != weather.weather_string(summary):
                x['lblSummary'].text = weather.weather_string(summary)
            if x['picIcon'].file_normal != os.path.join(script_dir, 'Icons', summary.icon + '.png'):
                x['picIcon'].surface_normal = os.path.join(script_dir, 'Icons', summary.icon + '.png')
            i += 1

    lblTime.draw()

    for cast in forecast_list:
        cast['lblBg'].draw()
        cast['picIcon'].draw()
        cast['lblHeader'].draw()
        cast['lblSummary'].draw()

    pygame.display.update()
    time_game.tick(10)
