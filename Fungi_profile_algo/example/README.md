## 一、流程梗概
#### 1、物种的特有基因和共有基因
想要进行这一步我们需要两个对应关系：基因组的物种信息、基因的聚类信息。 基因聚类，我们使用MMseqs2软件对所有真菌的基因核酸序列进行聚类(一些参数)。聚类完成后根据基因组注释信息，就可以得获取哪些基因是特有的，哪些是共有的情况。

#### 2、相对丰度计算
1、在计算相对丰度的时候，为了准确性，我们只考虑了比对相似度在95及以上的对齐结果（你可以指定额外的相似度）
2、首先挑出了只比对到物种特有基因的比对结果，根据这些结果初步计算物种的相对丰度
3、如果一条reads比对到了多个物种的特有基因或物种的共有基因上，则根据第2步计算的结果对这一条reads按比例分配后加和到最初的reads count
4、最后根据每个基因组的特有基因的长度归一化相对丰度

## 二、Example
### 1.gene cluster
```
mmseqs easy-cluster genes/* database/geneset tmp --min-seq-id 0.95 --cov-mode 1 -c 0.9 --cluster-mode 2 --cluster-reassign 1 --kmer-per-seq 200 --kmer-per-seq-scale 0.8 --threads 80 --compressed 1 \
    && rm -r tmp
```
### 2.generate mapping file
这一步需要准备的文件有每个基因组的基因以及基因组的物种分类
```
cat database/geneset_cluster.tsv | perl -e 'while(<>){chomp;@s=split/\s+/;push @{$h{$s[0]}},$s[1];} for(keys %h){@a=@{$h{$_}}; print "$_\t".($#a+1)."\t".(join",", @a)."\n";}' > database/geneset_cluster.tsv.f
cat database/genomes.taxo | perl -e '%h;while(<>){chomp;@l=split/\s+/; $h{$l[0]}=$l[1]}; open I,"database/geneset_cluster.tsv.f"; while(<I>){chomp; @l=split/\s+/; %m=(); @x=split(/,/, $l[-1]); foreach $k(@x){$k=~/(\S+?)_/; $m{$h{$1}}=1; }; @ks=keys %m; print "$l[0]\t".join(",", @ks)."\n";  }'  > database/gene2clu.map
grep -v "," database/gene2clu.map > database/gene2clu.map.uniq

../bin/print_id_len.py database/geneset_rep_seq.fasta > database/geneset_rep_seq.fasta.len
../bin/matrix_sum.py -t 0 -i database/geneset_rep_seq.fasta.len -g database/gene2clu.map.uniq  -o database/clu.uniq_gene.sum -s 1
```

### 3.build bowtie2 database
```
bowtie2-build database/geneset_rep_seq.fasta database/bwt.index.geneset
```

### 4.relative abundance
```sh
./database/flow_fungi.map.sh database/bwt.index.geneset fastq/t1.fq.gz 999999999 result/t1.relative 12
./database/flow_fungi.map.sh database/bwt.index.geneset fastq/t2.fq.gz 999999999 result/t1.relative 12
./database/flow_fungi.map.sh database/bwt.index.geneset fastq/t3.fq.gz 999999999 result/t1.relative 12

# 也可以使用paralle代替上面的命令
# parallel -j 5 ./database/flow_fungi.map.sh database/bwt.index.geneset fastq/t{}.fq.gz 999999999 result/t{}.relative 12 ::: 1 2 3
```

### 5.merged abundance
```
../bin/combine_file_zy_folder_allsample.py -D result/ -o merged.profile -s *.relative
```
