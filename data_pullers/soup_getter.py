import urllib.request
from bs4 import BeautifulSoup

log_number = 0
# log_frequency = N means we print every N-th log line. 1 means print them all.
log_frequency = 1

def Get(url, debug_data):
  global log_number
  log_number += 1
  if log_number % log_frequency == 0:
    print(log_number, ': ', debug_data, ' (', url, ')')
  page = urllib.request.urlopen(url)
  return BeautifulSoup(page, "html.parser")

def WithRetries(url, debug_data, retries):
  for att in range(retries):
    try:
      return Get(url, debug_data)
    except Exception as e:
      print('Failure ', att, ' to get ', debug_data, ' (', url, '): ', e)
  return Get(url, debug_data)
