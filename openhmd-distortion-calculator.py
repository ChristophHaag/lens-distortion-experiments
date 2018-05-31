#!/usr/bin/env python3
import json
import sys
INPUT = None
OUTPUT = None
MODE = None
PANOPARAMS = None
MODES = {
    "OSVR_MESH_TO_PANO_PARAMS": "OSVR_MESH_TO_PANO_PARAMS",
    "OSVR_INTERNAL_TO_PANO_PARAMS": "OSVR_INTERNAL_TO_PANO_PARAMS",
    "STEAMVR_PARAMS_TO_PANO_PARAMS": "STEAMVR_PARAMS_TO_PANO_PARAMS"
}

def checkInput():
    if not MODE:
        print("Need mode with -m MODE [" + str(MODES.keys()) + "]")
        sys.exit(1)
    if MODE in [MODES["OSVR_MESH_TO_PANO_PARAMS"], MODES["OSVR_INTERNAL_TO_PANO_PARAMS"]]:
        if not INPUT:
            print("Need input with -i inputfile")
            sys.exit(1)
    if MODE in [MODES["STEAMVR_PARAMS_TO_PANO_PARAMS"]]:
        if not INPUT:
            print("Need input with -i inputfile")
            sys.exit(1)


for argnum in range(len(sys.argv)):
    if sys.argv[argnum] == "-i" and argnum < len(sys.argv) - 1:
        INPUT = sys.argv[argnum+1]
    if sys.argv[argnum] == "-o" and argnum < len(sys.argv) - 1:
        OUTPUT = sys.argv[argnum+1]
    if sys.argv[argnum] == "-m" and argnum < len(sys.argv) - 1  :
        if sys.argv[argnum+1] in MODES.keys():
            MODE = MODES[sys.argv[argnum+1]]
    if sys.argv[argnum] == "-pano" and argnum < len(sys.argv) - 1:
        PANOPARAMS = sys.argv[argnum+1].split(",")


if INPUT:
    print("Input: " + INPUT)
if OUTPUT:
    print("Output: " + OUTPUT)
if MODE:
    print("Mode: " + MODE)

checkInput()

from PIL import Image
import os

if MODE == MODES["OSVR_INTERNAL_TO_PANO_PARAMS"]:
    with open(INPUT, "r") as f:
        header = f.read().rstrip()
    print("Read internal header " + INPUT)
    hdk2 = header.split("static const char osvr_display_config_built_in_osvr_hdk20_v1[] = {")[1]
    hdk2 = hdk2.replace("};", "").rstrip()
    #print(hdk2)
    hex = hdk2.split(",")
    decoded = ""
    for h in hex:
        h = h.strip()
        if not h or not h.startswith("0x"):
            continue
        h = h.replace("0x", "")
        #print(h)
        decoded += bytes.fromhex(h).decode('utf-8')
    print("Decoded:", decoded)
if MODE == MODES["OSVR_MESH_TO_PANO_PARAMS"]:
    with open(INPUT, "r") as f:
        jsonmesh = json.load(f)
    print("Read json mesh " + INPUT)
    r,g,b = jsonmesh["display"]["hmd"]["distortion"]["red_point_samples"], jsonmesh["display"]["hmd"]["distortion"]["green_point_samples"], jsonmesh["display"]["hmd"]["distortion"]["blue_point_samples"]
    for redsample in r:
        print(redsample)
        print()
        #print("({}, {}) -> ({}, {})".format(redsample[0][0],redsample[0][1],redsample[1][0], redsample[1][1]))ß