from recode import Recoder

recoder = Recoder('../tables/113 ICD-10 Recodes_cov.txt')
print(recoder)
codes = ['G20', 'C101', 'U07.1', 'U071']
for code in codes:
    print(recoder.get_codes(code))
