::to run this you must have elyxer installed.  see http://alexfernandez.github.io/elyxer/
::wherever you put it, you must append the path to the file elyxer.py in your PYTHONPATH
::you may also need to install imagemagick in order to convert pictures.  see http://www.imagemagick.org/script/index.php
python -m elyxer --title "PySI Help" --splitpart 3  --nofooter --toc --notoclabels --directory "./Help" "./Help/PySIHelp.lyx" "./Help/PySIHelp.html.LyXconv/PySIHelp.html"
START /WAIT explorer "Help\PySIHelp.html.LyXconv\PySIHelp.html"
