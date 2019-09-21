import json
import os
import sys

import pandas as pd


class Config(pd.Series):
    def __init__(self, env: str):
        config_filepath = os.path.join(__path__[0], f'{env.lower()}.json')
        config_file = open(config_filepath, 'r')
        config_json = json.load(config_file)
        config_file.close()

        super().__init__(pd.io.json.json_normalize(config_json, sep='_').T[0],
                         name=env.upper())

    def __setattr__(self, name, value):
        frame = sys._getframe(2)
        calling_file = frame.f_code.co_filename
        calling_func = frame.f_code.co_name

        if calling_file == __file__ and calling_func == '__init__':
            # We only set attributes in the initializing function
            super().__setattr__(name, value)
        else:
            raise TypeError('Config objects are immutable')

    def set_env(self, env: str):
        self.__init__(env)


sys.modules[__name__] = Config(os.getenv('JOBHUNTER_ENV', 'DEV'))
