import os

from . import constants
from .base import FileError
from .xmllib.base import XMLFile


def load_xml_files(rootpath):
    files = []
    types = set()

    for fname in os.listdir(rootpath):
        try:
            with XMLFile(os.path.join(rootpath, fname)) as fobj:
                files.append(fobj)
                types.add(fobj.name)
        except FileError as e:
            pass

    return {type_: [fobj for fobj in files if fobj.name == type_]
            for type_ in types}
