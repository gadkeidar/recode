# recode

Converts ICD-10 codes to CDC/NCHS Selected Causes of Death codes. 

* ICD-10 stands for International Classification of Diseases v.10.
* CDC stands for Centers for Diseases Control and Prevention.
* NCHS stands for National Center for Health Statistics.

To install run:
```
pip install icd10_c2cdc
```

How this can be used:
```
    from icd10_c2cdc import Recoder
    recoder = Recoder('tables/358 ICD-10 Recodes.txt')  # Read about tables below
    print(recoder)  # Prints a tree of the recodes' hierarchy
    print(recoder.get_codes('G20'))  # Prints related Causes of Death codes: ['18500', '18800']
```

Recoder is based on NCHS text files that were downloaded from [ResDAC](https://www.resdac.org/search-data-variables?name=icd-10%20cause%20of%20death%20recodes), each file is a table that specify the grouping classification for each ICD-10 code. 
These files had a few errors (for example, some "1" were mistakenly typed as the letter "l"), which we fixed.
Download the fixed tables from [tables](https://github.com/gadkeidar/recode/tree/master/tables).   
