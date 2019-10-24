#!/bin/bash
python -tt "/usr/share/lyx/lyx2lyx/lyx2lyx" -V 2.1 -o "Help.21.lyx" "Help.lyx"
python ~/Work/elyxer-1.2.5/elyxer.py --title "Help" --embedcss lyx.css --splitpart 3  --nofooter --toc --notoclabels Help.21.lyx Help.html.LyXconv/Help.html

