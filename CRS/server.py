import hashlib
import psycopg2
import psycopg2.extras
import os
import sys  
from flask import Flask, session, redirect, url_for, escape, request, render_template
reload(sys)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.secret_key= os.urandom(24).encode('hex')

currentUser = ''


def connectToDB():
    connectionString='dbname=crs user=postgres password=maher123 host=localhost'
    print connectionString
    try:
        return psycopg2.connect(connectionString)
    except:
        print ("Can't connect to database")

@app.route('/')
def mainIndex():
    conn=connectToDB()
    cur= conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    return render_template('index.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    print "We are here"
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        return redirect(url_for('mainIndex'))
    if request.method == 'POST':
      username = request.form['username']
      currentUser = username
        
      pw = request.form['password']
      print pw
      query = "select * from administrator WHERE email = '%s' AND password = '%s'" % (username, pw)
      print query
      cur.execute(query)
      r=cur.fetchall()
      if r:
         session['username'] = request.form['username']
         return render_template('index.html')
         #return redirect(url_for('mainIndex',user=currentUser,c=ch))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method=='POST':
        session.pop('username', None)
        return redirect(url_for('mainIndex'))
    return redirect(url_for('mainIndex'))



if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)