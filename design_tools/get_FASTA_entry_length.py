# script_no_module.py

import sys

def get_first_sequence_length(file_path):
    with open(file_path, 'r') as file:
        sequence_started = False  # Flag to indicate the start of a sequence
        sequence = ''

        # Read line by line
        for line in file:
            line = line.strip()

            if line.startswith('>'):
                if sequence_started:
                    # If a sequence has already been captured, break
                    break
                sequence_started = True  # Set flag to start capturing sequence
                continue

            if sequence_started:
                sequence += line

        length = len(sequence)
        return length

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_FASTA_entry_length.py input.fasta")
        sys.exit(1)

    file_path = sys.argv[1]
    length = get_first_sequence_length(file_path)
    print(length)

