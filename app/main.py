from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import gspread

app = Flask(__name__)

gc = gspread.service_account(filename='credentials.json')

sheet = gc.open_by_key('1FHES6WEgXTEmbQB1Dce6Q7mQNceHIosdKu8UEUHDf2g')

worksheet = sheet.sheet1

class Tweet:
    def __init__(self, message, time, status, row_idx):
        self.message = message
        self.time = time
        self.status = status
        self.row_idx = row_idx

def get_date_time(date_time_str):
    date_time_obj = None
    error_code = None
    try:
        date_time_obj = datetime.strptime(date_time_str, '%d-%m-%Y %H:%M:%S')
    except ValueError as e:
        error_code = f'Error! {e}'

    if date_time_obj is not None:
        now_time_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
        if not date_time_obj>now_time_ist:
            error_code = 'Error! Time must be in the future'
    return date_time_obj, error_code



@app.route("/")
def tweet_list():
    tweet_records = worksheet.get_all_records()
    tweets = []
    for idx, tweet in enumerate(tweet_records, start=2):
        tweet = Tweet(**tweet, row_idx=idx)
        tweets.append(tweet)
        
    n_open_tweets = sum(1 for tweet in tweets if not tweet.status)
    return render_template('index.html', tweets=tweets, n_open_tweets=n_open_tweets)

@app.route("/tweet", methods=['POST'])
def add_tweet():
    message = request.form['message']
    if not message:
        return "Error! No tweet message found"
    time = request.form['time']
    if not time:
        return "Error! No time is given"
    if len(message) > 280:
        return "Error! Tweet message longer than 280 characters"
    
    date_time_obj, error_code = get_date_time(time)
    if error_code is not None:
        return error_code

    tweet = [str(date_time_obj), message, 0]
    worksheet.append_row(tweet)
    return redirect('/')