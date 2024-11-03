import general 
from fireNFX_Utils import ColorToDelphiColor

if(general.getVersion() >= 37):
    import configparser
    import os
    print('')
    print('Your FireNFX Bridge App should use this folder: ')
    print(' ', os.getcwd())
    print('')

    INIFile = os.getcwd() + '\\fireNFX_Bridge.ini'

    def WriteINI( section, key, value):
        try:
            #print('WriteINI()', section, key, value)
            # Create a config parser object
            config = configparser.ConfigParser()
            
            # Read the existing file if it exists
            config.read(INIFile)
            
            # Check if the section exists, if not add it
            if not config.has_section(section):
                config.add_section(section)
            
            if 'olor' in key:
                value = '${:08X}'.format(ColorToDelphiColor(value)) # value to delphi style hex

            # Set the key-value pair in the section
            config.set(section, key, str(value))
            
            # Write the changes back to the file
            with open(INIFile, 'w') as configfile:
                config.write(configfile)

        except Exception as e:
            print(e)
else:
    print('')
    print('Your FL Version is not compatible with the FireNFX Bridge App.')
    print('')    
    def WriteINI(section, key, value):
        #print('WriteINI() insufficient version ', general.getVersion(), 'requires version >= 37')
        pass