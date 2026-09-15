#클래스연습.py

#1)클래스 정의

class Person:
    #초기화 매소드
    def __init__(self):
        self.name = "default name"
    def print(self):
        print("My name is {0}".format(self.name))

#2)인스턴스 생성
p1 = Person()
p2 = Person()
p2.name = "홍길동"
#3)메소드 호출
p1.print()
p2.print()

print("="*50)

strName = "Not Class Member"

class DemoString:
    def __init__(self):
        self.strName = "" 
    def set(self, msg):
        self.strName = msg
    def print(self):
        print(self.strName)

d = DemoString()
d.set("First Message")
d.print()

print("="*50)

#클래스 연습 self

class BankAccount:
    def __init__(self,id,name,bal):
        self.id = id
        self.name = name
        self.__bal = bal
    def deposit(self,amt):
        self.__bal += amt
    def withdraw(self,amt):
        self.__bal -= amt
    def __str__(self):
        return "id : {0}, name : {1}, bal : {2}".format(self.id,self.name,self.__bal)


account1 = BankAccount(1004,"홍길동",1234000)
account1.deposit(111)
print("1:", account1)
account1.bal = 888
print("2:", account1)

print("="*50)

def add_many(*args):
    result = 0
    for i in args:
        result += i
    return result

print(add_many(1,2,7,80))

print("="*50)

a=input()
print(a)