#!/usr/bin/perl

die "Target_FASTA\tBinder_FASTA\tOutput_Path\n" unless $#ARGV == 2;
my($target, $binder, $output) = @ARGV;
open(TAR, "<$target") or die "Can't open $target for reading!\n";

$targetProt = "";
while($line = <TAR>) {  $targetProt .= $line; }
close TAR;

@ARRAY = split(/\//, $binder);
@ID = split(/\./, $ARRAY[$#ARRAY]);
#print $ID[0]."\n";

open(BIN, "<$binder") or die "Can't open $binder for reading!\n";
$COUNTER = 1;
while($line = <BIN>) {
        chomp($line);
        if($line =~ ">") {
                open(OUT, ">$output/$ID[0]\_ESM-$COUNTER\.fasta") or die "Can't open $ID[0]\_ESM-$COUNTER\.fasta for writing!\n";
                print OUT ">$ID[0]\_ESM-$COUNTER\n";
                $line = <BIN>;
                print OUT $line;
                print OUT $targetProt;
                close OUT;
                $COUNTER++;
        }
}
close BIN;
