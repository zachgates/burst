import argparse

from . import constants
from .common import load_xml_files


parser = argparse.ArgumentParser()
parser.add_argument('--root', type=str, default='./dna')
args = parser.parse_args()

for type_, files in load_xml_files(args.root).items():
    for fobj in files:
        print(fobj)
