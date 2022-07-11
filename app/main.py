#! /usr/bin/python3
# -*- coding: utf-8 -*-

###########################################################################
# Copyright 2019 (C) Hui Lan <hui.lan@cantab.net>
# Written permission must be obtained from the author for commercial uses.
###########################################################################

from WordFreq import WordFreq
from wordfreqCMD import youdao_link, sort_in_descending_order
from UseSqlite import InsertQuery, RecordQuery
import pickle_idea, pickle_idea2
import os
import random, glob
from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, session, abort, flash, get_flashed_messages
from difficulty import get_difficulty_level, text_difficulty_level, user_difficulty_level
import tools

app = Flask(__name__)
app.secret_key = 'lunch.time!'


path_prefix = '/var/www/wordfreq/wordfreq/'
path_prefix = './'  # comment this line in deployment

@app.route("/<username>/reset", methods=['GET', 'POST'])
def user_reset(username):
    if request.method == 'GET':
        session['articleID'] = None
        return redirect(url_for('userpage', username=username))
    else:
        return 'Under construction'


@app.route("/mark", methods=['GET', 'POST'])
def mark_word():
    if request.method == 'POST':
        d = tools.load_freq_history(path_prefix + 'static/frequency/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, 1))
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency/frequency.p')
        return redirect(url_for('mainpage'))
    else:
        return 'Under construction'


@app.route("/", methods=['GET', 'POST'])
def mainpage():

    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        lst = f.get_freq()
        page = '<form method="post" action="/mark">\n'
        count = 1
        for x in lst:
            page += '<p><font color="grey">%d</font>: <a href="%s">%s</a> (%d)  <input type="checkbox" name="marked" value="%s"></p>\n' % (
                count, youdao_link(x[0]), x[0], x[1], x[0])
            count += 1
        page += ' <input type="submit" value="确定并返回"/>\n'
        page += '</form>\n'
        # save history
        d = tools.load_freq_history(path_prefix + 'static/frequency/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency/frequency.p')

        return page
    elif request.method == 'GET':  # when we load a html page
        page = ''
        ads = tools.get_random_ads()
        username = session.get('username')

        amount = {
                'article_amount': tools.total_number_of_essays(),
                'username': username,
                'ads': ads,
        }

        return render_template('mainpage.html', amount = amount)




@app.route("/<username>/mark", methods=['GET', 'POST'])
def user_mark_word(username):
    username = session[username]
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    if request.method == 'POST':
        d = tools.load_freq_history(user_freq_record)
        lst_history = pickle_idea2.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, [tools.get_time()]))
        d = pickle_idea2.merge_frequency(lst, lst_history)
        pickle_idea2.save_frequency_to_pickle(d, user_freq_record)
        return redirect(url_for('userpage', username=username))
    else:
        return 'Under construction'


@app.route("/<username>/<word>/unfamiliar", methods=['GET', 'POST'])
def unfamiliar(username, word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea.unfamiliar(user_freq_record, word)
    session['thisWord'] = word  # 1. put a word into session
    session['time'] = 1
    return redirect(url_for('userpage', username=username))


@app.route("/<username>/<word>/familiar", methods=['GET', 'POST'])
def familiar(username, word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea.familiar(user_freq_record, word)
    session['thisWord'] = word  # 1. put a word into session
    session['time'] = 1
    return redirect(url_for('userpage', username=username))


@app.route("/<username>/<word>/del", methods=['GET', 'POST'])
def deleteword(username, word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea2.deleteRecord(user_freq_record, word)
    flash(f'<strong>{word}</strong> is no longer in your word list.')
    return redirect(url_for('userpage', username=username))

@app.route("/<username>/open", methods=['GET', 'POST'])
def openit(username):
    session['flag'] = 1
    return redirect(url_for('userpage', username=username))

@app.route("/<username>/close", methods=['GET', 'POST'])
def closeit(username):
    session['flag'] = 0
    return redirect(url_for('userpage', username=username))


@app.route("/<username>", methods=['GET', 'POST'])
def userpage(username):
    if not session.get('logged_in'):
        return '<p>请先<a href="/login">登录</a>。</p>'

    user_expiry_date = session.get('expiry_date')
    if datetime.now().strftime('%Y%m%d') > user_expiry_date:
        return '<p>账号 %s 过期。</p><p>为了提高服务质量，English Pal 收取会员费用， 每天0元。</p> <p>请决定你要试用的时间长度，扫描下面支付宝二维码支付。 支付时请注明<i>English Pal Membership Fee</i>。 我们会于12小时内激活账号。</p><p><img src="static/donate-the-author-hidden.jpg" width="120px" alt="支付宝二维码" /></p><p>如果有问题，请加开发者微信 torontohui。</p> <p><a href="/logout">登出</a></p>' % (
            username)

    username = session.get('username')

    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)

    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        cc={
            'f':WordFreq(content),
            'lst':f.get_freq(),
            'username':username,
        }
        return render_template('userpage.html',cc=cc)



    elif request.method == 'GET':  # when we load a html page
        d = tools.load_freq_history(user_freq_record)
        page = ''
        if len(d) > 0:
            page += '<p><b>我的生词簿</b></p>'
            lst = pickle_idea2.dict2lst(d)
            lst2 = []
            for t in lst:
                lst2.append((t[0], len(t[1])))
            for x in sort_in_descending_order(lst2):
                word = x[0]
                freq = x[1]
                if session.get('thisWord') == x[0] and session.get('time') == 1:
                    page += '<a name="aaa"></a>'  # 3. anchor
                    session['time'] = 0  # discard anchor
                if isinstance(d[word], list):  # d[word] is a list of dates
                    if freq > 1:
                        page += '<p class="new-word"> <a class="btn btn-light" href="%s" role="button">%s</a>(<a title="%s">%d</a>) <a class="btn btn-success" href="%s/%s/familiar" role="button">熟悉</a> <a class="btn btn-warning" href="%s/%s/unfamiliar" role="button">不熟悉</a>  <a class="btn btn-danger" href="%s/%s/del" role="button">删除</a> </p>\n' % (
                            youdao_link(word), word, '; '.join(d[word]), freq, username, word, username, word, username,
                            word)
                    else:
                        page += '<p class="new-word"> <a class="btn btn-light" href="%s" role="button">%s</a>(<a title="%s">%d</a>) <a class="btn btn-success" href="%s/%s/familiar" role="button">熟悉</a> <a class="btn btn-warning" href="%s/%s/unfamiliar" role="button">不熟悉</a>  <a class="btn btn-danger" href="%s/%s/del" role="button">删除</a> </p>\n' % (
                            youdao_link(word), word, '; '.join(d[word]), freq, username, word, username, word, username,
                            word)
                elif isinstance(d[word], int):  # d[word] is a frequency. to migrate from old format.
                    page += '<a href="%s">%s</a>%d\n' % (youdao_link(word), word, freq)

        ee = {
            # 'msg':get_flashed_messages_if_any(),
            'article': (tools.highlight(tools.get_today_article(user_freq_record, session['articleID']), pickle_idea2.dict2lst(
                tools.load_freq_history(user_freq_record)))),
            'username': username,
            'page': page,
        }

        return render_template('personnalpage.html', ee=ee)





### Sign-up, login, logout ###
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        available = tools.check_username_availability(username)
        if not available:
            flash('用户名 %s 已经被注册。' % (username))
            return render_template('signup.html')
        elif len(password.strip()) < 4:
            return '密码过于简单。'
        else:
            tools.add_user(username, password)
            verified = tools.verify_user(username, password)
            if verified:
                session['logged_in'] = True
                session[username] = username
                session['username'] = username
                session['expiry_date'] = tools.get_expiry_date(username)
                session['articleID'] = None
                return '<p>恭喜，你已成功注册， 你的用户名是 <a href="%s">%s</a>。</p>\
                <p><a href="/%s">开始使用</a> <a href="/">返回首页</a><p/>' % (username, username, username)
            else:
                return '用户名密码验证失败。'


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return '你已登录 <a href="/%s">%s</a>。 登出点击<a href="/logout">这里</a>。' % (
                session['username'], session['username'])
    elif request.method == 'POST':
        # check database and verify user
        username = request.form['username']
        password = request.form['password']
        verified = tools.verify_user(username, password)
        if verified:
            session['logged_in'] = True
            session[username] = username
            session['username'] = username
            user_expiry_date = tools.get_expiry_date(username)
            session['expiry_date'] = user_expiry_date
            session['articleID'] = None
            return redirect(url_for('userpage', username=username))
        else:
            return '无法通过验证。'


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('mainpage'))



if __name__ == '__main__':
    # app.secret_key = os.urandom(16)
    # app.run(debug=False, port='6000')
    app.run(debug=True)
    # app.run(debug=True, port='6000')
    # app.run(host='0.0.0.0', debug=True, port='6000')
