import sys
import random

header = """<html>
<head>
<title>%(title)s</title>
</head>
"""

filename = sys.argv[1]

def topic_sentences(parts):
	with open(filename + '_topic.html', 'w') as f:
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
		for p in parts:
			if '.' not in p:
				continue
			f.write("<li>" + p.split('. ')[0] + '.\n') 
		f.close()

def consistent_paragraph(parts):
	with open(filename + '_para.html', 'w') as f:
		f.write(header % dict(title='Paragraph consistency'))
		f.write("""<h1>Paragraph consistency</h1>
		Each paragraph should make sense on its own. 
		They should not be too long.
		Here they are in random order.
		<hr/>
		""")
		random.shuffle(parts)
		for p in parts:
			if '.' not in p:
				continue
			f.write("<hr/>" + p + '\n') 
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

doc = open(filename).read()
while '\n\n\n' in doc:
	doc = doc.replace('\n\n\n', '\n\n')

parts = doc.split('\n\n')

parts = [p for p in parts if len(p) > 10]

topic_sentences(parts)
consistent_paragraph(parts)

"""
for p in parts[4:20]:
	for q in p.split('.xxxx\n'):
		q = q.strip()
		if len(q) == 0: continue
		if not q.endswith('.'):
			q = q + '.'
		print q
		#print '--'
	print '-----'
	"""
	#block = p.replace('\n', ' ').replace('   ', ' ').replace('  ', ' ')
	#if '.' in block:
	#	sentences = [s.strip() + '.' for s in block.split('. ')]
	#else:
	#	sentences = [block]
	#for s in sentences:
	#	print s.strip()
	#	break
	#print 

#[:100]

