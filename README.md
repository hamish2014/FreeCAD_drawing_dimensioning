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
  * center lines
  * adding, editing and moving dimension text
  * deleting dimensions

Limitations
  * No parametric updating, if the drawing is updated the dimensions need to be redone
  * undo and other similar features not supported
  * only works with FreeCAD version 0.15


Linux Installation Instructions
-------------------------------

To use this workbench clone this git repository under your FreeCAD MyScripts directory, and install the pyside and numpy python libraries.
On a Linux Debian based system such as Ubuntu, installation can be done through BASH as follows

  $ sudo apt-get install git python-numpy python-pyside

  $ mkdir ~/.FreeCAD/Mod

  $ cd ~/.FreeCAD/Mod

  $ git clone https://github.com/hamish2014/FreeCAD_drawing_dimensioning.git


Once installed, use git to easily update to the latest version:

  $ cd ~/.FreeCAD/Mod/FreeCAD_drawing_dimensioning

  $ git pull

Windows Installation Instructions
---------------------------------

Tested with 015.4415 Development Snapshot on a Windows 7 64bit-System (thanks BPLRFE )

  * download the git repository as ZIP
  * assuming FreeCAD is installed in "C:\PortableApps\FreeCAD 0_15",  go to "C:\PortableApps\FreeCAD 0_15\Mod" within Windows Explorer
  * create new directory named "DrawingDimensioning"
  * unzip downloaded repository in "C:\PortableApps\FreeCAD 0_15\Mod\DrawingDimensioning"
  
FreeCAD you will now have a new workbench-entry called "DrawingDimensioning".

*Pyside and Numpy are integrated in the FreeCAD dev-Snapshots 0.15, so these Python packages do not need to be installed individually*

Mac Installation Instructions
-----------------------------

Copy or unzip the drawing dimensioning folder to the directory *FreeCAD.app*/Contents/Mod

where *FreeCAD.app* is the folder where FreeCAD is installed. (thanks PLChris)

Setting your dimensioning preferences
-------------------------------------

Unit preferences are taken from the General unit preferences (excluding number of decimal places!).
To set unit preferences goto edit -> preferences -> general -> units

To set up your desired dimensioning style
  1. open FreeCAD
  2. switch to the Drawing dimensioning workbench
  3. edit -> preferences -> drawing dimensioning


Bugs
----

Please report bugs at https://github.com/hamish2014/FreeCAD_drawing_dimensioning/issues

