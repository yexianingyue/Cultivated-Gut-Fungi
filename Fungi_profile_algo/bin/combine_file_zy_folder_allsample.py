#!/share/data1/software/miniconda3/bin/python
# -*- encoding: utf-8 -*-
##########################################################
# Creater       :  夜下凝月
# Created  date :  2021-01-22, 15:43:55
# Modiffed date :  2023-07-06, 16:47:06
##########################################################

'''
combine file of each sample(must 2 line)
# ----------------------------------------
example:
    id\tvalue   <---- this is tittle
name_1\t123
name_2\t456
name_3\t789
...

当前版本可以用于合并压缩文件.gz .bz2
缺陷： 用于和并的表中，不要有重复的名字出现，否则我也不知道会发生什

suffix: 一定要把后缀都写上。如：sample1.log   ->  .log 
                            或：sample2_xxx   ->  _xxx

'''
import argparse
import sys, gzip, re, os, bz2
import copy
import numpy as np


def get_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-D', metavar='if', type=str, default="./", help='Input Dir')
    parser.add_argument('-o', metavar='of', type=str, default="combined.profile", help='Output Matrix')
    parser.add_argument('-t', metavar='Title',type=int, default=0, choices=[0, 1], help='\033[31mwhther have tittle. [1/0:default]\033[0m')
    parser.add_argument('-n', metavar='posite',type=int, default=1, help='\033[31mWhich col is name. [1:default]\033[0m')
    parser.add_argument('-v', metavar='posite',type=int, default=2, help='\033[31mWhich col is value. [2:default]\033[0m')
    parser.add_argument('-f', metavar='format',type=str, default='float', choices=['int', 'float', 'fraction', 'str'], help='\033[31mdata format. [int, fraction, float:default]\033[0m')
    parser.add_argument('-a', metavar='NA', type=str, default="0", help='\033[31mHow to fill na values.[0:default]\033[0m')
    parser.add_argument("-suffix", type=str, required=True,help="file suffix")
    parser.add_argument("--skip", type=int, default=0, help="How many lines should be skipped.  \033[31mDon't appear with parameter -n\033[0m")
    parser.add_argument("-s", required=False, type=int,  default=1, choices=[0,1,2,3], help="Split Str fo matrix and group.[default: 1] \033[31mThey must have similary split str\033[0m\n0 -> \\s+\n1 -> \\t\n2 -> |\n3 -> ,")
    args = parser.parse_args()
    return args

def filter_file(input_Dir, suffix, default_value):
    '''
    input_Dir: the path to files
    suffix: the file's suffix
    default_value: how to fill na value
    '''
    global INIT_CAZY
    global STRAIN_LIST
    global STRAIN_INDEX_DICT
    global STRAIN_LIST_LEN

    STRAIN_LIST = os.listdir(input_Dir)
    STRAIN_LIST = [x for x in STRAIN_LIST if re.search(f"{suffix}$", x)]
    STRAIN_LIST = [re.search(r"(.*)" + suffix, x).group(1) for x in STRAIN_LIST]
    STRAIN_LIST = sorted(STRAIN_LIST)
    INIT_CAZY = [default_value for _ in STRAIN_LIST]
    STRAIN_INDEX_DICT = dict(map(reversed, enumerate(STRAIN_LIST))) # {strain_1: index_1, strain_2: index_2}
    STRAIN_LIST_LEN = len(STRAIN_LIST)
    if STRAIN_LIST_LEN == 0:
        print(f"ERROR: {STRAIN_LIST_LEN} files are eligible for combine.")
        exit(127)

def judge_file_format(file_name):
    my_open = {'gz':gzip.open, 'bz2':bz2.open} # 输入文件格式
    ff = file_name.split(".")[-1]
    if my_open.get(ff):
        return(my_open[ff])
    return open

def parse_file(sstr, path, strain, position, result_dict, suffix, f_title, positions, n_files):
    """解析每个文件"""
    global INIT_CAZY
    global STRAIN_LIST_LEN
    global TERMINAL_SIZE
    global MY_OPEN

    rcf = f"{path}/{strain}{suffix}"
    f = judge_file_format(rcf)(rcf, 'rt')

    sys.stdout.write(f"\rfile:{strain+suffix:{TERMINAL_SIZE}s}\t\tprocess: {n_files}/{STRAIN_LIST_LEN}")

    # 如果有表头，就跳过
    while(f_title > 0):
        f.readline() # 跳过抬头
        f_title -= 1
    for line in f:
        line_split = re.split(sstr, line.strip("\n"))
        #line_split = re.split(r"\t", line.strip())
        try:
            cazy_name, cazy_count = line_split[positions[0]-1], line_split[positions[1]-1]
        except:
            sys.stderr.write(f"\n")
            sys.stderr.write(str(line_split))
            sys.stderr.write(f"\n\033[31mthe line only have {len(line_split)} columns\033[0m, \033[1;33mplease check your parameter -n and -v \033[1m\n")
            exit(0)
        try:
            result_dict[cazy_name][position] = cazy_count
        except:
            result_dict[cazy_name] = copy.deepcopy(INIT_CAZY)
            result_dict[cazy_name][position] = cazy_count
    f.close()

def main(sstr, input_Dir, output_file, suffix, f_title, position, format_function, default_value):
    """循环列表"""
    global STRAIN_LIST
    global STRAIN_INDEX_DICT
    global INIT_CAZY
    result_dict = {} # {ko-number: [ INIT_CAZY ] }
    judge_value = format_function(default_value)

    # 循环所有文件
    for index_, strain in enumerate(STRAIN_LIST):
        parse_file(sstr, input_Dir, strain, STRAIN_INDEX_DICT[strain], result_dict, suffix, f_title, positions, index_+1)

    print("\nwrite result") # 为了掩饰前面进度条的问题
    # 写入结果
    sstr = "\t" if sstr == "\s+" else sstr
    # with open(output_file, 'w') as f:
    with open(output_file, 'w') as f:
        f.write("name" + sstr + sstr.join(STRAIN_LIST) + "\n") # 表头
        for k, v in result_dict.items():
            #v_temp = [float(x) for x in v]
            v_temp = np.array([format_function(x) for x in v])
            if (v_temp == judge_value).all(): # 如果所有的值都为默认值，那就跳过
                sys.stderr.write(f"\033[31m{k} abundance is miss,\033[0m it will not be written to {output_file}\n")
                continue
            v = sstr.join(v)
            f.write(f"{k}{sstr}{v}\n")

def fraction(x):
    '''解析分数的值'''
    xx = x.split("/")
    try:
        return float(xx[0])/float(xx[1])
    except:
        return float(xx[0])

if __name__ == "__main__":
    args = get_args()
    positions = [args.n, args.v]

    INIT_CAZY = [] # 矩阵数值的默认值
    STRAIN_LIST = []  # 文件列表
    STRAIN_INDEX_DICT = {} # 记录每个文件的序号，矩阵填充时防止错位
    STRAIN_LIST_LEN = 0 # 文件列表长度

    # 记录终端宽度，有时候screen，貌似不能记录，所以直接赋值
    try:
        TERMINAL_SIZE = int(os.get_terminal_size().columns*0.3)
    except:
        TERMINAL_SIZE = 100

    format_dict = {'int':int, 'float':float, 'fraction':fraction, 'str':str}

    filter_file(args.D, args.suffix, args.a)
    sstr = {0:"\s+", 1:"\t", 2:"\|", 3:","}[args.s]


    format_function = format_dict[args.f]
    if args.t and args.skip:
        parser.print_help() 
    else:
        f_title = args.t if args.t else args.skip

    main(sstr, args.D, args.o, args.suffix, f_title, positions, format_function, args.a) 
