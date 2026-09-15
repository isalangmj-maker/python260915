#튜플과세트형식.py

tp=(100,200,300)
print(len(tp))
print(tp.count(300))
print(tp.index(200))

#한방에 입력
print("id:%s, name:%s" % ("kim","김유신"))

#여려개를 리턴
def times(a,b):
    return a+b, a*b

#호출
result = times(3,4)
print(result)

#형식변환(type casting)
a = list((1,2,3))
a.append(4)
print(a)
b = set(a)
print(b)

#Dict 형식(사전식)
print('\n')

fruits={"apple":10,"kiwi":20}

fruits["banana"]=50
print(fruits)

fruits["apple"]=15
del fruits["kiwi"]
print(fruits)

for item in fruits.items():
    print(item)

print('\n')
