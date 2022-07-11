from WordFreq import WordFreq
from wordfreqCMD import youdao_link, sort_in_descending_order
from UseSqlite import InsertQuery, RecordQuery
import pickle_idea, pickle_idea2
import os
import random, glob
from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, session, abort, flash, get_flashed_messages
from difficulty import get_difficulty_level, text_difficulty_level, user_difficulty_level

# 生词高亮
def highlight(article, wordlist):
        flag = session.get('flag')
        if flag == 1:
            list1 = []
            for t in wordlist:  #此处的wordlist是从生词库中提取出来的
                list1.append(t[0])  #由于生词库中单词是字典形式的，因此将
            wordlist = sort_in_descending_order(list1)
            len_w = len(wordlist)
            len_a = len(article)
            word = list(wordlist)
            for j in range(len_w):
                for i in range(len_a - len(word[j]), -1, -1):
                    if article[i:i + len(word[j])] == word[j]:
                        article = article[:i] + u"<mark><font color=#FF0000>" + word[j] + u"</font></mark>" + article[i + len(word[j]):]
            return article
        else:
            return article
#旧代码
# path_prefix = '/var/www/wordfreq/wordfreq/'
# path_prefix = './'  # comment this line in deployment
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("englishpal\\")+len("englishpal\\")]
path_prefix_ = os.path.abspath(rootPath + '/app/')
path_prefix = path_prefix_.replace("\\", "/")
path_prefix += '/'

def get_random_image(path):
    img_path = random.choice(glob.glob(os.path.join(path, '*.jpg')))
    return img_path[img_path.rfind('/static'):]


def get_random_ads():
    ads = random.choice(['个性化分析精准提升', '你的专有单词本', '智能捕捉阅读弱点，针对性提高你的阅读水平'])
    return ads + '。 <a href="/signup">试试</a>吧！'


def total_number_of_essays():
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM article")
    rq.do()
    result = rq.get_results()
    return len(result)


def load_freq_history(path):
    d = {}
    if os.path.exists(path):
        d = pickle_idea.load_record(path)
    return d


def verify_user(username, password):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions_with_parameters("SELECT * FROM user WHERE name=? AND password=?", (username, password))
    rq.do_with_parameters()
    result = rq.get_results()
    return result != []


def add_user(username, password):
    start_date = datetime.now().strftime('%Y%m%d')
    expiry_date = '20211230'
    rq = InsertQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("INSERT INTO user Values ('%s', '%s', '%s', '%s')" % (username, password, start_date, expiry_date))
    rq.do()


def check_username_availability(username):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM user WHERE name='%s'" % (username))
    rq.do()
    result = rq.get_results()
    return result == []


def get_expiry_date(username):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT expiry_date FROM user WHERE name='%s'" % (username))
    rq.do()
    result = rq.get_results()
    if len(result) > 0:
        return result[0]['expiry_date']
    else:
        return '20191024'


def within_range(x, y, r):
    return x > y and abs(x - y) <= r


def get_article_title(s):
    return s.split('\n')[0]


def get_article_body(s):
    lst = s.split('\n')
    lst.pop(0)  # remove the first line
    return '\n'.join(lst)


def get_today_article(user_word_list, articleID):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    if articleID == None:
        rq.instructions("SELECT * FROM article")
    else:
        rq.instructions('SELECT * FROM article WHERE article_id=%d' % (articleID))
    rq.do()
    result = rq.get_results()
    random.shuffle(result)

    # Choose article according to reader's level
    d1 = load_freq_history(path_prefix + 'static/frequency/frequency.p')
    d2 = load_freq_history(path_prefix + 'static/words_and_tests.p')
    d3 = get_difficulty_level(d1, d2)

    d = {}
    d_user = load_freq_history(user_word_list)
    user_level = user_difficulty_level(d_user,
                                       d3)  # more consideration as user's behaviour is dynamic. Time factor should be considered.
    random.shuffle(result)  # shuffle list
    d = random.choice(result)
    text_level = text_difficulty_level(d['text'], d3)
    if articleID == None:
        for reading in result:
            text_level = text_difficulty_level(reading['text'], d3)
            factor = random.gauss(0.8,
                                  0.1)  # a number drawn from Gaussian distribution with a mean of 0.8 and a stand deviation of 1
            if within_range(text_level, user_level, (8.0 - user_level) * factor):
                d = reading
                break

    s = '<div class="alert alert-success" role="alert">According to your word list, your level is <span class="badge bg-success">%4.2f</span>  and we have chosen an article with a difficulty level of <span class="badge bg-success">%4.2f</span> for you.</div>' % (
        user_level, text_level)
    s += '<p class="text-muted">Article added on: %s</p>' % (d['date'])
    s += '<div class="p-3 mb-2 bg-light text-dark">'
    article_title = get_article_title(d['text'])
    article_body = get_article_body(d['text'])
    s += '<p class="display-3">%s</p>' % (article_title)
    s += '<p class="lead">%s</p>' % (article_body)
    s += '<p><small class="text-muted">%s</small></p>' % (d['source'])
    s += '<p><b>%s</b></p>' % (get_question_part(d['question']))
    s = s.replace('\n', '<br/>')
    s += '%s' % (get_answer_part(d['question']))
    s += '</div>'
    session['articleID'] = d['article_id']
    return s


def appears_in_test(word, d):
    if not word in d:
        return ''
    else:
        return ','.join(d[word])


def get_time():
    return datetime.now().strftime('%Y%m%d%H%M')  # upper to minutes


def get_question_part(s):
    s = s.strip()
    result = []
    flag = 0
    for line in s.split('\n'):
        line = line.strip()
        if line == 'QUESTION':
            result.append(line)
            flag = 1
        elif line == 'ANSWER':
            flag = 0
        elif flag == 1:
            result.append(line)
    return '\n'.join(result)


def get_answer_part(s):
    s = s.strip()
    result = []
    flag = 0
    for line in s.split('\n'):
        line = line.strip()
        if line == 'ANSWER':
            flag = 1
        elif flag == 1:
            result.append(line)
    # https://css-tricks.com/snippets/javascript/showhide-element/
    js = '''
<script type="text/javascript">

    function toggle_visibility(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
    }
</script>   
    '''
    html_code = js
    html_code += '\n'
    html_code += '<button onclick="toggle_visibility(\'answer\');">ANSWER</button>\n'
    html_code += '<div id="answer" style="display:none;">%s</div>\n' % ('\n'.join(result))
    return html_code


def get_flashed_messages_if_any():
    messages = get_flashed_messages()
    s = ''
    for message in messages:
        s += '<div class="alert alert-warning" role="alert">'
        s += f'Congratulations! {message}'
        s += '</div>'
    return s
