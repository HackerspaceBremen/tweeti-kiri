#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
README / MANUAL

Please look at the bottom of this script to find verbose description
of how to setup and operate this script in a meanigful and safe manner.

Thank you, have fun!
"""

# needed for basic file I/O
import sys, os, traceback, math

import anyjson
import zipfile
import twitter

# configuration storage & retrieval
from ConfigParser import SafeConfigParser
from datetime import date

# APP CONSTANTS
APP_PATH                    = os.path.dirname(os.path.abspath(__file__))
APP_CONFIG_FILE             = 'configuration.cfg'
APP_ESTIMATED_RATE_LIMIT    = 10 # docu says 180 Requests per 15 min (900 seconds) window makes 5 seconds per operation (lets stay with 10 secs per op)
APP_VERSION                 = 'v0.92'

# APP CONFIGURATION GLOBAL
APP_CFG_CONSUMER_KEY        = None
APP_CFG_CONSUMER_SECRET     = None
APP_CFG_ACCESS_TOKEN_KEY    = None
APP_CFG_ACCESS_TOKEN_SECRET = None
APP_CFG_TWITTER_NICK        = None
APP_CFG_TWITTER_ARCHIVE     = None

# DEFAULT CONFIG VALUES
APP_DFT_CONSUMER_KEY        = None # e.g. 'UEGC5s9Jk7A3pg1ZvYg4h35Dj'
APP_DFT_CONSUMER_SECRET     = None # e.g. 'OkunqjD6MkQxoxvTjcHayZm3yfq1CgfQM5JRjQYSqKoglMRKzh'
APP_DFT_ACCESS_TOKEN_KEY    = None # e.g. '3401492-cMrxN5eunq9kbeOfY0VtSYGHFwXpkp367gLeCnM26X'
APP_DFT_ACCESS_TOKEN_SECRET = None # e.g. 'Wmqy5GFsaVBlny51ZkZwDwNDRrnDf4hRswk9CIeJR0HhU'
APP_DFT_TWITTER_NICK        = None # e.g. 'tagesschau'
APP_DFT_TWITTER_ARCHIVE     = None # e.g. 'twitter_archiv_tagesschau_2016.zip'

global APP_API
APP_API = None

# If you had to interrupt the script, just put the last
# status ID here and it will resume from that point on.
last = 0

def query_yes_no( question, default="yes" ):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write( question + prompt )
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write( "Please respond with 'yes' or 'no' (or 'y' or 'n').\n" )

def read_fake_json( zip, filename ):
    data = zip.open( filename, 'rU' ).read()
    first_line, data = data.split( "\n", 1 )
    first_line = first_line.split( "=", 1 )[1]
    data = first_line + "\n" + data
    return anyjson.deserialize( data )

def tweets_extract_ids_from_zipfile( filename, tweets_year, tweets_month ):
    print "ZIPFILE, parsing now: %s" % filename
    tweet_ids = {}
    tweet_counter = 0
    with zipfile.ZipFile(filename, 'r') as zip:
        tweet_index = read_fake_json( zip, 'data/js/tweet_index.js' )
        for item in tweet_index:
            tweets_this_month = read_fake_json( zip, item['file_name'] )
            assert len( tweets_this_month ) == item['tweet_count']
            if int(item['year']) < int(tweets_year):
                tweet_ids[ "%d/%02d" % ( item['year'], item['month'] ) ] = [ x['id'] for x in tweets_this_month ]
                tweet_counter = tweet_counter + int( item['tweet_count'] )
            elif int( item['year'] ) == int( tweets_year ):
                if int(item['month']) <= int(tweets_month):
                    tweet_ids[ "%d/%02d" % ( item['year'], item['month'] ) ] = [ x['id'] for x in tweets_this_month ]
                    tweet_counter = tweet_counter + int(item['tweet_count'])
    return [tweet_ids, tweet_counter]

def is_api_configured():
    if not configuration_is_valid():
        print "API: No api-authorization configured, yet."
        print "API: Please configure account/authorization first before trying to use this script."
        print ""
        return False
    return True

def configure_print_status():
    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    print "CURRENT CONFIGURATION:"
    print "----------------------"
    print "            TWITTER NICK: %s" % APP_CFG_TWITTER_NICK
    print "         TWITTER ARCHIVE: %s" % APP_CFG_TWITTER_ARCHIVE
    print "       AUTH CONSUMER KEY: %s" % APP_CFG_CONSUMER_KEY
    print "    AUTH CONSUMER SECRET: %s" % APP_CFG_CONSUMER_SECRET
    print "   AUTH ACCESS TOKEN KEY: %s" % APP_CFG_ACCESS_TOKEN_KEY
    print "AUTH ACCESS TOKEN SECRET: %s" % APP_CFG_ACCESS_TOKEN_SECRET
    print "----------------------"

def configuration_is_valid():
    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    constants_to_check = [APP_CFG_TWITTER_NICK,
    APP_CFG_TWITTER_ARCHIVE,
    APP_CFG_CONSUMER_KEY,
    APP_CFG_CONSUMER_SECRET,
    APP_CFG_ACCESS_TOKEN_KEY,
    APP_CFG_ACCESS_TOKEN_SECRET]
    for current_constant in constants_to_check:
        if not current_constant or not len( current_constant ) > 0:
            return False
    return True

def configuration_clear():
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if os.path.exists( CONFIG_FILE_PATH ):
        continue_deleting = query_yes_no( "CONFIG DELETE: REALLY CLEAR CONFIG FOR ACCOUNT/AUTHORIZATION?", default="no" )
        if continue_deleting:
            print "CONFIG DELETE: Deleting config %s ..." % CONFIG_FILE_PATH
            os.remove( CONFIG_FILE_PATH )
            print "CONFIG DELETE: Deletion completed."

def configuration_autobackup():
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if APP_CFG_TWITTER_NICK and len( APP_CFG_TWITTER_NICK ) > 0:
        CONFIG_FILE_PATH_BACKUP = APP_PATH+'/'+'backup'+'_'+APP_CFG_TWITTER_NICK+'_'+APP_CONFIG_FILE
    else:
        CONFIG_FILE_PATH_BACKUP = APP_PATH+'/'+'backup'+'_'+APP_CONFIG_FILE
    if os.path.exists( CONFIG_FILE_PATH ):
        print "CONFIG AUTOBACKUP: Autorenaming old config %s to %s ..." % ( CONFIG_FILE_PATH, CONFIG_FILE_PATH_BACKUP )
        os.rename( CONFIG_FILE_PATH, CONFIG_FILE_PATH_BACKUP )
        print "CONFIG AUTOBACKUP: Autorenaming completed."

def configuration_read():
    global APP_API

    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    global APP_DFT_TWITTER_NICK
    global APP_DFT_TWITTER_ARCHIVE
    global APP_DFT_CONSUMER_KEY
    global APP_DFT_CONSUMER_SECRET
    global APP_DFT_ACCESS_TOKEN_KEY
    global APP_DFT_ACCESS_TOKEN_SECRET

    # CHECK EXISTENCE
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if not os.path.exists( CONFIG_FILE_PATH ):
        print "CONFIG READ: No config %s found. Configuring default values." % CONFIG_FILE_PATH
        # APPLY DEFAULT VALUES FROM GLOBAL CONSTANTS
        APP_CFG_TWITTER_NICK        = APP_DFT_TWITTER_NICK
        APP_CFG_TWITTER_ARCHIVE     = APP_DFT_TWITTER_ARCHIVE
        APP_CFG_CONSUMER_KEY        = APP_DFT_CONSUMER_KEY
        APP_CFG_CONSUMER_SECRET     = APP_DFT_CONSUMER_SECRET
        APP_CFG_ACCESS_TOKEN_KEY    = APP_DFT_ACCESS_TOKEN_KEY
        APP_CFG_ACCESS_TOKEN_SECRET = APP_DFT_ACCESS_TOKEN_SECRET
        # SAVE DEFAULTS TO A NEW CONFIG INSTEAD NOW...
        if configuration_is_valid():
            configuration_write()
        return
    else:
        print "CONFIG READ: %s" % CONFIG_FILE_PATH

    # READ FILE
    config_file = SafeConfigParser()
    try:
        config_file.read( CONFIG_FILE_PATH )
    except:
        print "CONFIG READ: Reading config %s failed. (WARNING: API unconfigured!)" % CONFIG_FILE_PATH
        return

    APP_CFG_TWITTER_NICK        = config_file.get( 'account', 'nick' )
    APP_CFG_TWITTER_ARCHIVE     = config_file.get( 'account', 'archive_file' )
    APP_CFG_CONSUMER_KEY        = config_file.get( 'authorization', 'consumer_key' )
    APP_CFG_CONSUMER_SECRET     = config_file.get( 'authorization', 'consumer_secret' )
    APP_CFG_ACCESS_TOKEN_KEY    = config_file.get( 'authorization', 'access_token_key' )
    APP_CFG_ACCESS_TOKEN_SECRET = config_file.get( 'authorization', 'access_token_secret' )

    # getfloat() raises an exception if the value is not a float
    # a_float = config.getfloat('main', 'a_float')
    # getint() and getboolean() also do this for their respective types
    # an_int = config.getint('main', 'an_int')

def configuration_write():
    global APP_API

    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    global APP_DFT_TWITTER_NICK
    global APP_DFT_TWITTER_ARCHIVE
    global APP_DFT_CONSUMER_KEY
    global APP_DFT_CONSUMER_SECRET
    global APP_DFT_ACCESS_TOKEN_KEY
    global APP_DFT_ACCESS_TOKEN_SECRET

    # WRITE FILE
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE

    # BACKUP PREXISTING CONFIG
    if os.path.exists( CONFIG_FILE_PATH ):
        configuration_autobackup();

    config_file = SafeConfigParser()
    config_file.read( CONFIG_FILE_PATH )
    # STORE account
    config_file.add_section( 'account' )
    config_file.set( 'account', 'nick', APP_CFG_TWITTER_NICK )
    config_file.set( 'account', 'archive_file', APP_CFG_TWITTER_ARCHIVE )
    # AUTH account
    config_file.add_section( 'authorization' )
    config_file.set( 'authorization', 'consumer_key', APP_CFG_CONSUMER_KEY )
    config_file.set( 'authorization', 'consumer_secret', APP_CFG_CONSUMER_SECRET )
    config_file.set( 'authorization', 'access_token_key', APP_CFG_ACCESS_TOKEN_KEY )
    config_file.set( 'authorization', 'access_token_secret', APP_CFG_ACCESS_TOKEN_SECRET )

    print "CONFIG WRITE: Writing config %s ..." % CONFIG_FILE_PATH
    with open( CONFIG_FILE_PATH, 'w' ) as file_to_write:
        config_file.write( file_to_write )
    print "CONFIG WRITE: Writing succeeded."

def configure_account():
    configure_print_status()
    print ""
    continue_configuring = True
    if configuration_is_valid():
        continue_configuring = query_yes_no( "CONFIG: REALLY RECONFIGURE ACCOUNT/AUTHORIZATION?", default="no" )

    if not continue_configuring:
        print "CONFIG: Aborted configuration."
        return
    # NOW ASK DETAILS FROM USER
    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    APP_CFG_TWITTER_NICK        = raw_input( "        ENTER TWITTER NICK NAME: " ).rstrip()
    APP_CFG_TWITTER_ARCHIVE     = raw_input( "ENTER PATH TO TWEET-ZIP-ARCHIVE: " ).rstrip()
    APP_CFG_CONSUMER_KEY        = raw_input( "             ENTER CONSUMER KEY: " ).rstrip()
    APP_CFG_CONSUMER_SECRET     = raw_input( "          ENTER CONSUMER SECRET: " ).rstrip()
    APP_CFG_ACCESS_TOKEN_KEY    = raw_input( "         ENTER ACCESS TOKEN KEY: " ).rstrip()
    APP_CFG_ACCESS_TOKEN_SECRET = raw_input( "      ENTER ACCESS TOKEN SECRET: " ).rstrip()

    print ""
    if configuration_is_valid():
        configuration_write()
        print "CONFIG: Succeeded. Restart script now!"
    else:
        print "CONFIG: Entered data is invalid. Something is missing... have a close look..."
        print ""
        configure_print_status()
    print ""


def analyze_account():
    global APP_API
    print ""
    screen_name = None
    if configuration_is_valid():
        choice_string = "ACCOUNT: ANALYZE CONFIGURED ACCOUNT (Current: %s)?" % APP_CFG_TWITTER_NICK
        continue_using_default_account = query_yes_no( choice_string, default="yes" )
        if continue_using_default_account:
            screen_name = APP_CFG_TWITTER_NICK
        else:
            screen_name = raw_input( "ENTER TWITTER NICK NAME TO ANALYZE: " )
            screen_name = screen_name.rstrip()
    else:
        screen_name = raw_input( "ENTER TWITTER NICK NAME TO ANALYZE: " )
        screen_name = screen_name.rstrip()

    print ""
    if not screen_name or len( screen_name ) < 2:
        print "ACCOUNT: No valid account twitter nick entered. Aborting."
        return

    MAX_ALLOWED_MESSAGES = 200
    MAX_ALLOWED_FAVS = 200
    MAX_ALLOWED_FOLLOWERS = 2000
    try:
        print "ACCOUNT: ACQUIRING DATA... PLEASE WAIT..."
        print ""
        if not is_api_configured():
            return
        account_owner = APP_API.GetUser( user_id=None, screen_name=screen_name, include_entities=True )
        #account_blocked_users = api.GetBlocks( user_id=None, screen_name=None, cursor=-1, skip_status=True, include_user_entities=True)
        #account_direct_messages = api.GetDirectMessages( since_id=None, max_id=None, count=MAX_ALLOWED_MESSAGES, include_entities=True, skip_status=False )
        #account_favourites = api.GetFavorites( user_id=None, screen_name=None, count=MAX_ALLOWED_FAVS, since_id=None, max_id=None, include_entities=True )
        #account_followers = api.GetFollowerIDs( user_id=None, screen_name=None, cursor=-1, stringify_ids=False, count=None, total_count=None )
        #account_following = api.GetFriendIDs( user_id=None, screen_name=None, cursor=-1, stringify_ids=False, count=None )
        #account_sent_direct_messages = api.GetSentDirectMessages( since_id=None, max_id=None, count=None, page=None, include_entities=True )
    except twitter.error.TwitterError, e:
        try:
            message = e.message[0]['message']
        except:
            message = repr( e.message )
        print "ACCOUNT: Error acquiring account data."
        print "ACCOUNT: ERROR   %s" % (message,)
        return

    # list data
    print "----------------------"
    print "       NAME: %s" % account_owner.name
    print " SCREENNAME: %s" % account_owner.screen_name
    print "  PROTECTED: %s" % account_owner.protected
    print " USER SINCE: %s" % account_owner.created_at
    print "DESCRIPTION: \n\n%s\n" % account_owner.description
    print "----------------------"
    print "     TWEETS: %s" % str( account_owner.statuses_count )
    print "  FOLLOWERS: %s" % str( account_owner.followers_count )
    print "  FOLLOWING: %s" % str( account_owner.friends_count )
    print " FAVOURITES: %s" % str( account_owner.favourites_count )
    print "----------------------"
    return

def estimated_time_of_arrival( num_of_operations ):
    global APP_ESTIMATED_RATE_LIMIT
    estimated_seconds = num_of_operations * APP_ESTIMATED_RATE_LIMIT
    estimated_minutes = math.floor( estimated_seconds / 60 )
    estimated_seconds = estimated_seconds - ( estimated_minutes * 60 )
    estimated_hours = math.floor( estimated_minutes / 60 )
    estimated_minutes = estimated_minutes - ( estimated_hours * 60 )
    if estimated_hours > 0:
        if estimated_minutes > 0:
            eta_string = "%d hours and %d minutes" % ( estimated_hours, estimated_minutes )
        else:
            eta_string = "%d hours" % ( estimated_hours, )
    else:
        if estimated_seconds > 0:
            eta_string = "%d minutes and %d seconds" % ( estimated_minutes, estimated_seconds )
        else:
            eta_string = "%d minutes" % ( estimated_minutes, )
    return eta_string

def delete_favourites():
    global APP_API
    print "FAVOURITES: Not yet implemented."

def delete_followers():
    global APP_API
    print "FOLLOWERS: Not yet implemented."

def delete_friends():
    global APP_API
    print "FRIENDS: Not yet implemented."

def delete_directmessages():
    global APP_API
    MAX_ALLOWED_MESSAGES = 200
    messages_to_delete = None
    try:
        if not is_api_configured():
            return
        messages_to_delete = APP_API.GetSentDirectMessages(since_id=None, max_id=None, count=MAX_ALLOWED_MESSAGES, page=None, include_entities=True)
        num_to_delete = len( messages_to_delete )
        num_deleted = 0
    except:
        print "MESSAGES: Error determining amount of direct messages."
        return
    if num_to_delete == 0:
        print "MESSAGES: No more messages to delete. Everything already cleaned."
        return

    print "MESSAGES: There are %d sent direct messages to delete." % num_to_delete

    estimated_time_needed = estimated_time_of_arrival( num_to_delete )
    print "MESSAGES: Deletion will take an estimated %s to finish." % estimated_time_needed

    continue_deleting = query_yes_no( "MESSAGES: REALLY DELETE ALL DIRECT MESSAGES SENT", default="no" )

    if not continue_deleting:
        print "MESSAGES: Aborted deleting."
        return

    # start destroying messages one by one
    print "MESSAGES: Deleting %d direct messages now..." % num_to_delete
    for current_message in messages_to_delete:
        error_counter = 0
        while True:
            try:
                api.DestroyDirectMessage( current_message.id, include_entities=True )
                num_deleted += 1
                print "MESSAGES: %d DELETED (%d of %d) TO %s" % ( current_message.id, num_deleted, num_to_delete, current_message.recipient_screen_name )
                break
            except twitter.error.TwitterError, e:
                try:
                    message = e.message[0]['message']
                    retry = False
                except:
                    message = repr( e.message )
                    retry = True
                print "MESSAGES: %d ERROR   %s" % (current_message.id, message)
                error_counter += 1
                if error_counter > 5:
                    print "MESSAGES: Too many errors, aborting!"
                    exit(1)
                if not retry:
                    break # exit endless while loop
    print "MESSAGES: DELETION COMPLETED."
    return

def delete_tweets_choose_time_range( filename_archive ):
    year_today = date.today().year
    year_choice = "PLEASE CHOOSE YEAR UP TO WHICH WE DELETE TWEETS (ENTER for %s): " % str(year_today)
    action_raw = raw_input( year_choice ).rstrip()
    if not action_raw:
        year_chosen = 2016
    else:
        year_chosen = int( action_raw )

    month_today = date.today().month
    month_choice = "PLEASE CHOOSE MONTH (1-12) UP TO WHICH WE DELETE TWEETS (ENTER for %s): " % str(month_today)
    action_raw = raw_input( month_choice ).rstrip()
    if not action_raw:
        month_chosen = 12
    else:
        month_chosen = int( action_raw )

    continue_deleting = query_yes_no( "TWEETS: SELECT ALL TWEETS UNTIL AND INCLUDING MONTH/YEAR %s/%s ?" % (str(month_chosen), str(year_chosen)), default="no" )
    if not continue_deleting:
        print "TWEETS: Aborted deleting."
        return
    delete_tweets_from_archive_until_year( filename_archive, year_chosen, month_chosen )


def delete_tweets_from_archive_until_year( filename_archive, tweets_year, tweets_month ):
    global APP_API
    FILE_PATH = APP_PATH+'/'+filename_archive
    if not os.path.exists( FILE_PATH ):
        print 'TWEETS: Das twitter-Archiv in '+FILE_PATH+' ist nicht vorhanden.'
        return

    if not is_api_configured():
        return
    # get list of ids to destroy from zip file
    result_array = tweets_extract_ids_from_zipfile( filename_archive, tweets_year, tweets_month )
    
    tweet_ids = result_array[0]
    num_to_delete = result_array[1]

    # sort in reversed order
    tweet_ids_sorted = sorted( tweet_ids.keys(), reverse=True )

    print "TWEETS: There are %d tweets to delete." % num_to_delete

    estimated_time_needed = estimated_time_of_arrival( num_to_delete )
    print "TWEETS: Deletion will take an estimated %s to finish." % estimated_time_needed

    continue_deleting = query_yes_no( "TWEETS: REALLY DELETE ALL TWEETS NOW?", default="no" )
    if not continue_deleting:
        print "TWEETS: Aborted deleting."
        return
    
    begin = False
    for date in tweet_ids_sorted:
        year, month = date.split("/")
        if int(year) < tweets_year:
            print "TWEETS: Deleting from: %s" % date
            num_to_delete = len( tweet_ids[date] )
            num_deleted = 0
            for tid in tweet_ids[date]:
                if begin or last == 0 or tid == last:
                    begin = True
                    error_counter = 0
                    while True:
                        try:
                            APP_API.DestroyStatus(tid)
                            num_deleted += 1
                            print "TWEETS: %d DELETED (%d of %d)" % ( tid, num_deleted, num_to_delete )
                            break
                        except twitter.error.TwitterError, e:
                            try:
                                message = e.message[0]['message']
                                retry = False
                            except:
                                message = repr( e.message )
                                retry = True
                            print "TWEETS: %d ERROR   %s" % (tid, message)
                            error_counter += 1
                            if error_counter > 5:
                                print "TWEETS: Too many errors, aborting!"
                                exit(1)
                            if not retry:
                                break # exit endless while loop
    print "TWEETS: DELETION COMPLETED."


# main app call
if __name__ == "__main__":
    print ""
    print "******************************************"
    print "***            TWEETI-KIRI             ***"
    print "***  YOUR SOCIAL MEDIA VACUUM CLEANER  ***"
    print "***                                    ***"
    print "***       by trailblazr in 2016        ***"
    print "***  (derived from Mario Vilas' code)  ***"
    print "******************************************"
    print ""
    configuration_read()
    # configure_print_status()
    if configuration_is_valid():
        # Configure API with keys & secrets of app
        APP_API = twitter.Api( 
            consumer_key=APP_CFG_CONSUMER_KEY, 
            consumer_secret=APP_CFG_CONSUMER_SECRET,
            access_token_key=APP_CFG_ACCESS_TOKEN_KEY, 
            access_token_secret=APP_CFG_ACCESS_TOKEN_SECRET, )
    else:
        APP_CFG_TWITTER_NICK = None

    if APP_CFG_TWITTER_NICK and len( APP_CFG_TWITTER_NICK ) > 0:
        account_string =  " (Current: %s)" % APP_CFG_TWITTER_NICK
    else:
        account_string = ""

    num_menu_items = 7
    print ""
    print "MENU OF AVAILABLE ACTIONS"
    print ""
    print "(1) Account configure%s" % account_string
    print "(2) Account analyze"
    print "(3) Remove tweets"
    print "(4) Remove direct messages"
    print "(5) Remove favourites - Not yet implemented -"
    print "(6) Remove followers - Not yet implemented -"
    print "(7) Remove friends/following - Not yet implemented -"

    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if os.path.exists( CONFIG_FILE_PATH ):
        print "(8) Remove configuration"
        num_menu_items += 1

    print "(0) EXIT/ABORT"
    print ""
    print "VERSION: %s" % APP_VERSION
    print "   INFO: EVERY POTENTIALLY DESTRUCTIVE ACTION WILL ASK FOR CONFIRMATION AGAIN!"
    print ""

    menu_choice = "PLEASE CHOOSE ITEM FROM MENU [0..%d]: " % num_menu_items
    action_raw = raw_input( menu_choice ).rstrip()
    if not action_raw:
        action_chosen = 0
    else:
        action_chosen = int( action_raw )
    print ""
    print "WELCOME."
    if action_chosen == 1:
        print "CONFIGURING..."
        configure_account()
    elif action_chosen == 2:
        print "ANALYZING..."
        analyze_account()
    elif action_chosen == 3:
        print "RETRIEVING TWEETS..."
        delete_tweets_choose_time_range( APP_CFG_TWITTER_ARCHIVE )
    elif action_chosen == 4:
        print "RETRIEVING DIRECT MESSAGES..."
        delete_directmessages()
    elif action_chosen == 5:
        print "RETRIEVING FAVOURITES..."
        delete_favourites()
    elif action_chosen == 6:
        print "RETRIEVING FOLLOWERS..."
        delete_followers()
    elif action_chosen == 7:
        print "RETRIEVING FRIENDS..."
        delete_friends()
    elif action_chosen == 8 and num_menu_items >= 8:
        print "Cleaning CONFIG..."
        configuration_clear()
    elif action_chosen == 0:
        print "EXIT/ABORT..."
    else:
        print "ERROR: INVALID CHOICE/INPUT"

    print "GOOD BYE!"
    print ""

"""
HINTS FOR INSTALLING AND MODIFYING THIS SCRIPT:
(added by trailblazr from hackerspace bremen, germany)

- to make this script run you need certain installed python modules which are best installed in a virtualenv directory
- so first create a virtualenv directory using 'virtualenv tweeti-kiri'
- then change dir into it and type 'source bin/activate'
- now copy this script into the tweeti-kiri-directory
- continue installing the missing/needed python modules
- you need to install 'anyjson' and 'python-twitter' using 'pip install anyjson' and 'pip install python-twitter'
- also put your downloaded zip.archive of tweets you ordered at twitter in this directory (keep it zipped)
- that's it. you are set. please read the original instructions by Mario Vilas below now...
- to modify the script try e.g. typing 'pydoc'-commands to learn about the twitter api
- type e.g. 'pydoc twitter.DirectMessage' to get more info on classes in the twitter module and how they work
- try to keep stuff simple (use KISS design principle)
- use comments in your code and simplify this code and do make pull-requests

ORIGINAL CODE SOURCE / BLOGPOST / IDEA:
https://breakingcode.wordpress.com/2016/04/04/how-to-clean-up-your-twitter-account/
by Mario Vilas, Security Consultant at NCC Group
see also https://www.linkedin.com/in/mariovilas
on Twitter @Mario_Vilas

EXCERPT FROM THE ORIGINAL BLOG POST (HERE TEXT ONLY):
How to clean up your Twitter account
(Filed under: Privacy, Programming, Tools)
(Tags: LinkedIn, python, tool, Twitter, web, webapp — Mario Vilas at 5:47 am)

Recently I decided to get rid of all of my old tweets, specifically all of them from last year and before.
I had no use for most of them and curating them would have been too much of a burden (over 66.000 tweets! 
so much procrastination!).

Now, there are a number of online applications to do that, but they have at least one of the following problems,
fundamentally the last one:

They pull your Twitter posts from the API, which only allows you to read at most the latest 200 tweets, so removing
the older ones becomes impossible. Some of them get around this by asking you to upload your entire Twitter archive…
which contains a lot more than just your tweets (i.e. your private messages). (EDIT: I’m being told this is no longer
the case, now it just contains your public timeline)

I don’t trust them.

So naturally I rolled my own. The code is crude but it worked for me. It uses the Twitter archive zip file as well,
but since it works locally you don’t need to trust a third party with your personal data. With this I managed to delete
over 60.000 tweets in a day and a half, roughly – it can’t be done much faster because of the API rate limiting, but then
again, what’s the rush? :)

Now, to use it, follow these steps:

(1) Get your Twitter archive.

You can do this by going to Settings -> Account -> Your Twitter archive.
This will send you an email with a download link to a zip file.

(2) Get this script and place it in the same directory as the zip file you just downloaded.

(3) Go to https://apps.twitter.com/ and create a new application.

This will get you the consumer key and the consumer secret, take note of those.
Authorize your app to access your own account (you do it in the same place right after creating your new app).
Check that you change permissions to also allow the app to access your direct messages if you want to delete them too.

(4) Now you have the access token key and secret if not yet generate them, take note of those too. Store that info on your machine.

(5) Edit the script and add all those tokens and secrets at the beginning of the file to the default values.

Add the name of the zip file as well to the default values.
Since you’re at it, review the source code of this script – you shouldn’t be running code you downloaded from
some random place on the interwebz without reading it first!

(6) Run the script. This will take some time. Disable powersave-mode on your machine, lock it and get off the chair. Go out.

Enjoy the real world. It’s the ultimate 3D experience, and it comes in HD!

"""