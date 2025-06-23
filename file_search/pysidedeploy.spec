[app]

# title of your application
title = pyside_app_demo

# project root directory. default = The parent directory of input_file
project_dir = C:\Users\ryanw\python_projects2\file_search\file_search

# source file entry point path. default = main.py
input_file = C:\Users\ryanw\python_projects2\file_search\file_search\__main__.py

# directory where the executable output is generated
exec_directory = C:\Users\ryanw\python_projects2\file_search\file_search

# path to the project file relative to project_dir
project_file = 

# application icon
icon = C:\Users\ryanw\.virtualenvs\file_search-FloKkQVk\Lib\site-packages\PySide6\scripts\deploy_lib\pyside_icon.ico

[python]

# python path
python_path = C:\Users\ryanw\.virtualenvs\file_search-FloKkQVk\Scripts\python.exe

# python packages to install
packages = Nuitka==2.6.8

# buildozer = for deploying Android application
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]

# paths to required qml files. comma separated
# normally all the qml files required by the project are added automatically
qml_files = qml\AsyncRequest.qml,qml\FileList.qml,qml\HelpScreen.qml,qml\main.qml,qml\ManageIgnore.qml,qml\ManageTableListDelegate.qml,qml\ManageTables.qml,qml\MenuItemWithShortcut.qml,qml\RecurringFiles.qml,qml\Utils.qml,qml\Viewer.qml,qml\viewers\ImageViewerComponent.qml,qml\viewers\PdfViewer.qml,qml\viewers\PdfViewerComponent.qml,qml\viewers\TextViewerComponent.qml

# excluded qml plugin binaries
excluded_qml_plugins = QtCharts,QtQuick3D,QtSensors,QtTest,QtWebEngine

# qt modules used. comma separated
modules = Qml,Core,Gui,QuickControls2,Quick

# qt plugins used by the application. only relevant for desktop deployment
# for qt plugins used in android application see [android][plugins]
plugins = platformthemes,egldeviceintegrations,generic,iconengines,scenegraph,xcbglintegrations,qmllint,platforminputcontexts,platforms/darwin,qmltooling,imageformats,accessiblebridge,platforms

[android]

# path to pyside wheel
wheel_pyside = 

# path to shiboken wheel
wheel_shiboken = 

# plugins to be copied to libs folder of the packaged application. comma separated
plugins = 

[nuitka]

# usage description for permissions requested by the app as found in the info.plist file
# of the app bundle. comma separated
# eg = extra_args = --show-modules --follow-stdlib
macos.permissions = 

# mode of using nuitka. accepts standalone or onefile. default = onefile
mode = onefile

# specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations

[buildozer]

# build mode
# possible values = ["aarch64", "armv7a", "i686", "x86_64"]
# release creates a .aab, while debug creates a .apk
mode = debug

# path to pyside6 and shiboken6 recipe dir
recipe_dir = 

# path to extra qt android .jar files to be loaded by the application
jars_dir = 

# if empty, uses default ndk path downloaded by buildozer
ndk_path = 

# if empty, uses default sdk path downloaded by buildozer
sdk_path = 

# other libraries to be loaded at app startup. comma separated.
local_libs = 

# architecture of deployed platform
arch = 

