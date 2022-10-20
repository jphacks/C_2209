import collections.abc
from operator import imod # インポートしないとエラーが発生する
import pptx
from pptx.enum.shapes import MSO_SHAPE    # 図形の定義がされているクラス
from pptx.dml.color import RGBColor
from pptx.util import Cm,Pt,Inches              # 単位指定をするクラス(センチメートル, ポイント単位)
import os
from PIL import Image 
from pptx.enum.text import PP_ALIGN       # 段落の水平位置のEnume

#画像の格納ディレクトリ
IMG_DIR = "./output_func5/"
#img画像のファイル名を取得
img_names = os.listdir(IMG_DIR)
img_names = [name for name in img_names if name.endswith(".jpeg")]

prs = pptx.Presentation()
prs.slide_width = Inches(11.69) #A4サイズ
prs.slide_height = Inches(8.27)

#画像のアスペクト比を取得
im = Image.open(IMG_DIR + img_names[0])
aspect_ratio = im.width /im.height

#画像の高さの設定と幅の取得
pic_height = Cm(9.5)
pic_width = aspect_ratio * pic_height


#画像を１枚のパワポに出力 1段4枚ずつ
pic_left = Cm(2.5)
pic_left2 = Cm(7.2)
for i, name in enumerate(img_names):
    path = IMG_DIR + name

    if i % 8 == 0:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        pic_top = Cm(0.5)

    #画像追加
    image = slide.shapes.add_picture(path, pic_left, pic_top, height=pic_height)
    image.line.color.rgb = RGBColor(0, 0, 0)
    image.line.width = Pt(1.5)
    
    #テキストを追加
    width = height = Pt(28)
    textbox = slide.shapes.add_textbox(pic_left-Cm(1), pic_top, width, height)
    tf = textbox.text_frame
    tf.text = str(i+1)
    tf.paragraphs[0].font.size = Pt(28)  # font size
    tf.paragraphs[0].alignment = PP_ALIGN.RIGHT

    pic_left += Cm(7)

    if i % 4 == 3:
        pic_top += Cm(10)
        pic_left = Cm(2.5)
        pic_left2 = Cm(7.2)
        pic_top2 += Cm(11)
    elif i != len(img_names)-1:

    #矢印出力
        pic_top2 = pic_top + pic_height/2 - Cm(1)
        rect0 = slide.shapes.add_shape(		# shapeオブジェクト➀を追加
                MSO_SHAPE.RIGHT_ARROW,   	                    # 図形の種類を[丸角四角形]に指定
                pic_left2, pic_top2,               # 挿入位置の指定：左からの座標と上からの座標の指定
                Cm(2), Cm(2))               # 挿入図形の幅と高さの指定
        rect0.fill.solid()                                   # shapeオブジェクト➀を単色で塗り潰す
        rect0.fill.fore_color.rgb = RGBColor(74, 126, 187)  # RGB指定で色を指定
        pic_left2 += Cm(7) 

#画像を２枚ずつパワポに出力
pic_height = Cm(16)
pic_width = aspect_ratio * pic_height
slide_width = prs.slide_width
slide_height = prs.slide_height
pic_top = ( slide_height - pic_height ) / 2

for i, name in enumerate(img_names):
    path = IMG_DIR + name

    if i % 2 == 0:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) 
        pic_left = ( slide_width/2 - pic_width ) / 2
    else:
        pic_left += slide_width/2

    #画像を追加
    image = slide.shapes.add_picture(path, pic_left, pic_top, height=pic_height)   
    image.line.color.rgb = RGBColor(0, 0, 0)
    image.line.width = Pt(1.5)

    #テキストを追加
    width = height = Pt(36)
    textbox = slide.shapes.add_textbox(pic_left-Cm(1.5), pic_top, width, height)
    tf = textbox.text_frame
    tf.text = str(i+1)
    tf.paragraphs[0].font.size = Pt(36)  # font size
    tf.paragraphs[0].alignment = PP_ALIGN.RIGHT

    #矢印出力
    ratio = 0.45
    pic_left2 = slide_width/2 - pic_width*ratio/2
    pic_top2 = slide_height/2 - pic_width*ratio/2
    rect0 = slide.shapes.add_shape(		# shapeオブジェクト➀を追加
            MSO_SHAPE.RIGHT_ARROW,   	                    # 図形の種類を[丸角四角形]に指定
            pic_left2, pic_top2,               # 挿入位置の指定：左からの座標と上からの座標の指定
            pic_width*ratio, pic_width*ratio)               # 挿入図形の幅と高さの指定
    rect0.fill.solid()                                   # shapeオブジェクト➀を単色で塗り潰す
    rect0.fill.fore_color.rgb = RGBColor(74, 126, 187)  # RGB指定で色を指定

prs.save("./test.pptx")
