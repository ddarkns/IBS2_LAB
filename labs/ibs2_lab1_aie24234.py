from Bio.Seq import Seq

def complement(dna_seq):
    ans = ''
    a={'A':'T',"T":"A","G":'C','C':'G'}
    for base in dna_seq:
        ans+=a[base]
    return ans

def reverse_complement(dna_seq):
    ans = ''
    a={'A':'T',"T":"A","G":'C','C':'G'}
    for base in dna_seq:
        ans+=a[base]
    return ans[::-1]

def transcription(dna_seq):
    ans = ''
    a={'A':'A',"T":"U","G":'G','C':'C'}
    for base in dna_seq:
        ans+=a[base]
    return ans


def translate_rna_to_protein(rna_sequence):
  codon_table={
      'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
      'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
      'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',
      'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
      'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
      'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
      'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
      'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
      'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',
      'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
      'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
      'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
      'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
      'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
      'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
      'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
  }

  protein_sequence = ""
  for i in range(0, len(rna_sequence), 3):
    codon = rna_sequence[i:i+3]
    
    if len(codon) < 3:
      break
    
    amino_acid=codon_table.get(codon)
    if amino_acid == '*':
      break
    
    if amino_acid is not None:
      protein_sequence += amino_acid
  return protein_sequence


def main():
    dna_sequence = "GTAGCCATGGCGCCCAGAACTGAGATCAATAGTACCCGTAGTA"
    print("orignal seq: ",dna_sequence)
    ans=reverse_complement(dna_sequence)
    print("after reverse compliment seq: ",ans )
    ans=transcription(ans)
    print("after transctipion: ",ans)
    protein_sequence = translate_rna_to_protein(ans)
    print("after transilation the protein sequence : ",protein_sequence)

if __name__ == "__main__":
    main()


