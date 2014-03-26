'''
Show the number of additions/deletions in pulls, grouped by label.  Useful for
project-tracking.
'''

from collections import defaultdict

def setup(globalEnv, localEnv):
   globalEnv['stats']['additionsByLabel'] = defaultdict(int)
   globalEnv['stats']['deletionsByLabel'] = defaultdict(int)

def analyze_pull(globalEnv, localEnv):
   issue = localEnv['issue']
   pr = localEnv['pr']

   for label in issue.labels:
      globalEnv['stats']['additionsByLabel'][label.name] += pr.additions
      globalEnv['stats']['deletionsByLabel'][label.name] += pr.deletions
   if not issue.labels:
      globalEnv['stats']['additionsByLabel']['<no label>'] += pr.additions
      globalEnv['stats']['deletionsByLabel']['<no label>'] += pr.deletions

def print_report(globalEnv, localEnv):
   globalEnv['print_histogram'](globalEnv['stats']['additionsByLabel'].items(),
                                'Additions by Label')
   globalEnv['print_histogram'](globalEnv['stats']['deletionsByLabel'].items(),
                                'Deletions by Label')

