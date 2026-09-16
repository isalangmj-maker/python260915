
strA = "파이썬은 정말 강력크 하다"
i = 100
j = 3.14
print(strA, i, j)
print(len(strA), len(str(i)), len(str(j)))
print(dir())
print("""
파이썬
내가
정복하고 말거야!
""")
print("파\n이\n썬\n내가 \\정복하고 말거야!")
print(strA[2])
print(strA[0:5])
print(strA[-5:])

colors = ["red", "green", "blue"]
print(colors,type(colors))
colors.append("white")
print(colors)
colors.insert(1,"black")
print(colors)
colors.remove("blue")
print(colors)
# colors.pop()
# print(colors)
colors.pop(0)
print(colors)
colors.reverse()
print(colors)