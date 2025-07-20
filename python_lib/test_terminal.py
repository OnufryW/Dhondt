import terminal

def count_words(s):
  if s == 'bork':
    raise ValueError('Borked!')
  return ['Number of words: ' + str(len(s.split()))]

terminal.run(count_words)
