# Auto-Face-Lock

This program allows you to lock and blank your computer if you are not present or someone else tries to use your computer. The functionality is configurable.

By default, the configuration will lock and blank your computer when you leave after 10 seconds. The configuration is stored in `~/.config/auto-face-lock/conf.json`. Your face information is stored numerically in `face_data.json`.

## Installation

You need to install the `face_recognition` library.

```bash
sudo apt install python3-numpy x11-xserver-utils build-essential cmake
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build; cd build; cmake ..; cmake --build .
cd ..
sudo python3 setup.py install
cd ..
rm -rf dlib
sudo pip3 install face_recognition
```

The software assumes you are using xscreensaver. If not, please see the configuration section before proceeding.

After installing the library, run the software with:
```bash
./auto-face-lock.py
```
It will prompt you to press enter before it takes the initial photo of you to train the system. After that, it will automatically blank the screen and lock your computer if you walk away.

## Configuration

This program is written to use xscreensaver. If you use some other screen locker, you will have to reconfigure the lock commands in the config file. The configuration options are:

 - **blank_cmd**: The command to blank your screen. *Default: `xset dpms force off`*
 - **blank_if_not_present**: Blank your screen if you walk away. *Default: true*
 - **blank_if_unknown**: Blank your screen if someone else is nearby. *Default: false*
 - **blank_interval**: Blank the screen every x seconds. *Default: 10*
 - **interval**: Check the webcam every x seconds. *Default: 5*
 - **lock_cmd**: The command to lock your computer. *Default: `xscreensaver-command -lock`*
 - **lock_if_not_present**: Lock your computer if you walk away. *Default: true*
 - **lock_if_unknown**: Lock your computer if someone else is nearby. *Default: false*
 - **lock_tolerance**: The number of times checks can fail before locking. *Default: 1*
 - **release_after_img**: Causes the webcam to only be on while taking pictures. *Default: true*
 - **tolerance**: The tolerance value for facial checking. Try 0.6 if you have problems. *Default: 0.54*
 - **unblank_cmd**: The command to unblank your screen. *Default: `xset dpms force on`*
