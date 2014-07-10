#!/bin/bash
# Sun May 25 00:51:42 EEST 2014, nickkouk

# Makefile for quickly compiling to python code the .ui files from the Qt-Designer 

tool="pyside-uic-2.7"

$tool ../ui_files/Main_window.ui -o python_gui.py
$tool ../ui_files/Settings.ui -o python_settings.py
$tool ../ui_files/history_dialog.ui -o history_settings.py
$tool ../ui_files/new_dev.ui -o device_configuration.py
$tool ../ui_files/parameters_change.ui -o parameters_change.py
$tool ../ui_files/about_dialog.ui -o about_dialog.py
$tool ../ui_files/SyringePick.ui -o syringe_pick.py
