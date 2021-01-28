#!/usr/local/bin/python3 -m tests

import asyncio
import signal
import sys

from . import __all__


class TestChain(object):

    def __init__(self):
        self._tasks = asyncio.Queue()
        for name in __all__:
            self._tasks.put_nowait(
                (name, asyncio.create_subprocess_exec(
                    sys.executable, '-m', f'tests.{name}',
                    # stdout = asyncio.subprocess.DEVNULL,
                    # stderr = asyncio.subprocess.DEVNULL,
                    )))

    def write_header(self, msg: str):
        print('=' * 36, f'||{msg:^32s}||', '=' * 36, sep = '\n')

    async def start(self):
        while self._tasks.qsize() > 0:
            name, task = await self._tasks.get()
            self.write_header(f'Running: {name}')
            proc = await task
            await proc.wait()
            self._tasks.task_done()

    def stop(self):
        while self._tasks.qsize() > 0:
            name, task = self._tasks.get_nowait()
            self.write_header(f'Skipping: {name}')
            task.close()
            self._tasks.task_done()


try:
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
except AttributeError:
    pass
finally:
    test = TestChain()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, test.stop)
    loop.run_until_complete(test.start())
