from Bio.PDB import PDBParser
from Bio.PDB.NeighborSearch import NeighborSearch
import sys

def find_interaction_surface(pdb_file, cutoff):
    """Finds the interaction surface between all chain pairs in a PDB file.

    Args:
        pdb_file (str): Path to the PDB file.
        cutoff (float): Distance cutoff for defining an interaction.

    Returns:
        dict: A dictionary with chain pair keys and their respective interacting residues.
    """

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", pdb_file)
    
    # Get a list of chains and their IDs
    chains = list(structure[0].get_chains())
    chain_ids = [chain.id for chain in chains]
    
    # Dictionary to store interaction results
    all_interactions = {}

    # Iterate over all chain pairs
    for i in range(len(chain_ids)):
        for j in range(len(chain_ids)):
            if i != j:  # Avoid self-interaction
                chain_a = chains[i]
                chain_b = chains[j]

                atoms_a = list(chain_a.get_atoms())
                atoms_b = list(chain_b.get_atoms())

                
                # Use NeighborSearch to find interactions
                ns = NeighborSearch(atoms_a)
                interacting_residues = {}

                for atom_b in atoms_b:
                    #print(atom_b.get_full_id())
                    neighbors = ns.search(atom_b.coord, cutoff, level='R')
                    #print(neighbors)
                    for neighbor in neighbors:
                        n=str(neighbor)
                        #print(neighbor)
                        #residue = neighbor.get_parent()
                        #print(residue)
                        #if residue.id[0] != " ":  # Exclude heteroatoms
                        start = n.find('<Residue ') + len('<Residue ')
                        end = n.find(' het=', start)
                        aa= n[start:end]
                        pos= n.split('resseq=')[1].split(' icode= >')[0]
                        interacting_residues[pos]=aa   

                # Store results for the current chain pair
                pair_key = f"{chain_ids[i]} to {chain_ids[j]}"
                all_interactions[pair_key] = interacting_residues

    return all_interactions

if __name__ == "__main__":
    pdb_file = sys.argv[1]
    interactions = find_interaction_surface(pdb_file)

    for pair, residues in interactions.items():
        print(f"Interaction between {pair}:")
        residue_list = [int(x) for x in list(residues.keys())]
        residue_list_sorted = sorted(residue_list)
        print(residue_list_sorted)
        print(f"Number of interacting residues: {len(residues)}")
        print()

    

