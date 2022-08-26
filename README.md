Various statistics on the pull requests in your repo.

# Usage

    Usage:
       github-pr-stats [options] <user or organization> [<repo>]
       github-pr-stats --version
       github-pr-stats (-h | --help)

    Options:
       -h --help                     Show this screen.
          --version                  Print the program's installed version.
          --github-url=<url>         Github Enterprise URL.
          --basic                    Basic statistics about merged/closed rate.
          --days-open                Analyze number of days opened.
          --comments                 Analyze number of comments created.
          --day-created              Analyze day of the week opened.
          --day-closed               Analyze day of the week closed.
          --hour-created             Analyze hour of the day opened.
          --hour-closed              Analyze hour of the day closed.
          --week-created             Analyze week opened.
          --week-closed              Analyze week closed.
          --user-creating            Analyze user who opened.
          --user-closing             Analyze user who closed.
          --labels                   Analyze attached labels.
          --additions                Analyze number of lines added.
          --deletions                Analyze number of lines deleted.
          --bucketSize=<bucketSize>  The size of the display groups for line
                                     additions and deletions. [default: 10]
          --since=<date>             Only consider pull requests opened on or after
                                     this date.
          --until=<date>             Only consider pull requests opened before this
                                     date.
          --plugins=<plugins>        Comma-separated list of plugins to load.

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

    [$]> python3 -m venv env
    [$]> source env/bin/activate
    [$]> pip install -r requirements.txt
    [$]> pip install -e . # So we can import the version from inside bin/ .

# Plugins

github-pr-stats has a plugin architecture to allow you to run arbitrary
additional code without hacking the source.

A plugin should implement three functions that gain access to the full
environment at different points in the analysis process:

1. `setup(globalEnv, localEnv)` - called once when we first initialize
   variables
2. `analyze_pull(globalEnv, localEnv)` - called for every pull request
3. `print_report(globalEnv, localEnv)` - called once after all analysis is done

Take a look at the examples in `github_pr_stats/example_plugins/` for more
information.

# Changelog

## 0.6

* (Feature) Add Github Enterprise support (#3, @arikon).  You'll need to
  reauthenticate or change the `[github-pr-stats]` section in `~/.gitconfig` to
  `[github-pr-stats "github.com"]`.

## 0.5.2

* (Bugfix) Allow importing of plugins on systems using `pip install`.

## 0.5.1

Pulled.

## 0.5

* (Feature) Add plugin architecture.

## 0.4

* (Feature) Add percentages to all data points.
* (Feature) Optionally analyze all of a user's repos.
* (Feature) `--labels` now shows the count of pulls without a label.
* (Feature) Add LOC analysis with `--additions` and `--deletions`.
* (Bugfix) Fix broken mean in `--basic`.
* (Bugfix) Don't error on repos without issues.

