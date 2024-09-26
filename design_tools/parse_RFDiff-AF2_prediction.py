import sys
import re

def extract_ids(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    lines = content.split('\n')
    ids = []

    # /storage/home/wkl2/u1o/default/wkl2/240417_CDK9/DESIGN9/slurm-10935666.out:Tag: unguided_design_ppi_50-70aa_91_dldesign_0 finished AF2 prediction in 18.882733151083812 seconds
    for i, line in enumerate(lines):
        pattern = r'/DESIGN(\d+)/'
        match = re.search(pattern, line)
        if match:
            ids.append("DESIGN" + str(match.group(1)) + ":" + line.split()[1])

    return ids

def extract_pae_interactions(file_path, ids, plddt_threshold):
    with open(file_path, 'r') as file:
        content = file.read()

    #/projects/bbse/wklai/00_proteinDesign/TESTDIR/DESIGN0/slurm-2842697.out:{'plddt_total': 82.91436736940761, 'plddt_binder': 43.43945510606657, 'plddt_target': 97.01255032060084, 'pae_binder': 12.918124, 'pae_target': 2.785919, 'pae_interaction': 28.09891700744629, 'binder_aligned_rmsd': 7.8659573, 'target_aligned_rmsd': 26.045813, 'time': 111.03088777093217}

    pattern = r"{'plddt_total': \d+\.\d+, 'plddt_binder': (\d+\.\d+), 'plddt_target': \d+\.\d+, 'pae_binder': \d+\.\d+, 'pae_target': \d+\.\d+, 'pae_interaction': (\d+\.\d+), 'binder_aligned_rmsd': \d+\.\d+, 'target_aligned_rmsd': \d+\.\d+, 'time': \d+\.\d+}"
    matches = re.findall(pattern, content)

    if len(matches) != len(ids):
        print("Error: Number of matches doesn't match number of IDs.")
        print("Matches: " + str(len(matches)) + "\tIDs: " + str(len(ids)))
        sys.exit(1)

    pae_interactions = {ids[i]: {'plddt_binder': float(match[0]), 'pae_interaction': float(match[1])} for i, match in enumerate(matches) if float(match[0]) > plddt_threshold}

    return pae_interactions

def write_output(output_path, data):
    with open(output_path, 'w') as output_file:
        for item in data:
            output_file.write(f"{item[0]}\t{item[1]['pae_interaction']}\t{item[1]['plddt_binder']}\n")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python parse_RFDiff-AF2_prediction.py <RF_id.tab> <RF_score.tab> <plddt_binder threshold> <output_path>")
        sys.exit(1)

    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    plddt_threshold = float(sys.argv[3])
    output_path = sys.argv[4]

    ids = extract_ids(file1_path)
    pae_interactions = extract_pae_interactions(file2_path, ids, plddt_threshold)

    sorted_data = sorted(pae_interactions.items(), key=lambda x: x[1]['pae_interaction'])
    write_output(output_path, sorted_data)

