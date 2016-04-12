# tweeti-kiri
Your Social Media Vacuum Cleaner. Python application to help with housekeeping on Twitter.

## Screenshot
![image](https://raw.githubusercontent.com/HackerspaceBremen/tweeti-kiri/master/screenshot_tweeti_kiri_v0_9.png)

## Features
The program runs on the command line and provides an **interactive** way of requesting userinput to be setup and configured. Every action can be chosen individually and will only be executed after user confirmation.

Following features are provided by this application:

* Configure and store authorization credentials
* Analyze your own and any other twitter account
* Remove all tweets
* Remove all direct messages
* Remove all favourites
* Remove all followers
* Remove all friends/following
* Clear any configured authorization credentials

## Installation
Before starting the installation, make sure you have **Python**, **pip** and **virtualenv** installed.

1. Create a directory using **virtualenv** like so ```virtualenv tweeti-kiri``` and change into that directory.
2. Activate the virtual environment by typing ```source bin/activate``` on the commandline
3. Now copy the python file ```tweeti_kiri.py``` into the directory
4. We need to install two python modules needed by the programm to run those are **'anyjson'** and **'python-twitter'** so please type after another ```pip install anyjson``` and ```pip install python-twitter```.
5. Now you are basically set to use the program running ```python tweeti_kiri.py``` from the command line. **BUT** you need to do some configuration now with your twitter account which is described in the ```tweeti_kiri.py``` file. Just follow those instructions and have fun!

## Versions

* Version 0.9 (12. April 2016)

## Contact

Helpful hints for improving this piece of code can be transmitted to [trailblazr@noxymo.com](mailto:trailblazr@noxymo.com) or via Twitter to [@hspacehb](http://twitter.com/@hspacehb) the Twitter-Account of [Hackerspace Bremen](https://www.hackerspace-bremen.de/).

## License
This code is licensed under the GPLv3 License.



