# FIRE-NFX-V2-OG+
The most advanced MIDI interface for FL Studio and the Akai FIRE ever created.  

This script consists of two scripts in one.

**FIRE-NFX-V2** - is the advanced script that does not use the step sequncer mode but does provide many advances features and acts as a control surface.

**FIRE-NFX-OG+** - is the original Akai FIRE script with some minor modifications. This one does allow fo rthe step sequnceing modes but does not have the advanced features of FIRE-NFX-V2

Once installed, pressing SHIFT+ALT+REC and releasing on the Akai FIRE will change modes.

## *Intro and Installation*

Please read each following section for proper set up and usage. It is vital you can identify the proper folders and can download and copy files to be sucessful at installation.  

This script requires FL Studio 20.9 or greater and an Akai FIRE Midi device.

## *User Data Folder*

Before installing this, you must know the location of your **User Data Folder** used by FL Studio. And more specifically you need to know how to get to the **MIDI Hardware Folder** that is located within/below the **User Data Folder**

You can find out how to get your specific **User Data Folder** location from the official [FL Studio documentation on the User Data Folder](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/envsettings_files.htm#userdata)

I recommend you open a file explorer and navigate to the folder.

For example purposes and to keep it short, I'll refer to example locations using my **User Data Folder** as:  

    C:\users\nfx\image-line\

**Your's will be different**. 

Once you have the location, you need to navigate to the **MIDI Hardware Folder** under the ***User Data Folder\FL Studio\Settings\Hardware***

So using my example, I would go to:

    C:\users\nfx\image-line\FL Studio\Settings\Hardware\

You may see a few folders in this location already for other devices.

Next, inside of the **MIDI Hardware Folder**, you need to create a folder named **FIRE-NFX-V2-OG-Plus** if it doesn't already exist.

This is our **Script Destination Folder** for the FIRE-NFX-V2-OG-Plus files (as an example, yours will be different):

    C:\users\nfx\image-line\FL Studio\Settings\Hardware\FIRE-NFX-V2-OG-Plus\

If you prefer to leave you file explorer open with this folder open, it might make copying the files easier later.  

## *Script File Download*
Once you have the folder properly identified, you can download the files from the the "main" or from the "releases": 

### Main Branch
The "main branch" is the lastest of the latest, and may have newer/improved features but also potential new bugs that go with the devlopment of the features. You can get the main branch files here: https://github.com/nfxbeats/FIRE-NFX-V2-OG-Plus/archive/refs/heads/main.zip

### Releases 
The release version is usually an older version that runs smoothly, but may be lacking in up to date features and fixes. You can get the latest release (and previous releases, if needed) from here: https://github.com/nfxbeats/FIRE-NFX-V2-OG-Plus/releases 

Find the ZIP download for the latest version. It should be the first link labelled as "**Source code (zip)** " on the page.

Pick a version, (main or release) and then download it and open it in a new window.

In the ZIP file you downloaded, you should open it and go into the first folder it may be named something similar to **FIRE-NFX-V2-OG-1**. Inside this folder you will see several files. The most important file is the script file named **device_FIRE__NFX__V2__OG_plus.py**. If you see this file, this is the correct source folder.

Next, copy/drag all of the files from this ZIP folder to your **Script Destination Folder** named "FIRE-NFX-V2-OG-Plus" that you created in the previous step.

In my example, the files would be copied into:

    C:\users\nfx\image-line\FL Studio\Settings\Hardware\FIRE-NFX-V2-OG-Plus\

## *First Time Activating The Script*
At this point you should have the files downloaded and copied into the correct folder and are ready to activate the script in FL Studio.

* In FL Studio press **F10** or select *Options>MIDI Settings*.

* Next click the button labelled **Refresh Device List**.

* Highlight the Akai FIRE device named "**FL STUDIO FIRE**" in the Input section.

* click on the **Controller Type** drop down.

* On the drop down's should be listed all the "User" scripts. Look for and select "FIRE-NFX-V2-OG+" from the right side of the list

If you don't see the "FIRE-NFX-V2-OG+" device, it means FL Studio does not see the file. You can try restarting FL Studio or double check your **User Data Folder** location. 

If you had no errors, you should be good to go! Remember, you can switch back the original script in the **Controller Type** drop down at anytime.

## *Switching Operating Modes* (Optional)
This version of the script has a slightly updated original script available. This means that you can go back to the old step sequencer style script of the original Fire release. To toggle between the modes, press SHIFT-ALT-REC and let go. Please not ethat when using the old script mode you only have the original features available as well.

## *User Settings and User Macros* (Optional)
To add your own custom user settings or use user macros, you need to run the ```MakeUserFiles.bat``` file (Windows only) and they will be created for you. 

Alternatively, You can manually make the files by copy/renaming the files like this:

|Original Filename| |New Filename|
|-----------------|-|------------|
|```fireNFX_UserSettings_EXAMPLE_.py```| renamed to |```fireNFX_UserSettings.py```|
|```fireNFX_UserMacros_EXAMPLE_.py```| renamed to |```fireNFX_UserMacros.py```|

There is text inside each of the files to provide guidance on how to edit them properly.

### *IMPORTANT Note For FL24 and up:* 
As of FL24, the user settings are stored in ```Settings.json``` and this file is created automatically after the script runs for the first time.

## FireNFX Bridge - Windows Helper App
If you are running FL24 or greater on Windows, you can use a helper app to get realtime information about the macros and knob definitions. The app is located in the script folder inside a .ZIP file named ```fireNFX_Bridge.zip```. Please watch the video [Fire NFX Bridge App Video](https://youtu.be/Uyy_Ideo5Sw) to see how it works and how to install and set it up.

## *Finally....*
A 30 minute demo of some of the features in FIRE-NFX-V2 (2024):

[![FireNFX V2](https://i9.ytimg.com/vi_webp/i6euDmrA4wk/mq2.webp?sqp=CJSMwbEG-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGEsgYShlMA8=&rs=AOn4CLCzL1PGv678HFHTjQCmKml3N--K6w)](http://www.youtube.com/watch?v=i6euDmrA4wk "FIRE-NFX-V2")

You can find some older basic video tutorials on each mode here (2023):  
* [FIRE-NFX V2.0 Mode Usage Playlist at YouTube](
https://www.youtube.com/watch?v=OioXZP5parw&list=PLcoTHKe9_nBqurVeWsaSKxhbmhQIU3xRH) (recommended)

* [Google Slideshow used in video presentation](https://docs.google.com/presentation/d/18H4eEFmZKqKtpXtdgnVxO4Pf-vFTQKxcoGKxqe7uSs4/edit#slide=id.g187abea832f_0_2) (incomplete but very useful as an intro)

Please leave me feedback/bug reports on one of the following:  
* [Official FL Studio MIDI Scripting Forum Thread](https://forum.image-line.com/viewtopic.php?p=1944203#p1944180)
* [/r/warbeats subreddit](https://reddit.com/r/warbeats/) 

## *Credits*
Much of this work was helped along by the following:
* Maddy Guthridge, aka HDSQ in the forums. Their [FL Studio API Stubs](https://github.com/MaddyGuthridge/FL-Studio-API-Stubs) have been invaluable to me while developing. They are also a powerhouse of help in the forums and even has their own FL script - [Universal Controller Script](https://github.com/MaddyGuthridge/Universal-Controller-Script) - that supports several devices.
* Anyone who gave me some honest and accurate feedback - you guys help tremendously with ideas and bugs, thank you.
* The author of the original AKAI Fire python script - I don't know who it is specifically (Miro?). Thank for the great code to learn from..

