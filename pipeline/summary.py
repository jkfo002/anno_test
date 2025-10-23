import argparse
import textwrap
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Summary script')
    parser.add_argument('-i', '--gff3', type=str, help='Path to gff3 file', required=True)
    parser.add_argument('-b', '--busco', type=str, help='Path to busco result', required=True)
    parser.add_argument('-m', '--omark', type=str, help='Path to omark result', required=True)
    parser.add_argument('-k', '--mikado', type=str, help='Path to mikado result', required=False, default=None)
    parser.add_argument('-c', '--mapping_back', type=str, help='Path to mapping back dir', required=False, default=None)
    parser.add_argument('-o', '--output_path', type=str, help='Path to output dir', required=True)
    
    args = parser.parse_args()

    return args

def stat_busco(args):
    pass

def stat_omark(args):
    pass

def stat_mikado(args):

    # check input
    if not os.path.exists(args.gff3):
        raise FileNotFoundError(f"gff3 file {args.gff3} not found")
    if not os.path.exists(args.mikado):
        raise FileNotFoundError(f"mikado result {args.mikado} not found")

    # check output
    s_mikado_output = os.path.join(args.output_path, "mikado")
    if not os.path.exists(s_mikado_output):
        os.mkdir(s_mikado_output)
    
    cmd_compare = f"""
    mikado compare -r {args.mikado} -p {args.gff3} \
        -o {os.path.join(args.output_path, "mikado.compare")}
        -l {os.path.join(args.output_path, "mikado.compare.log")}
    """
    os.system(cmd_compare)

def stat_mapping(args):
    pass

def main():

    args = parse_args()

    summary_output_dir = args.output_path
    if os.path.exists(summary_output_dir) is False:
        os.mkdir(summary_output_dir)
    
    stat_busco(args)
    stat_omark(args)
    if args.mikado is not None:
        stat_mikado(args)
    if args.mapping_back is not None:
        stat_mapping(args)