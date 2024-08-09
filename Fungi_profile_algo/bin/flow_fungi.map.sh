#!/usr/bin/bash
db="/share/data1/Database/NCBI/Fungi.2024/01.human_correlative/index/bwt.index.gut_fungi_geneset"

if [ $# -lt 4 ] || [[ $1 =~ "-h" ]];then
    echo -e "\n\tUsage:\t$0 index fq/fa[,fq1/fa1,fq2/fa2,...] <nreads:max 999999999> <output_file_name_prefix> <threads>\n\n"
    echo -e "\tlatest_index:\t${db}\n"
    exit 127
fi

#--------------------
#       parameters
index=$1
in_f=$2
nreads=$3
out_f=`realpath -s $4`
threads=$5

#--------------------
#       software
alias="/usr/local/bin/bowtie2"

#--------------------
#       Database 需要自定义修改
#--------------------
db_human="/share/data1/Database/human_genome/chm13v2.0.fa"
db_uhgg='/share/data1/Database/uhgg_20220401/UHGG'
db_rRNA='/share/data1/Database/NCBI/TargetedLoci/Fungi/btw.fungi.all.fna'
gene2len='clu.uniq_gene.sum' # 参考example/database/clu.uniq_gene.sum
gene2clu='gene.map' # 参考example/database/gene2clu.map

if [ ! -f gene2len -a ! -f gene2clu ];then
    echo -e "\n\tERROR:\tPlease change $0 \033[31mline: 28 and 29\033[0m.\n"
    exit 127
fi

step1_db=$index
step2_db=$db_human
step3_db=$db_uhgg
step4_db=$db_rRNA

#--------------------
#       Parameters

step1_log=${out_f}.step1_map2fungi.log
step2_log=${out_f}.step2_rmHost.log
step3_log=${out_f}.step3_rmUHGG.log
step4_log=${out_f}.step4_rmrRNA.log
step5_log=${out_f}.step5_map2fungi.log

flag="" # 如果是fastq，bowtie2就不用添加其他参数
step1_data=${out_f}.step1_map2fungi.fq.gz
step2_data=${out_f}.step2_rmHost.fq.gz
step3_data=${out_f}.step3_rmUHGG.fq.gz
step4_data=${out_f}.step4_rmrRNA.fq.gz
step5_data=${out_f}.step5_map2fungi.sam
step6_data=${out_f}


## 如果第一次输入的数据是fasta格式的，那么后面的输出文件都是fasta，否则都是fastq
inf1=`echo $in_f | cut -d "," -f 1`
content=`less $inf1 | head -n 3 | tail -n 1`
if [ $content != "+" ];then 
    flag=" -f "
    step1_data=${out_f}.step1_map2fungi.fa.gz
    step2_data=${out_f}.step2_rmHost.fa.gz
    step3_data=${out_f}.step3_rmUHGG.fa.gz
    step4_data=${out_f}.step4_rmrRNA.fa.gz
    step5_data=${out_f}.step5_map2fungi.sam
fi

function run_bowtie(){
    check_point=$1
    step=$2
    cmd_log=$3
    pars=$4
    cmd="bowtie2 --end-to-end --mm --fast --no-head --no-unal --no-sq ${pars}"
    printf "#step${step} >> map2fungi\n$cmd\n\n" | sed 's/[ ][ ]+/ /g;s/     / /g' >> ${cmd_log}
    $cmd || ! echo "ERROR" >> ${cmd_log} || exit 127
}

## map to fungi step1
run_bowtie "${out_f}.st1" 1 ${out_f}.cmd.log "-U ${in_f}       -x ${step1_db} -S /dev/null --al-gz ${step1_data} ${flag} -p ${threads} 2> ${step1_log} "

## filter human step2
run_bowtie "${out_f}.st2" 2 ${out_f}.cmd.log "-U ${step1_data} -x ${step2_db} -S /dev/null --un-gz ${step2_data} ${flag} -p ${threads} 2> ${step2_log} "

## filter uhgg step3
run_bowtie "${out_f}.st3" 3 ${out_f}.cmd.log "-U ${step2_data} -x ${step3_db} -S /dev/null --un-gz ${step3_data} ${flag} -p ${threads} 2> ${step3_log} "

## filter rRNA step4
run_bowtie "${out_f}.st4" 4 ${out_f}.cmd.log "-U ${step3_data} -x ${step4_db} -S /dev/null --un-gz ${step4_data} ${flag} -p ${threads} 2> ${step4_log} "

## map to fungi step5
# 目的是为了找出比对到多个地方的reads (这一步需要很大的内存)
run_bowtie "${out_f}.st5" 5 ${out_f}.cmd.log "-U ${step4_data} -x ${step1_db} -S ${step5_data} ${flag} -k 1000 -p ${threads} 2> ${step5_log}"

## get abundance
full_name=`realpath -s $0`
dirname=${full_name%/*}
${dirname}/GPA.py -i ${step5_data} -o ${step6_data} -s 0.95
