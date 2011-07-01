#!usr/bin python
#-*- coding: utf-8 -*-

__doc__ =  "Program that enable usage of functions from statisticdb.py - running query, collecting data from database, displaying resulats and calculating z-score."
__author__ = "Bioinformatyka V, UAM, Poznań"

from statisticdb import *
import time
   
try:
    # DB connection
    db = my.connect(host='localhost', user='nazwa_uzytkownika', passwd='haslo', db='bioinfo')
    db_cursor = db.cursor()
    
    # Display some records from database
    wanted_word = raw_input("Podaj slowo-query: ")
    cutoff_v = input("Podaj wartosc graniczna wystapien slow powyzej ktorej dane slow bedzie brane pod uwage w statystykach.\n Wartosc graniczna: ")
    word_after = stem(wanted_word)
    file = open("Statistics_res.txt","a")
    list_p = show_words_from_table_words(word_after, db_cursor, wanted_word, file)    
    
    # Words statistic
    show_words_from_paragraphs(list_p, cutoff_v, db_cursor, file)
    
    start = time.time()
    
    #Display highest z-score
    all_words = all_words_list(word_after, db_cursor)
    all_zscores = []
    for correlated_word in all_words:
        result = zscore(word_after, correlated_word, db_cursor, file)
        if type(result) == tuple:
            zscore_val, pmid_list = result[0], result[1]
            all_zscores.append((zscore_val, correlated_word, pmid_list))
    all_zscores.sort()
    all_zscores.reverse()
    
    stop = time.time()

    head_msg = '\n10 slow skorelowanych ze slowem %s z zapytania o najwyzszej wartosci z-score.\n' %(wanted_word)
    print head_msg
    file.write(head_msg)
    
    for el in all_zscores[:10]:
        msg = 'Skorelowane slowo: %s,\n wartosc z-score: %f,\n pmid_paragraf, w ktorych wystepuja slowo szukane i slowo skorelowane: %s\n' %(el[1], el[0], str(el[2]))
        print msg
        file.write(msg+'\n')
    
    time_proc = '\nCzas obliczenia z-score wynosi: ' + str(stop-start)
    print time_proc
    file.write(time_proc)
    
    '''
    # Display z-score - calculated for 2 words 
    correlated_word = raw_input('Podaj skorelowane slowo, do slowa z zapytania: ')
    correlated_word_after = stem(correlated_word)
    print zscore(word_after, correlated_word_after, db_cursor, file)
    '''
    
    file.close()
    
    # DB connection close
    db_cursor.close()
    db.close()

except my.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
