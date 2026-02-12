from Bio.Seq import Seq

def complement(dna_seq):
    ans = ''
    a={'A':'T',"T":"A","G":'C','C':'G'}
    for base in dna_seq:
        ans+=a[base]
    return ans

def reverse_complement(dna_seq):
    ans = ''
    a={'A':'U',"T":"A","G":'C','C':'G'}
    for base in dna_seq:
        ans+=a[base]
    
    return ans[::-1]

def main():
    seq="AGTACACTGGT"
    ans=reverse_complement(seq)
    print(ans)
    my_dna = Seq("AGTACACTGGT")
    ans = my_dna.complement()
    print(ans)

if __name__ == "__main__":
    main()
