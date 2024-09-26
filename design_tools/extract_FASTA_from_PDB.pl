#!/usr/bin/perl

die "PDB_File\tFASTA_Output\n" unless $#ARGV == 1;
my($input, $output) = @ARGV;

open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUT, ">$output") or die "Can't open $output for writing!\n";

@HEADER = split(/\//, $input);
print OUT ">$HEADER[$#HEADER]\n";

# Define a hash to map 3-letter codes to 1-letter codes
my %three_to_one = (
    'ALA' => 'A', 'ARG' => 'R', 'ASN' => 'N', 'ASP' => 'D',
    'CYS' => 'C', 'GLN' => 'Q', 'GLU' => 'E', 'GLY' => 'G',
    'HIS' => 'H', 'ILE' => 'I', 'LEU' => 'L', 'LYS' => 'K',
    'MET' => 'M', 'PHE' => 'F', 'PRO' => 'P', 'SER' => 'S',
    'THR' => 'T', 'TRP' => 'W', 'TYR' => 'Y', 'VAL' => 'V'
);

# ATOM      1  N   VAL A   1     -16.906   9.685  -7.200  1.00  0.00           N
# ATOM      2  CA  VAL A   1     -15.458   9.769  -7.362  1.00  0.00           C
# ATOM      3  C   VAL A   1     -14.806  10.109  -6.024  1.00  0.00           C
# ATOM      4  O   VAL A   1     -15.243  11.031  -5.331  1.00  0.00           O
# ATOM      5  CB  VAL A   1     -15.067  10.817  -8.428  1.00  0.00           C
# ATOM      6  CG1 VAL A   1     -13.548  10.901  -8.571  1.00  0.00           C
# ATOM      7  CG2 VAL A   1     -15.715  10.481  -9.770  1.00  0.00           C
# ATOM      8 1H   VAL A   1     -17.328   9.462  -8.079  1.00  0.00           H

$currentChain = "";
$sequence = "";
while($line = <IN>) {
    chomp($line);
    # Extract the chain ID and amino acid sequence

    $ATOM = substr $line, 13, 2;
    #print $ATOM,"\n";
    $CHAIN = substr $line, 21, 1;
    if($ATOM eq "CA") {
        $AA = substr $line, 17, 3;
        my $aa_1 = $three_to_one{$AA};
        #print $aa_1,"\n";
        if ($CHAIN eq "A") {
            $sequence .= $aa_1;
        }
    }
}

close IN;

# Print the extracted sequence
print OUT "$sequence\n";
