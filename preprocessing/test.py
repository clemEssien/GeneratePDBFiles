import Bio.PDB
import numpy

def calc_residue_dist(residue_one, residue_two) :
    """Returns the C-alpha distance between two residues"""
    diff_vector  = residue_one["CA"].coord - residue_two["CA"].coord
    return numpy.sqrt(numpy.sum(diff_vector * diff_vector))

def calc_dist_matrix(chain_one, chain_two) :
    """Returns a matrix of C-alpha distances between two chains"""
    answer = numpy.zeros((len(chain_one), len(chain_two)), numpy.float)
    for row, residue_one in enumerate(chain_one) :
        for col, residue_two in enumerate(chain_two) :
            answer[row, col] = calc_residue_dist(residue_one, residue_two)
    return answer


RES_DIR = "../resource/pdb_files/"
structure = Bio.PDB.PDBParser().get_structure("1XI4", RES_DIR+"1XI4.pdb")
model = structure[0]

dist_matrix = calc_dist_matrix(model["D"], model["M"])

contact_map = dist_matrix < 12.0
print(contact_map)