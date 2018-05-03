Language checking for scientific papers
--------------------------------------------

This program attempts to assist you in improving your paper before submission.

Features
---------

* Makes reports that help you:

  * find common grammar mistakes (e.g. prepositions)
  * find wordy phrases and suggest replacements
  * find long, wordy sentences
  * find tense inconsistencies
  * check visual impression of paper
  * check topic sentences
  * check a vs an before a consonant/vowel
  * spell-check

* Can analyse any LaTeX papers, and Overleaf projects.


Requirements
-------------

* python
* convert command (ImageMagick): Install with your distribution
* nltk: Install with pip
* nltk data: Install with python -m nltk.downloader all
* detex command (usually comes with LaTeX)
* pyhunspell (optional): Install with pip

Installation
--------------

These commands should not give you an error::

	$ which convert
	$ which python
	$ which detex
	$ which hunspell
	$ ls /usr/share/hunspell/{en_US,en_UK}.{dic,aff}

Then install the python packages and data:

	$ pip install pyhunspell  --user
	$ pip install nltk  --user
	$ python -m nltk.downloader punkt cmudict stopwords


Usage:
--------------

Using directly:

* create PDF from your latex file -> mypaper.pdf
* use detex to create pure text file -> mypaper.txt
* run $ python languagecheck.py mydir/mypaper.txt mydir/mypaper.pdf
* open with a web browser mypaper_index.html to see all reports

Using with Overleaf:

$ bash languagecheck_overleaf.sh <overleaf_url> <name of tex file>

For example:

$ bash languagecheck_overleaf.sh https://www.overleaf.com/123456789 mypaper.tex

Demo output
-------------

Under the following link is an analysis using an early draft of this paper: http://adsabs.harvard.edu/abs/2017MNRAS.465.4348B
Program output: https://johannesbuchner.github.io/languagecheck/demo/agnpaper.txt_index.html

See also - Statistics checklist
---------------------------------

Check for common statistics mistakes with this checklist
http://astrost.at/istics/minimal-statistics-checklist.html

