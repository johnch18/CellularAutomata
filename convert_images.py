#!/usr/bin/python3
import imageio

import os
from os import listdir
from os.path import isfile, join

mypath = "./conway"

filenames = [os.path.abspath(f"{mypath}/{f}") for f in listdir(mypath) if isfile(join(mypath, f))]

filenames.sort()
print(filenames)

with imageio.get_writer('output.gif', mode='I', duration=0.2) as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)
