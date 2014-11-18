with open("/home/roz016/Dropbox/Data for Tree/METAR source/LEBL_clean.txt", "wt") as fout:
    with open("/home/roz016/Dropbox/Data for Tree/METAR source/LEBL.txt", "rt") as fin:
        for line in fin:
            if "NIL" not in line:
                mod_line = line.replace('LEBL', 'METAR LEBL')
                fout.write(' '.join(mod_line.split()) + "\n")