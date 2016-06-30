from flask import Flask, render_template, json, request, g, Markup, session, redirect
from werkzeug import generate_password_hash, check_password_hash
import time
from datetime import date
import sys
import os.path

import sqlite3

DATABASE = 'data/database.db'
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.with_')

def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
        in the instance directory.

        If the file does not exist, print instructions
        to create it from a shell with a random key,
        then exit.

        """
    filename = os.path.join(app.instance_path, filename)
    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print('Error: No secret key. Create it with:')
        if not os.path.isdir(os.path.dirname(filename)):
            print('mkdir -p {}'.format(os.path.dirname(filename)))
        print('head -c 24 /dev/urandom > {}'.format(filename))
        sys.exit(1)

install_secret_key(app, "secret_key")

def init_db():
    with app.app_context():
        db = get_db();
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._daabase = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

@app.route('/showAddOffer')
def showAddOffer():
    return render_template('addOffer.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error="Unauthorized access")

@app.route('/signUp',methods=['POST'])
def signUp():
        # read the posted values from the UI
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            conn = get_db()
            cur = conn.cursor()
            # TODO: check if already exists
            _hashed_password = generate_password_hash(_password)
            cur.execute('''INSERT INTO user 
                    (user_name, user_email, user_password)
                    VALUES (?,?,?)''', 
                    (_name, _email, _hashed_password))
            conn.commit()
            # TODO: not needed
            return json.dumps({'html':'<span>All fields good !!</span>'})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        conn = get_db()
        cur = conn.cursor()

        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        cur.execute('SELECT * FROM user WHERE user_email = (?)', (_email,))
        data = cur.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0]["user_password"]),_password):
                session['user'] = data[0]["user_email"]
                return redirect('/userHome')
            else:
                return render_template('error.html', error="Wrong Email or Password")
        else:
            return render_template('error.html', error="Wrong Email or Password")
    except Exception as e:
        return render_template('error.html', error = str(e))
    finally:
        cur.close()
        conn.close()

@app.route('/addOffer',methods=['POST'])
def addOffer():
    conn = get_db()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _company = request.form['inputCompany']
            _size = request.form['inputSize']
            _color = request.form['inputColor']
            _description = request.form['inputDescription']

            _company2 = request.form['inputCompany2']
            _size2 = request.form['inputSize2']
            _color2 = request.form['inputColor2']
            _description2 = request.form['inputDescription2']

            _user = session.get('user')

            cursor.execute('''
            INSERT INTO shirt
            (shirt_company, shirt_size, shirt_color, shirt_description)
            VALUES (?, ?, ?, ?)
            ''', (_company, _size, _color, _description))
            data = cursor.fetchall()

            if len(data) is not 0:
                return render_template('error.html', error= 'An Error occured!')
            conn.commit()
            _shirt = cursor.lastrowid

            cursor.execute('''
            INSERT INTO shirt
            (shirt_company, shirt_size, shirt_color, shirt_description)
            VALUES (?, ?, ?, ?)
            ''', (_company2, _size2, _color2, _description2))
            data = cursor.fetchall()
            if len(data) is not 0:
                return render_template('error.html', error= 'An Error occured!')
            conn.commit()
            _shirt2 = cursor.lastrowid

            cursor.execute('''
            INSERT INTO offer
            (offer_have, offer_want, offer_user, status)
            VALUES (?, ?, ?, ?)
            ''', (_shirt, _shirt2, _user, 0))
            data = cursor.fetchall()
            if len(data) is not 0:
                return render_template('error.html', error= 'An Error occured!')
            conn.commit()

            return redirect('userHome')
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/getOffer')
def getOffer():
    try:
        if session.get('user'):
            _user = session.get('user')

            conn = get_db()
            cursor = conn.cursor()
            #cursor.execute('''SELECT * FROM offer
            #WHERE offer_user = (?)
            #''', (_user,))

            cursor.execute('''SELECT * FROM offer
            ''')

            offers = cursor.fetchall()

            offers_dict = []
            for offer in offers:
                cursor.execute('''SELECT * FROM shirt
                WHERE shirt_id = (?)
                ''', (offer['offer_have'],))
                shirts = cursor.fetchall()
                _have = dict(shirts[0])

                for key, value in _have.items():
                    if not value:
                        _have[key] = "(any)"


                cursor.execute('''SELECT * FROM shirt
                WHERE shirt_id = (?)
                ''', (offer['offer_want'],))
                shirts = cursor.fetchall()
                _want = dict(shirts[0])

                for key, value in _want.items():
                    if not value:
                        _want[key] = "(any)"

                offer_dict = {
                        'Id': offer['offer_id'],
                        'Have': _have,
                        'Want': _want,
                        'User': offer['offer_user'],
                        'Status': offer['status']
                        }
                offers_dict.append(offer_dict)

            return json.dumps(offers_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    finally:
        pass

@app.route('/getOfferById',methods=['POST'])
def getOfferById():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM offer
            WHERE wish_id = ? AND
            wish_user_id = ?''', (_id, _user))
            result = cursor.fetchall()

            wish = []
            wish.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2]})
            return json.dumps(wish)
        else:
            return render_template('error.html', error="Unauthorized access")
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/updateOffer', methods=['POST'])
def updateOffer():
    conn = get_db()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _user = session.get('user')
            _title = request.form['title']
            _description = request.form['description']
            _wish_id = request.form['id']

            cursor.execute('''
            UPDATE tbl_wish
            SET wish_title = ?, wish_description = ?
            WHERE wish_id = ? and wish_user_id = ?
            ''', (_title, _description, _wish_id, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'ERROR'})
        else:
            return render_template('error.html', error="Unauthorized access")
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/deleteOffer', methods=['DELETE'])
def deleteOffer():
    conn = get_db()
    cursor = conn.cursor()
    try:
        if session.get('user'):
            _user = session.get('user')
            _wish_id = request.form['id']

            cursor.execute('''
            DELETE FROM tbl_wish
            WHERE wish_id = ? and wish_user_id = ?
            ''', (_wish_id, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'ERROR'})
        else:
            return render_template('error.html', error="Unauthorized access")
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

# run with python3
if __name__ == "__main__":
    app.run()


