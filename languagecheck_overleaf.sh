#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
	echo "SYNAPSIS: $1 overleafurl maintexfile"
	echo
	echo "Example: python languagecheck_overleaf.sh https://www.overleaf.com/1234567890abcdef mypaper.tex"
	exit
fi
rm -rf overleaf_repo
D=$(dirname $0)
url=$1
texname=$2
texname=${texname/.tex/}
giturl=${url/www.overleaf.com/git.overleaf.com/}
echo "Fetching overleaf repository ${giturl} (with git clone)..."
git clone --depth=1 ${giturl} overleaf_repo

pushd overleaf_repo
echo "Extracting text from "$texname.tex" file (with detex)..."
detex $texname.tex > $texname.txt || exit 1
echo "Running pdflatex on $texname"
pdflatex -interaction batchmode $texname 2>/dev/null
echo "Running bibtex on $texname"
bibtex $texname || exit 1
echo "Running pdflatex again on $texname"
pdflatex -interaction batchmode $texname  2>/dev/null
pdflatex -interaction batchmode $texname || exit 1
popd
echo 
echo "Building PDF of the paper seems to have succeeded!"
echo

python ${D}/languagecheck.py overleaf_repo/$texname.{tex,pdf} || exit 1

xdg-open overleaf_repo/${texname}.tex_index.html

