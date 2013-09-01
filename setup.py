#!/usr/bin/env python
import os
from distutils.core import setup

from github_pr_stats import VERSION

# I really prefer Markdown to reStructuredText.  PyPi does not.  This allows me
# to have things how I'd like, but not throw complaints when people are trying
# to install the package and they don't have pypandoc or the README in the
# right place.
try:
   import pypandoc
   description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   description = ''
try:
   license = open('LICENSE').read()
except IOError:
   license = 'WTFPL'

setup(
   name = 'github-pr-stats',
   version = VERSION,
   author = 'James Pearson',
   author_email = 'pearson@changedmy.name',
   packages = ['github_pr_stats'],
   scripts = ['bin/github-pr-stats'],
   url = 'https://github.com/xiongchiamiov/github-pr-stats',
   license = license,
   description = 'Various statistics on the pull requests in your repo.',
   long_description = description,
   install_requires = [
      'ascii-graph >= 0.1.0',
      'docopt >= 0.6, < 0.7',
      'envoy >= 0.0.2',
      'github3.py >= 0.7, < 0.8',
      'numpy >= 1.7, < 1.8',
   ],
)

