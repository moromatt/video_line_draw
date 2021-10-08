#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate video
read -p "Input video path: " this
python ./video_line_draw.py -i ${this}
read