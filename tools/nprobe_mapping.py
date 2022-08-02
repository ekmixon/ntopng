#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# A script to map nProbe fields to the ParserInterface.cpp and to the flow_utils.lua
#

import sys
import os
import re

def usage():
  print("""Usage: %s nprobe_help_filtered_file [indentation_level] [--c-output]

  Example invocations:
    - For ParserInterface.cpp:
      nprobe -h | python3 ./nprobe_mapping.py - 4

    - flow_utils.lua:
      nprobe -h | python3 ./nprobe_mapping.py - 2 --c-output""" % (os.path.basename(sys.argv[0])))
  exit(1)

if len(sys.argv) < 2:
  usage()

indentation = " " * int(sys.argv[2]) if len(sys.argv) >= 3 else "    "
c_output = len(sys.argv) >= 4 and sys.argv[3] == "--c-output"
# ------------------------------------------------------------------------------

fin = sys.stdin if sys.argv[1] == "-" else open(sys.argv[1])
start_ok = False

localized = []

for line in fin:
  lstripped = line.strip()

  if lstripped == "-------------------------------------------------------------------------------":
    # Start parsing output
    start_ok = True
  elif start_ok:
    if lstripped.startswith("Major protocol (%L7_PROTO) symbolic mapping"):
      break

    if pattern := re.search('^([^:]+):$', lstripped):
      # This is a section delimiter
      label = pattern.groups()[0]
      label = label.lstrip("Plugin ").rstrip("templates").strip()
      if not c_output:
        print("")
        print(f"{indentation}-- {label}")
    elif pattern := re.search(
          '^\[([^\]]+)\](\[([^\]]+)\]){0,1}\s+%(\w+)\s+(%(\w+)\s+){0,1}(.*)$',
          lstripped,
      ):
      (netflow_id, _, ipfix_id, netflow_label, _, ipfix_label, description) = pattern.groups()
      parts = netflow_id.split(" ")
      idx = parts[len(parts) - 1]

      if c_output:
        print('%saddMapping("%s", %s);' % (indentation, netflow_label, idx))

      else:
        loc_key = netflow_label.lower()
        localized.append((loc_key, description))
        print('%s["%s"] = i18n("flow_fields_description.%s"),' % (indentation, netflow_label, loc_key))
fin.close()

if not c_output:
  # Print localized mappings
  indentation = "   "
  indentation_double = indentation * 2

  print("\n------------------------ CUT HERE ------------------------\n")

  print(indentation + "flow_fields_description = {")

  for (idx, description) in localized:
    print('%s%s = "%s",' % (indentation_double, idx, description.replace("%", "%%")))

  print(indentation + "},")
