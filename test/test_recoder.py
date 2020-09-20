from recode import Recoder

recoder = Recoder('../tables/358 ICD-10 Recodes.txt')
print(recoder)
print(recoder.get_codes('G20'))
print(recoder.get_codes('C101'))
