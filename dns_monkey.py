import json
import os
import webbrowser
from subprocess import CREATE_NO_WINDOW, PIPE, Popen

import pystray
from PIL import Image


APP_NAME = "DNS Monkey"
VERSION = "0.1.0"
HOMEPAGE = "https://github.com/amis-shokoohi/dns_monkey"
SUBPROC_TIMEOUT = 10

resolvers = {
    "None": [],
    "Cloudflare": ["1.1.1.1", "1.0.0.1"],
    "Google": ["8.8.8.8", "8.8.4.4"],
    "Quad9": ["9.9.9.9", "49.112.112.112"],
    "Quad9 ECS": ["9.9.9.11", "149.112.112.11"],
    "Verisign": ["64.6.64.6", "64.6.65.6"],
    "AdGuard": ["94.140.14.14", "94.140.15.15"],
    "Electro": ["78.157.42.100", "78.157.42.101"],
    "Shecan": ["178.22.122.100", "185.51.200.2"],
    "Begzar": ["185.55.225.25", "185.55.226.26"],
    "Radar": ["10.202.10.10", "10.202.10.11"],
    "403": ["10.202.10.102", "10.202.10.202"],
}


class AppError(Exception):
    pass


class NetshError(Exception):
    pass


class TrayIcon:
    def __init__(self, name, icon_path):
        self.main_menu = self.create_main_menu()
        self.icon = pystray.Icon(
            name.lower().replace(" ", "_"),
            Image.open(icon_path),
            name,
            pystray.Menu(lambda: self.main_menu),
        )

    def run(self):
        self.icon.run()

    def create_main_menu(self):
        main_menu = []

        # Status
        for interface in get_interfaces():
            ips = get_dns(interface)
            item_submenu = pystray.Menu(*[pystray.MenuItem(ip, None) for ip in ips])
            item = pystray.MenuItem(
                f"{interface}: {find_resolver_by_ip(ips)}", item_submenu
            )
            main_menu.append(item)

        resolvers_menu = pystray.Menu(
            *[pystray.MenuItem(r, self.on_resolver_click) for r in resolvers.keys()]
        )

        main_menu += [
            pystray.MenuItem("Resolvers", resolvers_menu),
            pystray.MenuItem(
                "More",
                pystray.Menu(
                    pystray.MenuItem("Flush DNS", flush_dns),
                    pystray.MenuItem(
                        "Home page", lambda icon, item: webbrowser.open(HOMEPAGE)
                    ),
                    pystray.MenuItem(f"Version: v{VERSION}", None),
                ),
            ),
            pystray.MenuItem("Quit", lambda icon, item: icon.stop()),
        ]

        return main_menu

    def on_resolver_click(self, icon, item):
        resolver_name = str(item)
        try:
            set_dns(resolver_name)
        except (AppError, NetshError) as err:
            icon.notify("ERROR: " + "; ".join(err.args))
            return

        icon.notify(resolver_name)

        self.main_menu = self.create_main_menu()
        icon.update_menu()


def find_resolver_by_ip(ips):
    if len(ips) == 1:
        for k, v in resolvers.items():
            if ips[0] in v:
                return k
    if len(ips) == 2:
        for k, v in resolvers.items():
            if ips[0] in v and ips[1] in v:
                return k
    return "None"


def get_dns(interface):
    out, err = run_subproc(f'netsh interface ipv4 show dns "{interface}"')
    if err != "":
        raise NetshError(err)

    ips = []
    for line in out.split("\n"):
        line = line.strip()
        if line.startswith("Configuration") or line.startswith("Register"):
            continue
        if line.startswith("Statically") or line.startswith("DNS"):
            line = line.split(":")[1].strip()
        if line != "":
            ips.append(line)

    return ips


def set_dns(resolver_name):
    if resolver_name == "None":
        clear_dns()
        return

    ips = resolvers.get(resolver_name, None)
    if ips is None:
        raise AppError(f"not able to find {resolver_name} dns")

    for interface in get_interfaces():
        out, err = run_subproc(
            f'netsh interface ipv4 set dnsservers name="{interface}" source=static address="{ips[0]}" validate=no'
        )
        if out != "" or err != "":
            raise NetshError(f"{out}, {err}")

        out, err = run_subproc(
            f'netsh interface ipv4 add dnsservers name="{interface}" address="{ips[1]}" validate=no index=2'
        )
        if out != "" or err != "":
            raise NetshError(f"{out}, {err}")


def clear_dns():
    for interface in get_interfaces():
        out, err = run_subproc(
            f'netsh interface ipv4 delete dnsservers name="{interface}" address=all'
        )
        if (
            out != ""
            and out
            != "There are no Domain Name Servers (DNS) configured on this computer."
        ) or err != "":
            raise NetshError(f"{out}, {err}")


def flush_dns():
    out, err = run_subproc(f"ipconfig /flushdns")
    print(out)
    if err != "" or "Successfully" not in out:
        raise NetshError(f"{out}, {err}")


def get_interfaces():
    out, err = run_subproc("netsh interface show interface")
    if err != "":
        raise NetshError(err)

    interfaces = []
    for line in out.split("\n"):
        if "Connected" not in line:
            continue
        interface = line.split()[3]
        if not (interface.startswith("Ethernet") or interface.startswith("Wi-Fi")):
            continue
        interfaces.append(interface)

    return interfaces


def run_subproc(cmd):
    sp = Popen(
        cmd,
        stdout=PIPE,
        stderr=PIPE,
        encoding="utf-8",
        creationflags=CREATE_NO_WINDOW,
    )
    out, err = sp.communicate(timeout=SUBPROC_TIMEOUT)
    return out.strip(), err.strip()


if __name__ == "__main__":
    config_path = os.path.join(
        os.environ["USERPROFILE"],
        "." + APP_NAME.lower().replace(" ", "_"),
        "config.json",
    )

    # Check for config directory
    if not os.path.exists(os.path.dirname(config_path)):
        os.mkdir(os.path.dirname(config_path))

    # Check for config file
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            initial_cfg = {
                "resolvers": resolvers,
            }
            json.dump(initial_cfg, f, indent=2)

    # Load config
    cfg = {}
    with open(config_path, "r") as f:
        cfg = json.load(f)

    resolvers = cfg["resolvers"]

    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        APP_NAME.lower().replace(" ", "_") + ".ico",
    )
    icon = TrayIcon(APP_NAME, icon_path)
    icon.run()
