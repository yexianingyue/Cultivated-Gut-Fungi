```bash
cd example
```
### 1.make bowtie2 db
```bash
bowtie2-build test.fasta test.bwt.index
```

### 2.run bowtie2
```bash
../bin/flow_fungi.map.sh database/test.bwt.index fastq/t1.fq.gz 999999999 result/t1 12
```

### 3.get relative profile

```bash
../bin/assign.scale_by_length.py  database/gene.clu database/clu.len result/t1.sam result/t1.relative
```
