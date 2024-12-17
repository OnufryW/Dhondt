import curses
import traceback

lines = []
history = []
curline = ''
curlinesize = 1
histpos = 0
cursor = 0

def linesize(line, cols, curline):
  return 1 + max(((2 if curline else -1) + len(line)), 0) // cols

DEBUG = False
dbg_line = 0

def drawline(line, cy, cols, widget, scr):
  global dbg_line
  origcy = cy
  strings_drawn = 0
  s = '> ' + line if widget else line
  cpos = 0
  curspos = None
  while cpos < len(s):
    cut = s[cpos:cpos+cols]
    if cy >= 0:
      scr.addstr(cy, 0, cut)
      strings_drawn += 1
      if (cpos <= cursor + 2 < cpos + cols):
        curspos = (cy, cursor + 2 - cpos)
    cpos += cols
    cy += 1
  if not curspos:
    curspos = (cy, 0)
  if DEBUG:
    scr.addstr(dbg_line % curses.LINES, cols - 20, 
               str(len(s)) + ' ' + str(origcy) + ' ' + str(strings_drawn))
  dbg_line += 1
  return curspos

def redraw(scr):
  global dbg_line
  dbg_line = 0
  cols = curses.COLS
  rows = curses.LINES - 1
  scr.erase()
  scr.refresh()
  # Do we have enough lines to fill the screen?
  totsize = curlinesize
  large = False
  curspos = None
  for line in lines:
    totsize += linesize(line, cols, False)
    if totsize > rows:
      large = True
      break
  if large:
    curspos = drawline(curline, rows - curlinesize, cols, True, scr)
    cy = rows - curlinesize
    for line in reversed(lines):
      if cy < 0:
        break
      cy -= linesize(line, cols, False)
      drawline(line, cy, cols, False, scr)
  else:
    cy = 0
    for line in lines:
      drawline(line, cy, cols, False, scr)
      cy += linesize(line, cols, False)
    curspos = drawline(curline, cy, cols, True, scr)
  scr.move(curspos[0], curspos[1])
  scr.refresh()
  
# TODO: Change the import to finally move back to the old directory!!!
def main(stdscr, execute, welcome):
  global curline, curlinesize, lines, history, histpos, cursor
  lines = welcome
  redraw(stdscr)
  localhistory = [""]
  while True:
    key = stdscr.getkey()
    if key == 'q':
      return
    elif key == '\n' or key == 'KEY_ENTER' or key == '\r':
      lines.append('> ' + curline)
      try:
        res = execute(curline)
        for l in res:
          lines.append(l)
      except Exception as e:
        lines.extend(' '.join([str(x) for x in e.args]).split('\n'))
        if True:
          # TODO DISABLE THIS
          for l in traceback.format_list(traceback.extract_tb(e.__traceback__)):
            for internal_l in str(l).split('\n'):
              lines.append(internal_l)
      if curline.strip():
        history.append(curline)
      histpos = len(history)
      curline = ''
      curlinesize = 1
      cursor = 0
      localhistory = history[:] + [""]
    elif key == 'KEY_UP':
      if histpos == 0:
        curses.beep()
      else:
        localhistory[histpos] = curline
        histpos -= 1
        curline = localhistory[histpos]
        cursor = len(curline)
    elif key == 'KEY_DOWN':
      if histpos == len(localhistory) - 1:
        curses.beep()
      else:
        localhistory[histpos] = curline
        histpos += 1
        curline = localhistory[histpos]
        cursor = len(curline)
    elif key == 'KEY_BACKSPACE':
      if cursor == 0:
        curses.beep()
      else:
        curline = curline[:(cursor - 1)] + curline[cursor:]
        cursor -= 1
    elif key == 'KEY_LEFT':
      if cursor == 0:
        curses.beep()
      else:
        cursor -= 1
    elif key == 'KEY_RIGHT':
      if cursor == len(curline):
        curses.beep()
      else:
        cursor += 1
    elif key == 'KEY_RESIZE':
      pass
    else:
      curline = curline[:cursor] + key + curline[cursor:]
      cursor += 1
    curlinesize = max(curlinesize, linesize(curline, curses.COLS, True))
    redraw(stdscr)

def run(execute, welcome):
  # Execute should be a function that takes a string and returns a list of strs.
  # The input is the command the user input.
  # Welcome is a list of strings that we'll output.
  # The output is the resulting output of that command.
  wrapped = lambda scr: main(scr, execute, welcome)
  curses.wrapper(wrapped)
