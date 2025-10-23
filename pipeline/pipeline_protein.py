import argparse
import textwrap
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Protein completement')
    parser.add_argument('-g', '--genome', type=str, help='Path to ortho.tsv', required=True)
    parser.add_argument('-i', '--input_gff', type=str, help='Path to input gff', required=True)
    parser.add_argument('-p', '--prefix', type=str, help='Prefix for output', required=True)
    parser.add_argument('-o', '--output_path', type=str, help='Path to output dir', required=True)
    parser.add_argument('-t', '--threads', type=int, help='Threads for parallel', required=False, default=1)
    # busco
    parser.add_argument("-b", "--busco", type=bool, help="whether run busco", required=False, default=True)
    parser.add_argument("-l", "--busco_lineage", type=str, help="busco lineage", required=False, default="")
    # omark
    parser.add_argument("-m", "--omark", type=bool, help="whether run omark", required=False, default=True)
    parser.add_argument("--omark_database", type=str, help="omark database, LUCA.h5", required=False, default="")
    parser.add_argument("--omark_taxa", type=str, help="omark need NCBI taxa.sqlite, could convert from ete3", required=False, default="")
    
    args = parser.parse_args()

    return args

def get_candicated_pep(args):
    gffread_cmd = f"""
    gffread {args.input_gff} \
        -g {args.genome} \
        -y {args.output_path}/{args.prefix}.pep
    """
    os.system(gffread_cmd)

def run_busco(args):
    """
    run busco function
    """

    if os.path.exists(f"{args.output_path}/{args.prefix}.pep"):
        busco_cmd = f"busco -i {args.output_path}/{args.prefix}.pep \
                    -l {args.busco_lineage} \
                    -o {args.output_path}/{args.prefix}_busco \
                    -m proteins --offline -c {args.threads} > {args.output_path}/busco_run.log"
        os.system(busco_cmd)
    else:
        raise FileNotFoundError(f"{args.output_path}/{args.prefix}.pep not found for busco")

def run_omark(args):
    """
    run omark function
    """
    
    if os.path.exists(f"{args.output_path}/{args.prefix}.pep"):
        omark_cmd1 = f"omamer search --db {args.omark_database} \
            --query {args.output_path}/{args.prefix}.pep \
            --out {args.output_path}/{args.prefix}.pep.db"
        
        omark_cmd2 = f"omark -f {args.output_path}/{args.prefix}.pep.db \
            -d {args.omark_database} -e {args.omark_taxa} \
            -o {args.output_path}/{args.prefix}_omark"
        os.system(omark_cmd1)
        os.system(omark_cmd2)
    else:
        raise FileNotFoundError(f"{args.output_path}/{args.prefix}.pep not found for omark")

def main():
    
    args = parse_args()

    if os.path.exists(args.output_path) is False:
        os.mkdir(args.output_path)

    # get pep file
    get_candicated_pep(args)
    # busco
    if args.busco is True:
        if os.path.exists(args.busco_lineage):
            run_busco(args)
        else:
            raise FileNotFoundError(f"recheck busco database dir {args.busco_lineage}")
    # omark
    if args.omark is True:
        if os.path.exists(args.omark_database) and os.path.exists(args.omark_taxa):
            run_omark(args)
        else:
            raise FileNotFoundError(f"recheck omark database {args.omark_database} or taxa {args.omark_taxa}")

    
if __name__ == "__main__":
    main()