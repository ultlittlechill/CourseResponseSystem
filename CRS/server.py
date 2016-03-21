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
    connectionString='dbname=crs user=postgres password=root host=localhost'
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
        return redirect(url_for('controlPanel'))
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
                return redirect(url_for('controlPanel'))
         #return redirect(url_for('mainIndex',user=currentUser,c=ch))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
        
    return redirect(url_for('mainIndex'))

@app.route('/controlPanel', methods=['GET', 'POST'])
def controlPanel():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    i=1
    if 'username' in session:
        query = "select * from class " 
        cur.execute(query)
        results = cur.fetchall()
    
        if request.method == 'POST':
            classname = request.form['classname']
            try:
                classnumber = request.form['classnumber']
                cur.execute("""INSERT INTO class
                 VALUES (%s, %s);""",[classnumber,classname] )
      
                conn.commit()
            except:
                
                mess="The class code is already existed!"
                notification="error"
                return  redirect(url_for('controlPanel',mess=mess,notification=notification))
      
            
            query = "select * from class " 
            print query
            cur.execute(query)
            results = cur.fetchall()
            mess="Your calss has been created"
            notification="success"
            return  redirect(url_for('controlPanel',mess=mess,notification=notification))    
    if 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanel.html',results=results)

@app.route('/controlPanelD', methods=['GET', 'POST'])
def delete():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        query = "select * from class " 
        cur.execute(query)
        results = cur.fetchall()
    
        if request.method == 'POST':
            if request.form['submit']=='Delete':
                classname = request.form['classn']
                cur.execute("DELETE FROM class WHERE class_name ilike %s",[classname] )
      
                conn.commit()
                mess="Your calss has been deleted!"
                notification="success"
                query = "select * from class " 
                print query
                cur.execute(query)
                results = cur.fetchall()
                return  redirect(url_for('controlPanel',mess=mess,notification=notification))
            elif request.form['submit']=='Edit':
                 classname = request.form['classn']
                 cur.execute("select * FROM class WHERE class_name ilike %s",[classname] )
                 results = cur.fetchall()
                 for r in results:
                     name=r[1]
                     code=r[0]
                     print name,code
                     
                 return redirect(url_for('edit',code=code,name=name))
                
    if 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanel.html',results=results)



@app.route('/controlPanelE', methods=['GET', 'POST'])
def edit():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        if request.method == 'POST':
            if request.form['submit']=='Save':
                print"Y it is not working",
                classname = request.form['classn']
                print classname
                classc = request.form['classcode']
                print classc
                
                cur.execute("UPDATE class SET class_name = %s WHERE class_code = %s",[classname,classc] )
      
                conn.commit()
                mess="Your class info has been updated!"
                notification="success"
                return  redirect(url_for('controlPanel',mess=mess,notification=notification))
            elif request.form['submit']=='Cancel':
                 mess="Nothing has been updated!"
                 notification="notice"
                 return  redirect(url_for('controlPanel',mess=mess,notification=notification))
                
    if 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanelE.html')


@app.route('/controlPanelMQ', methods=['GET', 'POST'])
def manageQuestion():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        if request.method == 'POST':
            return render_template('controlPanelMQ.html')
    if 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanelMQ.html')    



if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)