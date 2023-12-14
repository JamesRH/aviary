#!/usr/bin/env python

#=======================================================================
# Author:
#
# Unit tests.
#
# Copyright
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License.
# If not, see <http://www.gnu.org/licenses/>.
#=======================================================================

import unittest
import os.path
import subprocess
import shutil

data = os.path.join(os.path.dirname(__file__), 'data')
path_to_conda = os.path.join(data,'.conda')

class Tests(unittest.TestCase):
    def setup_output_dir(self, output_dir):
        try:
            shutil.rmtree(output_dir)
        except FileNotFoundError:
            pass
        os.makedirs(output_dir)

    def test_short_read_assembly(self):
        output_dir = os.path.join("example", "test_short_read_assembly")
        self.setup_output_dir(output_dir)
        cmd = (
            f"aviary assemble "
            f"-o {output_dir}/aviary_out "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"--conda-prefix {path_to_conda} "
            f"-n 32 -t 32 "
        )
        subprocess.run(cmd, shell=True, check=True)

        self.assertTrue(os.path.isdir(f"{output_dir}/aviary_out"))
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/data/final_contigs.fasta"))
        self.assertTrue(os.path.islink(f"{output_dir}/aviary_out/assembly/final_contigs.fasta"))

    def test_long_read_assembly(self):
        output_dir = os.path.join("example", "test_long_read_assembly")
        self.setup_output_dir(output_dir)
        cmd = (
            f"aviary assemble "
            f"-o {output_dir}/aviary_out "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"-l {data}/pbsim.fq.gz "
            f"--longread-type ont "
            f"--min-read-size 10 --min-mean-q 1 "
            f"--conda-prefix {path_to_conda} "
            f"-n 32 -t 32 "
        )
        subprocess.run(cmd, shell=True, check=True)

        self.assertTrue(os.path.isdir(f"{output_dir}/aviary_out"))
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/data/final_contigs.fasta"))
        self.assertTrue(os.path.islink(f"{output_dir}/aviary_out/assembly/final_contigs.fasta"))

    def test_short_read_recovery(self):
        output_dir = os.path.join("example", "test_short_read_recovery")
        self.setup_output_dir(output_dir)
        cmd = (
            f"aviary recover "
            f"-o {output_dir}/aviary_out "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"--conda-prefix {path_to_conda} "
            f"-n 32 -t 32 "
        )
        subprocess.run(cmd, shell=True, check=True)

        bin_info_path = f"{output_dir}/aviary_out/bins/bin_info.tsv"
        self.assertTrue(os.path.isfile(bin_info_path))
        with open(bin_info_path) as f:
            num_lines = sum(1 for _ in f)
        self.assertTrue(num_lines > 1)

        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/data/final_contigs.fasta"))
        self.assertTrue(os.path.islink(f"{output_dir}/aviary_out/assembly/final_contigs.fasta"))

        self.assertTrue(os.path.islink(f"{output_dir}/aviary_out/diversity/singlem_out"))
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/diversity/singlem_out/metagenome.combined_otu_table.csv"))
        self.assertTrue(os.path.getsize(f"{output_dir}/aviary_out/diversity/singlem_out/metagenome.combined_otu_table.csv") > 0)
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/diversity/singlem_out/singlem_appraisal.tsv"))
        self.assertTrue(os.path.getsize(f"{output_dir}/aviary_out/diversity/singlem_out/singlem_appraisal.tsv") > 0)
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/diversity/singlem_out/singlem_appraise.svg"))

    def test_long_read_recovery(self):
        output_dir = os.path.join("example", "test_long_read_recovery")
        self.setup_output_dir(output_dir)
        cmd = (
            f"aviary recover "
            f"-o {output_dir}/aviary_out "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"-l {data}/pbsim.fq.gz "
            f"--longread-type ont "
            f"--min-read-size 10 --min-mean-q 1 "
            f"--conda-prefix {path_to_conda} "
            f"-n 32 -t 32 "
        )
        subprocess.run(cmd, shell=True, check=True)

        self.assertTrue(os.path.isdir(f"{output_dir}/aviary_out"))
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/data/final_contigs.fasta"))
        self.assertTrue(os.path.islink(f"{output_dir}/aviary_out/assembly/final_contigs.fasta"))

        self.assertTrue(os.path.islink(f"{output_dir}/aviary_out/diversity/singlem_out"))
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/diversity/singlem_out/metagenome.combined_otu_table.csv"))
        self.assertTrue(os.path.getsize(f"{output_dir}/aviary_out/diversity/singlem_out/metagenome.combined_otu_table.csv") > 0)
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/diversity/singlem_out/singlem_appraisal.tsv"))
        self.assertTrue(os.path.getsize(f"{output_dir}/aviary_out/diversity/singlem_out/singlem_appraisal.tsv") > 0)
        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/diversity/singlem_out/singlem_appraise.svg"))

    def test_short_read_recovery_fast(self):
        output_dir = os.path.join("example", "test_short_read_recovery_fast")
        self.setup_output_dir(output_dir)
        cmd = (
            f"aviary recover "
            f"--assembly {data}/assembly.fasta "
            f"-o {output_dir}/aviary_out "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"--skip-abundances "
            f"--skip-binners concoct rosella vamb maxbin2 metabat "
            f"--skip-qc "
            f"--refinery-max-iterations 0 "
            f"--conda-prefix {path_to_conda} "
            f"-n 32 -t 32 "
        )
        subprocess.run(cmd, shell=True, check=True)

        bin_info_path = f"{output_dir}/aviary_out/bins/bin_info.tsv"
        self.assertTrue(os.path.isfile(bin_info_path))
        with open(bin_info_path) as f:
            num_lines = sum(1 for _ in f)
        self.assertEqual(num_lines, 3)

        self.assertFalse(os.path.isfile(f"{output_dir}/aviary_out/data/final_contigs.fasta"))

    def test_short_read_recovery_queue_submission(self):
        output_dir = os.path.join("example", "test_short_read_recovery_queue_submission")
        self.setup_output_dir(output_dir)

        cmd = (
            f"aviary recover "
            f"--output {output_dir} "
            f"-o {output_dir}/aviary_out "
            f"-1 {data}/wgsim.1.fq.gz "
            f"-2 {data}/wgsim.2.fq.gz "
            f"--conda-prefix {path_to_conda} "
            f"-n 32 -t 32 "
            f"--snakemake-profile mqsub --cluster-retries 3 "
        )
        subprocess.run(cmd, shell=True, check=True)

        self.assertTrue(os.path.isfile(f"{output_dir}/aviary_out/data/final_contigs.fasta"))

        bin_info_path = f"{output_dir}/aviary_out/bins/bin_info.tsv"
        self.assertTrue(os.path.isfile(bin_info_path))
        with open(bin_info_path) as f:
            num_lines = sum(1 for _ in f)
        self.assertEqual(num_lines, 3)


if __name__ == "__main__":
    unittest.main()
