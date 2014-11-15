with open("metar_temp3.txt", "wt") as fout:
    with open("metar_temp.txt", "rt") as fin:
        for line in fin:
            if "NIL" not in line:
                fout.write(' '.join(line.split()) + "\n")