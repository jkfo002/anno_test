pixi run -e transcript python ./pipeline/pipeline_transcript.py \
    -i ./data/gff/A157.H1.pasa.rename.gff -g ./data/genome/A157.chr.fa \
    -o ./output \
    -t 16 -p A157 \
    -k False --mikado_sample data/RNA_Seq/A157_RNA.sample --mikado_refprot data/PanPotato.proteins.clean.fa \
    -c True 

# pixi run -e protein python ./pipeline/pipeline_protein.py \
#     -i ./data/gff/A157.H1.pasa.rename.gff -g ./data/genome/A157.chr.fa \
#     -o ./output \
#     -t 16 -p A157 \
#     -b False -l ./data/busco/embryophyta_odb12 \
#     -m True --omark_database ./data/omark/LUCA.h5