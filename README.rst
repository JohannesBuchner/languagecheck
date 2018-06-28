Language checking for scientific papers
--------------------------------------------

This program attempts to assist you in improving your paper before submission.

Features
---------

* Can analyse any LaTeX papers, and Overleaf projects.
* Makes automated reports to point you to improvements:

  * Word level:

    * find common grammar mistakes, like wrong prepositions
    * find wordy phrases and suggest replacements
    * a vs an
    * spell-check (using hunspell)

  * Sentence level:

    * find long, wordy sentences
    * check topic sentences

  * Paragraph level:

    * find tense inconsistencies

  * Paper level:

    * check visual impression of paper

* All analysis is done offline -- your text does not leave your computer.
* Supports British and American English, but focusses on issues applying to both.

Note that there are false positives -- only you can decide whether a 
change would make sense, the reports only point out potential issues.

If you find some rules useless (too many false positives), or you want to add more, please send a pull request!

Demo output
-------------

Example analysis (of an early draft of `this paper <http://adsabs.harvard.edu/abs/2017MNRAS.465.4348B>`_):

* `Example report for misused phrases <https://johannesbuchner.github.io/languagecheck/demo/agnpaper.txt_tricky.html>`_
* `Overview of all reports <https://johannesbuchner.github.io/languagecheck/demo/agnpaper.txt_index.html>`_

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

Then install the python packages and data::

	$ pip install pyhunspell  --user
	$ pip install nltk  --user
	$ python -m nltk.downloader cmudict stopwords punkt averaged_perceptron_tagger


Usage
--------------

*Using directly*:

* create PDF from your latex file -> mypaper.pdf

  * For example, run "pdflatex mypaper.tex"

* use detex to create pure text file -> mypaper.txt

  * For example, run "detex mypaper.tex > mypaper.txt". You need detex installed.
  * This does not capture figure captions. The detex.sh script can help you include those texts, "bash detex.sh mypaper.tex". You still need detex installed

* run $ python languagecheck.py mydir/mypaper.txt mydir/mypaper.pdf
* open with a web browser mypaper_index.html to see all reports

*Using with Overleaf*::

	$ bash languagecheck_overleaf.sh <overleaf_url> <name of tex file>
	# for example:
	$ bash languagecheck_overleaf.sh https://www.overleaf.com/123456789 mypaper.tex

See also
---------

* style-check, a similar program written in Ruby: https://github.com/nspring/style-check/
* Statistics checklist:  Check for common statistics mistakes with this checklist
   http://astrost.at/istics/minimal-statistics-checklist.html

