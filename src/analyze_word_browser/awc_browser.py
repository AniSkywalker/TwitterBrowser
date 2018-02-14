from collections import defaultdict
import datetime
import re
from bs4 import BeautifulSoup
import urllib.request
import os

from sklearn.externals.six.moves import urllib


class analyze_word_crawler:
    basepath = os.getcwd()[:os.getcwd().rfind('/')]
    basepath = basepath + '/../Data/resource/AnalyzeCrawler/'
    data = None
    twitter_handle = None

    def __init__(self):
        self.data = defaultdict()
        if (not os.path.exists(self.basepath + 'crawled/')):
            os.makedirs(self.basepath + 'crawled/')

    def crawl_by_twitter_handle(self, twitter_handle):
        # fw = open(basepath+'crawled/' + twitter_handle +'-'+ str(datetime.datetime.now())+ '.txt', 'w')
        self.twitter_handle = twitter_handle

        link = "http://analyzewords.com/index.php?handle=" + twitter_handle
        f = urllib.request.urlopen(link)

        html = BeautifulSoup(f.read(),'lxml')
        desc = html.find('h3').get_text()
        desc = desc.replace('Analysis of tweets from ' + twitter_handle + '(', '')
        desc = desc[:desc.find('most recent words')]

        self.data['now'] = desc

        # fw.write(desc+'\n')

        t3_tables = html.find_all('table')

        t3_rows = t3_tables[2].find_all('tr')
        for row in t3_rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols = [ele for ele in cols if ele]
            if (len(cols) == 2):
                if (cols[0].startswith('Upbeat ')):
                    self.data['Upbeat'] = cols[1]
                    # fw.write('Upbeat' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Worried ')):
                    self.data['Worried'] = cols[1]
                    # fw.write('Worried' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Angry ')):
                    self.data['Angry'] = cols[1]
                    # fw.write('Angry' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Depressed ')):
                    self.data['Depressed'] = cols[1]
                    # fw.write('Depressed' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Plugged In ')):
                    self.data['Plugged In'] = cols[1]
                    # fw.write('Plugged In' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Personable ')):
                    self.data['Personable'] = cols[1]
                    # fw.write('Personable' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Arrogant/Distant ')):
                    self.data['Arrogant/Distant'] = cols[1]
                    # fw.write('Arrogant/Distant ' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Spacy/Valley girl ')):
                    self.data['Spacy/Valley girl'] = cols[1]
                    # fw.write('Spacy/Valley girl' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Analytic ')):
                    self.data['Analytic'] = cols[1]
                    # fw.write('Analytic' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('Sensory ')):
                    self.data['Sensory'] = cols[1]
                    # fw.write('Sensory' + '\t' + cols[1] + '\n')
                if (cols[0].startswith('In-the-moment ')):
                    self.data['In-the-moment'] = cols[1]
                    # fw.write('In-the-moment' + '\t' + cols[1] + '\n')

        text = html.find('div', attrs={'id': 'textdiv'}).get_text()
        text = ' '.join([line.strip() for line in re.split(' |\n|\r', text)])
        self.data['text'] = text

    def get_dimension(self,dimension):
        if(dimension in self.data):
            return self.data.get(dimension)
        else:
            return None
    def get_dimensions(self):
        return self.data

    def get_dimensions_as_string(self):
        d = []
        for key,value in self.data.items():
            if(key!='now' and key!='text'):
                d.append(str(key.replace(' ','_'))+'@@'+str(value))
        return '|'.join(d)

    def convert_dimensions_as_string(self, dimensions):
        d = []
        for key,value in self.data.items():
            if(key!='now' and key!='text'):
                d.append(str(key.replace(' ','_'))+'@@'+str(value))
        return '|'.join(d)

# if __name__ == '__main__':
#     awc = analyze_word_crawler()
#
#     awc.crawl_by_twitter_handle('realdonaldtrump')
#     print(awc.get_dimensions_as_string())
#
#     for key, value in awc.get_dimensions().items():
#         print(key, value)
