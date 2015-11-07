# minesweeper_bot
Bot plays the Windows classic minesweeper.

[Alt text](minsweeper.gif)

  A bot that plays minesweeper blazingly fast still isn't that bright. It
first locates a running minesweeper and plays it at any difficulty by
reading the screen, deducing the possibilities, and operating the mouse.
The logic starts simple solving around a single cell. When not enough
implores adjacent cells and solves those not within their combined
influence. When there is lacking information it explores for more.
Although there is mine detecting pixel cheat this **does not** use it
thus will randomly discover mines.

  Originally a motivation to program, I've become rather proud of it.
Wins almost every beginner, most intermediate, some expert and custom.
If it had feelings it too would hate those 50/50 chances. The necessary
millisecond pauses allowing the game to catch-up is optimized and tested
on my own system, so adjustments my be necessary if AssertionErrors
occur often.

Run from the command line in it's directory, optional options include:
- -f flag: Will flag the mines instead of avoiding them.
- -p pause: Will pause between actions slowing it down.
- -r record: Will save the screen captures to the specified directory.
- -d display: Will print the minefield at the end as the bot sees it.

####Requires####

Python3: <https://www.python.org/downloads/>

Window Extensions for Python from:
- from pip: `python -m pip install pypiwin32`
- from unofficial binaries: <http://www.lfd.uci.edu/~gohlke/pythonlibs/>
- from: <http://sourceforge.net/projects/pywin32/>

And Minesweeper itself:
- from: an Windows XP installation. (Or maybe any Windows System before Window 7)
- from: an installation disk like described here
<http://www.makeuseof.com/tag/minesweeper-restoring-the-classic-windows-games-in-windows-8/>
