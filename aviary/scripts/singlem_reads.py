from subprocess import run
import os
import sys


def run_singlem(
    long_reads,
    short_reads_1,
    short_reads_2,
    pplacer_threads: int,
):
    try:
        os.mkdir("data/singlem_out/")
    except OSError:
        print("Using prexisting directory: data/singlem_out/")

    if long_reads != "none":
        singlem_pipe_cmd = f"singlem pipe --threads {pplacer_threads} --sequences {' '.join(long_reads)} --otu_table data/singlem_out/metagenome.longread_otu_table.csv".split()
        run(singlem_pipe_cmd)

    if short_reads_2 != "none":
        singlem_pipe_cmd = f"singlem pipe --threads {pplacer_threads} --forward {' '.join(short_reads_1)} --reverse {' '.join(short_reads_2)} --otu_table data/singlem_out/metagenome.shortread_otu_table.csv".split()
        run(singlem_pipe_cmd)

    elif short_reads_1 != "none":
        singlem_pipe_cmd = f"singlem pipe --threads {pplacer_threads} --sequences {' '.join(short_reads_1)} --otu_table data/singlem_out/metagenome.shortread_otu_table.csv".split()
        run(singlem_pipe_cmd)

    summarise_cmd = f"singlem summarise --input_otu_tables data/singlem_out/*.csv --output_otu_table data/singlem_out/metagenome.combined_otu_table.csv".split()
    run(summarise_cmd)


if __name__ == '__main__':
    long_reads = snakemake.config['long_reads']
    short_reads_1 = snakemake.config['short_reads_1']
    short_reads_2 = snakemake.config['short_reads_2']
    pplacer_threads = snakemake.config["pplacer_threads"]
    run_singlem(
        long_reads,
        short_reads_1,
        short_reads_2,
        pplacer_threads,
    )
