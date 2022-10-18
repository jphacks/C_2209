import collections.abc
from operator import imod # インポートしないとエラーが発生する
from pptx.util import Inches  # インチ
import pptx

from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.util import Cm,Pt               # 単位指定をするクラス(センチメートル, ポイント単位)
#from pptx.enum.text import PP_ALIGN  # 中央揃えにする用
#from pptx import Presentation # プレゼンテーションを作成
import os
from PIL import Image 

'''
配列outputにoutput_func5にある画像追加 
→ test.pyで画像出力するときに連番になるように変えていいなら、ここのコードはいらない
→ でもファイル名変えるとどの部分の画像か分からなくなって、改良しにくくなるかも
'''
output = []
num = 0
while True:  
    image_path = f'./output_func5/output1_{num:04d}.jpeg'
    if os.path.exists(image_path):
        output.append(image_path)
    num += 1
    if not os.path.exists(f'./output/output1_{num:04d}.jpeg'):
        break

#cd = os.getcwd()
prs = pptx.Presentation()
prs.slide_width = Inches(11.69) #A4サイズ
prs.slide_height = Inches(8.27)
slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白のスライドを追加

#画像のアスペクト比を取得
im = Image.open('./output/output1_0000.jpeg')
aspect_ratio = im.width /im.height

#画像の高さの設定と幅の取得
pic_height = Cm(9.5)
pic_width = aspect_ratio * pic_height


#画像を１枚のパワポに出力 1段4枚ずつ
pic_top = Cm(0.5)
pic_left = Cm(1)
pic_left2 = pic_left + pic_width
for i in range(len(output)):
    image = slide.shapes.add_picture(output[i], pic_left, pic_top, height=pic_height)
    image.line.color.rgb = RGBColor(0, 0, 0)
    image.line.width = Pt(1.5)
    pic_left += Cm(7)
    if i % 4 == 3:
        pic_top += Cm(10)
        pic_left = Cm(1)
        pic_left2 = pic_left + pic_width
        pic_top2 += Cm(11)
    elif i != len(output)-1:
    #矢印出力
        pic_top2 = pic_top + pic_height/2 - Cm(1)
        rect0 = slide.shapes.add_shape(		# shapeオブジェクト➀を追加
                MSO_SHAPE.RIGHT_ARROW,   	                    # 図形の種類を[丸角四角形]に指定
                pic_left2, pic_top2,               # 挿入位置の指定：左からの座標と上からの座標の指定
                Cm(7) - pic_width, Cm(2))               # 挿入図形の幅と高さの指定
        pic_left2 += Cm(7)

#画像を２枚ずつパワポに出力
pic_height = Cm(16)
pic_width = aspect_ratio*pic_height
slide_width = prs.slide_width
slide_height = prs.slide_height

pic_top = ( slide_height - pic_height ) / 2
for i in range(len(output)):
    if i % 2 == 0:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) 
        pic_left = ( slide_width/2 - pic_width ) / 2
    else:
        pic_left += slide_width/2
    image = slide.shapes.add_picture(output[i], pic_left, pic_top, height=pic_height)   
    image.line.color.rgb = RGBColor(0, 0, 0)
    image.line.width = Pt(1.5)

prs.save("./test.pptx")
