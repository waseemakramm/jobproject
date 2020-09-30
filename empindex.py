#!/usr/bin/env python
# coding: utf-8

# In[8]:


from pyresparser import ResumeParser
import re
import pandas as pd
import spacy
import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz
import xlrd
import mysql.connector
import sys



mydb = mysql.connector.connect(
  host="localhost",
  port="6118",
  user="root",
  password=""
)

def fetch_title(jobid):
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT job_type FROM bayt_data.job_type where id=%s",(jobid,))
    
    myresult = mycursor.fetchall()
    retresult=myresult[0][0]

    return retresult
    
    
def fetch_ides(jobid):
    mycursor = mydb.cursor()
    jobtitle=fetch_title(jobid)
    
    mycursor.execute("SELECT job_id FROM bayt_data.master_table where job_title=%s",(jobtitle,))
    
    myresult = mycursor.fetchall()
    ides=[]
    for x in myresult:
        ides.append(x)
        
    ides1=[]
    for x in range(0, len(ides)):
        ides1.append(ides[x][0])
        
    return ides1


def fetch_techskills(jobid):
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT top_technical_skills FROM bayt_data.technical_skills where job_id=%s",(jobid,))
    
    myresult = mycursor.fetchall()
    techs=[]
    for x in myresult:
        techs.append(x)
    return techs

def fetch_softskills(jobid):
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT top_soft_skills FROM bayt_data.soft_skills where job_id=%s",(jobid,))
    
    myresult = mycursor.fetchall()
    techs=[]
    for x in myresult:
        techs.append(x)
    return techs

def fetch_languages(jobid):
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT top_languages FROM bayt_data.programming_languages where job_id=%s",(jobid,))
    
    myresult = mycursor.fetchall()
    techs=[]
    for x in myresult:
        techs.append(x)
    return techs

def fetch_frameworks(jobid):
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT top_frameworks FROM bayt_data.programming_frameworks where job_id=%s",(jobid,))
    
    myresult = mycursor.fetchall()
    techs=[]
    for x in myresult:
        techs.append(x)
    return techs

def fetch_certifications(jobid):
    mycursor = mydb.cursor()
    
    mycursor.execute("SELECT top_certificates FROM bayt_data.certification where job_id=%s",(jobid,))
    
    myresult = mycursor.fetchall()
    certs=[]
    for x in myresult:
        certs.append(x)
    return certs



    

def getdata(cstring):
    # conver to the list
    datalist = cstring.split (",")
    return datalist


def get_ngrams(text, n ):
    # get a list of all possible distributions like :
        # 'have a nice weekend'
        # it will be :
        # ['have a','a nice','nice weekend']
    n_grams = ngrams(word_tokenize(text), n)
    return [' '.join(grams) for grams in n_grams]


def get_largest_match(title,skills,ngram):
    
    # make a default matching degree and title
#     skills=soft_skills
    ngram=ngram
    dic={}
    match_degree = 0
    match_skill = ''
    match_gram=''
    
    # try every skill in skill list
    for sk in skills:
        #print(sk)
        match_degree = 0
        # get a list of all possible distributions like :
        n_Gram_list = get_ngrams(title, ngram )
        
        # try every distributions in distributions list "n_Gram_list"
        for gram in n_Gram_list:
            #print(gram)
            
            # get similarity degree of job title "gram" and our title from title list 
            similarity_degree = fuzz.token_sort_ratio(sk, gram)
            # SequenceMatcher(None,gram.lower(),i.lower()).ratio()
            # get the most similarity butween the new and old(or default)
            
            if similarity_degree > match_degree:
                match_degree = similarity_degree
                match_skill = sk
                match_gram=gram
        dic[match_skill]=match_degree
#         if(title=="Eastern Province"):
#             print(match_skill,":",match_gram,":",match_degree)
        
    dic=sorted(dic.items(), key=lambda x: x[1], reverse=True)
    return dic
#     dic=[i[0] for i in dic]

    #return dic[:1]
    

def joblist(gotskills):
    test1=[]
    for x in range(1,11):
        test1.append(gotskills[:x][x-1][0])
    return test1

def cvlist(cvskills):
    test2=[]
    for x in range(0,len(cvskills)):
        test2.append(cvskills[x][0])
    return test2
    
def exactmatch(test):
    i=0
    for x in range(1,len(test)):
        if test[:x][x-1][1]>=70:
            i=i+1
    return i


def getskills(filename,strextskills, ngram):
    forsoft=pd.read_csv(filename)
    softskills=list(forsoft.columns.values)
    gotsoftskills=get_largest_match(strextskills, softskills, ngram)
    return gotsoftskills

def score(gotsoftskills):
    forsoftscore=[]
    j=0
    for i in range(1,10):
        if i==1:
            forsoftscore.append(gotsoftskills[:i][j][1])
        else:
            forsoftscore.append(gotsoftskills[:i][i-1][1])
            
    softscore=sum(forsoftscore)/len(forsoftscore)
    return softscore

def getscore(cvdatalist,fetch,ids,ngram):
    #ide=fetch_ides(classname)
    #gotsoftskills=getskills(filename, strextskills,ngram)
    cvsoft=fetch(ids)
    
    #softjoblist=joblist(gotsoftskills)
    softcvlist=cvlist(cvsoft)
    strsoftcvlist=' '.join(map(str, softcvlist))
    softmatches=get_largest_match(strsoftcvlist, cvdatalist, ngram)    
    j=exactmatch(softmatches)        
    return j*10



def finalfunc(strextskills, ides):    
    #Technical Skills
    techskills=getscore(strextskills,fetch_techskills,ides,2)
    #print("Technical Skill's Score: ",techskills)
    
    #softskills score
    softskills=getscore(strextskills,fetch_softskills,ides,1)
    #print("softskill's Score: ",softskills)
    
    
    #Languages score
    languages=getscore(strextskills,fetch_languages,ides,1)
    #print("Language's Score: ",languages)
    
    #frameworks
    frameworks=getscore(strextskills,fetch_frameworks,ides,1)
    #print("Framework's Score: ",frameworks)
    
    #frameworks
    certifications=getscore(strextskills,fetch_certifications,ides,2)
    #print("Framework's Score: ",frameworks)
    
    #added Courses
    #corscore=addedcor(strextskills,2)
    #print(corscore)
    
    #added certifications
    #certscore=addedcert(strextskills,2)
    #print(certscore)
    
    totalscore=techskills + softskills + languages + frameworks + certifications
    overallscore=totalscore/5
    return overallscore
    
    
def selected(coursestring,certstring):
    retlist=[]
    courselist=['a',]
    certlist=['a',]
    #print(coursestring)
    if coursestring:
        #print("Course Hai")
        courselist=courselist + getdata(coursestring)
        #print(len(courselist))
        mycursor = mydb.cursor()
        

        
        for x in range(1,len(courselist)):
            mycursor.execute("SELECT tech_skills, soft_skills, languages, frameworks, certifications FROM bayt_data.course_table where course_id=%s",(courselist[x],))
            
            myresult = mycursor.fetchall()
            
            tech=myresult[0][0]
            
            techskills=tech.split(",")
            #print(techskills)
            
            soft=myresult[0][1]
            
            softskills=soft.split(",")
            #print("\n",softskills)
            
            lang=myresult[0][2]
            
            languages=lang.split(",")
            #print("\n",languages)
            
            frame=myresult[0][3]
            
            frameworks=frame.split(",")
            #print("\n",frameworks)
            
            cert=myresult[0][4]
            
            certifications=cert.split(",")
            #print("\n",certifications)
            
            
            retlist=retlist + techskills + softskills + languages + frameworks + certifications
        #print(retlist)
        #if not certstring:
            #print("certstring wala check")
            #return retlist
        #return retlist
        
    elif certstring:
        #print("Certification Hai")

        certlist=certlist + getdata(certstring)
        #print(len(courselist))
        mycursor = mydb.cursor()
        

        
        for x in range(1,len(certlist)):
            mycursor.execute("SELECT tech_skills, soft_skills, languages, frameworks, certifications FROM bayt_data.certification_table where certification_id=%s",(certlist[x],))
            
            myresult = mycursor.fetchall()
            
            tech=myresult[0][0]
            
            techskills=tech.split(",")
            #print(techskills)
            
            soft=myresult[0][1]
            
            softskills=soft.split(",")
            #print("\n",softskills)
            
            lang=myresult[0][2]
            
            languages=lang.split(",")
            #print("\n",languages)
            
            frame=myresult[0][3]
            
            frameworks=frame.split(",")
            #print("\n",frameworks)
            
            cert=myresult[0][4]
            
            certifications=cert.split(",")
            #print("\n",certifications)
            
            
            retlist=retlist + techskills + softskills + languages + frameworks + certifications
        #print(retlist)
        #if not coursestring:
            #print("certstring wala check")
            #return retlist
    return retlist
    
    

def getcvdata(user_id,added,certifications):
    retlist=[]
    mydata=selected(added,certifications)
    #print(mydata)
    if mydata:
        retlist=mydata
    
        mycursor = mydb.cursor()
        
        mycursor.execute("SELECT tech_skills, soft_skills, programming_languages, programming_frameworks, certifications FROM bayt_data.cv_details where user_id=%s",(user_id,))
        
        myresult = mycursor.fetchall()
        
        tech=myresult[0][0]
        
        techskills=tech.split(",")
        
        soft=myresult[0][1]
        
        softskills=soft.split(",")
        
        lang=myresult[0][2]
        
        languages=lang.split(",")
        
        frame=myresult[0][3]
        
        frameworks=frame.split(",")
        
        cert=myresult[0][4]
        
        certifications=cert.split(",")
        
        retlist=retlist + techskills + softskills + languages + frameworks + certifications
    
        return retlist
    
    else:
        
        mycursor = mydb.cursor()
        
        mycursor.execute("SELECT tech_skills, soft_skills, programming_languages, programming_frameworks, certifications FROM bayt_data.cv_details where user_id=%s",(user_id,))
        
        myresult = mycursor.fetchall()
        
        tech=myresult[0][0]
        
        techskills=tech.split(",")
        
        soft=myresult[0][1]
        
        softskills=soft.split(",")
        
        lang=myresult[0][2]
        
        languages=lang.split(",")
        
        frame=myresult[0][3]
        
        frameworks=frame.split(",")
        
        cert=myresult[0][4]
        
        certifications=cert.split(",")
        
        retlist=techskills + softskills + languages + frameworks + certifications
        
        return retlist

    
def employability_index(user_id,job_id,courses,certifications):
    addeddata=getcvdata(user_id,courses,certifications)
    #print(addeddata)
    gotides=fetch_ides(job_id)
    scores=[]
    for x in range(0, len(gotides)):
        overall=finalfunc(addeddata, gotides[x])
        scores.append(overall)
        

    overallscore=sum(scores)/len(scores)
    return overallscore
    #print("Employability Index: ",int(overallscore))
    
args=sys.argv

def main():
    #Inputs[User_id, Job_type,Course_id_string,Certification_id_string]
    #gotscore=employability_index(1,54,"1","1")
    gotscore=employability_index(args[1],args[2],args[3],args[4])
    print(gotscore)
    #gotscore=employability_index(1,54,"","")

    
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:




