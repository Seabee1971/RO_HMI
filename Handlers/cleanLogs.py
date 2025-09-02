import os
import glob
os.chdir(r'c:\Users\ShaneP\Documents\Coding\Python\RO_HMI')
print(os.getcwd())
def check_for_logfiles():
   for file in glob.glob("*.log"):
        os.remove(file)
        print(f' Deleted: {file}')

