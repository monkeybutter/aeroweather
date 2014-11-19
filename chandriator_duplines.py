with open("/home/roz016/Dropbox/Data for Tree/METAR source/LEBL_clean_dups.txt", "wt") as fout:
    with open("/home/roz016/Dropbox/Data for Tree/METAR source/LEBL_clean.txt", "rt") as fin:
        prev = None
        for line in fin:
            if line[20:26] != prev:
                fout.write(line)
            prev = line[20:26]