#!/share/data1/software/miniconda3/bin/python
# -*- encoding: utf-8 -*-
##########################################################
# Creater       :  夜下凝月
# Created  date :  2023-09-06, 11:31:24
# Modiffed date :  2023-10-20, 11:02:32
##########################################################

import argparse
import re
import re,gzip,bz2

PATTERN_READS_LEN = re.compile("(\d+)[M=XDI]") # fq_len = re.findall("(\d+)[M=XDI]", cigar)
PATTERN_MDTAG = re.compile("MD:Z:(\S+)")
PATTERN_MATCH_NUM = re.compile("(\d+)")


def get_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', metavar='if', type=str, required=True, help='Input samfile')
    parser.add_argument('-o', metavar='of', type=str, required=True, help='Output')
    parser.add_argument('-l', metavar='',type=str, default="", help='length file')
    parser.add_argument('-m', metavar='',type=str, default="", help='gene mapping file')
    parser.add_argument('-s', metavar='',type=float, default=0.97, help='minimum similarity [0 ~ 1]. (default:0.97)')
    args = parser.parse_args()
    return args

#------------------------------------------------------------------
#       根据相似度过滤sam文件
def is_remain(flag=0, ncolumns=0, cigar="*", tags="", similar=0.97):
    '''
    aim:
        过滤不符合条件的比对记录
    return:
        True/False

    tags: sam文件第11列以后的内容
    '''

    # 跳过没有匹配的记录
    if int(flag) & 0x4 != 0 :
        return False

    # 如果正好等于11列，那就说明整个sam文件没有最后的tag说明文档，直接报错退出
    if ncolumns == 11:
        sys.stderr.write("can't find tags in samfile.")
        exit(127)

    #------------------------------
    #       根据相似度过滤
    match_count = 0

    fq_len = PATTERN_READS_LEN.findall(cigar)
    fq_len = sum([int(x) for x in fq_len]) # 获取reads的长度

    # 获取正确匹配的碱基个数
    mdtag = PATTERN_MDTAG.search(tags)
    if not mdtag:
        return False
    match_count = sum( [int(x) for x in PATTERN_MATCH_NUM.findall(mdtag[1])] )

    # 计算相似度
    identity = match_count / fq_len
    # print(identity)
    if identity < similar:
        return False
    return True


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


def main(args):

    gene2clu = args.m
    clu_len = args.l
    similar = args.s # default 0.97

    outf = args.o
    samfile = args.i


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
    try:
        f1 = open(gene2clu, 'r') # seq2tax
        f2 = open_file(clu_len) # taxs_sumlen
        f3 = open_file(samfile) # samfile
    except Exception as e:
        print(e)
        exit(0)

    #------------------------------------------------------------------
    #       read map file (ctg to genome/species/genus/family....)
    #           note:
    #               允许对应的分组是多个的，使用逗号链接

    seq2tax = {} #  {"gene": "tax1,tax2,tax3", "gene1":"tax1", "gene2": "tax3,tax4", ...}
    for line in f1:
        ctg, genome = line.strip().split()
        seq2tax[ctg] = genome
    f1.close()

    taxs_sumlen = {} # 每个cluster，涉及到的所有基因的总长度
    for line in f2:
        genome,length = line.strip().split()[0:2]
        taxs_sumlen[genome] = float(length)
    f2.close()



    #------------------------------------------------------------------
    #       循环sam文件：
    #           1、过滤未对齐的reads   -> align.match
    #           2、去重(如果一条reads比对到了基因组的不同位置，只记录一次)   --> align_to_one_genomes.get
    #           3、记录reads是否是唯一匹配   --> reads_stat

    reads_stat = {} # 记录reads比对情况，是否比对到了不同的基因组
    align_dict = {}
    align_to_one_genomes = {} # "readsgenome":1

    for line in f3:
        # 如果以@开头，就认定是注释信息
        if line[0] == "@":
            continue
        line_split = line.strip().split("\t", 11)

        # 根据相似度过滤比对结果
        if not is_remain(flag = line_split[1], ncolumns = len(line_split), cigar = line_split[5], tags = line_split[-1], similar = similar):
            continue

        reads = line_split[0]
        taxs = seq2tax[line_split[2]]

        for tax in taxs.split(","):
            key1 = f"{reads}{tax}"

            # 如果一条reads比对到了同一物种的不同基因，就只记录一次
            if align_to_one_genomes.get(key1):
                continue
            align_to_one_genomes[key1] = 1

            # 如果比对到了不同的物种，就分别记录
            align_dict[key1] = (reads, tax)

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
    #           3、如果是多匹配，则记录每条reads比对到的基因组   --> reads_map_taxs

    taxs_reads_count = {} # {'genomes1': reads_escrow_uniq_count }
    reads_map_taxs = {} # {reads: (tax1, tax2, tax3), ...} 每条reads被分配给多基因组的情况

    for k, v in align_dict.items():
        reads, tax = v

        # 如果是唯一匹配，记录基因组比对到的reads数量
        if reads_stat[reads] == 1:
            if taxs_reads_count.get(tax) != None:
                taxs_reads_count[tax] += 1
            else:
                taxs_reads_count[tax] = 1
                summary_dict['1.vs.1']['genome'] += 0 # 唯一匹配中，涵盖了多少基因组
            summary_dict['total']['single'] += 1
            continue

        # 如果是多物种匹配,记录每条reads对应的物种信息
        if reads_map_taxs.get(reads) != None:
            reads_map_taxs[reads].append(tax)
        else:
            summary_dict['total']['multiple'] += 1 # 记录多匹配的reads个数
            reads_map_taxs[reads] = [tax]


    #------------------------------------------------------------------
    # 计算唯一匹配中，基因组的相对丰度%
    # taxs_reads_count[k] = [reads_count, reads_count/tax_length, reads_count_accumulative]
    for k, v in taxs_reads_count.items():
        X = v / taxs_sumlen[k]  # reads_count/tax_length 直接用reads数量除以物种的特异性偏度序列长度，方便后面计算相对百分比
        taxs_reads_count[k] = [v, X, v]



    #------------------------------------------------------------------
    # 根据相对丰度，对多匹配情况的reads重新分配
    # 看了一下大致的情况，很多的基因组，都是没有唯一匹配到的reads
    for k, v in reads_map_taxs.items():
        reads, taxs = k, v
        X = [ taxs_reads_count.get(x,(0,0))[1] for x in taxs ] # 获取每个基因组的相对丰度，如果没有任何reads唯一匹配，那就为0
        if sum(X) == 0:
            # 如果reads匹配到多个目标序列，并且这些基因组相对丰度都为0，那就就这样的reads个数,以及这些基因组是什么
            summary_dict['1.vs.multiple.only']['reads'] += 1
            summary_dict['1.vs.multiple.only']['genomes'].update(taxs)
            continue
        Y = relative(X, 1)
        for index, value in enumerate(taxs):
            if taxs_reads_count.get(value):
                taxs_reads_count[value][2] += Y[index]
    # print(taxs_reads_count)


    X = []
    Y = []
    for k, v in taxs_reads_count.items():
        X.append(k)
        Y.append( v[2] / taxs_sumlen[k] )
    Y = relative(Y, 100)

    try:
        ## 输出相对丰度
        f4 = open(f"{outf}", 'w')
        for index, value in enumerate(X):
            f4.write(f"{value}\t{Y[index]}\n")
        f4.close()
    except:
        print("output error")


if __name__ == "__main__":
    args = get_args()
    main(args)


