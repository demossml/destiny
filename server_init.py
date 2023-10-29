from subprocess import Popen
import asyncio

filename = "run python3 bot/__init__.py"

while True:
    print("\nStarting " + filename)
    p = Popen("/Library/Frameworks/Python.framework/Versions/3.9/bin/poetry " + filename, shell=True)
    p.wait()