Documentation
=============

This repository contains a package for the automatic computing
of scores and rankings for the Play.it Dinasty keeper league.

The package has been used to officially compute the scores and
the rankings for both the 2013-14 and 2014-15 seasons.

The Play.it Dinasty is a keeper league originated in the early 
2000s thanks to the passionate NBA fans who have been discussing
USA sports at http://forum.playitusa.com/.

The website http://basketball.sports.ws/ had been originally
employed to help the Dinasty Commissioners with the schedule of
the games and, more recently, with the computation of the scores.

In the last two years, the boxscores have been automatically
scraped from http://basketball.sports.ws/ with this Python
package, which also applies some tricks to correctly calculate
the scores according to the league rules.

Therefore, this package (or parts of it)  can be used by other
leagues too, providing that they adapt the code to their own
rules.

Besides the four Python files, the repository contains two YAML
files:

- dinasty.yaml
- schedule_2014-15.yaml

The first is a simple data structure to initialize some variables
associated to the teams competing in the league. In particular,
the *name* of the team, its *number*, *division* and *conference*
in http://basketball.sports.ws/ must be specified.

The second is another data structure containing the schedule of
the league. In this particular case, the schedule has been copied
from http://basketball.sports.ws/, but it can be customized by
the league Commissioners.


Author
======

Andrea Pinna (andreapinna@gmail.com)


Disclaimer
==========

Warning!

This package works on Linux, but it has not been thoroughly tested!

Moreover, errors and exceptions are barely handled!

Therefore, please, use with care! :forza:


Dependencies
============

- Python 2.6+: http://www.python.org/
- Beautiful Soup: http://www.crummy.com/software/BeautifulSoup/
- PyYAML: http://pyyaml.org/
- Numpy: http://www.numpy.org/


Examples
========

To retrieve the scores for games 1 to 5, and to finally
print the rankings after game 5:

    python dinasty.py --retrieve_scores --games=1,5 --print_rankings

To simply print the rankings after the last game:

    python dinasty.py --print_rankings
