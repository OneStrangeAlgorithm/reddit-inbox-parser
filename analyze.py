import datetime
import logging
import sys

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

summary_stats = {}

def read_and_filter(input_file):
    f = pd.read_csv(input_file)
    logging.debug("Rows in file = {0}".format(len(f)))
    
    # "t4" are messages
    # "t1" are post/comment replies - we don't want those
    # Select just messages
    c = f[f["KIND"] == "t4"]
    logging.debug("Remove non-messages. Remaining = {0}".format(len(c)))

    # remove any messages from 'reddit' (e.g. "Your 2021 Reddit Recap")
    c = c[(c["FROM_USER"] != "reddit") & (c["TO_USER"] != 'reddit')]
    logging.debug("Remove messages from 'reddit'. Remaining = {0}".format(len(c)))

    # remove any messages from 'dirty-penpal-bot'
    c = c[(c["FROM_USER"] != "dirty-penpal-bot") & (c["TO_USER"] != 'dirty-penpal-bot')]
    logging.debug("Remove messages from 'dirty-penpal-bot'. Remaining = {0}".format(len(c)))

    # remove any messages from 'AutoModerator'
    c = c[(c["OTHER_USER"] != "AutoModerator")]
    logging.debug("Remove messages from 'AutoModerator'. Remaining = {0}".format(len(c)))

    # add a column with all rows having a value of 1
    # this will simplify the aggregation functions that come later
    c = c.assign(MSG_COUNT=1)

    return c

def aggregate_by_thread(df, summary_stats):
    # Narrow to only the columns we care about for aggregation
    before_thread_pivot = df[["THREAD_ID", "OTHER_USER", 
        "SENT_VS_RECEIVED", "MSG_COUNT"]]

    agg_by_thread = pd.pivot_table(before_thread_pivot,
        index=['THREAD_ID', 'OTHER_USER'], aggfunc='count',
        columns='SENT_VS_RECEIVED')
    logging.debug(agg_by_thread)

    # convert 'NaN' to '0'
    agg_by_thread = agg_by_thread.fillna(0)
    logging.debug(agg_by_thread)
    logging.debug("^ aggregate by thread")
    summary_stats['total_threads'] = len(agg_by_thread)

    return agg_by_thread

def count_deleted_threads(agg_by_thread, summary_stats):
    deleted = agg_by_thread.query('OTHER_USER=="[deleted]"')
    logging.debug(deleted)
    logging.debug("^ agg by thread deleted")
    summary_stats['threads_with_deleted_other_user'] = len(deleted)

def find_threads_with_no_replies(agg_by_thread, summary_stats):
    threads_with_no_replies = agg_by_thread[
           (agg_by_thread["MSG_COUNT"]["sent"] >= 1)
         & (agg_by_thread["MSG_COUNT"]["received"] == 0) ]
    logging.debug(threads_with_no_replies)
    logging.debug("^ threads with no replies")
    summary_stats['threads_with_no_replies'] = len(threads_with_no_replies)

    threads_with_1_to_5_replies = agg_by_thread[
           (agg_by_thread["MSG_COUNT"]["sent"] >= 1)
         & (agg_by_thread["MSG_COUNT"]["received"] >=1)
         & (agg_by_thread["MSG_COUNT"]["received"] <=5) ]
    summary_stats['threads_with_1_to_5_replies'] = len(threads_with_1_to_5_replies)

    threads_with_6_to_20_replies = agg_by_thread[
           (agg_by_thread["MSG_COUNT"]["sent"] >= 1)
         & (agg_by_thread["MSG_COUNT"]["received"] >=6)
         & (agg_by_thread["MSG_COUNT"]["received"] <=20) ]
    summary_stats['threads_with_6_to_20_replies'] = len(threads_with_6_to_20_replies)

    threads_with_21_to_50_replies = agg_by_thread[
           (agg_by_thread["MSG_COUNT"]["sent"] >= 1)
         & (agg_by_thread["MSG_COUNT"]["received"] >21)
         & (agg_by_thread["MSG_COUNT"]["received"] <=50) ]
    summary_stats['threads_with_21_to_50_replies'] = len(threads_with_21_to_50_replies)

    threads_with_gte_51_replies = agg_by_thread[
           (agg_by_thread["MSG_COUNT"]["sent"] >= 1)
         & (agg_by_thread["MSG_COUNT"]["received"] >=51)]
    summary_stats['threads_with_gte_51_replies'] = len(threads_with_gte_51_replies)


def find_threads_i_ignored(agg_by_thread, summary_stats):
    threads_i_ignored = agg_by_thread[
           (agg_by_thread["MSG_COUNT"]["received"] >= 1)
         & (agg_by_thread["MSG_COUNT"]["sent"] == 0) ]
    logging.debug(threads_i_ignored)
    logging.debug("^ threads I ignored")
    summary_stats['threads_i_ignored'] = len(threads_i_ignored)

def find_total_msg_sent_received(agg_by_thread, summary_stats):
    total_thread_stats = agg_by_thread.agg(['sum'])
    summary_stats['total_messages_sent'] = total_thread_stats["MSG_COUNT"]["sent"][0]
    summary_stats['total_messages_received'] = total_thread_stats["MSG_COUNT"]["received"][0]
    logging.debug(total_thread_stats)
    logging.debug("^ total_messages_sent")
    #MSG_COUNT       
    #SENT_VS_RECEIVED  received   sent
    #sum                  483.0  500.0

def find_word_counts(df, summary_stats):
    sent_sums = df[df["SENT_VS_RECEIVED"] == "sent"]
    sent_sums = sent_sums[["WORD_COUNT"]].sum()
    summary_stats['total_words_sent'] = sent_sums[0]

    sent_sums = df[df["SENT_VS_RECEIVED"] == "sent"]
    sent_sums = sent_sums[["CHAR_COUNT"]].sum()
    summary_stats['total_chars_sent'] = sent_sums[0]

    sent_sums = df[df["SENT_VS_RECEIVED"] == "received"]
    sent_sums = sent_sums[["WORD_COUNT"]].sum()
    summary_stats['total_words_received'] = sent_sums[0]

    sent_sums = df[df["SENT_VS_RECEIVED"] == "received"]
    sent_sums = sent_sums[["CHAR_COUNT"]].sum()
    summary_stats['total_chars_received'] = sent_sums[0]

def graph_received_messages_by_thread(agg_by_thread):
    threads_with_gte_2_replies = agg_by_thread[agg_by_thread["MSG_COUNT"]["received"] >=2]
    slice = threads_with_gte_2_replies["MSG_COUNT"]["received"]
    ax=slice.hist(bins=20)
    matplotlib.pyplot.title("Aggregate messages per thread (threads with >=2 messages)")
    ax.set_xlabel('# Messages received per thread')
    ax.set_ylabel('# threads')
    fig = ax.get_figure()
    fig.savefig('aggregate_messages_received_per_thread.jpg')
    matplotlib.pyplot.close()

def graph_all_received_messages_by_thread_gte_2(agg_by_thread):
    threads_with_gte_2_replies = agg_by_thread[agg_by_thread["MSG_COUNT"]["received"] >=2]
    slice = threads_with_gte_2_replies["MSG_COUNT"]["received"]
    sorted = slice.sort_values(ascending=True)
    sorted = sorted.reset_index()
    ax=sorted.plot.bar()
    matplotlib.pyplot.title("Messages per thread (threads with >=2 messages)")
    ax.set_xlabel('thread')
    ax.set_ylabel('# messages')
    fig = ax.get_figure()
    fig.savefig('messages_received_per_thread_n_gte_2.jpg')
    matplotlib.pyplot.close()
    
def graph_active_threads_per_month(df):
    f=df
    # convert date string to date object, and truncate to month-level date
    f['YEAR-MONTH'] = pd.to_datetime(df["DATE_UTC"])
    logging.debug(f)
    f['YEAR-MONTH'] = f['YEAR-MONTH'].apply(lambda date_in:  datetime.date(date_in.year,date_in.month,1))
    logging.debug(f)
    logging.debug("^ YEAR-MONTH raw")

    # Narrow to only the columns we care about for aggregation
    before_pivot = f[["THREAD_ID", "YEAR-MONTH", "MSG_COUNT"]]
    grouped = before_pivot.groupby(['YEAR-MONTH', 'THREAD_ID'])
    grouped_sum = grouped.sum()
    grouped_sum = grouped_sum[grouped_sum['MSG_COUNT']>2]
    grouped_sum = grouped_sum.groupby('YEAR-MONTH').count()
    grouped_sum = grouped_sum.rename(columns={"MSG_COUNT":"ACTIVE_THREADS"})
    logging.debug(grouped_sum)
    logging.debug("^ grouped_sum YEAR-MONTH")

    ax=grouped_sum.plot()
    matplotlib.pyplot.title("Active Threads per month (>2 messages)")
    fig = ax.get_figure()
    fig.savefig('active_threads_by_month.jpg')
    matplotlib.pyplot.close()

def graph_words_sent_per_month(df):
    f=df
    # convert date string to date object, and truncate to month-level date
    f['YEAR-MONTH'] = pd.to_datetime(df["DATE_UTC"])
    f['YEAR-MONTH'] = f['YEAR-MONTH'].apply(lambda date_in:  datetime.date(date_in.year,date_in.month,1))
    f = f[f["SENT_VS_RECEIVED"]=="sent"]

    # Narrow to only the columns we care about for aggregation
    before_pivot = f[["YEAR-MONTH", "WORD_COUNT"]]
    grouped = before_pivot.groupby(['YEAR-MONTH'])
    grouped_sum = grouped.sum()
    logging.debug(grouped_sum)
    logging.debug("^ grouped_sum words per month")

    ax=grouped_sum.plot()
    matplotlib.pyplot.title("Words sent per month")
    fig = ax.get_figure()
    fig.savefig('words_sent_per_month.jpg')
    matplotlib.pyplot.close()

def graph_words_sent_per_month_box(df):
    f=df
    # convert date string to date object, and truncate to month-level date
    f['YEAR-MONTH'] = pd.to_datetime(df["DATE_UTC"])
    f['YEAR-MONTH'] = f['YEAR-MONTH'].apply(lambda date_in:  datetime.date(date_in.year,date_in.month,1))
    f = f[f["SENT_VS_RECEIVED"]=="sent"]

    # Narrow to only the columns we care about for aggregation
    before_pivot = f[["YEAR-MONTH", "CHAR_COUNT"]]
    ax=before_pivot.boxplot(column='CHAR_COUNT',by='YEAR-MONTH')
    plt.xticks(rotation=45)
    matplotlib.pyplot.title("Characters sent per message by month")
    fig = ax.get_figure()
    fig.savefig('boxplot_chars_per_msg_by_month.jpg')
    matplotlib.pyplot.close()

def print_summary_stats(summary_stats):
    print("****************************************************")
    print("** THREAD SUMMARY")
    print("****************************************************")
    print('   {0: <35} = {1:4,d}'.format("Total Threads", summary_stats['total_threads']))
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with no replies",
        summary_stats['threads_with_no_replies'],
        summary_stats['threads_with_no_replies']*100/summary_stats['total_threads']))
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with at least 1 reply",
        summary_stats['total_threads']-summary_stats['threads_with_no_replies'],
        (summary_stats['total_threads']-summary_stats['threads_with_no_replies'])*100/summary_stats['total_threads']))
    print(' ')
    print("****************************************************")
    print("** THREAD DETAILED RESPONSE RATES ")
    print("****************************************************")
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with 1-5 replies",
        summary_stats['threads_with_1_to_5_replies'],
        summary_stats['threads_with_1_to_5_replies']*100/summary_stats['total_threads']))
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with 6-20 replies",
        summary_stats['threads_with_6_to_20_replies'], 
        summary_stats['threads_with_6_to_20_replies']*100/summary_stats['total_threads']))
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with 21-50 replies",
        summary_stats['threads_with_21_to_50_replies'], summary_stats['threads_with_21_to_50_replies']*100/summary_stats['total_threads']))
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with >50 replies",
        summary_stats['threads_with_gte_51_replies'], 
        summary_stats['threads_with_gte_51_replies']*100/summary_stats['total_threads']))
    print(' ')
    print("****************************************************")
    print("** THREAD MISC STATS ")
    print("****************************************************")
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads I didn't respond to",
        summary_stats['threads_i_ignored'],
        summary_stats['threads_i_ignored']*100/summary_stats['total_threads']))
    print('   {0: <35} = {1:4,d} ({2:2.0f}%)'.format("Threads with a now-deleted partner",
        summary_stats['threads_with_deleted_other_user'],
        summary_stats['threads_with_deleted_other_user']*100/summary_stats['total_threads']))
    print(' ')
    print("****************************************************")
    print("** MESSAGE STATS ")
    print("****************************************************")
    print('   {0: <35} = {1:10,.0f}'.format("Total Messages Sent", 
        summary_stats['total_messages_sent']))
    print('   {0: <35} = {1:10,.0f}'.format("Total Messages Received", 
        summary_stats['total_messages_received']))
    print(' ')
    print('   {0: <35} = {1:10,.0f}'.format("Total Words Sent", 
        summary_stats['total_words_sent']))
    print('   {0: <35} = {1:10,.0f}'.format("Total Words Received", 
        summary_stats['total_words_received']))
    print(' ')
    print('   {0: <35} = {1:10,.0f}'.format("Total Characters Sent", 
        summary_stats['total_chars_sent']))
    print('   {0: <35} = {1:10,.0f}'.format("Total Characters Received", 
        summary_stats['total_chars_received']))
    print(' ')
    print('   {0: <35} = {1:10,.0f}'.format("Avg chars sent per message", 
        summary_stats['total_chars_sent']/summary_stats['total_messages_sent']))
    print('   {0: <35} = {1:10,.0f}'.format("Avg chars received per message", 
        summary_stats['total_chars_received']/summary_stats['total_messages_received']))
    print(' ')

# print all of the stats in summary_stats
# use this when debugging
def print_debug_summary_stats(summary_stats):
    for k,v in summary_stats.items():
        print(f'{k: <35} = {v}')

def parse_input_args():
    if len(sys.argv) != 2:
        print(" ")
        print("Usage: ")
        print("   {0} [input-csv-file]".format(sys.argv[0]))
        print(" ")
        print("e.g.")
        print("   {0} reddit.csv".format(sys.argv[0]))
        exit(1)
    else:
        return sys.argv[1]

if __name__=="__main__":
    logging.basicConfig(level=logging.ERROR)
    input_file = parse_input_args()

    filtered = read_and_filter(input_file)

    agg_by_thread = aggregate_by_thread(filtered, summary_stats=summary_stats)

    find_threads_with_no_replies(agg_by_thread=agg_by_thread, summary_stats=summary_stats)
    find_threads_i_ignored(agg_by_thread=agg_by_thread, summary_stats=summary_stats)
    find_total_msg_sent_received(agg_by_thread=agg_by_thread, summary_stats=summary_stats)
    find_word_counts(filtered, summary_stats=summary_stats)

    graph_received_messages_by_thread(agg_by_thread=agg_by_thread)
    graph_active_threads_per_month(filtered)
    count_deleted_threads(agg_by_thread=agg_by_thread, summary_stats=summary_stats)
    graph_all_received_messages_by_thread_gte_2(agg_by_thread=agg_by_thread)
    graph_words_sent_per_month(filtered)
    graph_words_sent_per_month_box(filtered)
    print_summary_stats(summary_stats)
