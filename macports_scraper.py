import requests
import json
import pprint
import os
from collections import OrderedDict

import seaborn

OS_VERSION_KEY = "submission__os_version"
COUNT_KEY = "count"

# Name of the MacPorts package to scan
PACKAGE_NAME = "rust"
# Any "special versions" of the package to scan. If its not Python, probably not
# needed so just leave an empty string around.
PACKAGE_VERSIONS = [""]
# PACKAGE_NAME = "python"
# PACKAGE_VERSIONS = [
#     "32",
#     "33",
#     "34",
#     "35",
#     "36",
#     "37",
#     "38",
#     "39",
#     "310",
#     "311",
#     "312",
# ]

# Versions of macOS that Rust currently supports.
INTERESTED_MACOS_VERSIONS = [
    "10.7",
    "10.8",
    "10.9",
    "10.10",
    "10.11",
    "10.12",
    "10.13",
    "10.14",
    "10.15",
    "11",
    "12",
    "13",
    "14",
]

storage_path = f"./output/{PACKAGE_NAME}_data.json"

needs_stored = True
if os.path.isfile(storage_path):
    needs_stored = False

os_data = OrderedDict.fromkeys(INTERESTED_MACOS_VERSIONS, 0)

if needs_stored == False:
    with open(storage_path, "r") as data:
        os_data = json.load(data, object_pairs_hook=OrderedDict)
else:
    for package in map(lambda version: f"{PACKAGE_NAME}{version}", PACKAGE_VERSIONS):
        fetch_url = "https://ports.macports.org/api/v1/statistics/port?name={}&days=365&days_ago={}&property=submission__os_version&sort_by=submission__os_version"
        resp = list(json.loads(requests.get(fetch_url.format(package, 0)).content)["result"])

        print(f"Package {package}")    
        for data in resp:
            data = dict(data)

            print(data)

            os_version = str(data[OS_VERSION_KEY])
            count = int(data[COUNT_KEY])

            if os_version.startswith("11") or os_version.startswith("12") or os_version.startswith("13"):
                os_version = os_version.split(".", 1)[0]

            # Discard junk in the datasets
            if os_version == "" or os_version == " ":
                print(f"Skipping {count} unattributed counts")
                continue

            # Skip any truly ancient versions
            if os_version not in INTERESTED_MACOS_VERSIONS:
                print(f"Skipping {count} for macOS {os_version} because its not supported")
                continue

            os_data[os_version] += count
        print("-----------------------------------------------")

pprint.pprint(os_data)

if needs_stored:
    with open(storage_path, "w") as data:
        json.dump(os_data, data)

plot = seaborn.barplot(x=list(os_data.keys()), y=list(os_data.values()))
plot.set(xlabel='macOS version', ylabel='Installs', title=f"{PACKAGE_NAME} macOS version distribution")
plot.tick_params(axis='x', labelsize=7)
fig = plot.get_figure()
fig.savefig(f"./output/{PACKAGE_NAME}_graph.png")
