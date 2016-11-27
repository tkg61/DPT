from flask import Flask, render_template, request, redirect, url_for, abort, session
from app import app, db, models, web_scrape as ws, cruise_methods as cm
import schedule
import time

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
    schedule.every(120).seconds.do(ws.refresh_token)
    #schedule.every(2).seconds.do(job)
    schedule.run_continuously()


if __name__ == '__main__':
    run_scheduled_tasks()

    # t = Thread(target=run_scheduled_tasks)
    # t.start()
    cm.update_all_cruises()
    app.run(use_reloader=False, debug=True)
