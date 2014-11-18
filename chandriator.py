with open("/home/roz016/Dropbox/Data for Tree/METAR source/EDDT_clean.txt", "wt") as fout:
    with open("/home/roz016/Dropbox/Data for Tree/METAR source/EDDT.txt", "rt") as fin:
        for line in fin:
            if "NIL" not in line:
                fout.write(' '.join(line.split()) + "\n")