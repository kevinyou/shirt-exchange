from flask import Flask, render_template, json, request, g, Markup
import time
from datetime import date

import sqlite3

DATABASE = 'data/database.db'
app = Flask(__name__)

def get_db():
    print("loooooo")
    db = getattr(g, '_database', None)
    if db is None:
        db = g._daabase = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    print("tearing down")
    db = getattr(g, '_daabase', None)
    if db is not None:
        print("closed")
        db.close()

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/hello")
@app.route("/hello/<name>")
def wowpage(name=None):
    searchword = request.args.get('key', 'default')
    if name:
        name = Markup('<i>{}</i> {}'.format(name, searchword))
    return render_template('wow.html', name=name)

@app.route("/upload", methods=['POST'])
def upload_file():
    f = request.files['the_file']
    return "woot"

@app.route("/~ans/")
def ans():
    day = date.weekday(date.today())
    days = {0: "Mo+nda*y",
            1: "Tu+esda*y",
            2: "We+dnesda*y",
            3: "Thu+rsda*y",
            4: "Fri+da*y",
            5: "Sa+turda*y",
            6: "Su+nda*y"}
    day_of_month = int(date.today().strftime("%d"))
    month = int(date.today().strftime("%m"))
    
    output = days[day]
    vowel = output[output.index('+')-1]
    output = output.replace(vowel+'+', vowel*day_of_month)
    output = output.replace("a"+"*", "a"*month)
    #output += "({} {}'s and {} {}'s)".format(day_of_month, vowel, month, "a")
    return "Hey y'all, welcome to {}! ({} {}'s and {} {}'s)\n".format(output, day_of_month, vowel, month, "a")

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/sellers',methods=['GET','POST'])
def sellers():
    if request.method == 'GET':
        return "GETted"
    else:
        return str(request.get_json())
    cur = get_db().cursor()
    return "hi" 



@app.route('/signUp',methods=['POST'])
def signUp():
        # read the posted values from the UI
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            return json.dumps({'html':'<span>All fields good !!</span>'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

# run with python3
if __name__ == "__main__":
    app.run()


