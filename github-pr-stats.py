#!/usr/bin/env python
'''github-pr-stats

Usage:
   github-pr-stats <user> <repo>
   github-pr-stats (-h | --help)

Options:
   -h --help           Show this screen.
'''

# May you recognize your weaknesses and share your strengths.
# May you share freely, never taking more than you give.
# May you find love and love everyone you find.

from __future__ import division

import signal
import sys
from collections import defaultdict, OrderedDict

from ascii_graph import Pyasciigraph
from docopt import docopt
from envoy import run
from github3 import authorize, login, GitHub
from numpy import array, median as calcMedian

# Stack traces are ugly; why would we want to print one on ctrl-c?
def nice_sigint(signal, frame):
   print("")
   sys.exit(0)
signal.signal(signal.SIGINT, nice_sigint)

arguments = docopt(__doc__)

# Use a stored OAuth token so we don't have to ask for the user's password
# every time (or save the password on disk!).
token = run('git config --global github-pr-stats.token').std_out.strip()
if not token:
   from getpass import getpass
   user = password = ''

   while not user:
      user = raw_input('Username: ')
   while not password:
      password = getpass('Password: ')

   auth = authorize(user, password,
                    scopes=['repo'],
                    note='github-pr-stats',
                    note_url='https://github.com/xiongchiamiov/github-pr-stats')
   token = auth.token
   # We need to un-unicode token for now.
   # https://github.com/kennethreitz/envoy/issues/34
   run("git config --global github-pr-stats.token '%s'" % str(token))
gh = login(token=token)

repo = gh.repository(arguments['<user>'], arguments['<repo>'])
stats = {
   'count': 0,
   'merged': 0,
   'daysOpen': [],
   'daysOpenHistogram': defaultdict(int),
   'comments': [],
   'commentsHistogram': defaultdict(int),
   'dayOfWeekCreated': OrderedDict(),
   'dayOfWeekClosed': OrderedDict(),
   'hourOfDayCreated': OrderedDict(),
   'hourOfDayClosed': OrderedDict(),
}
dayMapping = {
   0: 'M',
   1: 'T',
   2: 'W',
   3: 'R',
   4: 'F',
   5: 'Sa',
   6: 'Su',
}

def initialize_ordered_dict(dictionary, keys, value=None):
   '''Initialize a dictionary with a set of ordered keys.
   
   This is primarily useful in two situations.
   
   First, you may desire the attributes of both an OrderedDict and a
   defaultdict.  If you know ahead of time the keys that will exist in the
   dictionary, you can created an OrderedDict and use this function to
   initialize the values.
   
   Secondly, you may have a defaultdict with holes you wish to fill.  This can
   happen if you use integer keys, but don't know the minimum and maximum key
   values at creation.  Using this function with ``value=None`` will reference
   the keys, not changing their values, but forcing the dictionary to think
   they exist (and thus having them show up in d.keys() and d.items()).
   
   :param dictionary dictionary: The dictionary to initialize.
   :param iterable keys: The keys to initialize.
   :param any value: The value to set keys to.  If ``None``, don't set a value,
                     but just touch the key.
   '''
   for key in keys:
      if value is not None:
         dictionary[key] = value
      else:
         dictionary[key]

initialize_ordered_dict(stats['dayOfWeekCreated'], dayMapping.values(), 0)
initialize_ordered_dict(stats['dayOfWeekClosed'], dayMapping.values(), 0)
initialize_ordered_dict(stats['hourOfDayCreated'], range(24), 0)
initialize_ordered_dict(stats['hourOfDayClosed'], range(24), 0)

progressMeter = 'Data fetches remaining:   0'
print progressMeter,
for pr in repo.iter_pulls(state='closed'):
   # We'll just assume we won't go over three digits of issues, which is
   # perhaps a bad assumption.
   print '\b\b\b\b%3d' % pr.number,
   sys.stdout.flush()
   
   daysOpen = (pr.closed_at - pr.created_at).days
   comments = len(list(pr.iter_comments()))
   stats['count'] += 1
   if pr.is_merged():
      stats['merged'] += 1
   stats['daysOpen'].append(daysOpen)
   stats['daysOpenHistogram'][daysOpen] += 1
   stats['comments'].append(comments)
   stats['commentsHistogram'][comments] += 1
   dayAbbreviation = dayMapping[pr.created_at.weekday()]
   stats['dayOfWeekCreated'][dayAbbreviation] += 1
   dayAbbreviation = dayMapping[pr.closed_at.weekday()]
   stats['dayOfWeekClosed'][dayAbbreviation] += 1
   stats['hourOfDayCreated'][pr.created_at.hour] += 1
   stats['hourOfDayClosed'][pr.closed_at.hour] += 1
print '\b' * (len(progressMeter) + 1), # +1 for the newline

percentageMerged = round(100 - (stats['count'] / stats['merged']), 2)
print '%s%% (%s of %s) closed pulls merged.' % (percentageMerged, stats['merged'], stats['count'])

def print_report(subject):
   '''Do various calculations on the subject, then print the results.
   
   This should be like, 8 different functions or something, but bad API design
   is easier.
   '''
   # It'd be a lot nicer to do these calculations using
   # http://www.python.org/dev/peps/pep-0450/ or even
   # https://pypi.python.org/pypi/stats/ instead of the
   # sometimes-difficult-to-install Numpy.  But alas, we're stuck with that for
   # Python 2.x.
   data = array(stats[subject])
   mean = data.mean()
   median = calcMedian(data) # I don't know why narray doesn't have this as a method.
   stdDev = data.std()
   min = data.min()
   max = data.max()
   print '%s: %s (mean) %s (median) %s (std. dev.) %s (min) %s (max)' \
       % (subject, mean, median, stdDev, min, max)

   initialize_ordered_dict(stats[subject+'Histogram'], range(min, max))
   
   print_histogram(stats[subject+'Histogram'].items())

def print_histogram(data, label=''):
   # Work around a bug in ascii_graph.
   # https://github.com/kakwa/py-ascii-graph/issues/3
   histogram = [(str(key), value) \
                for (key, value) \
                in data]
   graph = Pyasciigraph()
   for line in graph.graph(label, histogram):
      print line

print_report('daysOpen')
print_report('comments')
print_histogram(stats['dayOfWeekCreated'].items(), 'Day of Week Created')
print_histogram(stats['dayOfWeekClosed'].items(), 'Day of Week Closed')
print_histogram(stats['hourOfDayCreated'].items(), 'Hour of Day Created')
print_histogram(stats['hourOfDayClosed'].items(), 'Hour of Day Closed')

