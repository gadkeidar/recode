# recode

recode.py converts ICD-10 codes to CDC/NCHS Selected Causes of Death codes. 

ICD-10 stands for International Classification of Diseases v.10.

CDC stands for Centers for Diseases Control and Prevention.

NCHS stands for National Center for Health Statistics.

The folder "tables" has the text files that specify the grouping classification for each ICD-10 code. These files have been downloaded from here:
https://www.resdac.org/search-data-variables?name=icd-10%20cause%20of%20death

The text files available online had a few errors (for example, some "1" were mistakenly typed as the letter "l"). We have already fixed those.

test_recoder.py, in folder "test", provides an example on how this code can be used.

Requires Python 3.8+.

