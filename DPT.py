from flask import Flask, render_template, request, redirect, url_for, abort, session
from app import app, db, models, web_scrape as ws
import schedule
import time
from threading import Thread

@app.route('/')
def home():
    return render_template('index.html')
    #return 'Hello World!'


@app.route('/signup', methods=['POST'])
def signup():
    user = models.User(request.form['username'], request.form['message'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('message', username=user.username))


@app.route('/message')
def message():
    if 'username' not in session:
        return abort(403)
    return render_template('message.html', username=session['username'],
                                           message=session['message'])

def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    schedule.every(10).seconds.do(ws.refresh_token)
    t = Thread(target=run_scheduled_tasks)
    t.start()
    app.run()
