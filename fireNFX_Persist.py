import general 
from fireNFX_Colors import *

cwd = ''

if(general.getVersion() >= 37):
    import json
    import os

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
    #MakeFiles('fireNFX_UserSettings')
    MakeFiles('fireNFX_CustomPlugins')

    def check_line_exists(file_path, line_to_check):
        """
        Checks if a specific line exists in a text file.

        Parameters:
        file_path (str): The path to the text file.
        line_to_check (str): The line to search for, including any necessary line endings.

        Returns:
        bool: True if the line exists, False otherwise.
        """
        with open(file_path, 'r') as file:
            for line in file:
                if line == line_to_check:
                    return True
        return False

    def add_line_to_file(file_path, line_to_add):
        """
        Adds a line to the end of a text file.

        Parameters:
        file_path (str): The path to the text file.
        line_to_add (str): The line to add to the file. This function will automatically add a newline character.

        """
        with open(file_path, 'a') as file:
            file.write(line_to_add + '\n')  # Adds the line with a newline at the end
            

    def save_code(code, file_path, overwrite=False):
        if os.path.exists(file_path) and not overwrite:
            print(file_path + " file exists. Nothing saved.")
            return False
        else:
            print("Saving " + file_path + ".")
            with open(file_path, 'w') as file:
                for line in code:
                    file.write(line + '\n') 
            return True

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
    
    def save_code(code, file_path, overwrite=False):
        print('save_code() insufficient version ', general.getVersion(), 'requires version >= 37')
        return False 
    
    def check_line_exists(file_path, line_to_check):
        print('check_line_exists() insufficient version ', general.getVersion(), 'requires version >= 37')

    def add_line_to_file(file_path, line_to_add):
        print('add_line_to_file() insufficient version ', general.getVersion(), 'requires version >= 37')