Various statistics on the pull requests in your repo.

# Usage

    Usage:
       github-pr-stats [options] <user> [<repo>]
       github-pr-stats --version
       github-pr-stats (-h | --help)
    
    Options:
       -h --help           Show this screen.
          --version        Print the program's installed version.
          --basic          Basic statistics about merged/closed rate.
          --days-open      Analyze number of days opened.
          --comments       Analyze number of comments created.
          --day-created    Analyze day of the week opened.
          --day-closed     Analyze day of the week closed.
          --hour-created   Analyze hour of the day opened.
          --hour-closed    Analyze hour of the day closed.
          --week-created   Analyze week opened.
          --week-closed    Analyze week closed.
          --user-creating  Analyze user who opened.
          --user-closing   Analyze user who closed.
          --labels         Analyze attached labels.
          --since=<date>   Only consider pull requests opened on or after this
                           date.
          --until=<date>   Only consider pull requests opened before this date.
# Example

    [$]> github-pr-stats --basic --user-creating ifixit itbrokeand.ifixit.com
     99.0% (20 of 20) closed pulls merged.
    User Creating Pull Request
    ###############################################################################
    ████                                                         1  treyhunner
    ██████████████████████████████████████████████████████████  12  danielbeardsley
    █████████████████████████████████                            7  xiongchiamiov

# Installation

    [$]> pip install github-pr-stats

or

    [$]> easy_install github-pr-stats

# Hacking

I highly recommend using virtualenv:

    [$]> virtualenv --no-site-packages --distribute env
    [$]> source env/bin/activate
    [$]> pip install -r requirements.txt
    [$]> pip install -e . # So we can import the version from inside bin/ .

