#!usr/bin python
#-*- coding: utf-8 -*-

__author__ = "Bioinformatyka V, UAM, Poznań"

import MySQLdb as my
from BeautifulSoup import BeautifulSoup as bs
from xml_parser6c import * 
import sys, os
import Stemmer


def parsing_file(f_n):
    '''Function that parse the given file and return list of touples.'''
    
    xml = XmlParser()
    xml_doc = open(f_n,'r').read()
    bs_doc = bs(xml_doc)
    xml_doc_important = xml.get_important_parts(xml.important_parts_list, bs_doc)
    paragraphs_list = xml.get_paragraphs(xml_doc_important)
    cleaned_tuples = xml.remove_junk(xml.get_text_from_paragraphs(xml_doc_important, bs_doc))
    #returns one list of touples from one .nxml file
    return cleaned_tuples
    
    

def getting_files():
    '''Function that takes .nxml files and parse it with xml_parser.'''
    
    dir_cont = os.listdir('.')
    pars_res = []

    for f in dir_cont:
	extension = os.path.splitext(f)[1]
	#take only .nxml files
	if extension == '.nxml':
	      pars_res = pars_res + parsing_file(f)
	else: pass
    #returns big list of all touples from all .nxml files from current directory
    #print pars_res
    return pars_res
    
    

def ltouple2ltoupdict(all_t):
    '''Function prepares the list of touples to insert into database.'''
    
    mega_list = []

    for parag in all_t:
	pmid_nrp = str(parag[0]) + '_' + str(parag[1])
	w_dict = {}
	for i in parag[2]:
	    #omitt empty ones
	    if i != '':
		#ommiting redundants & counting words
		#w_dict[i] = w_dict.setdefault(i, 0)+1
		if i not in w_dict.keys():
		    w_dict[i] = 1
		else:	        
		    w_dict[i] = w_dict[i] + 1
	    else: pass
	mega_list.append((pmid_nrp,w_dict))
    #print mega_list
    return mega_list
    
    

def insert2tab1(m_l):
    '''Function inserts the values into the paragrah and word tables in bioinfodb.'''
    
    temp = []
    for el in m_l:  
	text = ''
	for i in el[1].keys():
	    if i not in temp: 
		  temp.append(i)
	    #creating word_list to insert into table
	    text = text + i + ','
	    c.execute("INSERT INTO wcount (PMID_PNR, WORD, NRPARAGAPPEARANCE) VALUES (%s, %s, %s)" , (el[0], i, el[1][i]))
	#c.execute("INSERT INTO paragraphs (PMID_PNR, WORD_LIST) VALUES (%s, %s)" , (el[0], text[:-1]))
    #print temp
    return temp
    
    

def insert2tab2(t_l, ml):
    '''Function inserts values into the wcount table in bioinfodb.'''
    
    pl_text= ''
    app_c = 0
    fin_list = []

    for j in t_l: 
	for p in ml: 
	    if j in p[1].keys():
		#creating pmid_list to insert into table
		pl_text = pl_text + str(p[0]) + ','
		#caunting word appearance in all base (or PubMed) 
		app_c = app_c + p[1][j]
	fin_list.append((j, pl_text[:-1], app_c))
	pl_text= ''
	app_c = 0


    #for el1, el2, el3 in fin_list:
	#c.execute("INSERT INTO words (WORD, PMID_LIST, NRALLAPPEARANCE) VALUES (%s, %s, %s)" , (el1, el2, el3))     



if __name__ == '__main__':
  '''Main function that connects to bioinfodb, parses the .nxml files and insert values into db. '''
  
  try:
      #DB connection
      db = my.connect(host='localhost', user='root', passwd='bioinfo5', db='bioinfodb')
      c = db.cursor() 
      getting_files()
      alltouples = getting_files()
      prep_toup = ltouple2ltoupdict(alltouples)
      t = insert2tab1(prep_toup)
      insert2tab2(t, prep_toup)
      db.commit()  
      #DB connection closed
      c.close()
      db.close() 
      
  except my.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)