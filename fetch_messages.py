import csv
import datetime
import json
import requests
import sys
import time

import ipp_secrets

OPERATING_SYSTEM = 'MacOs'
AGENT_NAME = 'InboxPersonalParser'
VERSION = '0.0.1'
# setup our header info, which gives reddit a brief description of our app
headers = {'User-Agent': f'{OPERATING_SYSTEM}:{AGENT_NAME}:{VERSION} (by /u/{ipp_secrets.REDDIT_USERNAME})'}

def get_token(headers):
    # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
    auth = requests.auth.HTTPBasicAuth(ipp_secrets.CLIENT_ID, ipp_secrets.SECRET_TOKEN)

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': ipp_secrets.REDDIT_USERNAME,
            'password': ipp_secrets.REDDIT_PASSWORD}

    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    return TOKEN

def get_messages(token, headers, after, limit, url):
    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {token}"}}

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    params = {'mark': 'false', 'after' : after, 'limit' : limit}
    req = requests.get(url, params=params, headers=headers)
    print("{0} - {1} - {2}".format(req.status_code, after, url))
    if (req.status_code != 200):
        print("ERROR! Aborting")
        exit(1)

    # add a sleep to ensure that we don't exceed the API rate limits 
    # for the Reddit API, which is 60 req/minute.
    # Since we can download a max of 100 messages per request,
    # this means we would need to have more than 6000 messages in the inbox
    # before this is a problem.  Still, adding a sleep is safe, and
    # will ensure that even large inboxes don't have rate-limit issues.
    
    time.sleep(1)
    
    #
    #removeBody(req.text)
    #
    return req

def remove_body(jsonMessage):
    messages = json.loads(jsonMessage)['data']['children']
    for m in messages:
        d = m['data']
        d['body'] = None
        d['body_html'] = None
        print(d)

def get_all_messages(token, headers,url):
    after = None
    limit = 100
    allMessages = []
    toDo = True
    while toDo:
        req = get_messages(token, headers, after, limit, url)
        jsonMessage = json.loads(req.text)
        after = jsonMessage['data']['after']
        listOfMessages = jsonMessage['data']['children']
        print(f'Found {len(listOfMessages)} messages')
        if (len(listOfMessages) > 0):
            allMessages.extend(listOfMessages)
        else:
            toDo = False
        if after == None:
            toDo = False
    return allMessages


def print_output(messages, redditUsername, output_file):
    #print(f'Got list with {len(messages)} entries')
    with open(output_file, 'w') as f:  
        cw = csv.writer(f)
        cw.writerow(['FROM_USER', 'TO_USER', 'OTHER_USER', 'SENT_VS_RECEIVED', 
            'DATE_UTC', 'THREAD_ID', 'KIND', 'CHAR_COUNT', 'WORD_COUNT', 'SUBJECT', 'BODY'])
        for m in messages:
            d = m['data']
            displayDate = datetime.datetime.utcfromtimestamp(d['created_utc']).strftime('%Y-%m-%d %H:%M:%S')
            otherUser = d['author']

            threadId = ''
            if d['first_message_name'] == None:
                # If no first_message_name, then this is the first message in the thread
                # Use the ID of this message
                threadId = d['name']  # e.g. t4_abcdef
            else:
                threadId = d['first_message_name']

            sentReceived = 'received'
            if d['author'] == redditUsername:
                sentReceived = 'sent'
                otherUser = d['dest']
            # cw.writerow(['{0}','{1}','{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format(d['author'],
            #     d['dest'],otherUser,sentReceived,displayDate,threadId,
            #     m['kind'],len(d['body']),len(d['body'].split()), d['subject'], d['body'])])
            cw.writerow([d['author'],
                d['dest'], otherUser, sentReceived, displayDate, threadId,
                m['kind'], len(d['body']), len(d['body'].split()), 
                d['subject'], d['body']])

def parse_input_args():
    if len(sys.argv) != 2:
        print(" ")
        print("Usage: ")
        print("   {0} [output-csv-file]".format(sys.argv[0]))
        print(" ")
        print("e.g.")
        print("   {0} reddit.csv".format(sys.argv[0]))
        exit(1)
    else:
        return sys.argv[1]

if __name__=="__main__":
    output_file = parse_input_args()

    token = get_token(headers)
    messages = []
    receivedMsgs = get_all_messages(token, headers, url='https://oauth.reddit.com/message/inbox')
    messages.extend(receivedMsgs)
    sentMsgs = get_all_messages(token, headers, url='https://oauth.reddit.com/message/sent')
    messages.extend(sentMsgs)
    print_output(messages, ipp_secrets.REDDIT_USERNAME, output_file)

