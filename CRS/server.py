import hashlib
import psycopg2
import psycopg2.extras
import os
import sys 
import uuid
import re
from collections import Counter
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import datetime
import pytz
from datetime import datetime,date
from pytz import timezone
from flask import Flask, session, redirect, url_for, escape, request, render_template
from werkzeug import secure_filename
import matplotlib.pyplot as plt
from flask import Markup
import pygal
from PIL import Image
from string import lowercase



reload(sys)
sys.setdefaultencoding('utf8')

#from pytagcloud import create_tag_image, make_tags
#from pytagcloud.lang.counter import get_tag_counts
#import webbrowser


reload(sys)

UPLOAD_FOLDER = './static/images/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key= os.urandom(24).encode('hex')

currentQuestion = ''
currentClass = ''
answerstext=[]
answersList=[]
answersListA=[]
answersListB=[]
answersListC=[]
answersListD=[]
answersListE=[]
choices=[]
modifyQu=[]
multiplechoice=[]
multiplechoice.append(False)




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
           
def connectToDB():
    connectionString='dbname=crs1 user=postgres password=maher123 host=localhost'
    print connectionString
    try:
        return psycopg2.connect(connectionString)
    except:
        print ("Can't connect to database")

@app.route('/',methods=['GET', 'POST'])
def mainIndex():
    conn=connectToDB()
    cur= conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        if not session['username'].isdigit() :
            return redirect(url_for('menu'))
        if session['username'].isdigit():
            return redirect(url_for('studentHome'))
    if 'username' not in session:
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

            try:
                query = "select * from administrator WHERE email = '%s' AND password = '%s'" % (username, pw)
                print query
                cur.execute(query)
            except:
                notification="password"
                mess="The email or password you inputted is incorrect!"
                return redirect(url_for('login',mess=mess,notification=notification))

            r=cur.fetchall()
            if r:
                session['username'] = request.form['username']
                return redirect(url_for('menu'))
         #return redirect(url_for('mainIndex',user=currentUser,c=ch))
    return render_template('login.html')



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
        query = "select * from class ORDER BY class_name " 
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
      
            
            query = "select * from class ORDER BY class_name " 
            print query
            cur.execute(query)
            results = cur.fetchall()
            mess="Your class has been created"
            notification="success"
            return  redirect(url_for('controlPanel',mess=mess,notification=notification))    
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanel.html',results=results)

@app.route('/controlPanelD', methods=['GET', 'POST'])
def delete():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        query = "select * from class ORDER BY class_name " 
        cur.execute(query)
        results = cur.fetchall()
    
        if request.method == 'POST':
            classCode = request.form['classn']
            print classCode
            if request.form['submit']=='Delete':
                classname = request.form['classn']
                
                cur.execute("DELETE FROM answers WHERE class_code = %s",[classCode] )
                cur.execute("DELETE FROM class WHERE class_code = %s",[classCode] )
      
                conn.commit()
                mess="Your class has been deleted!"
                notification="success"
                query = "select * from class ORDER BY class_name" 
                print query
                cur.execute(query)
                results = cur.fetchall()
                return  redirect(url_for('controlPanel',mess=mess,notification=notification))
            elif request.form['submit']=='Edit':
                 classname = request.form['classn']
                 cur.execute("select * FROM class WHERE class_name = %s",[classname] )
                 results = cur.fetchall()
                 for r in results:
                     name=r[1]
                     code=r[0]
                     print name,code
                     
                 return redirect(url_for('edit',code=code,name=name))
                
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanel.html',results=results)



@app.route('/controlPanelE', methods=['GET', 'POST'])
def edit():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        if request.method == 'POST':
            if request.form['submit']=='Save':
                if request.form['classn']:
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
                else:
                    mess="Invalid inputted!"
                    notification="error"
                    return  redirect(url_for('controlPanel',mess=mess,notification=notification))
            elif request.form['submit']=='Cancel':
                 mess="Nothing has been updated!"
                 notification="notice"
                 return  redirect(url_for('controlPanel',mess=mess,notification=notification))
                
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanelE.html')


@app.route('/controlPanelMQ1', methods=['GET', 'POST'])
def manageQuestion():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    mess=''
    notification=''
    if 'username' in session:
        query = "select question from question ORDER BY question_id ASC" 
        cur.execute(query)
        res = cur.fetchall()
        print"Tryin to go to deleteq"
        
        query = "select * from class ORDER BY class_name ASC " 
        cur.execute(query)
        results = cur.fetchall()
        if request.method == 'POST':
            
            if('createq' in request.form and (request.form['type']=="Short Answer") ):
                
                print"we inter post"
                question = request.form['question']
                comment=request.form['comment']
            
                try:
                    cur.execute("""INSERT INTO question
                    VALUES (DEFAULT,1,%s, %s,NULL);""",[question,comment] )
                    #cur.execute = ("select question_id from question where question_id=%s ",[question])
                    #QuestionId=cur.fetchall()
                except:
                    print "could not add the question!!"
                    mess="could not add the question!!"
                    notification="error"
                    conn.rollback()
                conn.commit() 
                cur.execute("select count(question_id) from question")
                qid = cur.fetchone()
                print qid[0]
            
            
            elif('type' in request.form and (request.form['type']=="Multiple Choices")):
                question = request.form['question']
                comment=request.form['comment']
                
                try:
                    cur.execute("""INSERT INTO question
                    VALUES (DEFAULT,0,%s, %s,NULL);""",[question,comment] )
                    #cur.execute = ("select question_id from question where question_id=%s ",[question])
                    #QuestionId=cur.fetchall()
                except:
                    print "could not add the question!!"
                    mess="could not add the question!!"
                    notification="error"
                    conn.rollback()
                conn.commit()
                cur.execute("select question_id from question where question='%s'" % question )
                qid = cur.fetchone()
                print"we inter type"
                questiontype= request.form['type']
                answerA=request.form['answerA']
                answerB=request.form['answerB']
                answerC=request.form['answerC']
                answerD=request.form['answerD']
                answerE=request.form['answerE']
                print answerA,answerB,answerC,answerD,answerE
                if('correct' in request.form):
                        print"we inter correct"
                        correctAnswer=request.form['correct']
                        print correctAnswer
                
                try:  
                        
                        cur.execute("""INSERT INTO multiple_choice_question 
                        VALUES(%s,%s,%s,%s,%s,%s,%s);""",[qid[0],answerA,answerB,answerC,answerD,answerE,correctAnswer] )
                        
                        
                        
                        
                except:
                        print (cur.mogrify("""INSERT INTO multiple_choice_question 
                        VALUES(%s,%s,%s,%s,%s,%s,%s);""",[qid[0],answerA,answerB,answerC,answerD,answerE,correctAnswer] ))
                        print "could not add the multiple_choice_question!!"
                        conn.rollback()
                conn.commit() 
                query = "select question from question " 
                cur.execute(query)
                res = cur.fetchall()
                return render_template('controlPanelMQ1.html',results=results,res=res)
            
            elif('type' in request.form and (request.form['type']=="Short Answer")):
                
                try:
                    shortanswer=request.form['shortAnswer']
                    cur.execute("""INSERT INTO short_answer
                        VALUES(%s,%s);""",[qid[0],shortanswer] )
                except:
                    print "could not add the short answer!!"
                    print (cur.mogrify("""INSERT INTO short_answer
                        VALUES(%s,%s);""",[qid[0],shortanswer] ))
                    conn.rollback()
                conn.commit()
            
                    
                #resp.status_code = 204
            return render_template('controlPanelMQ1.html')
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('controlPanelMQ1.html',results=results,res=res)    


@app.route('/modifyQ', methods=['GET', 'POST'])
def modifyQ():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    a=''
    b=''
    c=''
    d=''
    e=''
    if 'username' in session:
        query = "select question from question ORDER BY question_id ASC" 
        cur.execute(query)
        res = cur.fetchall()
        print"Tryin to go to deleteq"
        
        query = "select * from class " 
        cur.execute(query)
        results = cur.fetchall()
        if request.method == 'POST':
        
            if('deleteQ' in request.form ):
                print "we trying to delete this question"
                curq = request.form['question']
                print curq
                cur.execute("SELECT question_id FROM question WHERE question = %s" , [curq])
                results = cur.fetchone()
                print results
                cur.execute("DELETE FROM answers WHERE question_id = %s",[results[0]] )
                conn.commit()
                cur.execute("DELETE FROM multiple_choice_question WHERE question_id = %s",[results[0]] )
                conn.commit()
                cur.execute("DELETE FROM map_question WHERE question_id = %s",[results[0]] )
                conn.commit()
                cur.execute("DELETE FROM question WHERE question_id = %s",[results[0]])
                conn.commit()
                
                query = "select question from question ORDER BY question_id ASC" 
                cur.execute(query)
                res = cur.fetchall()
                
                mess="Your question has been deleted!"
                notification="success"
                return render_template('modifyQ.html',mess=mess,notification=notification,results=results,res=res)
            elif 'modify' in request.form:
                 print"trying to edit question"
                 curq = request.form['question']
                 cur.execute("select * FROM question WHERE question = %s",[curq] )
                 dis=False
                 results = cur.fetchall()
                 for r in results:
                     questionID=r[0]
                     questionType=r[1]
                     question=r[2]
                     modifyQu.append(question)
                     questionComment=r[3]
                 if questionType==0:
                    cur.execute("select * FROM multiple_choice_question WHERE question_id= %s",[questionID] )
                    res = cur.fetchall()
                    dis=True
                    for i in res:
                        a=i[1]
                        b=i[2]
                        c=i[3]
                        d=i[4]
                        e=i[5]
                        return redirect(url_for('modifyQuestion',a=a,b=b,c=c,d=d,e=e,question=question,questionComment=questionComment,questionType=questionType,dis=dis))
                 elif questionType==1:
                     print "short answer question"
                     #print name,code
                     return redirect(url_for('modifyQuestion',question=question,questionComment=questionComment,questionType=questionType))
                     
                 
                
                
        #return render_template('modifyQ.html')
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('modifyQ.html',results=results,res=res) 


@app.route('/modifyQuestion', methods=['GET', 'POST'])
def modifyQuestion():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    comment=''
    question=''
    questionID=''
    if 'username' in session:
        print "we are in session"
        if request.method == 'POST':
            if 'save' in request.form:
                print cur.mogrify("select * from question where question=%s",[modifyQu[0]])
                cur.execute("select * from question where question=%s",[modifyQu[0]])
                res = cur.fetchall()
                print res
                for r in res:
                    questionID=r[0]
                    questiontype=r[1]
                    question=r[2]
                    comment=r[3]
                
                if 'optionA' in request.form:
                    print "Something is wrong"
                    if(request.form['comment'] and request.form['question'] and request.form['optionA'] and request.form['optionB'] and request.form['optionC'] and request.form['optionD'] and request.form['optionE']):
                        print "Are we in this statement?"
                        try:
                            query = "UPDATE question SET question = %s, admin_comments=%s WHERE question_type=0 and question=%s and question_id=%s ;"
                            cur.execute(query,[request.form['question'],request.form['comment'],question,questionID])
                            try:
                                
                                #conn.commit()
                                query = "UPDATE multiple_choice_question SET option_a= %s, option_b= %s , option_c=%s, option_d=%s, option_e=%s, correct_answer=%s WHERE question_id=%s ;"
                                cur.execute(query,[request.form['optionA'],request.form['optionB'],request.form['optionC'],request.form['optionD'],request.form['optionE'],request.form['option'],questionID])
                                
                            except:
                                print cur.mogrify(query,[request.form['optionA'],request.form['optionB'],request.form['optionC'],request.form['optionD'],request.form['optionE'],questionID])
                                print "Cannot update multiplechoice"
                                
                        except:
                                query = "UPDATE question SET question = %s, admin_comments=%s WHERE question_type=0 and question=%s and question_id=%s ;"
                                print cur.mogrify(query,[request.form['question'],comment,question,questionID])
                                print "Cannot update question table"
                        conn.commit()
                        mess="Question has been updated successfully!"
                        notification="notice"
                        del modifyQu[0]
                        return  redirect(url_for('modifyQ',mess=mess,notification=notification))
                    else:
                            mess="Question has not been updated!"
                            notification="error"
                            return  redirect(url_for('modifyQ',mess=mess,notification=notification))
                else:
                    print request.form['question']
                    print ("Short answer questionnnnnnnnnnnnn")
                    query = "UPDATE question SET question = %s, admin_comments=%s WHERE question=%s and question_id=%s ;"
                    try:
                        print "We are updating the comment and the question"
                        cur.execute(query,[request.form['question'],request.form['comment'],modifyQu[0],questionID])
                        
                    except:
                        print "connat update"
                    conn.commit()
                    mess="Question has been updated successfully!"
                    notification="notice"
                    del modifyQu[0]
                    return  redirect(url_for('modifyQ',mess=mess,notification=notification))
                        
            elif 'cancel' in request.form:
                 mess="Nothing has been updated!"
                 notification="notice"
                 return  redirect(url_for('modifyQ',mess=mess,notification=notification))
                
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
    return render_template('modifyQuestion.html')
    



@app.route('/controlPanelMQL', methods=['GET', 'POST'])
def loadimage():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        if request.method == 'POST':
            cur.execute("select count(question_id) from question")
            qid = cur.fetchone()
            print qid[0]
            if('type' in request.form and (request.form['type']=="Map")):
                print "Tring to upload the image"
                file =request.files['image']
                print "Tring to upload the image"
                if file and allowed_file(file.filename):
                    print " the image is here now"
                    filename = secure_filename(file.filename)
                    i=filename.find('.')
                    filename=str(uuid.uuid1())+str(qid[0]+1)+filename[i:]
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename) )
                    
                    return filename
"""
@app.route('/changeBackground', methods=['GET', 'POST']) 
def changeBackground():
    conn=connectToDB()
    bg =request.files['x']
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'username' in session:
        print "trying to change Background"
        if request.method == 'POST':
            try:
                query = "UPDATE administrator SET background = %s;"
                cur.execute(query,[bg])
            except:
                print cur.mogrify("select count(question_id) from administrator")
                print "cannot update background!"
                return "error"
                        
        return "pass" """




 
@app.route('/controlPanelImage', methods=['GET', 'POST']) 
def hiliteimage():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print " Hi"
    if 'username' in session:
        return  render_template('controlPanelImage.html')
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex')) 
    return  render_template('controlPanelImage.html')
    



#multiple coice answer
@app.route('/answerQuestion', methods=['GET','POST'])
def answerQuestion():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    results4 = []
    shortanswer=''
    results2=''
    
    if 'username' in session:
        
        print currentClass + currentQuestion + "This is it"
        query = "SELECT question_id FROM answers WHERE class_code = %s AND status ='display' " 
        cur.execute(query,[session['username']])
        results = cur.fetchall()
        print results
        if not results:
            mess="Your Professor has not displayed any question yet"
            return render_template('answer.html',answers='', mess=mess)
        
        query = "SELECT question,question_type FROM question WHERE question_id = %s" 
        cur.execute(query,[results[0][0]])
        results2 = cur.fetchall()
        print results2
        if not results2:
            mess="Your Professor has not displayed a question yet"
            return render_template('answer.html',answers='', mess=mess)
        
        if results2[0][1]==0:
            
            query = "SELECT * FROM multiple_choice_question WHERE question_id = %s"
            cur.execute(query,[results[0][0]])
            results3 = cur.fetchall()
            results4 = []
            resultsTemp = results3
            #print resultsTemp
            del resultsTemp[0][6]
            for result in resultsTemp[0]:
                if result != None:
                    results4.append(result)
            del results4[0]
            #print results4 
        if results2[0][1]==1:
            # this is for short answer question
            shortanswer="<textarea rows='4' cols='30' id='shortAnswer' name='shortAnswer' style='color:black;' placeholder='write your answer here' required='required' type='textfield' ></textarea>"
            
            
        print results2
        if request.method == 'POST':
            if 'shortAnswer' in request.form:
                answersList.append(request.form['shortAnswer'])
                answerstext=[]
                print answersList
                multiplechoice[0]=False
                
                print "it should be an empty list" 
            elif 'option' in request.form:
                multiplechoice[0]=True
                ans=request.form['option']
                a=results4[0]
                choices.append(a)
                b=results4[1]
                choices.append(b)
                c=results4[2]
                choices.append(c)
                d=results4[3]
                choices.append(d)
                e=results4[4]
                choices.append(e)
                if a==ans:
                    answersListA.append(ans)
                elif b==ans:
                    answersListB.append(ans)
                elif c==ans:
                    answersListC.append(ans)
                elif d==ans:
                    answersListD.append(ans)
                elif e==ans:
                    answersListE.append(ans)
                
            print answersListE
            
            return redirect(url_for('studentHome'))
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex')) 
        
        
    return render_template('answer.html', answers=results2,answers2=results4,shortanswer=shortanswer)
    """
    # check current class (cc)
    cc = session['username']
    print cc
    #fix below
    query = "SELECT question_id FROM answers WHERE class_code = %s AND status = 1" % (cc) 
    #query = "SELECT question_id FROM answers WHERE status = 1 AND class_code = 1234"
    cur.execute(query)
    results = cur.fetchall()
    print results

    query = "SELECT * FROM question WHERE question_id = %s" % (results[0][0])
    cur.execute(query)
    results2 = cur.fetchall()
    print results2
    
    query = "SELECT * FROM multiple_choice_question WHERE question_id = %s" % (results[0][0])
    cur.execute(query)
    results3 = cur.fetchall()
    print results3
    
    results4 = []
    resultsTemp = results3
    #print resultsTemp
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
            return redirect(url_for('studentHome'))
    
    #add to database from here
    
    qImage = "questionImages/math2.png"
    #qImage = None
    
    return render_template('answer.html', answers=results2, answers2=results4, qImage=qImage)
    """

#short answer question
@app.route('/answer2', methods=['GET','POST'])
def answerQuestion2():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cc = 1111
    
    query = "SELECT question_id FROM answers WHERE class_code = %s AND status = 1" 
    #query = "SELECT question_id FROM answers WHERE status = 1 AND class_code = 1234"
    cur.execute(query,[cc])
    results = cur.fetchall()
    #print results


    query = "SELECT * FROM question WHERE question_id = %s" 
    cur.execute(query,[results[0][0]])
    results2 = cur.fetchall()
    #print results2
    
    if request.method == 'POST':
        if request.form['submit']:
            #print 'I did it!'
            print request.form['answer']
            #make this (below) student home page
            return redirect(url_for('studentHome'))
    
    #add to database from here
    
    qImage = "questionImages/math2.png"
    #qImage = None
    
    return render_template('answer2.html', answers=results2, qImage=qImage)
    


@app.route('/menu', methods=['GET', 'POST']) 
def menu():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    display=False
    curC=''
    chart=''
    fmt = "%Y-%m-%d"

    # Current time in UTC
    now_utc = datetime.now(timezone('UTC'))
    print now_utc.strftime(fmt)
    # Convert to US/Pacific time zone
    now_pacific = now_utc.astimezone(timezone('US/Eastern'))
    print now_pacific.strftime(fmt)
    dateT=now_pacific.strftime(fmt)
    
    
    
    
    print " Hi"
    if 'username' in session:
        query = "select * from class ORDER BY class_name ASC" 
        cur.execute(query)
        results = cur.fetchall()
        query = "select question from question ORDER BY question_id ASC " 
        cur.execute(query)
        res = cur.fetchall()
        question=''
        qcChange=''
        print res
        #print "We here?"
        
        
        if request.method == 'POST':
            #print "why don't you work?"
            #print request.form['q']
            curQ = request.form.get('question')
            print curQ
            curC = request.form.get('className')
            print curC
            currentQuestion=curQ
            currentClass=curC
            #on button press
            
            if('display' in request.form ):
              
                display=True
                del answersList[:]
                print "it should be here"
                #buicom = 'CREATE TABLE tempy(id serial, answer text, PRIMARY KEY (id))'
                #cur.execute(buicom)
                # find class code and question code, then change question state to be 1
                cmd1 = "SELECT class_code FROM class WHERE class_name = '%s'" % curC
                #print cmd1
                cur.execute(cmd1)
                ccChange = cur.fetchall()[0][0]
                classcode=ccChange
                #print ccChange
                cmd2 = "SELECT question_id FROM question WHERE question = '%s'" % curQ
                cur.execute(cmd2)
                qcChange = cur.fetchall()[0][0]
                #print qcChange
                
                print dateT
                print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
                try:
                    cmd3 = 'SELECT * FROM answers where class_code = %s and question_id = %s' % (ccChange, qcChange)
                    cur.execute(cmd3)
                    test = cur.fetchall()
                    if  test:
                        query = "UPDATE answers SET status = 'display', date= '%s' WHERE class_code = %s and question_id=%s ;" % (dateT,ccChange, qcChange)
                        cur.execute(query)
                        print "The question already in the table"
                    else:
                        query = """INSERT INTO answers VALUES('%s', 'display', %s, %s, null,FALSE)""" % (dateT, ccChange, qcChange)
                        cur.execute(query)

                except:
                    print "Could not update answers table"
                    
                    #notification="error"
                    #mess="You cannot display this question, this question has been already displayed to this class"
                    display=False
                    return  render_template('menu.html',display=display,classcode=classcode, curC=curC,results=results,res=res,currentQuestion=currentQuestion,currentClass=currentClass)
                conn.commit()
                cmd4 = 'SELECT * FROM answers where class_code = %s and question_id = %s' % (ccChange, qcChange)
                cur.execute(cmd4)
                conf="<script type='text/javascript'> var submitFormOkay = false; window.onbeforeunload = function() {if (!submitFormOkay){return 'Hey, you should hide the question before going to a different page!';} }</script>"
                #print cur.fetchall();
                notification="success"
                mess="The question has been displayed successfully"
                return  render_template('menu.html',display=display,classcode=classcode, curC=curC,results=results,res=res,currentQuestion=currentQuestion,currentClass=currentClass,conf=conf,mess=mess,notification=notification)
            elif  'hide' in request.form :
                
                    query = "UPDATE answers SET status = 'undisplay' WHERE status = 'display';" 
                    cur.execute(query)
                    conn.commit()
                    display=False
                    print currentQuestion
                    print currentClass
                    return  render_template('menu.html',display=display, curC=curC,results=results,res=res,question=question,qcChange=qcChange,currentQuestion=currentQuestion,currentClass=currentClass)
            
            elif 'shareResult' in request.form:
                print "trying to share result 1"
                imgPath=request.form['imgR']
                print imgPath
                notification="success"
                mess="The result has been shared"
                print currentClass
                cmd1 = "SELECT class_code FROM class WHERE class_name = '%s'" % currentClass
                #print cmd1
                cur.execute(cmd1)
                ccChange = cur.fetchall()[0][0]
                #print ccChange
                cmd2 = "SELECT question_id FROM question WHERE question = '%s'" % currentQuestion
                cur.execute(cmd2)
                qcChange = cur.fetchall()[0][0]
                print dateT
                try:
                    cmd3 = "UPDATE answers SET share = True, date='%s', answer_filepath='%s' WHERE question_id=%s and status= 'undisplay' and class_code=%s ;" % (dateT,imgPath,qcChange, ccChange)
                    cur.execute(cmd3)
                    print cur.mogrify(cmd3)
                except:
                    print "cannot update!!"
                conn.commit()
                #UPDATE films SET kind = 'Dramatic' WHERE kind = 'Drama';
                del answersList[:]
                del answersListA[:]
                del answersListB[:]
                del answersListC[:]
                del answersListD[:]
                del answersListE[:]
                return  render_template('menu.html',display=display, curC=curC,results=results,res=res,question=question,qcChange=qcChange,mess=mess,notification=notification,currentQuestion=currentQuestion,currentClass=currentClass)   
            elif 'showr' in request.form:
                query = "SELECT question_type FROM question WHERE question = '%s'" % curQ
                cur.execute(query)
                questionType = cur.fetchall()[0][0]
                answerstext=''
                #text="The generated image is saved to a file and displayed on screen. The lines displaying the image can be removed if interactivity is not needed, and the matplotlib package is not installed."
                
                
                # this part need to be fix so the wordclod can wrok
                
                    

                    
                    
                    
                    
                    
                    #for a in lines:
                        #answerstext.extend(re.split("[,/]+", a))
                    #answerstext = map(lambda s: s.strip(' -').lower(), answerstext)
                    #stopWords = {"agile", "tdd", "bdd"}
                    #answerstext = filter(lambda s: s and s not in stopWords, answerstext)
                    #cnt = Counter()
                    #for word in answerstext:
                        #cnt[word] += 1
                    #wordcloud = WordCloud(width=800, height=600, relative_scaling=.8).generate_from_frequencies(cnt.items())
                    
                    #wordcloud.to_file(fname)
                    
                    
                if multiplechoice[0]:
                    
                        
                    cmd2 = "SELECT question_id FROM question WHERE question = '%s'" % curQ
                    cur.execute(cmd2)
                    qcChange = cur.fetchall()[0][0]
                    print "showing results for choices"
                    print answersListE
                    
                    display=False
                    bar_chart = pygal.HorizontalBar()
                    bar_chart.title = "The Result"
                    #bar_chart.x_labels = "A","B","C","D","E"
                    bar_chart.add('Option A',[len(answersListA)])
                    bar_chart.add('Option B',[len(answersListB)])
                    bar_chart.add('Option C',[len(answersListC)])
                    bar_chart.add('Option D',[len(answersListD)])
                    bar_chart.add('Option E',[len(answersListE)])
                    #bar_chart.add('Padovan', [1, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12]) 
                    #chart = bar_chart.render()
                    filename="static/images/barChart/"+str(uuid.uuid1())+str(qcChange)+"_"+str(curC)+"_"+"bar_chart.svg"
                    bar_chart.render_to_file(filename)
                    barcarimage=""
                    """for i in answersListA:
                        del answersListA[0]
                    for i in answersListB:
                        del answersListB[0]
                    for i in answersListC:
                        del answersListC[0]
                    for i in answersListD:
                        del answersListD[0]
                    for i in answersListE:
                        del answersListE[0]"""
                    return  render_template('menu.html',display=display, curC=curC,results=results,res=res,question=question,filename=filename,currentQuestion=currentQuestion,currentClass=currentClass,barcarimage=barcarimage)
                
                
                
                else:
                    display=False
                    print "trying to wordcloud answers!"
                    print "showing results for short answer"
                    #cnt = Counter()
                    #wordList = re.sub("[^\w]", " ",  text).split()
                    for word in answersList:
                        print word
                        answerstext+=word+" "
                        #cnt[word] += 1
                    try:
                        wordcloud = WordCloud(width=600,height=400).generate(answerstext)
                    except:
                        notification="error"
                        mess="There is no resulte to show"
                        return  render_template('menu.html',display=display, curC=curC,results=results,res=res,question=question,qcChange=qcChange,mess=mess,notification=notification,currentQuestion=currentQuestion,currentClass=currentClass)
                        
                        
                    fname="static/images/wordcloud/"+str(uuid.uuid1())+str(qcChange)+"_"+str(curC)+"_"+"word_cloud.png"
                    wordcloud.to_file(fname)
                    #answersList=[]
                    
                    s=True
                    return  render_template('menu.html',display=display, curC=curC,results=results,res=res,question=question,fname=fname,s=s,currentQuestion=currentQuestion,currentClass=currentClass)
                
                #tags = make_tags(get_tag_counts(answerstext), maxsize=80)
                #create_tag_image(tags, 'static/images/cloud_large.png', size=(300, 600), fontname='Lobster')
                #webbrowser.open('cloud_large.png')
        return  render_template('menu.html',display=display, curC=curC,results=results,res=res,question=question,qcChange=qcChange)
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex')) 
    return  render_template('menu.html',question=question)



@app.route('/studentLogin', methods=['GET', 'POST'])
def studentLogin():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #reusing the username variable to store the class code
    #it is a number, but it is stored as a string type
    if 'username' in session:
         username_session = escape(session['username']).capitalize()
         return redirect(url_for('studentHome'))
    if request.method == 'POST':
            username = request.form['class_code']
            currentUser = username
            try:
                cur.execute("select * from class WHERE class_code = %s", (username,))
                r = cur.fetchall()
            except:
                notification="codeError"
                mess="The class code you inputted is incorrect!"
                return redirect(url_for('studentLogin',mess=mess,notification=notification))
            if r:
                session['username'] = request.form['class_code']
                return redirect(url_for('studentHome'))
            else:
                notification="codeError"
                mess="The class code you inputted is incorrect!"
                return redirect(url_for('studentLogin',mess=mess,notification=notification))
         #return redirect(url_for('mainIndex',user=currentUser,c=ch))
    
    return render_template('studentLogin.html')







@app.route('/studentHome', methods=['GET', 'POST'])
def studentHome():
    conn=connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    empty=True
    if 'username' in session:
        print "Trying to display previous question"
        if request.method == 'POST':
            empty=False
            classcode=''
            if 'browse' in request.form:
                questionid=request.form['browse']
                print questionid
                cur.execute("select * FROM question WHERE question_id = %s",[questionid] )
                results = cur.fetchall()
                
                #new way to track answer choices and correct answer
                multipleChoiceResults = []
                if results[0][1] == 0:
                    cur.execute("SELECT * FROM multiple_choice_question WHERE question_id = %s",[questionid])
                    multipleChoiceResults = cur.fetchall()
                    
                
                cur.execute("select * FROM answers WHERE share and class_code=%s and question_id = %s",[session['username'],questionid] )
                res = cur.fetchall()
                return render_template('sampleQuestion1.html',res=res,results=results,classcode=classcode,empty=empty,
                                        multipleChoiceLabels={0:'A',1:'B',2:'C',3:'D',4:'E'},multipleChoiceResults=multipleChoiceResults)
        else:
            try:
                empty=False
                print session['username']
                s=str(session['username'])
                query = "select DISTINCT * from answers where share=TRUE and class_code=%s ORDER BY date" 
                cur.execute(query,[session['username']])
                results = cur.fetchall()
                classcode=str(results[0][2])
                return render_template('studentHome.html',results=results,classcode=classcode,empty=empty)
                
            except:
                classcode="nothing"
                print classcode
                results=''
                empty=True
                return render_template('studentHome.html',results=results,classcode=classcode,empty=empty)
        
                
        
    elif 'username' not in session:  
        return  redirect(url_for('mainIndex'))
        
    return render_template('studentHome.html')

#placeholder question details pages
@app.route('/sampleQuestion1', methods=['GET','POST'])
def sampleQuestion1():
    bar_chart = pygal.HorizontalStackedBar()
    bar_chart.title = "Remarquable sequences"
    bar_chart.x_labels = map(str, range(11))
    bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
    bar_chart.add('Padovan', [1, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12]) 
    chart = bar_chart.render()
    return render_template('sampleQuestion1.html',chart=chart)
    
@app.route('/sampleQuestion2', methods=['GET','POST'])
def sampleQuestion2():
    return render_template('sampleQuestion2.html')
    
@app.route('/sampleQuestion3', methods=['GET','POST'])
def sampleQuestion3():
    return render_template('sampleQuestion3.html')
if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)