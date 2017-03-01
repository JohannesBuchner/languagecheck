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

def not_punctuation(w):
	return not (len(w)==1 and (not w.isalpha()))
def get_word_count(text): 
	return len(filter(not_punctuation, word_tokenize(text)))
def get_sent_count(text):
	return len(sent_tokenize(text))
# from https://github.com/mmautner/readability/blob/master/utils.py, Apache2 licensed
import syllables_en
def count_syllables(words):
	syllableCount = 0
	for word in words:
		syllableCount += syllables_en.count(word)
	return syllableCount

# from textstat/textstat.py, MIT licensed
import string
import re
exclude = list(string.punctuation)
easy_word_set = set([line.strip() for line in open(os.path.join(os.path.dirname(__file__), 'easy_words.txt')) 
	if not line.startswith('#')])

def count_words(words):
	count = 0
	for w in words:
		if w in exclude:
			continue
		count += 1
	return count

def count_syllables(words):
	for w in words:
		if w in exclude:
			continue
		s = syllables_en.count(w)
		if s > 7: # probably a latex thing and not a word
			continue
		yield s

def syllable_stats(words):
	totsyl = 0
	polysylcount = 0
	complexwords = 0
	for w in words:
		if w in exclude:
			continue
		s = syllables_en.count(w)
		
		if s > 7: # probably a latex thing and not a word
			continue
		totsyl += s
		if s >= 3:
			polysylcount += s
			complex_s = s
			# complex words are not nouns, have >= 3 syl, not counting common endings
			# (and are not compound words, not checked here)
			if any([w.endswith(ending) for ending in ('es', 'ed', 'ing')]):
				complex_s = s - 1
			if complex_s >= 3 and w[0].islower() and w not in easy_word_set:
				complexwords += 1
	return totsyl, polysylcount, complexwords

def readability(paragraphs):
	with codecs.open(filename + '_readability.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Reading ease'))
		colors = []
		#for flesch_reading_ease in 95, 85, 75, 65, 55, 40, 20:
		#	u = 1 - flesch_reading_ease / 100.
		for fog_index in [17,16,15,14,13,12,11,10,9,8,7,6]:
			u = (fog_index - 6) / (17 - 6.)
			u = max(0, min(1, u))
			
			# add color here
			g = max(0.1, 1 - u*1.3)
			b = g
			r = min(1, 1.7 - u*1.3)
			colors += [r*255, g*255, b*255]
		f.write("""<h1>Reading ease</h1>
		<style type="text/css">
		.readingeaseresults{
			color: #444444; 
			font-size: x-small;
		}
		.results {
			font-weight: bold;
			color: black;
			margin: 0.5em;
			padding: 0.5em;
		}
		.results p {
			background-color: white;
			margin: 0.5em;
			font-weight: normal;
		}
		.info {
			color: #444444;
		}
		.info table {
			font-size: x-small;
		}
		</style>
		
		<p class="info">
		Highlighting difficult passages by measure of the
		 <a href="https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests">reading ease</a>
		and <a href="https://en.wikipedia.org/wiki/Gunning_fog_index">fog index</a>, which measure
		average sentence length, average syllables and frequency of complex words. 
		These can point to passages which could be simplified to more direct language. 
		<p class="info">
		Warning: these should only be taken only as guides! Measuring language have severe limitations!
		</p>
		<div class="info">
<table>
<tr><th>Score	<th>Flesch radability ease
<tr><td>100.00-90.00	<td>Very easy to read. Easily understood by an average 11-year-old student.
<tr><td>90.0-80.0	<td>Easy to read. Conversational English for consumers.
<tr><td>80.0-70.0	<td>Fairly easy to read.
<tr><td>70.0-60.0	<td>Plain English. Easily understood by 13- to 15-year-old students.
<tr><td>60.0-50.0	<td>Fairly difficult to read.
<tr><td>50.0-30.0	<td>Difficult to read.
<tr><td>30.0-0.0	<td>Very difficult to read. Best understood by university graduates.
</table>

""")

		f.write("""
<table>
<tr><th>Fog Index<th>Reading level by grade
<tr style='background-color: rgb(%d,%d,%d)'><td>17<td>	College graduate
<tr style='background-color: rgb(%d,%d,%d)'><td>16<td>	College senior
<tr style='background-color: rgb(%d,%d,%d)'><td>15<td>	College junior
<tr style='background-color: rgb(%d,%d,%d)'><td>14<td>	College sophomore
<tr style='background-color: rgb(%d,%d,%d)'><td>13<td>	College freshman
<tr style='background-color: rgb(%d,%d,%d)'><td>12<td>	High school senior
<tr style='background-color: rgb(%d,%d,%d)'><td>11<td>	High school junior
<tr style='background-color: rgb(%d,%d,%d)'><td>10<td>	High school sophomore
<tr style='background-color: rgb(%d,%d,%d)'><td>9<td>	High school freshman
<tr style='background-color: rgb(%d,%d,%d)'><td>8<td>	Eighth grade
<tr style='background-color: rgb(%d,%d,%d)'><td>7<td>	Seventh grade
<tr style='background-color: rgb(%d,%d,%d)'><td>6<td>	Sixth grade
</table>
<hr/>
""" % tuple(colors))


#		f.write("""
#<tr><th>Fog Index<th>Reading level by grade
#<tr><td>17<td>	College graduate
#<tr><td>16<td>	College senior
#<tr><td>15<td>	College junior
#<tr><td>14<td>	College sophomore
#<tr><td>13<td>	College freshman
#<tr><td>12<td>	High school senior
#<tr><td>11<td>	High school junior
#<tr><td>10<td>	High school sophomore
#<tr><td>9<td>	High school freshman
#<tr><td>8<td>	Eighth grade
#<tr><td>7<td>	Seventh grade
#<tr><td>6<td>	Sixth grade
#</table>
#
#<table>
#<tr><th>Score	<th>Flesch radability ease
#<tr style='background-color: rgb(%d,%d,%d)'><td>100.00-90.00	<td>Very easy to read. Easily understood by an average 11-year-old student.
#<tr style='background-color: rgb(%d,%d,%d)'><td>90.0-80.0	<td>Easy to read. Conversational English for consumers.
#<tr style='background-color: rgb(%d,%d,%d)'><td>80.0-70.0	<td>Fairly easy to read.
#<tr style='background-color: rgb(%d,%d,%d)'><td>70.0-60.0	<td>Plain English. Easily understood by 13- to 15-year-old students.
#<tr style='background-color: rgb(%d,%d,%d)'><td>60.0-50.0	<td>Fairly difficult to read.
#<tr style='background-color: rgb(%d,%d,%d)'><td>50.0-30.0	<td>Difficult to read.
#<tr style='background-color: rgb(%d,%d,%d)'><td>30.0-0.0	<td>Very difficult to read. Best understood by university graduates.
#</table>
#		<hr/>
#		""" % tuple(colors))
		def reading_ease_name(v):
			if v > 90: return 'very easy'
			if v > 80: return 'easy'
			if v > 70: return 'fairly easy'
			if v > 60: return 'plain english'
			if v > 50: return 'fairly difficult'
			if v > 30: return 'difficult'
			return 'very difficult'
		#def time(txt, cls):
		#	return '<span class="%s">%s</span>' % (cls, txt)
		#f.write(time("Past: When describing your steps.", "past") + "<br/>")
		#f.write(time("Present: When describing general truths.", "present") + "<br/>")
		#f.write(time("Future: When describing future work.", "future") + "<br/>")
		#f.write(time("Mixed tenses.", "mixed") + "<br/>")
		#f.write("<br/>")
		paragraphs = list(paragraphs)
		
		word_count = 0
		sentence_count = 0
		grouped_paragraphs = []
		current_paragraphs = []
		for para in paragraphs:
			current_paragraphs.append(para)
			for txt, tags, entities in para:
				if is_full_sentence(txt, tags, entities):
					word_count += len(tags)
					sentence_count += 1
			
			#if word_count > 100:
			if sentence_count > 30:
				grouped_paragraphs.append(current_paragraphs)
				current_paragraphs = []
				word_count = 0
				sentence_count = 0
			
		for group in grouped_paragraphs:
			# compute statistics for this group
			out = ""
			sentence_count = 0
			sentence_lengths = []
			syllables = []
			poly_syllable_count = 0
			complex_word_count = 0
			for para in group:
				out += "<p>"
				for txt, tags, entities in para:
					sentence_count += 1
					words = [word for (word, tag) in tags]
					sentence_lengths.append(count_words(words))
					totsyl, polysyl, complexwords = syllable_stats(words)
					syllables.append(totsyl)
					poly_syllable_count += polysyl
					complex_word_count += complexwords
					out += txt + '\n'
				out += "\n</p>"
				
			# compute Flesch reading ease
			# average sentence length
			asl = sum(sentence_lengths) * 1. / sentence_count
			# average syllables per word
			asw = sum(syllables) * 1. / sum(sentence_lengths)
			flesch_reading_ease = 206.835 - 1.015 * asl - 84.6 * asw
			
			# compute fog index
			complex_word_fraction = complex_word_count * 100. / sum(sentence_lengths)
			fog_index = 0.4 * (asl + complex_word_fraction)
			smog_index = 1.0430 * (poly_syllable_count * 30. / sentence_count)**0.5 + 3.1291
			
			u = 1 - flesch_reading_ease / 100.
			u = (fog_index - 6) / (17 - 6.)
			u = max(0, min(1, u))
			
			# add color here
			g = max(0.1, 1 - u*1.3)
			b = g
			r = min(1, 1.7 - u*1.3)
			
			#f.write("<div class='readingeaseresults'>Reading ease (Flesch): %.1f, Fog index (Gunning reading level): %d</div>" % 
			#	(flesch_reading_ease, fog_index))
			#f.write("\n<div style='background-color: rgb(%d,%d,%d)'>%s</div>\n" % (r*255,g*255,b*255, out))
			
			#f.write("<div class='readingeaseresults'  style='background-color: rgb(%d,%d,%d)'>Reading ease (Flesch): %.1f, Fog index (Gunning reading level): %d</div>\n" % 
			#	(r*255,g*255,b*255, flesch_reading_ease, fog_index))
			#f.write(out)
			
			f.write("<div class='results'  style='border: 1em solid rgb(%d,%d,%d)'>%s <span class='readingeaseresults'>- Reading ease (Flesch): %.1f, Fog index (Gunning reading level):</span>%d\n" % 
				(r*255,g*255,b*255, reading_ease_name(flesch_reading_ease), flesch_reading_ease, fog_index))
			f.write(out)
			f.write("</div>")
			
			
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
	<a href="https://github.com/JohannesBuchner/languagecheck>This program</a> attempts to assist you in improving your paper.
	Language is ambiguous and subjective, a computer can not understand it.
	All results should be seen as suggestions; think about the highlighted sentences.
	
	<ul>
	<li>%(checkbox)s Do spell-checking (in your LaTeX editor, e.g. lyx)
	<li>%(checkbox)s Do grammar-checking (in LanguageTool)
	<li>%(checkbox)s <a href="%(prefix)s_topic.html">Each paragraph should open informatively.</a>
	<li>%(checkbox)s <a href="%(prefix)s_tricky.html">Tricky words, Prepositions & Wordiness</a>
	<li>%(checkbox)s <a href="%(prefix)s_wordiness.html">Wordiness & long sentences</a>
	<li>%(checkbox)s <a href="%(prefix)s_readability.html">Reading ease</a>
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
print 'analysis: reading ease'
readability(paragraphs)
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
