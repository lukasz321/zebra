from typing import List, Tuple
import subprocess
import re
import json

def system_command(command: str, timeout: int = 7):
    r = subprocess.run(command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout)
    return {
        "status": r.returncode,
        "stdout": r.stdout.decode("utf-8"),
        "stderr": r.stderr.decode("utf-8"),
    }

class Zebra:
    def __init__():
        pass

    @staticmethod
    def installed_printers() -> List[Tuple]:
        installed = system_command("lpstat -v")["stdout"]
        printers = {}

        for device in iter(installed.splitlines()):
            if any(i in device for i in ["Zebra", "ZTC", "ZPL"]):
                """
                n, u = device.split(": usb://")
                name = n.strip("device for ")
                printers[n.strip("device for ")] = "usb://" + u
                """
                
                uri = re.search(r'usb://[^ ]*', device)[0]
                name = device.split(":", maxsplit=1)[0].strip("device for ")
                printers[name] = uri

        return printers
    
    @staticmethod
    def discover_connected_printers():
        installed_printers = Zebra.installed_printers()

        cmd = "lpinfo --include-schemes usb -v"
        connected = system_command(cmd)["stdout"]
        printers = {}

        for device in iter(connected.splitlines()):
            if "Zebra" in device:
                uri = re.search(r'usb://[^ ]*', device)[0]
                serial_number = uri.rsplit("=", maxsplit=1)[-1]
                printers[serial_number] = {
                        "uri": uri,
                        "installed": uri in installed_printers.keys(),
                        }

        return printers
    
    def install():
        cmd = f"lpadmin -p 'Zebra-{serial_number}' -v '{uri}' -E"

    def print():
        pass



if __name__ == "__main__":
    printers = Zebra.discover_connected_printers()
    print(json.dumps(printers, indent=4))
    
    printers = Zebra.installed_printers()
    print(json.dumps(printers, indent=4))
