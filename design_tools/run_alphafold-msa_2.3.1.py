#!/usr/bin/python3

"""Singularity launch script for Alphafold."""

import os
from subprocess import run
import sys

def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Run AlphaFold structure prediction using singularity image.')

    parser.add_argument('--fasta_paths', required=True, help='Paths to FASTA files, each containing a prediction target that will be folded one after another. If a FASTA file contains multiple sequences, then it will be folded as a multimer. Paths should be separated by commas. All FASTA paths must have a unique basename as the basename is used to name the output directories for each prediction.')
    parser.add_argument('--gpu_devices', default=os.environ.get('SGE_GPU', '0'), help='Comma separated list GPU identifiers to set environment variable CUDA_VISIBLE_DEVICES.')
    parser.add_argument('--use_gpu_relax', type=str_to_bool, default=True, help='Whether to do OpenMM energy minimization using GPU.')
    parser.add_argument('--output_dir', default='/storage/group/u1o/default/vvm5242/temp', help='Path to a directory that will store the results.')
    parser.add_argument('--data_dir', default='/storage/icds/RISE/sw8/alphafold/alphafold_2.3_db', help='Path to directory with supporting data: AlphaFold parameters and genetic and template databases. Set to the target of download_all_databases.sh.')
    parser.add_argument('--mount_data_dir', default='/storage/icds/RISE/sw8/alphafold/alphafold_2.3_db', help='Path to directory where databases reside. On UCSF Wynton some of the databases are symbolic links to various locations in this directory and singularity needs to mount this directory to see them.')
    parser.add_argument('--singularity_image_path', default='/storage/group/u1o/default/vvm5242/CONTAINER/alphafold-msa_2.3.1', help='Path to the AlphaFold singularity image.')
    parser.add_argument('--max_template_date', default='2040-01-01', help='Maximum template release date to consider (ISO-8601 format: YYYY-MM-DD). Important if folding historical test sets.')
    parser.add_argument('--db_preset', default='full_dbs', choices=['full_dbs', 'reduced_dbs'], help='Choose preset MSA database configuration - smaller genetic database config (reduced_dbs) or full genetic database config (full_dbs)')
    parser.add_argument('--model_preset', default='multimer', choices=['monomer', 'monomer_casp14', 'monomer_ptm', 'multimer'], help='Choose preset model configuration - the monomer model, the monomer model with extra ensembling, monomer model with pTM head, or multimer model')
    parser.add_argument('--use_precomputed_msas', default=True, help='Whether to read MSAs that have been written to disk. WARNING: This will not check if the sequence, database or configuration have changed.')

    args = parser.parse_args()
    return args

def str_to_bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        import argparse
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    args = parse_args()

    hhblits_binary = os.path.expanduser('~/hh-suite/bin/hhblits')
    
    args.output_dir = '/home/vmathew/Desktop/temp/alphafold_run/OUTPUT'
    args.data_dir = '/mnt/ceph/alphafold_databases'
    args.mount_data_dir = '/mnt/ceph/alphafold_databases'
    args.singularity_image_path = '/home/vmathew/Desktop/temp/alphafold-msa_2.3.1.sif'
     
    # Set paths
    uniref90_database_path = os.path.join(args.data_dir, 'uniref90', 'uniref90.fasta')
    uniprot_database_path = os.path.join(args.data_dir, 'uniprot', 'uniprot.fasta')
    mgnify_database_path = os.path.join(args.data_dir, 'mgnify', 'mgy_clusters_2022_05.fa')
    bfd_database_path = os.path.join(args.data_dir, 'bfd', 'bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt')
    small_bfd_database_path = os.path.join(args.data_dir, 'small_bfd', 'bfd-first_non_consensus_sequences.fasta')
    uniref30_database_path = os.path.join(args.data_dir, 'uniref30', 'UniRef30_2021_03')
    pdb70_database_path = os.path.join(args.data_dir, 'pdb70', 'pdb70')
    pdb_seqres_database_path = os.path.join(args.data_dir, 'pdb_seqres', 'pdb_seqres.txt')
    template_mmcif_dir = os.path.join(args.data_dir, 'pdb_mmcif', 'mmcif_files')
    obsolete_pdbs_path = os.path.join(args.data_dir, 'pdb_mmcif', 'obsolete.dat')

    database_paths = [
        ('uniref90_database_path', uniref90_database_path),
        ('mgnify_database_path', mgnify_database_path),
        ('template_mmcif_dir', template_mmcif_dir),
        ('obsolete_pdbs_path', obsolete_pdbs_path),
    ]

    if args.model_preset == 'multimer':
        database_paths.append(('uniprot_database_path', uniprot_database_path))
        database_paths.append(('pdb_seqres_database_path', pdb_seqres_database_path))
    else:
        database_paths.append(('pdb70_database_path', pdb70_database_path))

    if args.db_preset == 'reduced_dbs':
        database_paths.append(('small_bfd_database_path', small_bfd_database_path))
    else:
        database_paths.append(('uniref30_database_path', uniref30_database_path))
        database_paths.append(('bfd_database_path', bfd_database_path))

    command_args = [f'--{name}={path}' for name, path in database_paths]
    command_args.extend([
        f'--fasta_paths={args.fasta_paths}',
        f'--hhblits_binary_path={hhblits_binary}',
        f'--output_dir={args.output_dir}',
        f'--max_template_date={args.max_template_date}',
        f'--db_preset={args.db_preset}',
        f'--model_preset={args.model_preset}',
        f'--use_precomputed_msas={args.use_precomputed_msas}',
        '--logtostderr',
    ])

    env_vars = {
        'CUDA_VISIBLE_DEVICES': args.gpu_devices,
        'NVIDIA_VISIBLE_DEVICES': args.gpu_devices,
        'TF_FORCE_UNIFIED_MEMORY': '1',
        'XLA_PYTHON_CLIENT_MEM_FRACTION': '4.0',
    }
    env_vals = ','.join(f'{key}={value}' for key, value in env_vars.items())

    tempdir = os.environ.get('TMPDIR', '/tmp')

    args_list = [
        'singularity', 'run',
        '-B', args.mount_data_dir,
        '-B', os.getcwd(),
        '-B', tempdir,
        '--env', env_vals,
        args.singularity_image_path
    ] + command_args

    cmd = ' '.join(args_list)
    print(cmd)

    run(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True, executable='/bin/bash', check=True)

if __name__ == '__main__':
    main()
