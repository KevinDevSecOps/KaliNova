#!/bin/bash
# Uso: ./rf_killchain.sh -f 433M -t TARGET_ID
while getopts "f:t:" opt; do
  case $opt in
    f) freq="$OPTARG" ;;
    t) target="$OPTARG" ;;
  esac
done
hackrf_sweep -f ${freq} -w 100000 -r /tmp/${target}_scan.csv
python3 rf_deauth.py -f ${freq} -t ${target}  # Jammer ético