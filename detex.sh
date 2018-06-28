#!/bin/bash

input=$1

if [ -z "$input" ]; then
echo "SYNAPSIS: $0 mylatex.tex"
echo
echo "Primarily runs detex mylatex.tex > mylatex.txt"
echo "Additionally, extracts texts from figure and table captions."
exit 1
fi

output=${input/.tex/.txt}
if [[ "$input" == "$output" ]]; then
output="$input".txt
fi

#if [ -e "$output" ]; then
#echo "Output file $output already exists, not overwriting. Please delete it first."
#exit 1
#fi

echo "detexing main text ..."

detex $input > $output

echo "extracting figure captions ..."

< $input sed 's/%.*//g' | 
grep -Pzo '(?s)\\caption\{.*?\\end\{' |
sed 's,\label{[^}]*},,g' |
sed 's,\ref{[^}]*},REF,g' |
tr '\n' ' ' | 
sed 's,\\caption{,\n,g' |
sed 's, *\\end{.*,,g'|
sed 's,$,\n,g' | 
detex >> $output

echo "$output created."

