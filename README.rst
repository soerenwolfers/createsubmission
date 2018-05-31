createsubmission: Create publication ready zip file from LaTeX directory
==========================================
:Author: Soeren Wolfers <soeren.wolfers@gmail.com>
:Organization: King Abdullah University of Science and Technology (KAUST) 

This package provides a command line tool to package a LaTeX directory in a zip file that is ready for publication. 

At the moment this includes copying packages and libraries from the filesystem into the zip file, warning about broken references and citations, and removing auxiliary files.

Installation: Relies on package :code:`swutil`, which can be installed with :code:`pip install swutil`. 
Usage: :code:`createsubmission <from> <to>` creates <to>.zip of directory <from>


