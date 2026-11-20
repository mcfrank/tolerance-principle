#!/bin/bash
# BabAR pilot on ccn2. Usage: G=<gpu> bash run_pilot.sh   (launch detached)
set -euo pipefail
W=/data2/mcfrank/tp_babyview/pilot
B=/data2/mcfrank/BabAR
mkdir -p $W/wav
cd $W
tail -n +2 list.tsv | cut -f1,3 | xargs -P 8 -L 1 bash -c \
  '[ -s wav/$0.wav ] || ffmpeg -nostdin -loglevel error -y -i "$1" -ac 1 -ar 16000 wav/$0.wav'
echo "wav done $(ls wav | wc -l)"
cd $B
CUDA_VISIBLE_DEVICES=$G .venv/bin/python src/pipeline.py --wavs $W/wav --output $W/vtc2 --device gpu
CUDA_VISIBLE_DEVICES=$G .venv/bin/python $W/../05_babar_alt.py --work $W --babar $B
touch $W/DONE
