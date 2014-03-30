# May you recognize your weaknesses and share your strengths.
# May you share freely, never taking more than you give.
# May you find love and love everyone you find.

from __future__ import division

import sys
from collections import defaultdict
try:
   from collections import OrderedDict
except ImportError:
   from ordereddict import OrderedDict
from datetime import datetime, timedelta

from ascii_graph import Pyasciigraph
from dateutil.parser import parse
from github3 import login
from importlib import import_module
from numpy import array, median as calcMedian

stats = {}
dayMapping = {
   0: 'M',
   1: 'T',
   2: 'W',
   3: 'R',
   4: 'F',
   5: 'Sa',
   6: 'Su',
}

def analyze(token, config, user, repo=None, since=None, until=None, \
            bucketSize=10, plugins=None, url=None):
   gh = login(token=token, url=url)
   stats.update({
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
      'weekCreated': defaultdict(int),
      'weekClosed': defaultdict(int),
      'userCreating': defaultdict(int),
      'userClosing': defaultdict(int),
      'labels': defaultdict(int),
      'additions': [],
      'additionsHistogram': OrderedDict(),
      'deletions': [],
      'deletionsHistogram': OrderedDict(),
   })

   if plugins is None:
      plugins = []
   plugins = [import_module(plugin) for plugin in plugins]
   for plugin in plugins:
      plugin.setup(globals(), locals())
   
   initialize_ordered_dict(stats['dayOfWeekCreated'], dayMapping.values(), 0)
   initialize_ordered_dict(stats['dayOfWeekClosed'], dayMapping.values(), 0)
   initialize_ordered_dict(stats['hourOfDayCreated'], range(24), 0)
   initialize_ordered_dict(stats['hourOfDayClosed'], range(24), 0)

   # If we get dates in string format, try to parse them out.  But leave Nones
   # and datetimes alone.
   if isinstance(since, basestring):
      since = parse(since)
   if isinstance(until, basestring):
      until = parse(until)

   if repo is None:
      repos = gh.iter_user_repos(user)
   else:
      repos = [gh.repository(user, repo)]
   
   for repo in repos:
      if not repo.has_issues:
         continue
      
      progressMeter = 'In %s, analyzing pull number:     ' % repo
      print progressMeter,

      for issue in repo.iter_issues(state='closed', direction='asc', since=since):
         if until and issue.created_at >= until:
            break

         # The 'since' parameter always applies to updates, even if we specify a
         # 'sort' of, say, creation date, so we can't rely on it to filter out
         # issues that were closed too long ago.
         if since and issue.created_at <= since:
            continue
         
         # Pull requests are gimped and not slicable by date.  So we get slice
         # issues instead and grab the pull requests out of them.  While this will
         # be more expensive for small repos, it makes it feasible to run
         # github-pr-stats for small date ranges on repos with many pulls.
         if not issue.pull_request:
            continue
         pr = repo.pull_request(issue.number)
         
         # We'll just assume we won't go over four digits of issues.
         print '\b\b\b\b\b%4d' % pr.number,
         sys.stdout.flush()
         
         stats['count'] += 1
         if config['basicStats']:
            if pr.is_merged():
               stats['merged'] += 1
         if config['daysOpen']:
            daysOpen = (pr.closed_at - pr.created_at).days
            stats['daysOpen'].append(daysOpen)
            stats['daysOpenHistogram'][daysOpen] += 1
         if config['comments']:
            comments = len(list(pr.iter_comments()))
            stats['comments'].append(comments)
            stats['commentsHistogram'][comments] += 1
         if config['dayOfWeekCreated']:
            dayAbbreviation = dayMapping[pr.created_at.weekday()]
            stats['dayOfWeekCreated'][dayAbbreviation] += 1
         if config['dayOfWeekClosed']:
            dayAbbreviation = dayMapping[pr.closed_at.weekday()]
            stats['dayOfWeekClosed'][dayAbbreviation] += 1
         if config['hourOfDayCreated']:
            stats['hourOfDayCreated'][pr.created_at.hour] += 1
         if config['hourOfDayClosed']:
            stats['hourOfDayClosed'][pr.closed_at.hour] += 1
         if config['weekCreated']:
            # Store the first day of the week.
            weekCreated = (pr.created_at - timedelta(days=pr.created_at.weekday()))
            weekCreated = weekCreated.date() # Discard time information.
            stats['weekCreated'][weekCreated] += 1
         if config['weekClosed']:
            weekClosed = (pr.closed_at - timedelta(days=pr.closed_at.weekday()))
            weekClosed = weekClosed.date() # Discard time information.
            stats['weekClosed'][weekClosed] += 1
         if config['userCreating']:
            stats['userCreating'][pr.user.login] += 1
         if config['userClosing']:
            # We don't seem to have information on who closed an issue if they didn't
            # merge it.
            if pr.is_merged():
               # For whatever reason, the user doing the merge isn't part of the initial
               # data set.
               pr.refresh()
               stats['userClosing'][pr.merged_by.login] += 1
         if config['labels']:
            for label in issue.labels:
               stats['labels'][label.name] += 1
            if not issue.labels:
               stats['labels']['<no label>'] += 1
         if config['additions']:
            stats['additions'].append(pr.additions)
         if config['deletions']:
            stats['deletions'].append(pr.deletions)

         for plugin in plugins:
            plugin.analyze_pull(globals(), locals())
      print '\b' * (len(progressMeter) + 1), # +1 for the newline
   print "\n"

   if config['basicStats']:
      percentageMerged = 100 * (stats['merged'] / stats['count'])
      print '%.2f%% (%s of %s) closed pulls merged.' % (percentageMerged, stats['merged'], stats['count'])
   
   if config['daysOpen']:
      print_report('daysOpen')
   if config['comments']:
      print_report('comments')
   if config['dayOfWeekCreated']:
      print_histogram(stats['dayOfWeekCreated'].items(), 'Day of Week Created')
   if config['dayOfWeekClosed']:
      print_histogram(stats['dayOfWeekClosed'].items(), 'Day of Week Closed')
   if config['hourOfDayCreated']:
      print_histogram(stats['hourOfDayCreated'].items(), 'Hour of Day Created')
   if config['hourOfDayClosed']:
      print_histogram(stats['hourOfDayClosed'].items(), 'Hour of Day Closed')
   if config['weekCreated']:
      print_date_report('weekCreated', 'Week Created')
   if config['weekClosed']:
      print_date_report('weekClosed', 'Week Closed')
   if config['userCreating']:
      print_histogram(stats['userCreating'].items(), 'User Creating Pull Request')
   if config['userClosing']:
      print_histogram(stats['userClosing'].items(), 'User Merging Pull Request')
   if config['labels']:
      print_histogram(stats['labels'].items(), 'Labels Attached')
   if config['additions']:
      print_diff_report('additions', bucketSize)
   if config['deletions']:
      print_diff_report('deletions', bucketSize)

   for plugin in plugins:
      plugin.print_report(globals(), locals())

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

def create_week_range(start, finish):
   '''Create a range of weeks from start and finish dates.
   
   :param date start: The date of the first day in the first week.
   :param date finish: The date of the first day in the last week.
   :rtype: An iterable of strings in ISO 8601 format.
   '''
   weeks = []
   week = start
   while week < finish:
      weeks.append(week.strftime('%Y-%m-%d'))
      week += timedelta(weeks=1)
   return weeks

def bucket_value(value, bucketSize):
   '''Determine which bucket a value resides in.

   For instance, given a bucketSize of 10, the values 10, 16, and 19 all reside
   in the bucket 10-19, while 20 is in the 20-29 bucket.
   '''
   bottom = (value // bucketSize) * bucketSize
   top = bottom + bucketSize - 1
   return '%s-%s' % (bottom, top)

def bucketed_range(min, max, bucketSize):
   values = []
   for value in range(min, max + 1, bucketSize):
      top = value + bucketSize - 1
      values.append('%s-%s' % (value, top))
   return values

def print_report(subject):
   '''Do various calculations on the subject, then print the results.
   
   This should be like, 8 different functions or something, but bad API design
   is easier.
   '''
   statsAnalysis = StatsAnalysis(array(stats[subject]), subject)
   print statsAnalysis

   initialize_ordered_dict(stats[subject+'Histogram'], range(statsAnalysis.min, statsAnalysis.max))
   
   print_histogram(stats[subject+'Histogram'].items())

def print_date_report(subject, name):
   # Calculate only the min and the max because the mean of a series of weeks
   # doesn't make much sense.
   data = array(stats[subject].keys())
   minWeek = data.min()
   maxWeek = data.max()
   
   allData = OrderedDict()
   initialize_ordered_dict(allData, create_week_range(minWeek, maxWeek), 0)
   for key, value in stats[subject].items():
      newKey = key.isoformat()
      allData[newKey] = value
   print_histogram(allData.items(), name)

def print_diff_report(subject, bucketSize):
   data = array(stats[subject])
   statsAnalysis = StatsAnalysis(data, subject)
   print statsAnalysis

   initialize_ordered_dict(stats[subject+'Histogram'], bucketed_range(statsAnalysis.min, statsAnalysis.max, bucketSize), 0)
   for value in data:
      bucket = bucket_value(value, bucketSize)
      stats[subject+'Histogram'][bucket] += 1
   print_histogram(stats[subject+'Histogram'].items())

class StatsAnalysis(object):
   def __init__(self, data, subject=''):
      self.subject = subject
      # It'd be a lot nicer to do these calculations using
      # http://www.python.org/dev/peps/pep-0450/ or even
      # https://pypi.python.org/pypi/stats/ instead of the
      # sometimes-difficult-to-install Numpy.  But alas, we're stuck with that for
      # Python 2.x.
      self.mean = data.mean()
      self.median = calcMedian(data) # I don't know why narray doesn't have self as a method.
      self.stdDev = data.std()
      self.min = data.min()
      self.max = data.max()

   def __str__(self):
      return '{subject}: {mean} (mean) {median} (median) {stdDev} (std. dev.) {min} (min) {max} (max)'.format(**vars(self))


def print_histogram(data, label=''):
   # Fill in percentages of the total.
   for key, datapoint in enumerate(data):
      name, value = datapoint
      percentage = (float(value) / stats['count']) * 100 if stats['count'] else 0
      name = '(%6.2f%%) %s' % (percentage, name)
      data[key] = (name, value)

   graph = Pyasciigraph()
   for line in graph.graph(label, data):
      # Encode explicitly to get around this bug:
      # https://github.com/kakwa/py-ascii-graph/issues/4
      print line.encode('utf-8')

