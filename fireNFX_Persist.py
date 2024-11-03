import general 
from fireNFX_Colors import *


if(general.getVersion() >= 37):
    import json
    import os

    cwd = os.getcwd() + '\\' 

    def save_object(obj, file_path):
        file_path = cwd + file_path        
        try:
            with open(file_path, 'w') as file:
                json.dump(vars(obj), file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving object {obj}: {e}")
            return False

    def load_object(obj, file_path):
        file_path = cwd + file_path
        try:
            with open(file_path, 'r') as file:
                settings_dict = json.load(file)
                for key, value in settings_dict.items():
                    if not isinstance(value, list) and not isinstance(value, dict): # don't process if its a list or dict
                        if value in SETTINGS_COLORS.keys():
                            # print(f"Setting Color {key} to {SETTINGS_COLORS[value]}")
                            value = SETTINGS_COLORS[value]
                    #     else:
                    #         print(f"Setting {key} to {value}")
                    #         pass
                    # else:
                    #     print(f"Setting {key} to {value}")
                    #     pass 
                    setattr(obj, key, value)
            return True
        except Exception as e:
            print(f"Error loading object {obj}: {e}")
            return False        
else:
    def save_object(obj, file_path):
        print('save_object() insufficient version ', general.getVersion(), 'requires version >= 37')
        return False

    def load_object(obj, file_path):
        print('load_object() insufficient version ', general.getVersion(), 'requires version >= 37')
        return False