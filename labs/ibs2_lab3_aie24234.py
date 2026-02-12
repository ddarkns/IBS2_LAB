aa={'g': 57,'a': 71,'s': 87,'p' :97,'v' :99,'t' :101,'c' :103,'I' :113,'l':113,'n' :114,'d' :115,'k':128,'q' :128,
'e'  :129, 
'm' :131,
'h' :137,
'f' :147,
'r' :156,
'y' :163,
'w' :186,}
def mass(Peptide):
    mass=0
    for i in Peptide:
        mass+=aa[i]
    return mass


def start(seq,spectrum,aa):
    for i in spectrum:
        for k in aa:
            if aa[k]==i:
               if k in seq:
                   continue
               seq.append([k])
    return seq
            
def Expand(seq,Spectrum,aa):
    for i in range(0,len(seq)):
        for k in aa:
            if mass(seq[i]+[k]) in spectrum:
                seq.append(seq[i]+[k])
                seq.remove(seq[i])
    return seq


                    
spectrum = [0,97,97,99,101,103,196,198,198,200,202,295,297,299,301,394,396,398,400,400,497]           
ans=0
CandidatePeptides=start([],spectrum,aa)
for i in range(0,5):
    CandidatePeptides = Expand(CandidatePeptides,spectrum,aa)
for i in CandidatePeptides:
    max_count = max(i.count(element) for element in set(i))
    print(max_count)
    if max_count>=3:
        continue
    else:
        ans=i
print(ans)
        