import argparse
import textwrap
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Transcript completement')
    parser.add_argument('-g', '--genome', type=str, help='Path to ortho.tsv', required=True)
    parser.add_argument('-i', '--input_gff', type=str, help='Path to input gff', required=True)
    parser.add_argument('-p', '--prefix', type=str, help='Prefix for output', required=True)
    parser.add_argument('-o', '--output_path', type=str, help='Path to output dir', required=True)
    parser.add_argument('-t', '--threads', type=int, help='Threads for parallel', required=False, default=1)
    # mikado
    parser.add_argument("-k", "--mikado", type=bool, help="whether run mikado", required=True, default=True)
    parser.add_argument("--mikado_sample", type=str, help="mikado RNASeq sample sheet path", required=True, default="")
    parser.add_argument("--mikado_refprot", type=str, help="mikado prot db path (fa)", required=True, default="")
    # mapping back to cds
    parser.add_argument("-c", "--mapping_cds", type=bool, help="whether run mapping pipeline", required=False, default=False)
    
    args = parser.parse_args()

    return args

def get_candicated_cds(args):
    gffread_cmd = f"""
    gffread {args.input_gff} \
        -g {args.genome} \
        -w {args.output_path}/{args.prefix}.cds
    """
    os.system(gffread_cmd)

def run_mikado(args):
    """
    run mikado function
    """

    if os.path.exists(f"{args.output_path}/mikado") is False:
        os.mkdir(f"{args.output_path}/mikado")

    cfg = f"{args.output_path}/mikado/config.yaml"

    # 内置plant.yaml
    cmd_mikado_config = f"""
    daijin configure \
      --scheduler "local" \
      --threads {args.threads} \
      --genome {args.genome} \
      --name {args.prefix} \
      --sample-sheet {args.mikado_sample} \
      -al hisat -as stringtie \
      --flank 500 \
      -od {args.output_path}/mikado \
      --prot-db {args.mikado_refprot} \
      --scoring plant.yaml \
      --copy-scoring data/plant.yaml \
      -o {cfg}
    """
    
    cmd_mikado_assemble = f"""
    daijin assemble --cores {args.threads} {cfg}
    """

    asm_dir = os.path.join(args.output_path, "mikado/3-assemblies", "output") # candicate output
    mikado_cfg = os.path.join(args.output_path, "mikado/mikado.yaml") # candicate output
    cmd_mikado_final = f"""
    daijin mikado {mikado_cfg}
    """

    # step1
    os.system(cmd_mikado_config)
    if not os.path.exists(cfg):
        raise FileNotFoundError(f"{cfg} not found for mikado")

    # step2
    os.system(cmd_mikado_assemble)
    ## check
    if not os.path.isdir(asm_dir):
        raise RuntimeError("assemble 步骤未生成 3-assemblies/output 目录")
    if not os.path.exists(mikado_cfg):
        raise FileNotFoundError(f"{mikado_cfg} not found for mikado final")
    
    # step3
    os.system(cmd_mikado_final)
    # check output
    if not os.path.exists(os.path.join(args.output_path, "mikado/5-mikado", "all.done")):
        raise FileNotFoundError(f"{mikado_cfg} not found for mikado final")

def run_remapping(args):

    if os.path.exists(f"{args.output_path}/mapping_back") is False:
        os.mkdir(f"{args.output_path}/mapping_back")
    
    rna_sample_file = args.mikado_sample
    rna_seq_f1, rna_seq_f2 = [], []
    with open(rna_sample_file, "r") as in_f:
        for line in in_f:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            rna_seq_f1.append(line.split("\t")[0])
            rna_seq_f2.append(line.split("\t")[1])
    
    # merged
    merged_cmd1 = f"""
    zcat {" ".join(rna_seq_f1)} > {args.output_path}/mapping_back/{args.prefix}_merged.R1.fq
    """
    merged_cmd2 = f"""
    zcat {" ".join(rna_seq_f2)} >> {args.output_path}/mapping_back/{args.prefix}_merged.R2.fq
    """
    os.system(merged_cmd1)
    os.system(merged_cmd2)

    # mapping index
    if os.path.exists(f"{args.output_path}/mapping_back/index") is False:
        os.mkdir(f"{args.output_path}/mapping_back/index")
    os.system(f"cp {args.output_path}/{args.prefix}.cds {args.output_path}/mapping_back/index/")
    os.system(
        f"""
        hisat2-build -p {args.threads} {args.output_path}/mapping_back/index/{args.prefix}.cds \
            {args.output_path}/mapping_back/index/{args.prefix}"
        """
    )
    # mapping
    os.system(
        f"""
        hisat2 --dta -p {args.threads} -x {args.output_path}/mapping_back/index/{args.prefix} \
            -1 {args.output_path}/mapping_back/{args.prefix}_merged.R1.fq \
            -2 {args.output_path}/mapping_back/{args.prefix}_merged.R2.fq \
            -S {args.output_path}/mapping_back/{args.prefix}_merged.sam
        """
    )
    os.system(
        f"""
        samtools view -b {args.output_path}/mapping_back/{args.prefix}_merged.sam -@ {args.threads} || \
        samtools sort -T ${args.prefix}.hisat2.sorted.tmp -o {args.output_path}/mapping_back/{args.prefix}_merged.sorted.bam -@ {args.threads}
        """
    )
    if os.path.exists(f"{args.output_path}/mapping_back/{args.prefix}_merged.sorted.bam") is False:
        raise FileNotFoundError(f"{args.output_path}/mapping_back/{args.prefix}_merged.sorted.bam not found")
    else:
        os.system(
            f"""
            rm {args.output_path}/mapping_back/{args.prefix}_merged.R1.fq \
                {args.output_path}/mapping_back/{args.prefix}_merged.R2.fq \
                {args.output_path}/mapping_back/{args.prefix}_merged.sam
            """
        )

def main():
    
    args = parse_args()

    if os.path.exists(args.output_path) is False:
        os.mkdir(args.output_path)

    # get pep file
    get_candicated_cds(args)
    # mikado
    if args.mikado is True:
        if os.path.exists(args.mikado_sample) and os.path.exists(args.mikado_refprot):
            run_mikado(args)
        else:
            raise FileNotFoundError(f"recheck mikado sample sheet {args.mikado_sample} or refprot {args.mikado_refprot}")
    if args.mapping_cds is True:
        run_remapping(args)
    
if __name__ == "__main__":
    main()