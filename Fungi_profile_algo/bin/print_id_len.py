#!/usr/bin/python3
# -*- encoding: utf-8 -*-
##########################################################
# Creater       :  夜下凝月
# Created  date :  2019-12-30, 20:05:24
# Modiffed date :  2019-12-30, 20:05:24
##########################################################
'''
print_id_len.py <fasta_file>  > output
'''
import sys
from Bio import SeqIO
from Bio.SeqUtils import GC

def all_info(file_):

    for i in SeqIO.parse(file_, 'fasta'):
        print("{}\t{}\t{}".format(i.id, len(i.seq), GC(i.seq)))

def get_len():

    for i in SeqIO.parse(sys.argv[1], 'fasta'):
        print("{}\t{}".format(i.id, len(i.seq)))

def main():
    if "-gc" in sys.argv:
        if sys.argv.index("-gc") == 1:
            all_info(sys.argv[2])
        else:
            all_info(sys.argv[1])
    else:
        get_len()

if __name__ == "__main__":
    if sys.argv.__len__() == 1 or sys.argv.__len__() > 3 :
        print(f"{sys.argv[0]} [-gc ] fasta_file")
        print("\033[31;1mif not -gc it only print len\033[0m")
        exit(0)
    main()


