

# High-level overview:

1) Go to Reddit and create an access token for your account
2) Download the python scripts
3) Install the prerequisites that the scripts need (Python, Anaconda, Pandas, etc.)
4) Run first script to fetch your data from Reddit and dump it to a CSV file
5) Run the second script to analyze the CSV file and show you the results

# Detailed steps:
## Part 1: Create Access Tokens on Reddit

1) Log into https://www.reddit.com/ with the Reddit account you want to analyze
2) Go to https://www.reddit.com/prefs/apps
3)    Scroll to the bottom and click "Create another app"
4)    Name: Inbox Personal Parser
5)    Select "script" as the type
6)    Redirect URI: http://example.org    (we won't use this value, but it requires something)
7)    Click "Create App"
8)  It will create an entry for you.
    You should see a boxed section just above where you are.
    You will see the name you gave: "Inbox Personal Parser".
    Then "personal use script"
    The third line is a the Client ID, and looks something like:
    UlJcjAgOdyg0DkJf2X30HkS574Ee1T
    Make note of this value, you will need it.

    You will also need the "secret" value shown just below the Client ID.
    It is also a random-looking string:
    XlIcj5gOdag0JkAx2Y3a9kSI74ye0R

## Part 2: Download the scripts from Github

1) Download the scripts from : 

https://github.com/OneStrangeAlgorithm/reddit-inbox-parser 

## Part 3: Install prerequisites

1) If you don't have Python installed already, do so:

 https://www.python.org/downloads/

2) Open a command terminal and go to where you downloaded the scripts
3) Run the following command to install the prerequisites

`pip3 install .`

# Part 4: Configure the scripts and run!

1) Edit the ipp_secrets.py file and fill in the four values

```
REDDIT_USERNAME='YourRedditNameHere'
REDDIT_PASSWORD='YourRedditPasswordHere'
CLIENT_ID='YourClientID'
SECRET_TOKEN='YourSecretToken'
```

The CLIENT_ID and SECRET_TOKEN are the values you created earlier.
Note that you MUST have quotes around the values!!

Save the file

2) Ok, you are ready to run!
   Open a command prompt on your computer and type:

   `python3 fetch_messages.py reddit.csv`

   This will run the script, and it will output something like this:

```
200 - None - https://oauth.reddit.com/message/inbox
Found 100 messages
200 - t4_19abcvk - https://oauth.reddit.com/message/inbox
Found 100 messages
200 - t4_17rip2p - https://oauth.reddit.com/message/inbox
Found 100 messages
200 - t4_14qwe1y - https://oauth.reddit.com/message/inbox
Found 100 messages
200 - t4_11aacl1 - https://oauth.reddit.com/message/inbox
Found 99 messages
200 - None - https://oauth.reddit.com/message/sent
Found 100 messages
200 - t4_19julk9 - https://oauth.reddit.com/message/sent
Found 100 messages
200 - t4_17uioaq - https://oauth.reddit.com/message/sent
Found 100 messages
200 - t4_13pkjkju - https://oauth.reddit.com/message/sent
Found 100 messages
200 - t4_11a8af7n - https://oauth.reddit.com/message/sent
Found 100 messages
200 - t4_yuuweff5 - https://oauth.reddit.com/message/sent
Found 3 messages
```

3) You should now have a file called reddit.csv in that directory.
This is the raw dump of your inbox data, in CSV format.
At this point, you can stop here, if you like.
Load this file up in Excel and go nuts!  Make pivot tables, graphs, drop any data
you don't want, etc.  
If you'd like to run the analytics script, proceed to the next step.

4) Run:  
  python3 analyze.py reddit.csv

  This will read in the reddit.csv file and create 5 graphs (as JPG files):

active_threads_by_month.jpg  
aggregate_messages_received_per_thread.jpg  
boxplot_chars_per_msg_by_month.jpg  
messages_received_per_thread_n_gte_2.jpg  
words_sent_per_month.jpg  

Also, a set of text stats will be printed to the screen:
```
****************************************************
** THREAD SUMMARY
****************************************************
   Total Threads                       =   67
   Threads with no replies             =   38 (57%)
   Threads with at least 1 reply       =   29 (43%)
 
****************************************************
** THREAD DETAILED RESPONSE RATES 
****************************************************
   Threads with 1-5 replies            =   11 (16%)
   Threads with 6-20 replies           =   11 (16%)
   Threads with 21-50 replies          =    5 ( 7%)
   Threads with >50 replies            =    2 ( 3%)
 
****************************************************
** THREAD MISC STATS 
****************************************************
   Threads I didn't respond to         =    0 ( 0%)
   Threads with a now-deleted partner  =   18 (27%)
 
****************************************************
** MESSAGE STATS 
****************************************************
   Total Messages Sent                 =        501
   Total Messages Received             =        479
 
   Total Words Sent                    =    168,766
   Total Words Received                =    106,618
 
   Total Characters Sent               =    960,460
   Total Characters Received           =    593,796
 
   Avg chars sent per message          =      1,917
   Avg chars received per message      =      1,240
```

5) That's it!  Whenever you want updated data, just re-run the two 
python scripts.

## Reference links

https://www.reddit.com/wiki/api  
https://www.reddit.com/dev/api  
https://github.com/reddit-archive/reddit/wiki/OAuth2  



   
