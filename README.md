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
4. We need to install two python modules needed by the program to run those are **'anyjson'** and **'python-twitter'** so please type after another ```pip install anyjson``` and ```pip install python-twitter```.
5. Now you are basically set to use the program running ```python tweeti_kiri.py``` from the command line. **BUT** you need to do some configuration now with your twitter account which is described in the ```tweeti_kiri.py``` file. Just follow those instructions and have fun!

## Configuration
After you installed the necessary Python modules to make the program work you need to create an App-authorization-entry in your twitter profile and afterwards configure the Python program with several credentials.

Just follow this step by step description:

1. To be able to remove all tweets from your account you first need to get your archive of tweets. You can do this by going to **Settings -> Account -> Your Twitter archive**.
2. Go to [https://apps.twitter.com/](https://apps.twitter.com/) and create a new application. You can name the application e.g. **tweeti-kiri-$myTwitterNickname** because this name has to be unique worldwide. Be aware that for setting up this app you need to add a mobile phone number to your account before this will succeed. You can remove that number after the app was successfully created.
3. Note down the **consumer key** and the **consumer secret** the new app provides to you.
4. Authorize your app to access your own account and change permissions to also give it access to direct messages. Then request the creation of the **access token key & access token secret** and note them down, too.
5. By this time Twitter should have mailed a link to you with your Twitter-archive as a **zip-file**. Give this file a meaningful name like e.g. **tweet_archive_$yourNick_2016.zip** and copy it to the ```tweeti-kiri``` folder
6. Now launch the program ```python tweeti_kiri.py``` from the command line and start with ```ACTION 1``` to configure your account & credentials.
7. **DONE!** You are now ready to do some housekeeping with your account.
8. If you want to work with different twitter accounts, you need to repeat the procedure of configuration with each of these accounts. You can make a simple backup of the **configuration.cfg** which is created for each successful configuration if you want to keep that somewhere safe for later use.


## Versions

* Version 0.9 (12. April 2016)

## Contact

Helpful hints for improving this piece of code can be transmitted to [trailblazr@noxymo.com](mailto:trailblazr@noxymo.com) or via Twitter to [@hspacehb](http://twitter.com/@hspacehb) the Twitter-Account of [Hackerspace Bremen](https://www.hackerspace-bremen.de/).

## Kudos
Many thanks go to [Mario Vilas](https://github.com/MarioVilas) for providing a really [useful piece of code](https://breakingcode.wordpress.com/2016/04/04/how-to-clean-up-your-twitter-account/) to start wrapping your head around. Thanks go also to the people maintaining the python-twitter module. Awesome piece of work without which this script won't be existing!

I also thank all the beta testers of the code and all the visitors at the presentation at [Hackerspace Bremen](https://www.hackerspace-bremen.de) which posed some good questions during the [presentation (slides as PDF)](https://raw.githubusercontent.com/HackerspaceBremen/tweeti-kiri/master/tweeti_kiri_presentation_april_2016.pdf).

## License
This code is licensed under the GPLv3 License.



