#!usr/bin python
#-*- coding: utf-8 -*-

__author__ = "Students of bioinformatics @ AMU, Poznan"


'''
ALGORITHM:

-all unwanted elements are removed from xml file (picture links, additional informations about methods, etc.)
-particular sections are chosen
-remaining text is divided into words; as a result a list of 3-element tupples (article PMID, section number, word)
is produced
-stopwords and punctuation marks are being removed; words are being changed to their derivational bases.
-there is a possibility of applying functions selecting all words regarding one article or section.
This enables counting the frequency of the word presence in the whole article and also section PMID+nr value for all
articles containing querried word.
'''

from BeautifulSoup import BeautifulSoup as bs
import Stemmer
import string
import re

class XmlParser():
    important_parts_list = ['article-title', 'abstract', 'body']
    list_of_punctuation = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
    
    def encode_list(self, list):
        """
	Decodes the list of words from utf-8
	"""
        list = [x.encode("utf-8") for x in list]
        return list

    def into_stems(self, words):
        stemmer = Stemmer.Stemmer('english')
        stems = []
        for w in words:
            stems.append(stemmer.stemWord(w))
        #print stems
        return stems

    def remove_digits(self, list):
        """
	Removes numbers that exist separetly.
	"""
        word_list = []
        for word in list:
            word_no_digit = re.sub(r"\b\d+\b", "", word)
            word_list.append(word_no_digit)
        return word_list

    def lower_words(self, list):
        list = [x.lower() for x in list]
        return list

    def replace_punc(self, list):
        """
	Removes punctuation marks from the begining and end of the string and non-standard
	marks starting with &#x that exist separetly.
	"""
        word_list = []
        for word in list:
            word_no_punc0 = re.sub("^&#x.*","", word)
            word_no_punc1 = re.sub("^\W*()","", word_no_punc0)
            word_no_punc2 = re.sub("()\W*$","", word_no_punc1)
            word_list.append (word_no_punc2)
        return word_list

    def get_important_parts(self, important_parts_list, xml_doc):
        """
	Gets only those elements that are important to search informations from articles with similar subject matter.
	"""

        important_tags = xml_doc.findAll(important_parts_list)
        xml_doc_important = ''
        for tag in important_tags:
            xml_doc_important += str(tag)
        return bs(xml_doc_important)
        
    def get_paragraphs(self, xml_doc_important):
        """
	Divides xml text into sections.
	"""
        return xml_doc_important.findAll('p')[0:6]
        
    def get_text_from_paragraphs(self, paragraphs_list, bs_doc):
        """
	Returns a list of elements corresponding to list of words from particular section.
	"""
        words_in_paragraph_list = []
        i=0
        for paragraph in paragraphs_list:
            try:
                pmid_in_bracket = bs(str(bs_doc.findAll(attrs = {'pub-id-type':'pmid'})[0])).findAll(text=True)
            except:
                pmid_in_bracket = bs(str(bs_doc.findAll(attrs = {'pub-id-type':'pmc'})[0])).findAll(text=True)
            pmid = str(pmid_in_bracket[0].encode("utf-8"))
            words_in_one_paragraph = []
            #print paragraph
            for text in paragraph.findAll(text=True):
                words = text.split()
                encoded = self.encode_list(words)
                cleaned = self.remove_digits(encoded)
                lowered = self.lower_words(cleaned)
                replaced = self.replace_punc(lowered)
                stems = self.into_stems(replaced)
                for word in stems:
                     words_in_one_paragraph.append(word)
            i+=1
            words_in_paragraph_list.append((pmid, i, words_in_one_paragraph))
        return words_in_paragraph_list

    def stopwords(self, stopwords_file):
        """
	Creates a list with stopwords.
	"""
        swords_file = open(stopwords_file, 'r').read().split(",")
        swords_list = []
        for word in swords_file:
            word = word.strip()
            title_like_word = word.title()
            swords_list.append(word)
            swords_list.append(title_like_word)
        return swords_list

    def remove_junk(self, words_list):
	"""
	Removes stopwords and punctuation marks.
	"""
	swords_list = self.stopwords('stopwords2.txt')
	punctuation_list = self.list_of_punctuation
	junk_list = swords_list + punctuation_list
        for wrong_word in junk_list:
            for tuple_el in words_list:
		for word in tuple_el[2]:
		    if wrong_word == word:
		        #print word
		        tuple_el[2].remove(word)
	return words_list
        
'''
if __name__ == '__main__':
xml = XmlParser()
xml_doc = open('plos.nxml','r').read()
bs_doc = bs(xml_doc)
xml_doc_important = xml.get_important_parts(xml.important_parts_list, bs_doc)
paragraphs_list = xml.get_paragraphs(xml_doc_important)
cleaned_tuples = xml.remove_junk(xml.get_text_from_paragraphs(paragraphs_list))
print cleaned_tuples
''' 