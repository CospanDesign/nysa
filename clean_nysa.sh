#! /bin/bash

find -name '*.pyc' -exec rm {} \;
find -name '*.swp' -exec rm {} \;
find -name '*.sim' -exec rm {} \;
find -name '*.vcd' -exec rm {} \;
