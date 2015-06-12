import glob
import os
import subprocess

base_dir = os.path.dirname(os.path.realpath(__file__))

for road in glob.glob(base_dir + '/roads/*.road'):
    subprocess.call(['python', base_dir + '/update_road.py', road])

