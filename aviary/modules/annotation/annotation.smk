
onstart:
    import os
    import sys

    from snakemake.utils import logger, min_version

    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)), "../../scripts"))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(workflow.snakefile)),"scripts"))

    # minimum required snakemake version
    min_version("6.0")
    long_reads = config["long_reads"]
    fasta = config["fasta"]
    short_reads_1 = config["short_reads_1"]
    short_reads_2 = config["short_reads_2"]
    min_contig_size = config["min_contig_size"]
    min_bin_size = config["min_bin_size"]
    gtdbtk_folder = config["gtdbtk_folder"]
    busco_folder = config['busco_folder']
    threads = config["max_threads"]
    ## pplacer deadlocks on too many threads
    pplacer_threads = min(48, int(config["pplacer_threads"]))

    if gtdbtk_folder != "none" and not os.path.exists(gtdbtk_folder):
        sys.stderr.write("gtdbtk_folder does not point to a folder\n")
    if busco_folder != "none" and not os.path.exists(busco_folder):
        sys.stderr.write("busco_folder does not point to a folder\n")

import os

if config['fasta'] == 'none':
    config['fasta'] = 'assembly/final_contigs.fasta'

if config['mag_directory'] == 'none':
    config['mag_directory'] = 'bins/final_bins'
if config['mag_extension'] == 'none':
    config['mag_extension'] = 'fna'

rule download_databases:
    input:
        'logs/download_gtdb.log',
        'logs/download_eggnog.log',
        'logs/download_checkm2.log'
    threads: 1
    log:
        temp("logs/download.log")
    shell:
        "touch logs/download.log"

rule download_eggnog_db:
    params:
        eggnog_db = os.path.expanduser(config['eggnog_folder']),
    conda:
        'envs/eggnog.yaml'
    threads: 1
    log:
        'logs/download_eggnog.log'
    shell:
        'mkdir -p {params.eggnog_db}; '
        'download_eggnog_data.py --data_dir {params.eggnog_db} -y 2> {log} '

rule download_gtdb:
    params:
        gtdbtk_folder = os.path.expanduser(config['gtdbtk_folder']),
        gtdbtk_version = '207.0'
    conda:
        '../../envs/gtdbtk.yaml'
    threads: 1
    log:
        'logs/download_gtdb.log'
    shell:
        'GTDBTK_DATA_PATH={params.gtdbtk_folder}; '
        'mkdir -p {params.gtdbtk_folder}; '
        # Configuration
        'N_FILES_IN_TAR=139919; '
        'DB_URL="https://data.gtdb.ecogenomic.org/releases/release207/207.0/auxillary_files/gtdbtk_r207_v2_data.tar.gz"; '
        'TARGET_TAR_NAME="gtdbtk_r207_v2_data.tar.gz"; '

        # Script variables (no need to configure)
        'TARGET_DIR=${{1:-$GTDBTK_DATA_PATH}}; '
        'TARGET_TAR="${{TARGET_DIR}}/${{TARGET_TAR_NAME}}"; '

        # Check if this is overriding an existing version
        'mkdir -p "$TARGET_DIR"; '
        'n_folders=$(find "$TARGET_DIR" -maxdepth 1 -type d | wc -l); '
        'if [ "$n_folders" -gt 1 ]; then'
        '  echo "[ERROR] - The GTDB-Tk database directory must be empty, please empty it: $TARGET_DIR"; '
        '  exit 1; '
        'fi; '

        # Ensure that the GTDB-Tk data directory exists
        'mkdir -p "$TARGET_DIR"; '

        # Start the download process
        # Note: When this URL is updated, ensure that the "--total" flag of TQDM below is also updated
        'echo "[INFO] - Downloading the GTDB-Tk database to: ${{TARGET_DIR}}"; '
        'wget $DB_URL -O "$TARGET_TAR"; '

        # Uncompress and pipe output to TQDM
        'echo "[INFO] - Extracting archive..."; '
        'tar xvzf "$TARGET_TAR" -C "${{TARGET_DIR}}" --strip 1 | tqdm --unit=file --total=$N_FILES_IN_TAR --smoothing=0.1 >/dev/null; '

        # Remove the file after successful extraction
        'rm "$TARGET_TAR"; '
        'echo "[INFO] - The GTDB-Tk database has been successfully downloaded and extracted."; '

        # Set the environment variable
        'if conda env config vars set TARGET_DIR="$TARGET_DIR"; then '
        '  echo "[INFO] - Added TARGET_DIR ($TARGET_DIR) to the GTDB-Tk conda environment."; '
        'else '
        '  echo "[INFO] - Conda not found in PATH, please be sure to set the TARGET_DIR envrionment variable"; '
        'fi; '

rule download_checkm2:
    params:
        checkm2_folder = os.path.expanduser(config['checkm2_db_folder'])
    conda:
        '../../envs/checkm2.yaml'
    threads: 1
    log:
        'logs/download_checkm2.log'
    shell:
        'checkm2 database --download --path {params.checkm2_folder} 2> {log}; '
        'mv {params.checkm2_folder}/CheckM2_database/*.dmnd {params.checkm2_folder}/; '

rule checkm2:
    input:
        mag_folder = config['mag_directory'],
        checkm1_out = 'bins/checkm.out'
    output:
        checkm2_folder = directory("bins/checkm2_output"),
        checkm2_output = "bins/checkm2_output/quality_report.tsv"
    params:
        mag_extension = config['mag_extension'],
        checkm2_db_path = config["checkm2_db_folder"]
    threads:
        config["max_threads"]
    benchmark:
        'benchmarks/checkm2.benchmark.txt'
    conda:
        "../../envs/checkm2.yaml"
    shell:
        'export CHECKM2DB={params.checkm2_db_path}/uniref100.KO.1.dmnd; '
        'echo "Using CheckM2 database $CHECKM2DB"; '
        'checkm2 predict -i {input.mag_folder}/ -x {params.mag_extension} -o {output.checkm2_folder} -t {threads} --force'

rule eggnog:
    input:
        mag_folder = config['mag_directory'],
        # mag_extension = config['mag_extension'],
    params:
        mag_extension = config['mag_extension'],
        eggnog_db = config['eggnog_folder'],
        tmpdir = config["tmpdir"]
    resources:
        mem_mb=int(config["max_memory"])*512
    group: 'annotation'
    output:
        done = 'data/eggnog/done'
    threads:
        config['max_threads']
    benchmark:
        'benchmarks/eggnog.benchmark.txt'
    conda:
        'envs/eggnog.yaml'
    shell:
        # 'download_eggnog_data.py --data_dir {input.eggnog_db} -y; '
        'mkdir -p data/eggnog/; '
        'find {input.mag_folder}/*.{params.mag_extension} | parallel -j1 \'emapper.py --data_dir {params.eggnog_db} '
        '--dmnd_db {params.eggnog_db}/*dmnd --cpu {threads} -m diamond --itype genome --genepred prodigal -i {{}} '
        '--output_dir data/eggnog/ --temp_dir {params.tmpdir} -o {{/.}} || echo "Genome already annotated"\'; '
        'touch data/eggnog/done; '

rule gtdbtk:
    input:
        mag_folder = config['mag_directory']
    group: 'annotation'
    output:
        done = "data/gtdbtk/done"
    params:
        gtdbtk_folder = config['gtdbtk_folder'],
        pplacer_threads = config["pplacer_threads"],
        extension = config['mag_extension']
    resources:
        mem_mb=int(config["max_memory"])*1024
    conda:
        "../../envs/gtdbtk.yaml"
    threads:
        config["max_threads"]
    benchmark:
        'benchmarks/gtdbtk.benchmark.txt'
    shell:
        "export GTDBTK_DATA_PATH={params.gtdbtk_folder} && "
        "gtdbtk classify_wf --cpus {threads} --pplacer_cpus {params.pplacer_threads} --extension {params.extension} "
        "--genome_dir {input.mag_folder} --out_dir data/gtdbtk && touch data/gtdbtk/done"

rule annotate:
    input:
         'data/gtdbtk/done',
         'data/eggnog/done',
    output:
         'annotation/done',
    shell:
         """
         ln -sr data/gtdbtk taxonomy; 
         ln -sr data/eggnog annotation; 
         touch annotation/done;
         """
