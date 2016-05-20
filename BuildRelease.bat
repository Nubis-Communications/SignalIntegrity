if exist dist rd dist /s /q
if exist build rd build /s /q
PyInstaller PySIApp\PySIApp.py --icon=AppIcon2.ico --onefile --noconsole --hidden-import=FileDialog
if exist dist goto built else goto notbuilt
:built
del PySIApp.spec
xcopy  PySIApp\icons dist\icons /E /I
xcopy  PySIApp\Help\PySIHelp.html.Lyxconv dist\Help\PySIHelp.html.Lyxconv /E /I
xcopy  PySIApp\Examples dist\Examples /E /I
rd build /s /q
cd dist
zip PySIApp.zip *.* -m -r
mv PySIApp.zip ..
cd ..
rd dist /s /q
goto done
:notbuilt
echo off
echo ERROR - NOT BUILT
:done
pause


