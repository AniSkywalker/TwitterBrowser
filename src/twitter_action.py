# offensivemagnet twitter account
import os
import os.path
import sys
sys.path.append('../../')
from collections import defaultdict
import time
import tweepy
import codecs
import re

from tweepy.error import TweepError
from twitter_browser.AWC_browser.awc_browser import analyze_word_crawler

reply_file = '/root/PycharmProjects/Projects/twitter_browser/reply_file.txt'
alltweets = []


class twitter_api():
    _api = None
    _auth = None

    # arghyaonline
    consumer_key = '99cnAj3A72xzGc44D4vbRjTmz'
    consumer_secret = 'tbXVZ3G2RL8JriHHrZ6Kb1qh5oE0TUFD5iVAKEiuIha4V8BuqG'
    access_token = '137083783-elwiZBwneilwyEZ5aazdTzfsWGQ1ObNhNUJ3oSt5'
    access_token_secret = 'mDpFCA4IZb0bg690pmsHFKqTiSRLQItD3iQo7sLnhgsWy'

    # onlinesarcasm
    # consumer_key = 'Z2nA5ErvUwTqCKfuKsYLSG9dV'
    # consumer_secret = 'YUL8mJrch9tZpMsOxfSuJGzxDep3xhvNWFroW7BOEP7qZwp6Ts'
    # access_token = '2807844465-EAirY93y3PL6JvcIZOhK7hf3zCgpI836YdNvtIB'
    # access_token_secret = 'PBCdaRWiyJIrwke3DBFnMUYcXuK9AsimW8YidL5ZnJD7B'

    def __init__(self):
        self.__authenticate()

    def __authenticate(self):
        self._auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self._auth.set_access_token(self.access_token, self.access_token_secret)

    def get_user_timeline(self, username):
        return self._api.user_timeline(username, count=100)

    def get_exists_user(self, username):
        try:
            return self._api.lookup_users(screen_names=username)
        except(TweepError):
            return None

    def get_follower_ids(self, id=''):
        try:
            return self._api.followers_ids(id)['ids']
        except(TweepError):
            self.__authenticate()
            return []

    def get_user(self, id=''):
        return self._api.get_user(id)

    def get_status_details(self, id):
        return self._api.get_status(id)

    def get_friends_id(self, id):
        return self._api.friends_ids(id)['ids']

    def get_status_text(self, id):
        try:
            return self._api.get_status(id)['text']
        except tweepy.TweepError as e:
            if (e.args[0][0]['code'] == '144'):
                return e.message[0]['message']
            return None

    def get_all_tweets(self, screen_name):
        # initialize a list to hold all the tweepy Tweets
        alltweets = []

        # make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = self._api.user_timeline(screen_name=screen_name, count=200)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # save the id of the oldest tweet less one
        oldest = alltweets[-1]['id'] - 1

        # print(alltweets[-1])

        # keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            print("getting tweets before %s" % (oldest))

            # all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = self._api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

            # save most recent tweets
            alltweets.extend(new_tweets)

            # update the id of the oldest tweet less one
            oldest = alltweets[-1]['id'] - 1

            print("...%s tweets downloaded so far" % (len(alltweets)))

        # transform the tweepy tweets into a 2D array that will populate the csv

        outtweets = [[tweet['id_str'], tweet['favorite_count'], tweet['retweet_count'],
                      convert_one_line(tweet['text']).encode("utf-8")] for tweet in alltweets]

        # write the csv
        with open('/root/PycharmProjects/Projects/twitter_browser/crawl/' + '%s_tweets.csv' % screen_name, 'w') as f:
            for outtweet in outtweets:
                f.write(str(outtweet[0]) + '\t' + str(outtweet[1]) + '\t' + str(outtweet[2]) + '\t' + str(
                    outtweet[3].strip()) + '\n')

        pass

    def get_all_liked_shared_tweets(self, screen_name):
        # initialize a list to hold all the tweepy Tweets
        # alltweets = []

        # make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = self._api.user_timeline(screen_name=screen_name, count=200)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # save the id of the oldest tweet less one
        oldest = alltweets[-1]['id'] - 1

        # print(alltweets[-1])

        # keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            print("getting tweets before %s" % (oldest))

            # all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = self._api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

            # save most recent tweets
            alltweets.extend(new_tweets)

            # update the id of the oldest tweet less one
            oldest = alltweets[-1]['id'] - 1

            print("...%s tweets downloaded so far" % (len(alltweets)))

        # transform the tweepy tweets into a 2D array that will populate the csv

        outtweets = []
        for tweet in alltweets:
            if (tweet['favorite_count'] > 0 or tweet['retweet_count'] > 0):
                try:
                    outtweets.append(
                        [tweet['id_str'], tweet['favorite_count'], tweet['retweet_count'], tweet['quoted_status_id'],
                         convert_one_line(tweet['text'])])
                except:
                    pass

        # print(len(outtweets))
        # write the csv

        list_of_tweets = defaultdict()

        with open('/root/PycharmProjects/Projects/twitter_browser/crawl/' + '%s_tweets.csv' % screen_name, 'r') as f:
            for line in f.readlines():
                id, fav_count, rt_count, quoted = line.split('\t')
                list_of_tweets[quoted] = [id, fav_count, rt_count]

        print(len(list_of_tweets.keys()))
        for outtweet in outtweets:
            try:
                tweet = self.get_status_details(id=outtweet[3])
                print(tweet['text'])
                list_of_tweets[convert_one_line(tweet['text'].strip())] = [outtweet[0], outtweet[1], outtweet[2]]
                time.sleep(8)
            except:
                pass

        with open('/root/PycharmProjects/Projects/twitter_browser/crawl/' + '%s_tweets.csv' % screen_name, 'w') as f:
            for key, value in list_of_tweets.items():
                f.write(str(value[0]) + '\t' + str(value[1]) + '\t' + str(value[2]) + '\t' + key + '\n')

                #

    def search_query(self, query):
        return self._api.search(q=query, count=200)

    def get_all_search_queries(self, query, count=100):
        # initialize a list to hold all the tweepy Tweets
        alltweets = []

        # make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = self._api.search(q=query, count=count, lang='en', result_type='mixed')

        # save most recent tweets
        alltweets.extend(new_tweets['statuses'])

        print('len', len(new_tweets['statuses']))

        # save the id of the oldest tweet less one
        oldest = alltweets[-1]['id'] - 1

        # keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets['statuses']) > 0:
            print("getting tweets before %s" % (oldest))

            # all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = self._api.search(q=query, count=count, max_id=oldest, lang='en', result_type='mixed')

            print(len(new_tweets['statuses']))

            # save most recent tweets
            alltweets.extend(new_tweets['statuses'])

            # update the id of the oldest tweet less one
            oldest = alltweets[-1]['id'] - 1

            print("...%s tweets downloaded so far" % (len(alltweets)))

        return alltweets

    def crawl_by_file_with_reply(self, input_file, output_file=None):
        parsed_tweets = set()
        with codecs.open(output_file, 'a+', 'utf-8') as f:
            f.seek(0)
            parsed_tweets.update([line.split('\t')[0] for line in f.readlines()])

        with codecs.open(input_file, 'r', 'utf-8') as f:
            with codecs.open(output_file, 'a', 'utf-8') as fw:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    print(i, line)

                    token = line.strip().split('\t')
                    id = token[0]
                    tag = '\t'.join(token[1:])
                    if (not parsed_tweets.__contains__(id)):
                        try:
                            status = self.get_status_details(id)
                            if (status != None):
                                target_status = status['text']
                                context_status = 'NA'
                                if (status['in_reply_to_status_id'] != None):
                                    context_status = ta.get_status_text(status['in_reply_to_status_id'])
                                    print(context_status)
                                    time.sleep(5)
                                fw.write(str(id) + '\t' + tag + '\t' + convert_one_line(target_status.strip())
                                         + '\t' + convert_one_line(context_status.strip()) + '\n')
                                # else:
                                #     fw.write(tag+'\t'+str(id)+'\t'+'not found'+'\n')
                        except:
                            pass
                        time.sleep(5)

    def crawl_by_file(self, input_file, output_file=None):
        parsed_tweets = set()
        print(output_file)

        # loading the parsed tweet ids
        if (os.path.exists(output_file)):
            with open(output_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parsed_tweets.add(line.strip().split('\t')[0])

        # reading the input file
        with open(input_file, 'r') as f:
            lines = f.readlines()

            for line in lines:
                token = line.strip().split('\t')

                if (token[0] not in parsed_tweets):
                    id = token[0]
                    label = token[1]
                    try:
                        fw = open(output_file, 'a')
                        status = self.get_status_details(id)
                        text = convert_one_line(status['text'])
                        context_id = 'NA'
                        if (text.startswith('@')):
                            context_id = str(status.in_reply_to_status_id_str)
                        fw.write(
                            str(id) + '\t' + label + '\t' + str(text) + '\t' + 'NA' + '\t' + context_id + '\t' + str(
                                status['user']['id']) + '\n')
                        fw.close()


                    except:
                        print(token[0] + ' not available')

                    time.sleep(5)


def convert_one_line(text):
    token = re.split(' |\n|\r', text)
    return ' '.join([t.strip() for t in token])


class SarcasmStreamListener(tweepy.StreamListener):
    awc = analyze_word_crawler()

    def __init__(self,ta):
        self.ta = ta

    def criteria_check(self, text, min_words=10, min_hashtags=0):
        if (text.startswith('RT')):
            return False

        tokens = text.split(' ')

        profile = 0
        hash_tag = 0
        links = 0
        words = 0

        for token in tokens:
            if (token.startswith('@')):
                profile = profile + 1
                continue
            if (token.startswith('#')):
                hash_tag = hash_tag + 1
                continue
            if (token.startswith('http')):
                links = links + 1
                continue

            words = words + 1

        if (words >= min_words and hash_tag >= min_hashtags):
            return True

        return False

    def on_status(self, status):
        text = status.text
        if (status.truncated):
            text = status.extended_tweet['full_text']

        if (text.startswith('@')):
            text = convert_one_line(text)
            if (self.criteria_check(text, 10, 1)):
                print(text)
                fw = open('../resource/crawl/sarcasm_v2.txt', 'a')
                self.awc.crawl_by_twitter_handle(status.user.screen_name)

                context = self.ta.get_status_text(status.in_reply_to_status_id_str)

                if(context!=None):
                    fw.write(
                        'TrainSen' + '\t' + '1' + '\t' + text + '\t' + self.awc.get_dimensions_as_string() + '\t' + convert_one_line(context) + '\t' + str(status.user.id) + '\n')
                else:
                    fw.write(
                        'TrainSen' + '\t' + '1' + '\t' + text + '\t' + self.awc.get_dimensions_as_string() + '\t' + str(
                            status.in_reply_to_status_id_str) + '\t' + str(status.user.id) + '\n')

                fw.close()
                time.sleep(2)

    def on_error(self, status_code):
        print(status_code)
        return True

class AnyStreamListener(tweepy.StreamListener):
    awc = analyze_word_crawler()

    def criteria_check(self, text, min_words=10, min_hashtags=0):
        if(text.startswith('RT')):
            return False

        tokens = text.split(' ')

        profile = 0
        hash_tag = 0
        links = 0
        words = 0

        for token in tokens:
            if (token.startswith('@')):
                profile = profile + 1
                continue
            if (token.startswith('#')):
                hash_tag = hash_tag + 1
                continue
            if (token.startswith('http')):
                links = links + 1
                continue

            words = words + 1

        if (words >= min_words and hash_tag >= min_hashtags):
            return True

        return False

    def on_status(self, status):
        text = status.text
        if (status.truncated):
            text = status.extended_tweet['full_text']

        # if (text.startswith('@')):
        text = convert_one_line(text)
        if (self.criteria_check(text, 10, 1)):

            try:
                # self.awc.crawl_by_twitter_handle(status.user.screen_name)
                print(text)
                fw = open('../resource/crawl/other1.txt', 'a')
                fw.write(
                    'TrainSen' + '\t' + '-1' + '\t' + text + '\n')
                # fw.write(
                #     'TrainSen' + '\t' + '-1' + '\t' + text + '\t' + self.awc.get_dimensions_as_string() + '\t' + str(
                #         status.in_reply_to_status_id_str) + '\t' + str(status.user.id) + '\n')
                fw.close()
            except:
                pass
            # time.sleep(5)

    def on_error(self, status_code):
        print(status_code)
        return True


class CustomStreamListener(tweepy.StreamListener):
    filters = []

    def read_filters(self, filename):
        f = open(filename, 'r')
        lines = f.readlines()
        self.filters = [line.strip().split('\t')[0] for line in lines]
        f.close()

    def on_status(self, status):
        text = convert_one_line(status.text)
        for f in self.filters:
            m = re.search(' as ' + f + ' as (.+?)$', text)
            if (m):
                fw = open('../resource/crawl/simile1.txt', 'a')
                fw.write(text.strip() + '\n')
                fw.close()
                print(text)
                break

    def on_error(self, status_code):
        print(status_code)
        return True


def get_relies(res):
    print(len(res))

    tweets = defaultdict(int)

    with open(reply_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            token = line.strip().split('\t')
            tweets[token[1] + '\t' + token[2] + '\t' + token[3]] = token[0]

    print(len(tweets.keys()))

    with open(reply_file, 'w') as fw:
        for r in res:
            try:
                print(r['text'])
                tweet = ta.get_status_details(r['in_reply_to_status_id'])
                reply_text = convert_one_line(tweet['text'])

                favorite_count = tweet['favorite_count']

                tweet = ta.get_status_details(id=tweet['quoted_status_id_str'])

                tweets[convert_one_line(tweet['text']) + '\t' + reply_text + '\t' + convert_one_line(
                    r['text'])] = favorite_count
                time.sleep(6)
            except:
                pass

        for key, value in tweets.items():
            fw.write(str(value) + '\t' + key + '\n')


if __name__ == '__main__':
    basepath = os.getcwd()[:os.getcwd().rfind('/')]
    ta = twitter_api()

    # twitter api
    ta._api = tweepy.API(ta._auth, parser=tweepy.parsers.JSONParser())
    print(ta._api)

    # ta.crawl_by_file(basepath + '/resource/irony-sarcasm-ling2016/regular.csv',
    #                  basepath + '/resource/irony-sarcasm-ling2016/regular_text.tsv')



    # fw = open('../resource/crawl/irony.txt', 'a')
    # tweets = ta.get_all_search_queries('#irony')
    # for tweet in tweets:
    #     # print(tweet)
    #     if(tweet['truncated']!=True):
    #         text = convert_one_line(tweet['text'])
    #         if(criteria_check(text,min_words=5)):
    #             fw.write('TrainSen' + '\t' + '1' + '\t' + text +'\n')
    # fw.close()


    # open word list
    # wordlist = ['a']

    # with open(basepath+'/resource/temp/xaa','r') as f:
    #     lines = f.readlines()
    #     wordlist.extend([line.strip().split('\t')[0] for line in lines])


    # twitter stream api
    # while (True):
    # try:
    #     aStreamListener = AnyStreamListener()
    #     stream = tweepy.Stream(auth=ta._auth, parser=tweepy.parsers.JSONParser(), listener=aStreamListener)
    #     stream.filter(track=wordlist, languages=['en'])
    # except:
    #     raise




    # twitter stream api
    while (True):
        try:
            sStreamListener = SarcasmStreamListener(ta)
            stream = tweepy.Stream(auth=ta._auth, parser=tweepy.parsers.JSONParser(), listener=sStreamListener)
            stream.filter(track=['#sarcasm','#sarcastic'], languages=['en'])
        except:
            pass

    # print(ta._api)
    # ta._api = tweepy.API(ta._auth)

    # ta.crawl_by_file(basepath + '/resource/data/'+'NAACL_SRW_2016.tsv',
    #                          basepath + '/resource/crawl_text/'+'NAACL_SRW_2016_text.tsv')
    # ta.crawl_by_file_with_reply(basepath + '/resource/data/'+'NAACL_SRW_2016.tsv',
    #                          basepath + '/resource/crawl_text_reply/'+'NAACL_SRW_2016_text_reply.tsv')


    # ta.get_all_tweets('onlinesarcasm')
    # ta.get_all_liked_shared_tweets('onlinesarcasm')

    # search_results = ta.get_all_search_queries('"as useful as"',count=100)
    #
    # fw = open('../resource/crawl/useful_simile.txt','a')
    # for s in search_results:
    #     fw.write(convert_one_line(s['text']).strip()+'\n')
    # fw.close()





    # get_relies(ta.get_all_search_queries('@onlinesarcasm'))



    # crawl_by_file()


    # list=set()
    #
    #
    # list.update(str(x) for x in ta.get_friends_id(id='onlinesarcasm'))
    # print(len(list),list)


    # print(t['id_str'])
    # twitter_account_list = []
    # twitter_account_list.append(ta.api.me()['id'])
    #
    # i=0

    # while(i<len(twitter_account_list)):
    #     time.sleep(1)
    #     id = twitter_account_list[i]
    #     i+=1
    #     screen_name = ta.get_user(id)['screen_name']
    #     followers = ta.get_follower_ids(id)
    #     print(screen_name,len(followers))
    #     if(len(followers)>100):
    #         print(screen_name, len(followers))
    #     for fid in followers:
    #         if(not twitter_account_list.__contains__(fid)):
    #             twitter_account_list.append(fid)