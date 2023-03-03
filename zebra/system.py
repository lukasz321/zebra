import os
import asyncio
import fileinput
import subprocess
import shlex
import pathlib
from typing import Tuple, Dict

def get_serial_port(vid=None, pid=None):
    lsusb = system_command("lsusb")[1]

    if vid and pid and vid not in lsusb and pid not in lsusb:
        print(f"No device with VID='{vid}' and PID='{pid}' enumerating.")
        return None
    elif vid and not pid and vid not in lsusb:
        print(f"No device with VID='{vid}' enumerating.")
        return None
    elif pid and not vid and pid not in lsusb:
        print(f"No device with PID='{pid}' enumerating.")
        return None
    elif not pid and not vid:
        print("You must pass either vid or pid args.")
        return None

    vid_match = pid_match = port_match = None
    for f in pathlib.Path("/dev/serial/by-id").glob("**/*"):
        port = "/dev/" + os.readlink(f).rsplit("/", maxsplit=1)[-1]

        if vid:
            cmd = f"udevadm info -n {port} -q property | grep VENDOR_ID | cut -d'=' -f2"
            status, stdout, stderr = pipeable_command(cmd)
            if vid == stdout.strip():
                vid_match = True

        if pid:
            cmd = f"udevadm info -n {port} -q property | grep MODEL_ID | cut -d'=' -f2"
            status, stdout, stderr = pipeable_command(cmd)
            if pid == stdout.strip():
                pid_match = True

        if (vid and vid_match) and (pid and pid_match) or (not vid and pid_match) or (not pid and vid_match):
            port_match = port
            break

    return port_match


async def exec_command_async(cmd: str) -> Tuple[int, str, str]:
    """ """

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    # io streams are returned as unicode bytes, so decode to get strings
    stdout = stdout.decode("utf8", errors="ignore")
    stderr = stderr.decode("utf8", errors="ignore")

    return proc.returncode, stdout, stderr


def pipeable_command(cmd: str) -> Tuple[int, str, str]:
    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    ) as p:
        stdout, stderr = p.communicate()
        status = int(p.returncode)

    stdout = stdout.decode("utf8", errors="ignore")
    stderr = stderr.decode("utf8", errors="ignore")

    return status, stdout, stderr


def noblock_command(cmd: str):
    subprocess.Popen([cmd], shell=True)


def system_command(cmd: str) -> Tuple[int, str, str]:
    """
    IMPORTANT: this function does not support pipes.
    """

    try:
        args = shlex.split(cmd)
        with subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        ) as p:
            stdout, stderr = p.communicate(cmd)
            status = p.wait()
    except Exception:
        status = -1
        stdout = stderr = None

    return status, stdout, stderr

