#!/bin/bash

if [ -z "$1" ]; then
	echo "SYNAPSIS: $0 overleafurl [maintexfile]"
	echo
	echo "Example: bash languagecheck_overleaf.sh https://www.overleaf.com/1234567890abcdef mypaper.tex"
	exit 1
fi
rm -rf overleaf_repo
D=$(dirname $0)
url=$1
giturl=${url/www.overleaf.com/git.overleaf.com/}
echo "Fetching overleaf repository ${giturl} (with git clone)..."
git clone --depth=1 ${giturl} overleaf_repo

pushd overleaf_repo
if [ -z "$2" ]; then
	if [ "$(ls *.tex|wc -l)" == "1" ]
	then
		texname=$(ls *.tex|head -n1)
		texname=${texname/.tex/}
		echo "Guessing manuscript name: '$texname'"
	else
		echo "Multiple manuscript names: '$(ls *.tex)'"
		echo "call this script again with either: "
		for texname in *.tex; do
			echo "  - bash $0 $url $texname"
		done
		exit 1
		
	fi
else
	texname=$2
	texname=${texname/.tex/}
fi
popd
echo "Extracting text from "$texname.tex" file (with detex)..."
bash $D/detex.sh overleaf_repo/$texname.tex || exit 1
pushd overleaf_repo
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

