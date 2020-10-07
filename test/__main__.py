import asyncio
import re
import sys

from direct.stdpy import file as stdpy
from panda3d import core as p3d


_INCLUDE = re.compile('test_([a-zA-Z_][a-zA-Z0-9_]+)', re.IGNORECASE)


async def find_modules(src_path):
    for path in map(p3d.Filename, stdpy.listdir(src_path)):
        path.make_absolute(src_path)
        if path.is_regular_file():
            if _INCLUDE.fullmatch(path.get_basename_wo_extension()):
                yield path


async def main(src_path, modules):
    async for path in find_modules(src_path):
        name = path.get_basename_wo_extension()
        if name in modules:
            process = await asyncio.create_subprocess_exec(
                sys.executable, '-m', f'Burst.test.{name}',
                stdout = asyncio.subprocess.DEVNULL,
                stderr = asyncio.subprocess.DEVNULL,
                cwd = burst.get_root().get_dirname())
            await process.wait()


if __name__ == '__main__':
    from . import __all__
    src_path = p3d.Filename(__file__)
    src_path = src_path.get_dirname()
    asyncio.run(main(src_path, __all__))
