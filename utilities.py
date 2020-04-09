import pytesseract
from pytesseract import Output
import pandas as pd
import os
import time
import numpy as np
import cv2
from PIL import ImageDraw
from PIL import ImageFont
from translate import *
import shutil
import fitz
import glob
import colorsys
import PIL.Image as Image


image_suffix = ".png"
result_pdf_fold = 'result_pdf/'
temp_fold = 'temp/'
result_fold = 'result/'
pdf_pic_fold = 'pdf_pic/'
recognized_result_fold = 'recognized_result/'
font_type = '/System/Library/Fonts/STHeiti Light.ttc'
font_medium_type = '/System/Library/Fonts/STHeiti Medium.ttc'
header_font = ImageFont.truetype(font_medium_type, 24)
title_font = ImageFont.truetype(font_medium_type, 20)

page_num = 0
pdf_name = 'translate_result'

font_color = '#000000'
google_url = 'https://translate.google.cn/#view=home&op=translate&sl=en&tl=zh-CN&text='


def draw_text(text, font_size, width, height, index, bkg_color):
    im_temp = Image.new("RGB", (width, height), bkg_color)
    dr = ImageDraw.Draw(im_temp)
    if 35 < font_size < 45:
        font = ImageFont.truetype(font_type, 30)
    elif font_size >= 45:
        font = ImageFont.truetype(font_medium_type, 45)
    else:
        font = ImageFont.truetype(font_type, 16)
    n = int(width / font.size)
    if n == 0:
        n = 1
    text_list = [text[i:i + n] for i in range(0, len(text), n)]
    for text_index, text in enumerate(text_list):
        dr.text((5, 5 + text_index * (font.size + 10)), u'%s' % text, font_color, font)
    im_temp.save(temp_fold + str(index) + '_tran' + image_suffix)


def trans_image(image_path, image_index):
    # open image
    image = Image.open(image_path)
    # code = pytesseract.image_to_string(image, lang='eng')
    data = pytesseract.image_to_data(image, output_type=Output.DATAFRAME, lang='eng')
    data = pd.DataFrame(data)
    conf_count = 0
    block_begin = False  # 分块开始标志
    par_flag = False  # 分段开始标志
    line_flag = False  # 分行开始标志
    block_rec = []  # 识别文字区块的左上和右下坐标
    block_count = 0  # 分块数量
    block_max_width = 0  # 考虑到首行缩进，需要得到分块的最大宽度
    block_text = []  # 分块文字
    trans_text = []  # 翻译后的分块文字
    font_height = []  # 字体平均高度，用来判断字体格式
    line_sum = 0  # 分块的行数，用来计算每一行的平均高度（当作字体平均高度）
    text = ''

    for index in data.index:
        conf = data.loc[index]['conf']
        word = data.loc[index]['text']
        if conf == -1:
            conf_count += 1
            line_flag = False
        else:
            if conf_count == 3:  # 如果判断到该字符时conf_count等于3，就说明遇到了分栏的情况
                width = data.loc[index - 4]['left'] + data.loc[index - 4]['width'] - block_rec[block_count][0][0]
                if width > block_max_width:
                    block_max_width = width
                # print("分栏")
                block_rec[block_count].append((block_rec[block_count][0][0] + block_max_width,
                                               data.loc[index - 4]['top'] + data.loc[index - 4]['height']))
                if line_sum != 0:
                    if data.loc[index - 3]['height'] > 1000 and data.loc[index - 4]['line_num'] == 1:  # 判断是否为小标题
                        font_height.append((block_rec[block_count][1][1] - block_rec[block_count][0][1]) / line_sum + 10)
                    else:
                        font_height.append((block_rec[block_count][1][1] - block_rec[block_count][0][1]) / line_sum)
                else:
                    font_height.append(0)
                block_count += 1
                block_max_width = 0
                block_begin = False
                line_sum = 0
            elif conf_count == 1:  # 如果conf_count只等于1就说明分行的情况
                width = data.loc[index - 1]['left'] + data.loc[index - 1]['width'] - block_rec[block_count][0][0]
                if width > block_max_width:
                    block_max_width = width
                par_flag = False
                if data.loc[index-1]['height'] > 45:  # 这里将其当作标题来处理 需要将其单独划分为一个block
                    # print("标题")
                    block_rec[block_count].append((block_rec[block_count][0][0] + block_max_width,
                                                   data.loc[index - 2]['top'] + data.loc[index - 2]['height']))
                    if line_sum != 0:
                        font_height.append((block_rec[block_count][1][1] - block_rec[block_count][0][1]) / line_sum)
                    else:
                        font_height.append(0)
                    block_text.append(text)
                    trans_text.append(trans(text))
                    text = ''
                    time.sleep(1)
                    block_count += 1
                    block_max_width = 0
                    block_begin = False
                    line_sum = 0
            elif conf_count == 2 and data.loc[index + 1]['conf'] != -1 and index != len(data) - 1:
                width = data.loc[index - 3]['left'] + data.loc[index - 3]['width'] - block_rec[block_count][0][0]
                if width > block_max_width:
                    block_max_width = width
                # print("分段")
                block_rec[block_count].append((block_rec[block_count][0][0] + block_max_width,
                                               data.loc[index - 3]['top'] + data.loc[index - 3]['height']))
                if line_sum != 0:
                    font_height.append((block_rec[block_count][1][1] - block_rec[block_count][0][1]) / line_sum)
                else:
                    font_height.append(0)
                block_count += 1
                block_max_width = 0
                block_begin = False
                line_sum = 0
            conf_count = 0
            if not block_begin:
                block_rec.append([])
                block_rec[block_count].append((data.loc[index]['left'], data.loc[index]['top']))
                block_begin = True
            if not par_flag:
                par_flag = True
                par_begin_x = data.loc[index]['left']
                if block_rec[block_count][0][0] > par_begin_x:
                    block_rec[block_count][0] = (par_begin_x, block_rec[block_count][0][1])
            if not line_flag:
                line_sum += 1
                line_flag = True
            if word[-1] == '-':
                text += word.strip('-')
            else:
                text += word + ' '
            if index != len(data) - 1:
                if data.loc[index]['par_num'] != data.loc[index + 1]['par_num']:
                    block_text.append(text)
                    trans_text.append(trans(text))
                    text = ''
                    time.sleep(1)
            else:  # 如果为整篇最后一个字符
                block_rec[block_count].append((block_rec[block_count][0][0] + block_max_width,
                                               data.loc[index]['top'] + data.loc[index]['height']))
                block_begin = False
                if line_sum != 0:
                    font_height.append((block_rec[block_count][1][1] - block_rec[block_count][0][1]) / line_sum)
                else:
                    font_height.append(0)
                line_sum = 0
                line_flag = False
                block_text.append(text)
                trans_text.append(trans(text))
                text = ''
                time.sleep(1)

    image_rec = cv2.imread(image_path)

    """根据识别出来的不同block进行裁剪并用中文替换掉原来位置上的英文"""
    for i in range(len(block_rec)):
        if block_text[i] != '  ':
            region = image.crop(
                (block_rec[i][0][0] - 5, block_rec[i][0][1] - 5, block_rec[i][1][0] + 5, block_rec[i][1][1] + 5))
            cv2.rectangle(image_rec, (block_rec[i][0][0], block_rec[i][0][1]), (block_rec[i][1][0], block_rec[i][1][1]), (255, 0, 0), 1)
            region.save(temp_fold + str(i) + image_suffix)
            region = region.convert('RGB')
            draw_text(trans_text[i], font_height[i], block_rec[i][1][0] - block_rec[i][0][0] + 10,
                      block_rec[i][1][1] - block_rec[i][0][1] + 10, i, get_dominant_color(region))
            image_tran = Image.open(temp_fold + str(i) + '_tran' + image_suffix)
            image.paste(image_tran,
                        (block_rec[i][0][0] - 5, block_rec[i][0][1] - 5, block_rec[i][1][0] + 5, block_rec[i][1][1] + 5))
    image.save(result_fold + str(image_index) + image_suffix)
    cv2.imwrite(recognized_result_fold+"rec_{}.jpg".format(image_index), image_rec)


def get_dominant_color(image):
    max_score = 0.0001
    dominant_color = None
    for count, (r, g, b) in image.getcolors(image.size[0] * image.size[1]):
        # 转为HSV标准
        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
        y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
        y = (y - 16.0) / (235 - 16)

        score = (saturation + 0.1) * count
        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)
    return dominant_color


def pdf2_image(pdf_path):
    global pdf_name
    doc = fitz.open(pdf_path)
    pdf_name = pdf_path.split('/')[-1]
    name, ext = os.path.splitext(pdf_name)
    pdf_name = name
    rotate = int(0)  # 设置图片的旋转角度
    zoom_x = 2.0  # 设置图片相对于PDF文件在X轴上的缩放比例
    zoom_y = 2.0  # 设置图片相对于PDF文件在Y轴上的缩放比例
    trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
    print("%s开始转换..." % pdf_path)
    if doc.pageCount >= 1:  # 获取PDF的页数
        for pg in range(doc.pageCount):
            page = doc[pg]  # 获得第pg页
            pm = page.getPixmap(matrix=trans, alpha=False)  # 将其转化为光栅文件（位数）
            pm.writeImage(pdf_pic_fold + str(pg) + ".jpg")  # 将其输入为相应的图片格式，可以为位图，也可以为矢量图
    print("%s转换完成！" % pdf_path)


def trans_pic():
    dirs = os.listdir(pdf_pic_fold)
    for file in dirs:
        filename = os.path.join(pdf_pic_fold, file)
        suffix = filename.split('.')[-1]
        name = filename.split('/')[-1]
        index, ext = os.path.splitext(name)
        if suffix == 'jpg':
            print(name + "开始翻译...")
            trans_image(filename, index)
            print(name + "翻译完成!")
    print("翻译完成！")


def image2_pdf():
    global pdf_name
    doc = fitz.open()
    for img in sorted(glob.glob(result_fold + "*")):  # 读取图片，确保按文件名排序
        imgdoc = fitz.open(img)  # 打开图片
        pdfbytes = imgdoc.convertToPDF()  # 使用图片创建单页的 PDF
        imgpdf = fitz.open("pdf", pdfbytes)
        doc.insertPDF(imgpdf)  # 将当前页插入文档
    if os.path.exists(result_pdf_fold + pdf_name + "_tran.pdf"):
        os.remove(result_pdf_fold + pdf_name + "_tran.pdf")
    doc.save(result_pdf_fold + pdf_name + "_tran.pdf")  # 保存pdf文件
    doc.close()
    print("图片转换称PDF完成！")
    clean_cache()


def clean_cache():
    """
    清理缓存文件夹
    :return:
    """
    clean_fold(temp_fold)
    clean_fold(pdf_pic_fold)
    clean_fold(result_fold)
    clean_fold(recognized_result_fold)


def clean_fold(path):
    shutil.rmtree(path)
    os.mkdir(path)