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
aspect_ratio = im.width/im.height

#画像の高さの設定と幅の取得
pic_height = Cm(9.5)
pic_width = aspect_ratio*pic_height


#画像を１枚のパワポに出力 1段4枚ずつ
start_top = 0.5
start_left = 1
start_left2 = start_left + pic_width/360000
for i in range(len(output)):
    pic_left = Cm(start_left)
    pic_top = Cm(start_top)
    image = slide.shapes.add_picture(output[i], pic_left, pic_top, height=pic_height)
    image.line.color.rgb = RGBColor(0, 0, 0)
    image.line.width = Pt(1.5)
    start_left += 7
    if i % 4 == 3:
        start_top += 10
        start_left = 1
        start_left2 = start_left + pic_width/360000
        start_top2 += 11
    elif i != len(output)-1:
    #矢印出力
        start_top2 = start_top + pic_height/360000/2 - 1
        rect0 = slide.shapes.add_shape(		# shapeオブジェクト➀を追加
                MSO_SHAPE.RIGHT_ARROW,   	                    # 図形の種類を[丸角四角形]に指定
                Cm(start_left2), Cm(start_top2),               # 挿入位置の指定：左からの座標と上からの座標の指定
                Cm(7 - pic_width/360000), Cm(2))               # 挿入図形の幅と高さの指定
        start_left2 += 7

#画像を２枚ずつパワポに出力
pic_height = Cm(16)
pic_width = aspect_ratio*pic_height

start_top = ( prs.slide_height/360000 - pic_height/360000 ) / 2
for i in range(len(output)):
    if i % 2 == 0:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) 
        start_left = ( prs.slide_width/2/360000 - pic_width/360000 ) / 2
    else:
        start_left += prs.slide_width/2/360000
    pic_left = Cm(start_left)
    pic_top = Cm(start_top)
    image = slide.shapes.add_picture(output[i], pic_left, pic_top, height=pic_height)   
    image.line.color.rgb = RGBColor(0, 0, 0)
    image.line.width = Pt(1.5)

prs.save("./test.pptx")
