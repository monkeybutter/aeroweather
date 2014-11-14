

with open("metar_temp2.txt", "wt") as fout:
    with open("metar_temp.txt", "rt") as fin:
        for line in fin:
            fout.write(line.replace('METAR', '\nMETAR').replace('<TITLE>', '\n<TITLE>').replace('SPECI', '\nSPECI'))

with open("metar_temp3.txt", "wt") as fout:
    with open("metar_temp2.txt", "rt") as fin:
        for line in fin:
            if line[:5] != 'METAR' and line[:7] != '<TITLE>' and line[:5] != 'SPECI' and "NIL" not in line:
                fout.write(' '.join(line.split()) + "\n")