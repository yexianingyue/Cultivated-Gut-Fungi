#!/usr/bin/python3
# -*- encoding: utf-8 -*-
###########################################################
# Author:				ZhangYue
# Description:				See below
# Time:				2020年07月06日	 Monday
# ModiffTime:       2020年09月01日
###########################################################
'''
Version : V3.0
change: 分组和名字相同时，只会在最后提醒，但不会报错
Tips:
    If names are not found in the group file, it will be classified as unknown.

group:
    name_1  group_1     Group_A
    name_1  group_4     Group_B
    name_2  group_2     Group_C
    name_3  group_3     Group_A
    ...     ...         ...

matrix:
    tittle sample_1 sample_2    ...
    name_1  1       1           0
    name_2  0       1           2
    name_3  3       4           9
    ...     ...     ...         ...
'''
import  argparse
import re,gzip,bz2

def get_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", metavar="Matrix", required=True, help="Input matrix")
    parser.add_argument("-t", metavar="Title", default=1, type=int,help="Whether have title")
    parser.add_argument("-g", metavar="group file", required=True, help="Input group")
    parser.add_argument("-N", metavar="Name col", default = 1, type=int, help="The ID's columns in group [default: 1]")
    parser.add_argument("-G", metavar="Group col", default = 2, type=int, help="The group's columns in group file [default: 2]")
    parser.add_argument("-o", metavar="output", required=True, help="Output matrix")
    parser.add_argument("-s", required=False, type=int,  default=1, choices=[0,1,2,3], help="Split Str fo matrix and group.[default: 1] \033[31mThey must have similary split str\033[0m\n0 -> \\s+\n1 -> \\t\n2 -> |\n3 -> ,")
    args = parser.parse_args()
    return args

def parse_group(file_, GRP, sstr, N, G):
    '''
    只是解析分组文件，{key: {taxo_1, taxo_2,...}, ...}
    '''
    if re.search(".gz$", file_):
        f = gzip.open(file_, 'rt')
    elif re.search(".bz2$", file_):
        f = bz2.open(file_,'rt')
    else:
        f = open(file_, 'r')

    for line in f:
        line_split = re.split(sstr, line.strip("\n"))
        if GRP.get(line_split[N]):
            GRP[line_split[N]].update({line_split[G]})
            continue
        try:
            GRP[line_split[N]] = {line_split[G]}
        except:
            print(line_split)
            print(line)
            exit(0)
    f.close()

def main(file_, sstr, output_file, title):
    result = {}

    if re.search(".gz$", file_):
        f = gzip.open(file_, 'rt')
    elif re.search(".bz2$", file_):
        f = bz2.open(file_,'rt')
    else:
        f = open(file_, 'r')

    if title:
        tittle = f.readline()
    for line in f:
        line_split = re.split(sstr, line.strip("\n"))
        name = line_split[0]
        try:
            groups = GRP[name] # 将名字转为分组 这边得到一个set，后面需要循环才行
        except:
            print(f"\033[31m{name}\033[0m can't find in group file, it will be changed to unknown.")
            groups = {'unknown'}
        num = [float(x) for x in line_split[1:]] # 如果需要整数，此处改为int即可
        for group in groups:
            if result.get(group):
                result[group] = list(map(lambda x,y: x+y, result[group], num))
            else:
                result[group] = num
    f.close()

    with open(output_file, 'w', encoding="utf-8") as f:
        if title:
            f.write(tittle)
        if sstr != "\|":
            sstr = "\t"
        for k,v in result.items():
            v = [str(x) for x in v]
            f.write(f"{k}{sstr}{sstr.join(v)}\n")


if __name__ == "__main__":
    args = get_args()
    GRP = {}
    sstr = {0:"\s+", 1:"\t", 2:"\|", 3:","}[args.s]
    if args.N < 0 or args.G < 0:
        print("Plese check Your parameter -N -G, they must >= 1")
        exit(127)
    N = args.N - 1 
    G = args.G - 1 
    parse_group(args.g, GRP, sstr, N, G)
    main(args.i, sstr, args.o, args.t)
    if args.N == args.G < 0:
        print(f"\033[40;31mYour name and group is equal -> {args.G}\033[0m")
