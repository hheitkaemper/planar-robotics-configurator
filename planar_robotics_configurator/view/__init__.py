import os

# Display the python and kivy log in the console
os.environ["KIVY_LOG_MODE"] = "MIXED"

from kivy import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '600')
Config.set('kivy', "log_level", "warning")
