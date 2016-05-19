#!/usr/bin/env python
import sys, os
import random
import codecs
import subprocess
import glob
import nltk # Install nltk: $ pip install nltk --user

header = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"> 
<title>%(title)s</title>
</head>
"""

if len(sys.argv) != 3:
	sys.stderr.write("""SYNOPSIS: %(cmd)s <txtfile> <pdffile>

txtfile: Use detex to remove tex from a latex file.
	Example: detex mn.tex > mn.txt
pdffile: PDF of your paper

Environment variables:
LANG: [en_UK|en_US]
	Choose language.

Usage example:
	LANG=UK %(cmd)s mn.txt mn.pdf

Johannes Buchner (C) 2016
http://github.com/JohannesBuchner/languagecheck/
""" % dict(cmd=sys.argv[0]))
	sys.exit(1)
filename = sys.argv[1]
pdf = sys.argv[2]
lang = os.environ.get('LANG', 'en_UK')
if 'US' in lang:
	lang = 'en_US'
elif 'UK' in lang:
	lang = 'en_UK'
else:
	lang = 'en_UK'
print 'Using language "%s". You can set LANG=en_UK or LANG=en_US.' % lang
	     
prefix = filename + '_vis-'
def list_img():
	return sorted(glob.glob(prefix + '*.png'))

for i in list_img():
	#print 'deleting old image %s' % i
	os.remove(i)

print 'creating visualisation ...'
process = subprocess.Popen(['convert', '-density', '40', '-blur', '5x3', pdf, prefix + "%02d.png"])

verb_classes = ['VB', 'VBD', 'VBN', 'VBP', 'VBZ']

def is_full_sentence(txt, sentence, entities):
	has_verb = False
	has_end = False
	has_noun = False
	for w, wt in sentence:
		if wt in verb_classes:
			has_verb = True
		if wt.startswith('NN'):
			has_noun = True
		if wt == '.':
			has_end = True
	if has_verb and has_noun and has_end:
		return True
	nsym = sum([wt in ['.', ':', ','] for w, wt in sentence])
	nwords = len(sentence)
	if nsym > 3:
		return False
	if nwords > 10:
		return True
	return False

def topic_sentences(paragraphs):
	with codecs.open(filename + '_topic.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Topic sentences'))
		f.write("""<h1>Topic sentences of each paragraph</h1>
		The first sentence of a should give the heading / selling 
		point of 
		the paragraph. Details follow inside the paragraph.
		Does this paper make sense when reading only the first
		sentences of the paragraph?
		<hr/>
		<ul>
		""")
		for para in paragraphs:
			txt, sentence, entities = para[0]
			if is_full_sentence(txt, sentence, entities):
				f.write("<li>" + txt.split('. ')[0] + '\n') 
		f.close()

def consistent_paragraph(paragraphs):
	with codecs.open(filename + '_para.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Paragraph consistency'))
		f.write("""<h1>Paragraph consistency</h1>
		<p>Each paragraph should make sense on its own. 
		They should not be too long.
		Here they are in random order.
		
		<p>Think of the inverted pyramid (important information first,
		then clarify). Comparable to a telegraph line, the attention of the 
		reader can break off at any point.
		</p>
		<hr/>
		""")
		paragraphs = list(paragraphs)
		random.shuffle(paragraphs)
		for para in paragraphs:
			if any((is_full_sentence(txt, sentence, entities) for txt, sentence, entities in para)):
				p = ' '.join([txt for txt, sentence, entities in para])
				f.write("<hr/>" + p + '\n') 
		f.close()

def count_tenses(tags):
	past_count = 0
	present_count = 0
	future_count = (' '.join([w for w, wt in tags])).count('going to')
	for w, wt in tags:
		if w in ['shall', 'will']:
			future_count += 1
		elif wt in ['VB', 'VBP', 'VBZ']:
			present_count += 1
		elif wt == 'VBD':
			past_count += 1
	return past_count, present_count, future_count

def guess_tense(tags, entities, last_tense):
	past_count, present_count, future_count = count_tenses(tags)
	if future_count > 0:
		return 'future'
	elif past_count > 2:
		return 'past'
	elif past_count > 0 and present_count == 0:
		return 'past'
	elif present_count > 0 and past_count == 0:
		return 'present'
	elif past_count > 1 and present_count <= past_count:
		return 'past'
	elif present_count > 1 and past_count < present_count:
		return 'present'
	else:
		return last_tense

def guess_tense_tree(tags, entities, last_tense):
	parts = []
	part = []
	for w, wt in tags:
		if w in [',', ':', ';']:
			parts.append(part)
			part = []
		else:
			part.append((w, wt))
	parts.append(part)
	parts = [part for part in parts if len(part) > 0]
	# if all put together:
	tense_full = guess_tense(tags, entities, last_tense)
	for part in parts:
		tense_part = guess_tense(part, [], tense_full)
		if tense_part != tense_full:
			return 'mixed'
	return tense_full
		
	
def tenses(paragraphs):
	with codecs.open(filename + '_tense.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Tenses'))
		f.write("""<h1>Tenses</h1>
		<style type="text/css">
		.past{color: blue}
		.present{color: green}
		.future{color: orange}
		.mixed{color: red}
		</style>
		""")
		def time(txt, cls):
			return '<span class="%s">%s</span>' % (cls, txt)
		f.write(time("Past: When describing your steps.", "past") + "<br/>")
		f.write(time("Present: When describing general truths.", "present") + "<br/>")
		f.write(time("Future: When describing future work.", "future") + "<br/>")
		f.write(time("Mixed tenses.", "mixed") + "<br/>")
		f.write("<br/>")
		paragraphs = list(paragraphs)
		for para in paragraphs:
			last_tense = None
			f.write("<p>")
			for txt, tags, entities in para:
				if is_full_sentence(txt, tags, entities):
					tense = guess_tense_tree(tags, entities, last_tense)
					if tense is None:
						f.write(txt)
					else:
						f.write(time(txt, tense))
					last_tense = tense
					f.write('\n')
			f.write("\n</p>")
		f.close()

stopwords = nltk.corpus.stopwords.words('english')
def wordiness(paragraphs):
	with codecs.open(filename + '_wordiness.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Wordiness'))
		f.write("""<h1>Wordiness, long sentences</h1>
		These sentences seem very long, have many sub-clauses or too many small words (stopwords). 
		Can you break them into smaller sentences? Can you reword them?
		<hr/>
		<style type="text/css">
		.evaluation{font-family: monospace; color: gray;}
		</style>
		""")
		ranked_sentences = []
		for para in paragraphs:
			for txt, tags, entities in para:
				if is_full_sentence(txt, tags, entities):
					n = len(tags)
					nclauses = sum([wt in [':', ';', ',', 'and'] for w, wt in tags])
					nstop = sum([w in stopwords for w, wt in tags])
					badness = 0
					reasons = []
					if n > 30:
						badness += n / 10 * 100
						reasons.append('long')
					if nclauses > 3:
						badness += nclauses * 10
						reasons.append('clauses')
					if n > 10 and nstop * 3 > n:
						badness += (nstop * 2 * 30 / n)
						reasons.append('stopwords')
					ranked_sentences.append((badness, reasons, txt))
		ranked_sentences.sort(reverse=True)
		for badness, reasons, txt in ranked_sentences:
			if badness < 30: break
			f.write("<hr/>%s <span class='evaluation'>(%d,%s)</span>\n" % (txt, badness, ','.join(reasons)))
		f.close()
	

def tricky_words(paragraphs):
	with codecs.open(filename + '_tricky.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Tricky words'))
		f.write("""<h1>Tricky words, Prepositions & Wordiness</h1>
		These phrases are misused often, colloquial or just wordy.
		Think about replacing them or rewriting the sentence; some suggestions are given.
		<hr/>
		<style type="text/css">
		.evaluation{font-family: monospace; color: gray;}
		</style>
		""")
		nrules = 0
		nused = 0
		rules = open(os.path.join(os.path.dirname(__file__), 'tricky.txt')).readlines()
		rules += open(os.path.join(os.path.dirname(__file__), 'tricky_%s.txt' % lang)).readlines()
		for rule in rules:
			rule = rule.strip()
			if rule.startswith('###'):
				f.write("<h2>%s</h2>\n" % rule.lstrip('# '))
				continue
			if rule.startswith('#') or len(rule) == 0:
				continue
			if ' -> ' not in rule:
				print 'bad rule in tricky.txt:', rule
			a, b = rule.split('->')
			a = a
			b = b
			used = False
			for para in paragraphs:
				for txt, tags, entities in para:
					if a in txt:
						if not used:
							f.write("<h5>%s</h5>\n" % rule)
							f.write("<ul>\n")
							used = True
						f.write("<li>%s\n" % (txt.replace(a, '<b>' + a + '</b>' + ' -> <em>'+b+'</em> ')))
			if used:
				nused += 1
				f.write("</ul>\n")
			nrules += 1
		
		nrules 
		f.write("<p>Only %d/%d rules have applied to this text</p>\n" % (nused, nrules))
		f.close()

with codecs.open(filename + '_index.html', 'w', 'latin1') as f:
	f.write(header % dict(title='Language analysis'))
	f.write("""<h1>Language analysis</h1>
	This program attempts to assist you in improving your paper.
	Language is ambiguous and subjective, a computer can not understand it.
	All results should be seen as suggestions; think about the highlighted sentences.
	
	<ul>
	<li>%(checkbox)s Do spell-checking (in your LaTeX editor, e.g. lyx)
	<li>%(checkbox)s Do grammar-checking (in LanguageTool)
	<li>%(checkbox)s <a href="%(prefix)s_topic.html">Each paragraph should open informatively.</a>
	<li>%(checkbox)s <a href="%(prefix)s_tricky.html">Tricky words, Prepositions & Wordiness</a>
	<li>%(checkbox)s <a href="%(prefix)s_wordiness.html">Wordiness & long sentences</a>
	<li>%(checkbox)s <a href="%(prefix)s_tense.html">Consistent use of tenses</a>
	<li>%(checkbox)s <a href="%(prefix)s_para.html">Paragraph consistency</a>
	<li>%(checkbox)s <a href="%(prefix)s_vis.html">Check the visual appeal</a>
	</ul>

	<p>
	This program may help you catch some classes of common mistakes,
	but does not replace careful reading and self-editing.
	Here are some steps:
	</p>

	<h3>Context-level</h3>
	<ul>
	<li>%(checkbox)s Is the text placed well in context (in relation to wider debate)?
	<li>%(checkbox)s Will readers from different contexts understand? Do they require more support?
	<li>%(checkbox)s Are there enough inter-text links? References, cross-links to sections, figures. Do you need to be more explicit?
	</ul>
	
	<h3>Concept-level</h3>
	<ul>
	<li>%(checkbox)s what concept involved? How difficult are they? Do they rely on culture?
	<li>%(checkbox)s Have the concepts been presented clearly and in enough detail?
	<li>%(checkbox)s What is the argument? How complicated is it? How obvious is the logic?
	</ul>

	<h3>Sentence-level</h3>
	<ul>
	<li>%(checkbox)s Spot inert sentences. Wordy, awkward connections. Those that do not advance the argument/text.
	<li>%(checkbox)s Delete whereever you can.
	<li>%(checkbox)s How lengthy are the sentences? How complex grammatically are the sentences? read most difficult sentence aloud.
	<li>%(checkbox)s Which sentence is most difficult to understand / easy to misinterpret?
	<li>%(checkbox)s Unclear grammar?
	<li>%(checkbox)s Add repetition only where useful
	<li>%(checkbox)s Consider different modes of presenting
	<li>%(checkbox)s How would one of my reader see this text?
	<li>%(checkbox)s Put best, shining ideas in the spotlight
	</ul>
	
	<h3>Word/Phrasing</h3>
	Tip: Try reading the text to yourself out loud! (alternatively, try a text-to-speech program)
	<ul>
	<li>%(checkbox)s word/phrase unfamiliar?
	<li>%(checkbox)s word/phrase ambiguous/confusing?
	<li>%(checkbox)s word/phrase synonyms, different meanings? distinct?
	</ul>
	
	<p>Repeat from above.</p>
	
	<h3>Slow reading, secretary-level work</h3>
	<ul>
	<li>%(checkbox)s Before doing this, it is best to take a break from your text for a day or two
	<li>%(checkbox)s Adopt the attitude: "There are bound to be some errors here and it is my job to find them now."
	<li>%(checkbox)s Reformat your text to double-spaced lines and read aloud.
	<li>%(checkbox)s Check completeness (internal references)
	<li>%(checkbox)s Check consistency (nomenclature, policies)
	<li>%(checkbox)s Check accuracy (of quotations, values, statistics, references).
	</ul>
	<p>
	
	<h3>Presentation</h3>
	<ul>
	<li>%(checkbox)s Adhere to style of publisher
	<li>%(checkbox)s Check figures
	</ul>
	<p>
	<ul>
	""" % dict(prefix=os.path.basename(filename), checkbox='<input type="checkbox" />'))


doc = codecs.open(filename, encoding='latin1').read()
while '\n\n\n' in doc:
	doc = doc.replace('\n\n\n', '\n\n')

chunks = doc.split('\n\n')

# those chunks are the parts of the documents
#print '\n\n---\n\n'.join(chunks[:20])
#print 'XXXXXXXX'
# python -m nltk.downloader all
#tagger = nltk.data.load(nltk.tag._POS_TAGGER).tag_sents
tagger = nltk.tag.pos_tag_sents
#from nltk.tag.hunpos import HunposTagger
#import os
#a = os.path.dirname(__file__)
#tagger = HunposTagger(path_to_model=a + '/hunpos-1.0-linux/hunpos-tag', path_to_bin=a + '/hunpos-1.0-linux/en_wsj.model')

paragraphs = []
for i, chunk in enumerate(chunks):
	sys.stdout.write('Analysing paragraph %d/%d  \r' % (i+1, len(chunks)))
	sys.stdout.flush()
	chunk = chunk.replace(' .', ' X.').replace('\n', ' ')
	chunk = chunk.replace('[', ' ').replace(']', ' ').replace('  ', ' ').replace('  ', ' ')
	# try to pass this on to ntkl
	sentences = nltk.sent_tokenize(chunk)
	tokens = [nltk.word_tokenize(sent) for sent in sentences]
	tags = tagger(tokens)
	#entities = nltk.chunk.ne_chunk_sents(tags)
	entities = [[] for tag in tags]
	para = zip(sentences, tags, entities)
	if para:
		paragraphs.append(para)

print
print 'analysis: tricky words'
tricky_words(paragraphs)
print 'analysis: wordiness'
wordiness(paragraphs)
print 'analysis: tenses'
tenses(paragraphs)
print 'analysis: topic sentences'
topic_sentences(paragraphs)
print 'analysis: paragraph consistency'
consistent_paragraph(paragraphs)


print 'analysis: visualisation'
r = process.wait()
if r != 0:
	print 'visualisation returned with', r
with codecs.open(filename + '_vis.html', 'w', 'latin1') as f:
	f.write(header % dict(title='Appearance'))
	f.write("""<h1>Appearance</h1>
	<p>Papers are also supposed to look attractive, 
	so that the reader wants to jump in.
	</p>

	<p>Do these pages look odd? Does the abstract look unusually long? 
	Are the figures well-placed and inviting?
	</p>
	""")
	j = 0
	for i in list_img():
		if os.path.exists(i):
			j = j + 1
			f.write("<img src='%s'\n />" % os.path.basename(i))
			if j % 2 == 0:
				f.write("<br/>\n")
	if j == 0:
		print 'WARNING: converting pdf to images seems to have failed.'


print 'done'

print
print 'open %s in a web browser' % (filename + '_index.html')
