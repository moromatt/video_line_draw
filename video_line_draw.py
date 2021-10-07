#!/usr/bin/env python
"""video_line_draw.py."""
__author__ = "amxrfe"
__copyright__ = "Copyright 2021, Planet Earth"


import os
import argparse
import pathlib
import cv2 as cv
from cairosvg import svg2png


def save_svg2png(path_svg_in, path_png_out, height_, width_):
    # get png from svg
    file_handle = open(path_svg_in)
    svg_handle = file_handle.read()
    file_handle.close()
    svg2png(bytestring=svg_handle,
            write_to=path_png_out,
            scale=2,
            parent_height=height_ / 2,
            parent_width=width_ / 2,
            output_height=height_ * 2,
            output_width=width_ * 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='text_video_draw.py')
    parser.add_argument("-i", "--input", type=str, help='input mp4 video')
    args = parser.parse_args()
    if not os.path.isfile(args.input):
        print("dude, no video selected")
        exit(-1)
    video_file = cv.VideoCapture(args.input)

    d = os.path.dirname(__file__)  # directory of script
    tmp_dir = r'{}/tmp_image/'.format(d)  # path to be created
    outpath_video = r'{}/output_video/'.format(d)  # path to be created
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(outpath_video, exist_ok=True)
    except OSError:
        pass

    # get images
    count_frame = 0
    img_path_png = ""
    while video_file.isOpened():
        ret, img = video_file.read()
        if ret:
            if os.path.isfile(img_path_png):
                # avoid to recreate the same image
                pass
            else:
                number_str = str(count_frame)
                zero_filled_number = number_str.zfill(5)
                tmp_image_name = "im" + str(zero_filled_number)
                height, width = img.shape[0], img.shape[1]
                # get svg sketch image
                img_path_png = tmp_dir + tmp_image_name + "_.png"
                img_path_svg = tmp_dir + tmp_image_name + ".svg"
                img_path_png2 = tmp_dir + tmp_image_name + ".png"
                # save img as png
                cv.imwrite(img_path_png, img)
                os.system("python ./linedraw.py -i " + img_path_png + " -o " + img_path_svg)
                # get png from svg
                save_svg2png(img_path_svg, img_path_png2, height, width)
                os.remove(img_path_png)
                os.remove(img_path_svg)
                count_frame += 1
        else:
            break
    os.system("ffmpeg -y -start_number 0 -i im%05d.png -c:v libx264 -r 24.97 " + outpath_video + "reconstructed_video.mp4")
    rm_imgs = [f for f in os.listdir(tmp_dir) if f.endswith('.jpg') or f.endswith('.png')]
    for rm_img in rm_imgs:
        os.remove(rm_img)
    print("done")
