amino_acid_masses = [
    57, 71, 87, 97, 99, 101, 103,
    113, 114, 115, 128, 129,
    131, 137, 147, 156, 163, 186
]

def expand(peptides):
    expanded = []
    for peptide in peptides:
        for mass in amino_acid_masses:
            expanded.append(peptide + [mass])
    return expanded

def mass(peptide):
    return sum(peptide)

def linear_spectrum(peptide):
    spectrum = [0]  
    for i in range(len(peptide)):
        current_sum = 0
        for j in range(i, len(peptide)):
            current_sum += peptide[j]
            spectrum.append(current_sum)
    return sorted(spectrum)

def cyclic_spectrum(peptide):
    spectrum = [0]
    peptide_mass = sum(peptide)
    length = len(peptide)
    
    extended = peptide + peptide  
    
    for i in range(length):
        current_sum = 0
        for j in range(i, i + length - 1):
            current_sum += extended[j]
            spectrum.append(current_sum)
    
    spectrum.append(peptide_mass)
    return sorted(spectrum)

def is_consistent(peptide, spectrum):
    peptide_spectrum = linear_spectrum(peptide)
    
    spectrum_copy = spectrum.copy()
    
    for mass_value in peptide_spectrum:
        if mass_value in spectrum_copy:
            spectrum_copy.remove(mass_value)
        else:
            return False
    return True

def cyclopeptide_sequencing(spectrum):
    
    candidate_peptides = [[]]
    final_peptides = []
    parent_mass = max(spectrum)
    
    while candidate_peptides:
        
        candidate_peptides = expand(candidate_peptides)
        
        peptides_copy = candidate_peptides[:]
        
        for peptide in peptides_copy:
            
            if mass(peptide) == parent_mass:
                
                if cyclic_spectrum(peptide) == sorted(spectrum):
                    if peptide not in final_peptides:
                        final_peptides.append(peptide)
                
                candidate_peptides.remove(peptide)
            
            elif not is_consistent(peptide, spectrum):
                candidate_peptides.remove(peptide)
    
    return final_peptides

spectrum = [0, 113, 128, 186, 241, 299, 314, 427] 

result = cyclopeptide_sequencing(spectrum)

print("Final Peptides:\n")
for peptide in result:
    print("-".join(map(str, peptide)))
