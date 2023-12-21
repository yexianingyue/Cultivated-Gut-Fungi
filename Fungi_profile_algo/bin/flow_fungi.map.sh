#!/usr/bin/bash
( [ $# -lt 4 ] || [[ $1 =~ "-h" ]] ) && echo -e "\n\tUsage:\t$0 index fq[,fq1,fq2..] <nreads:max 999999999> <output> <threads>" && echo -e "\n\tNOTE:\tBefore starting, the database/software path needs to be updated in the scripts.\n\n" && exit 127

#--------------------
#       parameters
index=$1
in_f=$2
nreads=$3
out_f=$4
threads=$5


shopt -s expand_aliases # use alias
#-----------------------------------------------------------
#                     << Software >>
#-----------------------------------------------------------
alias bowtie2="/usr/local/bin/bowtie2"
alias bbduk.sh='/share/data1/software/bbmap/bbduk.sh'

#-----------------------------------------------------------
#                     << Database >>
#-----------------------------------------------------------
db_human="/share/data1/Database/03.human/human_genome"
db_uhgg='/share/data1/Database//UHGG'
db_rRNA='/share/data1/Database/NCBI/TargetedLoci/Fungi/btw.fungi.all'


## map to fungi
cmd="bowtie2 --end-to-end  --mm --fast \
    --no-head --no-unal --no-sq \
    -U ${in_f} -x $index \
    -u $nreads \
    -S /dev/null \
    --al-gz ${out_f}.mapped.fq.gz \
    -p ${threads} 2> ${out_f}.map2fungi.log"
printf "#map2fungi\n$cmd\n" | sed 's/[ ][ ]+/ /g;s/     / /g' > ${out_f}.cmd.log
$cmd || ! echo "ERROR" >> ${out_f}.cmd.log || exit 127

## filter human
cmd="bowtie2 --end-to-end  --mm --fast \
     --no-head --no-unal --no-sq \
     -U ${out_f}.mapped.fq.gz -x $db_human \
     -S /dev/null \
     --un-gz ${out_f}.un2human.fq.gz \
      -p ${threads} 2> ${out_f}.human.log"
printf "\n#map2uhman$cmd\n" | sed 's/[ ][ ]+/ /g;s/     / /g' >> ${out_f}.cmd.log
$cmd || ! echo "ERROR" >> ${out_f}.cmd.log || exit 127

## filter uhgg
cmd="bowtie2 --end-to-end  --mm --fast \
     --no-head --no-unal --no-sq \
     -U ${out_f}.un2human.fq.gz \
     -x $db_uhgg \
     -S /dev/null \
     --un-gz ${out_f}.un2uhgg.fq.gz \
      -p ${threads} 2> ${out_f}.uhgg.log"
printf "\n#map2uhgg\n$cmd\n" | sed 's/[ ][ ]+/ /g;s/     / /g' >> ${out_f}.cmd.log
$cmd || ! echo "ERROR" >> ${out_f}.cmd.log || exit 127

## filter rRNA
cmd="bowtie2 --end-to-end  --mm --fast \
     --no-head --no-unal --no-sq \
     -U ${out_f}.un2uhgg.fq.gz \
     -x $db_rRNA \
     -S /dev/null \
     --un-gz ${out_f}.un2rRNA.fq.gz \
      -p ${threads} 2> ${out_f}.rRNA.log"
printf "\n#map2rRNA\n$cmd\n" | sed 's/[ ][ ]+/ /g;s/     / /g' >> ${out_f}.cmd.log
$cmd || ! echo "ERROR" >> ${out_f}.cmd.log || exit 127

## QC: Remove low complexity and tandem repeat sequences.
cmd="bbduk.sh in=${out_f}.un2rRNA.fq.gz out=${out_f}.un2rRNA.fq.qc.gz entropy=0.6 entropywindow=50 entropyk=5"
printf "\n#QC\ncmd\n" >> ${out_f}.cmd.log
$md || ! echo "ERROR" >> ${out_f}.cmd.log || exit 127

## map to fungi
# 目的是为了找出比对到多个地方的reads
# NOTE: 如果-k设置太大，会使用很多内存
cmd="bowtie2 --end-to-end  --mm --fast \
     --no-head --no-unal --no-sq \
     -k 100 \
     -U ${out_f}.un2rRNA.fq.gz \
     -x $index \
     -S ${out_f}.final.sam \
     -p ${threads} 2> ${out_f}.final.log"
printf "\n#map2fungi finall\n$cmd\n" | sed 's/[ ][ ]+/ /g;s/     / /g' >> ${out_f}.cmd.log
$cmd || ! echo "ERROR" >> ${out_f}.cmd.log || exit 127

