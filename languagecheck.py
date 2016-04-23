import sys
import random
import codecs

header = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"> 
<title>%(title)s</title>
</head>
"""

filename = sys.argv[1]

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
			#if '.' not in p:
			#	continue
			if is_full_sentence(txt, sentence, entities):
				f.write("<li>" + txt.split('. ')[0] + '\n') 
			else:
				print 'not a full sentence:', sentence
		f.close()

def consistent_paragraph(paragraphs):
	with codecs.open(filename + '_para.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Paragraph consistency'))
		f.write("""<h1>Paragraph consistency</h1>
		Each paragraph should make sense on its own. 
		They should not be too long.
		Here they are in random order.
		<hr/>
		""")
		paragraphs = list(paragraphs)
		random.shuffle(paragraphs)
		for para in paragraphs:
			if any((is_full_sentence(txt, sentence, entities) for txt, sentence, entities in para)):
				p = ' '.join([txt for txt, sentence, entities in para])
				f.write("<hr/>" + p + '\n') 
		f.close()

def guess_tense(sentence, entities, last_tense):
	past_count = 0
	present_count = 0
	future_count = (' '.join([w for w, wt in sentence])).count('going to')
	for w, wt in sentence:
		if w in ['shall', 'will']:
			print 'future:', w,
			future_count += 1
		elif wt in ['VB', 'VBP', 'VBZ']:
			print 'present:', w,
			present_count += 1
		elif wt == 'VBD':
			print 'past:', w,
			past_count += 1
	#print u' '.join([w.encode('utf-8') for w, wt in sentence])
	#entities.pprint()
	if future_count > 0:
		return 'future'
	elif past_count > 0:
		return 'past'
	elif present_count > 0:
		return 'present'
	else:
		return last_tense
	
def tenses(paragraphs):
	with codecs.open(filename + '_tense.html', 'w', 'latin1') as f:
		f.write(header % dict(title='Tenses'))
		f.write("""<h1>Tenses</h1>
		<style type="text/css">
		.past{color: blue}
		.present{color: green}
		.future{color: red}
		</style>
		""")
		def time(txt, cls):
			return '<span class="%s">%s</span>' % (cls, txt)
		f.write(time("Past: When describing your steps.", "past") + "<br/>")
		f.write(time("Present: When describing general truths.", "present") + "<br/>")
		f.write(time("Future: When describing future work.", "future") + "<br/>")
		f.write("<br/>")
		paragraphs = list(paragraphs)
		for para in paragraphs:
			last_tense = None
			f.write("<p>")
			for txt, sentence, entities in para:
				tense = guess_tense(sentence, entities, last_tense)
				if tense is None:
					f.write(txt)
				else:
					f.write(time(txt, tense))
				last_tense = tense
				f.write('\n')
			f.write("\n</p>")
		f.close()

def bad_words(parts):
	"""despite the fact that -> although, even though
regardless of the fact that -> although, even though
in the event that -> if
under circumstances in which -> if
the reason for -> because, since, why
for the reason that -> because, since, why
owing/due to the fact that -> because, since, why
in light of the fact that -> because, since, why
considering the fact that -> because, since, why
on the grounds that -> because, since, why
this is why -> because, since, why

"""
	pass

doc = codecs.open(filename, encoding='latin1').read()
while '\n\n\n' in doc:
	doc = doc.replace('\n\n\n', '\n\n')

chunks = doc.split('\n\n')

# those chunks are the parts of the documents
#print '\n\n---\n\n'.join(chunks[:20])
#print 'XXXXXXXX'
import nltk # python -m nltk.downloader all
tagger = nltk.data.load("taggers/maxent_treebank_pos_tagger/english.pickle")
paragraphs = []
for i, chunk in enumerate(chunks):
	sys.stdout.write('Analysing paragraph %d/%d  \r' % (i+1, len(chunks)))
	sys.stdout.flush()
	chunk = chunk.replace(' .', ' X.').replace('[', ' ').replace(']', ' ').replace('  ', ' ').replace('  ', ' ')
	# try to pass this on to ntkl
	tokens = nltk.word_tokenize(chunk)
	#entities = nltk.chunk.ne_chunk(tagged)
	tagged = nltk.pos_tag(tokens)
	sentences = []
	a = 0
	b = -1
	while len(tagged[a:]) > 0:
		found = False
		for b, t in enumerate(tagged[a:]):
			if t[1] == '.':
				sentences.append(tagged[a:a+b+1])
				a = a+b+1
				found = True
				break
		if not found:
			sentences.append(tagged[a:])
			break
	
	para = []
	for sentence in sentences:
		entities = nltk.chunk.ne_chunk(sentence)
		#print entities
		txt = sentence[0][0]
		for w, wt in sentence[1:]:
			if wt in ['.', ',', '[', ']', '(', ')']:
				txt += w
			else:
				txt += ' ' + w
		txt = txt.replace('  ', ' ').replace('( ', '(').replace(' )', ')')
		para.append((txt, sentence, entities))
	if para:
		paragraphs.append(para)


print 'analysis: tenses'
tenses(paragraphs)
print 'analysis: topic sentences'
topic_sentences(paragraphs)
print 'analysis: paragraph consistency'
consistent_paragraph(paragraphs)




