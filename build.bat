@echo off
set "scriptdir=%~dp0"
call pyinstaller --noconfirm --onedir --windowed ^
    --icon "%scriptdir%encircgui\i3dr_logo.ico" ^
    --paths "%scriptdir%encircgui" ^
    --add-data "%scriptdir%encircgui\i3dr_logo.png;." ^
    "%scriptdir%encircgui\encirc_GUI.py"
