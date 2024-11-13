import general 
from fireNFX_Colors import *

if(general.getVersion() >= 37):
    import json
    import os
    import shutil

    cwd = os.getcwd() + '\\'

    def MakeFiles(filename):
        source_path = cwd + filename + '_EXAMPLE.py'
        destination_path = cwd + filename + '.py' 
        if os.path.exists(destination_path):
            print(filename + " file exists.")
        else:
            print("Making " + filename + ".")
            # Open the source file in read mode and the destination file in write mode
            with open(source_path, 'rb') as source_file:
                with open(destination_path, 'wb') as destination_file:
                    # Read from the source and write to the destination
                    destination_file.write(source_file.read())            

    MakeFiles('fireNFX_UserMacros')
    MakeFiles('fireNFX_UserSettings')
    MakeFiles('fireNFX_CustomPlugins')

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