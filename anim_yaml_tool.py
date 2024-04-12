import sys, os, yaml
from kanimlib import readFile, writeFile

if len(sys.argv) >= 2:
    inputfile = sys.argv[1]
    dir = os.path.dirname(inputfile)
    file = os.path.splitext(os.path.basename(inputfile))
    filename = file[0]
    filetype = file[1]
    outputfile = None
    if len(sys.argv) > 2:
        outputfile = sys.argv[2]
    if filetype == ".yaml":
        if outputfile == None:
            outputfile = os.path.join(dir, filename+".bin")
        print("Converting yaml " + inputfile + " to ANIM " + outputfile)
        data = yaml.load(open(inputfile).read(), Loader=yaml.FullLoader)
        writeFile(data, outputfile)
        print("Done.")
    else:
        if outputfile == None:
            outputfile = os.path.join(dir, filename+".yaml")
        print("Converting ANIM " + inputfile + " to yaml " + outputfile)
        data = readFile(inputfile)
        out = open(outputfile, "w")
        out.write(yaml.dump(data, sort_keys=False))
        out.close()
        print("Done.")
elif len(sys.argv) == 1:
    print("USAGE: ", os.path.basename(sys.argv[0]) + " input [output]")
    print("When provided with a YAML file, converts it into a Klei ANIM file. If provided with a Klei ANIM file instead, converts it into a YAML file.")