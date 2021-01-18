#!/usr/local/bin/python3 -m tests

import asyncio
import pathlib
import sys

from panda3d import core as p3d


p3d.load_prc_file_data(
    '',
    """
    load-display pandagl
    win-origin -2 -2
    win-size 1 1
    fullscreen #f
    notify-level info
    textures-square none
    textures-power-2 none
    """)


async def find_modules(src_path):
    for file in burst.store.load_directory(src_path):
        if file.path.stem.startswith('test_'):
            yield file


async def main(src_path):
    async for file in find_modules(src_path):
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', f'tests.{file.path.stem}',
            # stdout = asyncio.subprocess.DEVNULL,
            # stderr = asyncio.subprocess.DEVNULL,
            )
        await process.wait()


if __name__ == '__main__':
    asyncio.run(main(pathlib.Path(__file__).parent))
