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
            # Vulnerable to sql injection? Might need to change to cur.mogrify("query",(parameters))
            query = "select * from administrator WHERE email = '%s' AND password = '%s'" % (username, pw)
            print query
            cur.execute(query)
            r=cur.fetchall()
            if r:
                session['username'] = request.form['username']
                return redirect(url_for('controlPanel'))
         #return redirect(url_for('mainIndex',user=currentUser,c=ch))
    return render_template('login.html')

@app.route('/studentLogin', methods=['GET', 'POST'])
def studentLogin():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #reusing the username variable to store the class code
    #it is a number, but it is stored as a string type
    if 'class_code' in session:
        return redirect(url_for('studentHome'))
    if request.method == 'POST':
            class_code = request.form['class_code']
            cur.execute("select * from class WHERE class_code = %s", (int(class_code),))
            r = cur.fetchall()
            if r:
                session['class_code'] = request.form['class_code']
                return redirect(url_for('studentHome'))
    return render_template('studentLogin.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('class_code',None)
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
                
                mess="This class code already exists!"
                notification="error"
                return  redirect(url_for('controlPanel',mess=mess,notification=notification))
      
            
            query = "select * from class " 
            print query
            cur.execute(query)
            results = cur.fetchall()
            mess="Your class has been created"
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

@app.route('/studentHome', methods=['GET', 'POST'])
def studentHome():
    if 'class_code' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('studentHome.html')

#multiple coice answer
@app.route('/answer', methods=['GET','POST'])
def answerQuestion():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # check current class (cc)
    cc = 1234
    #fix below
    query = "SELECT question_id FROM answers WHERE class_code = %s AND status = 1" % (cc) 
    #query = "SELECT question_id FROM answers WHERE status = 1 AND class_code = 1234"
    cur.execute(query)
    results = cur.fetchall()

    query = "SELECT * FROM question WHERE question_id = %s" % (results[0][0])
    cur.execute(query)
    results2 = cur.fetchall()
    #print results2
    
    query = "SELECT * FROM multiple_choice_question WHERE question_id = %s" % (results[0][0])
    cur.execute(query)
    results3 = cur.fetchall()
    #print results3
    
    results4 = []
    resultsTemp = results3
    del resultsTemp[0][6]
    for result in resultsTemp[0]:
        if result != None:
            results4.append(result)
    del results4[0]
    #print results4        
    
    if request.method == 'POST':
        if request.form['submit']:
            #print 'I did it!'
            #print request.form['option']
            #make this (below) student home page
            return render_template('studentHome.html')
    
    #add to database from here
    
    qImage = "questionImages/math2.png"
    #qImage = None
    
    return render_template('answer.html', answers=results2, answers2=results4, qImage=qImage)

#short answer question
@app.route('/answer2', methods=['GET','POST'])
def answerQuestion2():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cc = 1111
    
    query = "SELECT question_id FROM answers WHERE class_code = %s AND status = 1" % (cc) 
    #query = "SELECT question_id FROM answers WHERE status = 1 AND class_code = 1234"
    cur.execute(query)
    results = cur.fetchall()
    #print results

    query = "SELECT * FROM question WHERE question_id = %s" % (results[0][0])
    cur.execute(query)
    results2 = cur.fetchall()
    #print results2
    
    if request.method == 'POST':
        if request.form['submit']:
            #print 'I did it!'
            print request.form['answer']
            #make this (below) student home page
            return render_template('studentHome.html')
    
    #add to database from here
    
    qImage = "questionImages/math2.png"
    #qImage = None
    
    return render_template('answer2.html', answers=results2, qImage=qImage)
    
#placeholder question details pages
@app.route('/sampleQuestion1', methods=['GET','POST'])
def sampleQuestion1():
    return render_template('sample_question_1.html')
    
@app.route('/sampleQuestion2', methods=['GET','POST'])
def sampleQuestion2():
    return render_template('sample_question_2.html')
    
@app.route('/sampleQuestion3', methods=['GET','POST'])
def sampleQuestion3():
    return render_template('sample_question_3.html')

if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)