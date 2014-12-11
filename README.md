FreeCAD_drawing_dimensioning
============================

Drawing dimensioning workbench for FreeCAD v0.15.
Take note that this workbench is experimental and still contains bugs.

Intended work-flow:
  * create a drawing page and a drawing of the part using the drawing workbench
  * switch to the drawing dimensioning workbench to add dimensions to that drawing

Features
  * linear dimensioning
  * circular and radial dimensioning
  * angular dimension
  * adding, editing and moving dimension text
  * deleting dimensions

Limitations
  * No parametric updating, if the drawing is updated the dimensions need to be redone
  * undo and other similar features not supported


Installation Instructions
-------------------------

To use this workbench clone this git repository under your FreeCAD MyScripts directory, and install the pyside and numpy python libraries.
On a Linux Debian based system such as Ubuntu, installation can be done through BASH as follows

  $ sudo apt-get install git python-numpy python-pyside

  $ mkdir .FreeCAD/Mod

  $ cd .FreeCAD/Mod

  $ git clone https://github.com/hamish2014/FreeCAD_drawing_dimensioning.git


Updating to the latest version
------------------------------

  $ cd ~/.FreeCAD/Mod/FreeCAD_drawing_dimensioning

  $ git pull


Bugs
----

Please report bugs at https://github.com/hamish2014/FreeCAD_drawing_dimensioning/issues

