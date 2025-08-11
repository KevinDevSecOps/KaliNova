import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--freq", help="Frecuencia objetivo (ej: 868M)")
parser.add_argument("-t", "--target", help="MAC del dispositivo")
args = parser.parse_args()
os.system(f"hackrf_transfer -f {args.freq} -s 2M -n 1000000 -x 30 -m 0x01")  # Modo jammer