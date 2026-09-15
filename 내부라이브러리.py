#내부라이브러리.py

import os
import os.path
import glob

#raw string notation; r
fName = r"C:\python313\python.exe"

if os.path.exists(fName):
    print(f"{fName}파일의 크기 : {os.path.getsize(fName)} 바이트")
else:
    print(f"{fName} does not exist")

#print(glob.glob(r"C:\python313"))