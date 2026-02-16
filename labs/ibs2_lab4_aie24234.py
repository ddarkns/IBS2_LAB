import numpy as np
seq1 = "CGTGAATTCAT"
seq2 = "GACTTAC"

a = len(seq1)
b = len(seq2)

m = a+1
n = b+1
print("m: ",m,"n: ",n)
# m x n matrix
ans = np.zeros((n, m))
print(ans)
sum=0
gap=-1
match=1
mismatch = -1
for i in range(1,n):
    sum+=gap
    ans[i][0]=sum
sum=0
for i in range(1,m):
    sum+=gap
    ans[0][i]=sum
    
print(ans)

for i in range(1,n):
    for j in range(1,m):
        if seq1[j-1]==seq2[i-1]:
            match=1
        else:
            match=-1
        ans[i][j] = max(ans[i-1][j]+gap,ans[i][j-1]+gap,ans[i-1][j-1]+match)
print(ans)
final=[]
i=n-1
j=m-1

while i>=0 and j>=0:
    if seq1[j-1]==seq2[i-1]:
        final.append(int(ans[i][j]))
        i-=1
        j-=1
    elif seq1[j-2]==seq2[i-1]:
        final.append(int(ans[i][j]))
        if ans[i][j-1]>ans[i-1][j-1]:
            j-=1
        else:
            i-=1
            j-=1
    elif seq1[j-1]==seq2[i-2]:
        final.append(int(ans[i][j]))
        if ans[i-1][j]>ans[i-1][j-1]:
            i-=1
        else:
            i-=1
            j-=1
    else:
        i-=1
        j-=1
if i>0:
    while i>=0:
        i-=1
        final.append(int(ans[i][0]))
        
        
if j>0:
    while j>=0:
        j-=1
        final.append(int(ans[0][j]))
        
final.pop()
print(final)
        