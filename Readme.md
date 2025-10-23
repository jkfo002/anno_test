# anno_test
用于评估基因结构注释质量的pipeline

# 准备数据
```
1. gff 测试gff
2. genome gff对应物种基因组
3. RNA_Seq 近缘物种转录组数据
4. pep.fa 近缘物种蛋白数据
```

# 数据准备
## busco
busco数据库
```
https://busco-data.ezlab.org/v5/data/lineages/eukaryota_odb12.2025-07-01.tar.gz
https://busco-data.ezlab.org/v5/data/lineages/eudicots_odb10.2024-01-08.tar.gz
https://busco-data.ezlab.org/v5/data/lineages/embryophyta_odb12.2025-07-01.tar.gz
https://busco-data.ezlab.org/v5/data/lineages/viridiplantae_odb12.2025-07-01.tar.gz
```
## omark init
omark需要[LUCA.h5](https://omabrowser.org/All/LUCA.h5)与NCBI[taxdump.tar.gz](https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz)数据

下载NCBI taxonomy数据后需要ete3初始化（pixi protein 环境）
```python
from ete3 import NCBITaxa
ncbi = NCBITaxa(taxdump_file="/share/taxdump.tar.gz")
# 获取taxa.sqlite
# 默认在这里~/.etetoolkit/taxa.sqlite
```

# pixi 环境
流程环境基于pixi搭建，分为protein与transcript环境，pixi配置文件`pixi.toml`，

protein用于基于蛋白评估基因注释完整度，包括busco与omark

transcript用于基于RNA-Seq评估基因注释完整度，包括mikado，mapping-back

安装流程
```shell
pixi install pixi.toml
pixi shell -e protein
pixi shell -e transcript
```

# 脚本

## 蛋白
```
usage: pipeline_protein.py [-h] -g GENOME -i INPUT_GFF -p PREFIX -o OUTPUT_PATH [-t THREADS] [-b BUSCO] [-l BUSCO_LINEAGE] [-m OMARK]
                           [--omark_database OMARK_DATABASE] [--omark_taxa OMARK_TAXA]

Protein completement

options:
  -h, --help            show this help message and exit
  -g GENOME, --genome GENOME
                        Path to ortho.tsv
  -i INPUT_GFF, --input_gff INPUT_GFF
                        Path to input gff
  -p PREFIX, --prefix PREFIX
                        Prefix for output
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output dir
  -t THREADS, --threads THREADS
                        Threads for parallel
  -b BUSCO, --busco BUSCO
                        whether run busco
  -l BUSCO_LINEAGE, --busco_lineage BUSCO_LINEAGE
                        busco lineage
  -m OMARK, --omark OMARK
                        whether run omark
  --omark_database OMARK_DATABASE
                        omark database, LUCA.h5
  --omark_taxa OMARK_TAXA
                        omark need NCBI taxa.sqlite, could convert from ete3
```
## 转录本
```
usage: pipeline_transcript.py [-h] -g GENOME -i INPUT_GFF -p PREFIX -o OUTPUT_PATH [-t THREADS] -k MIKADO --mikado_sample MIKADO_SAMPLE --mikado_refprot
                              MIKADO_REFPROT [-c MAPPING_CDS]

Transcript completement

optional arguments:
  -h, --help            show this help message and exit
  -g GENOME, --genome GENOME
                        Path to ortho.tsv
  -i INPUT_GFF, --input_gff INPUT_GFF
                        Path to input gff
  -p PREFIX, --prefix PREFIX
                        Prefix for output
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path to output dir
  -t THREADS, --threads THREADS
                        Threads for parallel
  -k MIKADO, --mikado MIKADO
                        whether run mikado
  --mikado_sample MIKADO_SAMPLE
                        mikado RNASeq sample sheet path
  --mikado_refprot MIKADO_REFPROT
                        mikado prot db path (fa)
  -c MAPPING_CDS, --mapping_cds MAPPING_CDS
                        whether run mapping pipeline
```
## 示例
```shell
pixi run -e protein python ./pipeline/pipeline_protein.py \
    -i ./data/gff/A157.H1.pasa.rename.gff -g ./data/genome/A157.chr.fa \
    -o ./output \
    -t 16 -p A157 \
    -b False -l ./data/busco/embryophyta_odb12 \
    -m True --omark_database ./data/omark/LUCA.h5 --omark_taxa ./data/omark/taxa.sqlite

pixi run -e transcript python ./pipeline/pipeline_transcript.py \
    -i ./data/gff/A157.H1.pasa.rename.gff -g ./data/genome/A157.chr.fa \
    -o ./output \
    -t 16 -p A157 \
    -k False --mikado_sample data/RNA_Seq/A157_RNA.sample --mikado_refprot data/PanPotato.proteins.clean.fa \
    -c True 
```


