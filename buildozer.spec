[app]

# (str) Title of your application
title = 钻井参数监测系统
# (str) Package name
package.name = drilling_monitor

# (str) Package domain (needed for android/ios packaging)
package.domain = com.example.drilling

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
requirements = 
    python3,
    kivy==2.3.0,
    requests,
    certifi,
    chardet,
    idna,
    urllib3,
    openssl

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Enable AndroidX support.
android.enable_androidx = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) The format used to package the app for release mode
android.release_artifact = apk

# (str) The format used to package the app for debug mode
android.debug_artifact = apk

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (bool) Indicate whether the screen should stay on
android.wakelock = False

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

#
# Python for android (p4a) specific
#

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2