#!/usr/bin/python3
# -*- encoding: utf-8 -*-
##########################################################
# Creater       :  夜下凝月
# Created  date :  2023-09-06, 11:31:24
# Modiffed date :  2023-10-20, 11:02:32
##########################################################

import sys
import re
import re,gzip,bz2

if len(sys.argv) != 5:
    print(f"{sys.argv[0]} seq2clu clu_len samfile output.rc")
    exit(0)


#---------
summary_dict = {
        "total":{
            "single": 0,
            "multiple": 0
            },
        "1.vs.1":{
        # 唯一匹配的情况
            "reads": 0,
            "genome": 0
            },
        "1.vs.multiple.only":{
        # 其实就是这些基因组，没有唯一匹配的reads，所以没有先前的相对丰度，最后也没有丰度
            "reads": 0,
            "genome_num": 0,
            "genomes": set() # 记录到底是哪些基因组
            },
        "1.vs.multiple":{
        # 这些基因组之前在唯一匹配时有结果
            "reads": 0,
            "genome": 0
            }
        }

#-------------------
#   Define Function

def relative(x:list, to=100):
    xsum = sum(x)
    return([ x / xsum * to for x in x ])



def open_file(file_):
    if re.search(".gz$", file_):
        f = gzip.open(file_, 'rt')
    elif re.search(".bz2$", file_):
        f = bz2.open(file_,'rt')
    else:
        f = open(file_, 'r')
    return(f)

try:
    f1 = open(sys.argv[1], 'r') # ctg2genome
    f2 = open_file(sys.argv[2]) # genome_sumlen
    f3 = open_file(sys.argv[3]) # samfile
except:
    print(f"{sys.argv[0]} ctg2genome genome_sumlen samfile output.rc output.summary")
    exit(0)

#------------------------------------------------------------------
#       read map file (ctg to genome/species/genus/family....)
#           note:
#               允许对应的分组是多个的，使用逗号链接

ctg2genome = {}
for line in f1:
    ctg, genome = line.strip().split()
    ctg2genome[ctg] = genome
f1.close()

genome_sumlen = {} # 每个cluster，涉及到的所有基因的总长度
for line in f2:
    genome,length = line.strip().split()[0:2]
    genome_sumlen[genome] = float(length)
f2.close()


#------------------------------------------------------------------
#       循环sam文件：
#           1、过滤未对齐的reads   -> align.match
#           2、去重(如果一条reads比对到了基因组的不同位置，只记录一次)   --> align_to_one_genomes.get
#           3、记录reads是否是唯一匹配   --> reads_stat

align = re.compile("^\d+M$") # 定义，全部对齐后，才进行下一步操作
reads_stat = {} # 记录reads比对情况，是否比对到了不同的基因组
align_dict = {}
align_to_one_genomes = {} # "readsgenome":1

for line in f3:
    line_strip = line.strip().split()
    if not align.match(line_strip[5]):
        continue
    reads = line_strip[0]
    genomes = ctg2genome[line_strip[2]]

    # 如果一个比对结果代表了多个物种，那就认为这条reads比对到了多个基因组
    for genome in genomes.split(","):
        key1 = f"{reads}{genome}"

        # 如果一条reads比对到了基因组不同的基因，那就只记录一条，并跳过其余的
        if align_to_one_genomes.get(key1):
            continue
        align_to_one_genomes[key1] = 1

        align_dict[key1] = (reads, genome)

        # 每条reads出现的频数，如果为1，则是单个匹配，否则是多匹配
        if reads_stat.get(reads):
            reads_stat[reads] += 1
        else:
            reads_stat[reads] = 1
f2.close()

#------------------------------------------------------------------
#       循环比对情况：
#           1、记录总共唯一匹配的reads总数  --> summary_dict['total']['single']
#           2、记录总共唯一匹配的reads总数  --> summary_dict['total']['multiple']
#           3、如果是多匹配，则记录每条reads比对到的基因组   --> reads_map_genomes

genome_reads_count = {}
reads_map_genomes = {} # reads: (genome1, genome2, genome3) 每条reads被分配给多基因组的情况

for k, v in align_dict.items():
    reads, genome = v

    # 如果是唯一匹配，记录基因组比对到的reads数量
    if reads_stat[reads] == 1:
        if genome_reads_count.get(genome) != None:
            genome_reads_count[genome] += 1 / genome_sumlen[genome]
        else:
            genome_reads_count[genome] = 1 / genome_sumlen[genome]
            summary_dict['1.vs.1']['genome'] += 0 # 唯一匹配中，涵盖了多少基因组
        summary_dict['total']['single'] += 1 / genome_sumlen[genome]
        continue

    # 如果是多基因组匹配,记录每条reads对应的基因组信息
    if reads_map_genomes.get(reads) != None:
        reads_map_genomes[reads].append(genome)
    else:
        summary_dict['total']['multiple'] += 1 # 记录多匹配的reads个数
        reads_map_genomes[reads] = [genome]


#------------------------------------------------------------------
# 计算唯一匹配中，基因组的相对丰度%
for k, v in genome_reads_count.items():
    X = v / summary_dict['total']['single'] * 100 # 计算相对丰度
    genome_reads_count[k] = [v, X]



#------------------------------------------------------------------
# 根据相对丰度，对多匹配情况的reads重新分配
# 看了一下大致的情况，很多的基因组，都是没有唯一匹配到的reads
for k, v in reads_map_genomes.items():
    reads, genomes = k, v
    X = [ genome_reads_count.get(x,(0,0))[1]/genome_sumlen[x] for x in genomes ] # 获取每个基因组的相对丰度，如果没有任何reads唯一匹配，那就为0
    if sum(X) == 0:
        # 如果reads匹配到多个目标序列，并且这些基因组相对丰度都为0，那就就这样的reads个数,以及这些基因组是什么
        summary_dict['1.vs.multiple.only']['reads'] += 1
        summary_dict['1.vs.multiple.only']['genomes'].update(genomes)
        continue
    Y = relative(X, 100)
    for index, value in enumerate(genomes):
        if genome_reads_count.get(value):
            genome_reads_count[value][1] += Y[index]
summary_dict['1.vs.multiple.only']['genome_num'] = len(summary_dict['1.vs.multiple.only']['genomes'])

X = []
Y = []
for k, v in genome_reads_count.items():
    X.append(k)
    Y.append(v[1])
Y = relative(Y)

try:
    ## 输出相对丰度
    f4 = open(sys.argv[4], 'w')
    for index, value in enumerate(X):
        f4.write(f"{value}\t{Y[index]}\n")
    f4.close()
except:
    print("output error")

