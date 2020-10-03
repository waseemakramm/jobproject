#!/usr/bin/env python
# coding: utf-8

# In[4]:


#!/usr/bin/env python
# coding: utf-8

# In[23]:


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


def getdata(user_id,cv_path,skillsfile_path):
    #mycursor = mydb.cursor()
    #mycursor.execute("SELECT file FROM bayt_data.payment where user_id=%s",(user_id,))
    #myresult = mycursor.fetchall()
    #print(myresult[0][0])

    #data = ResumeParser(str(myresult[0][0]), skills_file='C:\\xampp\\htdocs\\doanalytica\\web\\py\\bothskills - Copy.csv').get_extracted_data()
    #print(user_id)
    #cvpath="C:\\xampp\\htdocs\\doanalytica\\web\\uploads\\"+str(user_id)+".pdf"

    cvpath=str(cv_path) + str(user_id)+".pdf"
    #print(cvpath)
    skillsfilepath=str(skillsfile_path)
    data = ResumeParser(cvpath, skills_file=skillsfilepath).get_extracted_data()

    #data = ResumeParser(cvpath, skills_file='C:\\xampp\\htdocs\\doanalytica\\web\\py\\bothskills - Copy.csv').get_extracted_data()
    
    extskills=list(data.values())[3]
    #print(extskills)
    
    #Tech Skills
    mycursor1 = mydb.cursor()
    mycursor1.execute("SELECT tech_skills FROM bayt_data.payment where user_id=%s",(user_id,))
    myresult1 = mycursor1.fetchall()
    for x in myresult1:
        extskills.append(x)
        
    #Soft Skills
    mycursor2 = mydb.cursor()
    mycursor2.execute("SELECT soft_skills FROM bayt_data.payment where user_id=%s",(user_id,))
    myresult2 = mycursor2.fetchall()
    for x in myresult2:
        extskills.append(x)
    
    #lanuages
    mycursor3 = mydb.cursor()
    mycursor3.execute("SELECT prog_lang FROM bayt_data.payment where user_id=%s",(user_id,))
    myresult3 = mycursor3.fetchall()
    for x in myresult3:
        extskills.append(x)
    
    #frameworks
    mycursor4 = mydb.cursor()
    mycursor4.execute("SELECT frameworks FROM bayt_data.payment where user_id=%s",(user_id,))
    myresult4 = mycursor4.fetchall()
    for x in myresult4:
        extskills.append(x)
    
    #Certifications
    mycursor5 = mydb.cursor()
    mycursor5.execute("SELECT certifications FROM bayt_data.payment where user_id=%s",(user_id,))
    myresult5 = mycursor5.fetchall()
    for x in myresult5:
        extskills.append(x)
    
    
    return extskills


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
    
    for sk in skills:
        match_degree = 0
        n_Gram_list = get_ngrams(title, ngram )
        
        for gram in n_Gram_list:
            
            similarity_degree = fuzz.token_sort_ratio(sk, gram)
            
            if similarity_degree > match_degree:
                match_degree = similarity_degree
                match_skill = sk
                match_gram=gram
        dic[match_skill]=match_degree
        
    dic=sorted(dic.items(), key=lambda x: x[1], reverse=True)
    return dic

    
    
def getscore(factorpath, gotskills):
    
    loc = (factorpath) 
    # To open Workbook
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    
    forscore=[]
    j=0
    for i in range(1,10):
        if i==1:
            for x in range(1,153):
                if gotskills[:i][j][j]==sheet.cell_value(x,j):
                    forscore.append(gotskills[:i][j][1]*sheet.cell_value(x,1))
        else:
            for x in range(2,153):
                if gotskills[:i][i-1][j]==sheet.cell_value(x,j):
                    #print(sheet.cell_value(x,j))
                    forscore.append(gotskills[:i][i-1][1]*sheet.cell_value(x,1))
    
    
    score=sum(forscore)/len(forscore)
    return score

def savedata(user_id, detaillist,scores):
    test1=[]
    test2=[]
    for y in range(0,5):
        for x in range(1,10):
            test1.append(detaillist[y][:x][x-1][0])
        
        my_list = test1
        my_string = ','.join(my_list)
        test2.append(my_string)
        test1.clear()

    mycursor1 = mydb.cursor()
    #mycursor1.execute("SELECT user_id FROM bayt_data.cv_details where user_id=%s",(user_id,))
    mycursor1.execute("SELECT EXISTS(SELECT * FROM bayt_data.cv_details WHERE user_id=%s)",(user_id,))
    myresult1 = mycursor1.fetchall()
    gotid=myresult1[0][0]
    #gotid=myresult1
    #print(gotid)
    if gotid == 0:
        #print("null hai")
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO bayt_data.cv_details (user_id,tech_skills, soft_skills, programming_languages, programming_frameworks, certifications,tech_score,soft_score,lang_score,frame_score,cert_score,overall_score) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)",(user_id,test2[0],test2[1],test2[2],test2[3],test2[4],scores[0],scores[1],scores[2],scores[3],scores[4],scores[5]))
        mydb.commit()
    else:
        #print("null nahi hai")
        mycursor = mydb.cursor()
        mycursor.execute("UPDATE bayt_data.cv_details SET tech_skills = %s WHERE user_id = %s",(test2[0],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET soft_skills = %s WHERE user_id = %s",(test2[1],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET programming_languages = %s WHERE user_id = %s",(test2[2],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET programming_frameworks = %s WHERE user_id = %s",(test2[3],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET certifications = %s WHERE user_id = %s",(test2[4],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET tech_score = %s WHERE user_id = %s",(scores[0],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET soft_score = %s WHERE user_id = %s",(scores[1],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET lang_score = %s WHERE user_id = %s",(scores[2],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET frame_score = %s WHERE user_id = %s",(scores[3],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET cert_score = %s WHERE user_id = %s",(scores[4],user_id,))
        mycursor.execute("UPDATE bayt_data.cv_details SET overall_score = %s WHERE user_id = %s",(scores[5],user_id,))

        #mycursor.execute("INSERT INTO bayt_data.cv_details (user_id,tech_skills, soft_skills, programming_languages, programming_frameworks, certifications) VALUES (%s, %s, %s, %s, %s, %s)",(user_id,test2[0],test2[1],test2[2],test2[3],test2[4],))
        mydb.commit()

    

def getskillsdata():
    techskills=[]
    softskills=[]
    languages=[]
    frameworks=[]
    certs=[]
    mycursor = mydb.cursor()
    #techskills
    mycursor.execute("SELECT techskills FROM bayt_data.techskills")
    myresult1 = mycursor.fetchall()
    for a in myresult1:
        techskills.append(a[0])
    #softskills
    mycursor.execute("SELECT softskills FROM bayt_data.softskills")
    myresult2 = mycursor.fetchall()
    for b in myresult2:
        softskills.append(b[0])
        
    #languages
    mycursor.execute("SELECT languages FROM bayt_data.languages")
    myresult3 = mycursor.fetchall()
    for c in myresult3:
        languages.append(c[0])
    #frameworks
    mycursor.execute("SELECT frameworks FROM bayt_data.frameworks")
    myresult4 = mycursor.fetchall()
    for d in myresult4:
        frameworks.append(d[0])
    #certs
    mycursor.execute("SELECT certs FROM bayt_data.certs")
    myresult5 = mycursor.fetchall()
    for e in myresult5:
        certs.append(e[0])
    #print(techkills)
    return [techskills,softskills,languages,frameworks,certs]
    
def finalfunc(user_id,skilllist,ngram,cv_path,skillsfile):
    myskills=getdata(user_id,cv_path,skillsfile)
    extskills=' '.join(map(str, myskills))
    
    mycursor = mydb.cursor()
    
    gotskills=get_largest_match(extskills, skilllist, ngram)
    #print(gotskills)
    forscore=[]
    j=0
    for i in range(1,10):
        if i==1:
            forscore.append(gotskills[:i][j][1])
        else:
            forscore.append(gotskills[:i][i-1][1])
            
    score=sum(forscore)/len(forscore)
    return [score,gotskills];
    
    
def scores(user_id,cv_path,skillsfile):
    data=[]
    scores=[]
    skills=getskillsdata()
    for x in range (0,5):
        gotdata=finalfunc(user_id,skills[x],2,cv_path,skillsfile)
        data.append(gotdata[1])
        scores.append(gotdata[0])
        
    score=sum(scores)/len(scores)
    scores.append(score)
    savedata(user_id,data,scores)
    return scores
    

    
args=sys.argv    
   
def main():
    #print(args[1])

    print(scores(args[1],args[2],args[3]))
    #print(scores(5))

    
    
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:




