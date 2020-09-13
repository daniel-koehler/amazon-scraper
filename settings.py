from dataclasses import dataclass, field, asdict
from typing import Dict
import sys
import os
import json

SETTINGS_PATH = 'settings.json'

def headers_factory():
        user_agent = 'MyApp/0.1 (Language=Python {}; Platform={})'.format(sys.version.split()[0], os.uname().sysname)
        return {'User-Agent': user_agent}

@dataclass
class Settings:
    """ Data class storing general settings of the scraper """

    version: str = '0.1'
    date_format: str = '%d/%m/%y'
    currency: str = '$'

    db_path: str = 'data'
    db_name: str = 'products.json'

    headers: Dict[str, str] = field(default_factory=headers_factory)
    base_url: str = 'https://www.amazon.'
    tld: str = 'de'
    
    def __repr__(self):
        return str(asdict(self))

    @classmethod
    def load(cls) -> 'Settings':
        """ Load settings from json file. Returns default settings if no settings file exists """
        settings = cls()
        try:
            with open(SETTINGS_PATH, 'r') as f:
                cfg_dict = json.load(f)

                for key in cfg_dict:
                    if hasattr(settings, key):
                        setattr(settings, key, cfg_dict[key])
        except FileNotFoundError:
            pass

        return settings

    def save(self):
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(asdict(self), f)


