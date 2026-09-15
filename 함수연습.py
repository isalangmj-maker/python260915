#함수연습
#1)함수 정의
def times(a,b):
    return a*b

#2)함수를 호출
result = times(3,4)
print(result)

#전역변수
x=5

def func(a):
    #지역변수
    #x=11
    return x+a

print(func(2))

#연습
print('\n')
def setValue(newValue):
    x = newValue
    print("지연변수 x=",x)

retValue = setValue(5)
print(retValue)
print(setValue(9))
print(retValue)