#!/usr/bin/env python
"""video_line_draw.py."""
__author__ = "amxrfe"
__copyright__ = "Copyright 2021, Planet Earth"


import os
import argparse
import cv2 as cv
from cairosvg import svg2png


def call_linedraw(linedraw_py_, img_path_png_, img_path_svg_, width_, contour=2):
    # '-i', '--input', help='Input path')
    # '-o', '--output', help='Output path.')
    # '-b', '--show_bitmap', help="Display bitmap preview.")
    # '-nc', '--no_contour', help="Don't draw contours.")
    # '-nh', '--no_hatch', help='Disable hatching.')
    # '-hs', '--hatch_size', help='Patch size of hatches. eg. 8, 16, 32')
    # '-cs', '--contour_simplify', help='Level of contour simplification. eg. 1, 2, 3')
    # '-r', '--resolution', help='Level of contour simplification. eg. 1, 2, 3')
    os.system("python " + linedraw_py_ +
              " -r " + str(width_) +
              " -i " + img_path_png_ +
              " -o " + img_path_svg_ + 
              " -cs " + str(contour)
              )


def save_svg2png(path_svg_in, path_png_out, height_, width_):
    # get png from svg
    multi = 2
    scale = 2
    file_handle = open(path_svg_in)
    svg_handle = file_handle.read()
    file_handle.close()
    svg2png(bytestring=svg_handle,
            write_to=path_png_out,
            scale=scale,
            parent_height=height_ / multi,
            parent_width=width_ / multi,
            output_height=height_ * multi,
            output_width=width_ * multi)


def progressBar(current, total, barLength=20):
    percent = float(current) * 100 / total
    arrow = '-' * int(percent/100 * barLength - 1) + '>'
    spaces = ' ' * (barLength - len(arrow))
    print("Progress: [%s%s] | Frame: %d / %d" % (arrow, spaces, current, total), end='\r')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='text_video_draw.py')
    parser.add_argument("-i", "--input", type=str, help='input mp4 video')
    parser.add_argument("-c", "--contour", type=str, default=False, help='True = variable contour, False = const contour')
    args = parser.parse_args()

    if args.contour == "T":
        args.contour = True
    else:
        args.contour = False

    if not os.path.isfile(args.input):
        print("dude, no video selected")
        exit(-1)
    video_file = cv.VideoCapture(args.input)

    d = os.path.dirname(__file__)  # directory of script
    tmp_dir = r'{}/tmp_image/'.format(d)  # path to be created
    outpath_video = r'{}/output_video/'.format(d)  # path to be created
    linedraw_py = r'{}/linedraw.py'.format(d)
    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(outpath_video, exist_ok=True)
    except OSError:
        pass

    # get images
    count_frame = 0
    total_frame = int(video_file.get(cv.CAP_PROP_FRAME_COUNT))
    img_path_png = ""
    contour_multiplier = int(video_file.get(cv.CAP_PROP_FPS)//2)  # each half second contour simplification will change
    contour_rotation = [2] * contour_multiplier + [3] * contour_multiplier + [2] * contour_multiplier + [1] * contour_multiplier
    while video_file.isOpened():
        ret, img = video_file.read()
        number_str = str(count_frame)
        zero_filled_number = number_str.zfill(5)
        tmp_image_name = "im" + str(zero_filled_number)
        progressBar(count_frame, total_frame)
        if args.contour:
            contour = contour_rotation[count_frame % len(contour_rotation)]
        else:
            contour = 2
        if ret:
            if os.path.isfile(tmp_dir + tmp_image_name + ".jpg"):
                # avoid to recreate the same image
                pass
            else:
                height, width = img.shape[0], img.shape[1]
                # get svg sketch image
                img_path_png = tmp_dir + tmp_image_name + "_.png"
                img_path_svg = tmp_dir + tmp_image_name + ".svg"
                img_path_png2 = tmp_dir + tmp_image_name + ".png"
                img_path_jpg = tmp_dir + tmp_image_name + ".jpg"

                # save img as png
                cv.imwrite(img_path_png, img)
                # os.system("python " + linedraw_py + " -r " + str(width) + " -i " + img_path_png + " -o " + img_path_svg)
                call_linedraw(linedraw_py, img_path_png, img_path_svg, width)
                # get png from svg
                save_svg2png(img_path_svg, img_path_png2, height, width, contour)
                os.remove(img_path_png)
                os.remove(img_path_svg)
                image_to_jpg = cv.imread(img_path_png2, cv.IMREAD_UNCHANGED)
                image_to_jpg = ~image_to_jpg[:, :, 3]  # extract and invert that alpha
                cv.imwrite(img_path_jpg, image_to_jpg, [int(cv.IMWRITE_JPEG_QUALITY), 100])
                os.remove(img_path_png2)
            count_frame += 1
        else:
            break
    os.system("ffmpeg -y -start_number 0 -i " + tmp_dir + "im%05d.jpg -c:v libx264 -r 24.97 " + outpath_video + "_reconstructed_video.mp4")
    # fix i frame re encoding
    os.system("ffmpeg -y -i " + outpath_video + "_reconstructed_video.mp4 -c:v libx264 -r 24.97 " + outpath_video + "reconstructed_video.mp4")
    os.remove(outpath_video + "_reconstructed_video.mp4")
    rm_imgs = [f for f in os.listdir(tmp_dir) if f.endswith('.jpg') or f.endswith('.png')]
    for rm_img in rm_imgs:
        os.remove(tmp_dir + rm_img)
    print("done")
