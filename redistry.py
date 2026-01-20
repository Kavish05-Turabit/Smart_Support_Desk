def Missing_And_Repeating(arr):
    missing, repeating = 0,0
    l = [0] * (len(arr) + 1)
    for i in arr:
        l[i] += 1
    for i in range(len(arr)+1):
        if l[i] == 0:
            missing = i
        if l[i] == 2:
            repeating = i
    return missing,repeating


m,r = Missing_And_Repeating([2,2])
print(m,r)