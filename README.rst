Language checking for scientific papers
--------------------------------------------

This program attempts to assist you in improving your paper before submission.

Features
---------

* find common grammar mistakes (e.g. prepositions)
* find wordy phrases and suggest replacements
* find long, wordy sentences
* find tense inconsistencies
* check visual impression of paper
* check topic sentences



Requirements
-------------

* python
* convert command (ImageMagick): Install with your distribution
* nltk: Install with pip
* nltk data: Install with python -m nltk.downloader all
* detex command (usually comes with LaTeX)

How to use
--------------

* create PDF from your latex file
* use detex to create pure text file.
* run $ python languagecheck.py mydir/mypaper.txt mydir/mypaper.pdf
* open with a web browser example/mypaper_index.html





