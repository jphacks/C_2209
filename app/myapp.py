import tkinter
import tkinter.filedialog
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from tqdm import tqdm # プログレスバーの導入

class Model():

    def __init__(self):

        # 動画オブジェクト参照用
        self.cap= None

        # 読み込んだフレーム
        self.frames = []

        # 読み込んだフレームの選択状態 0:選択、1:未選択 2:被り
        # 最初から2は消しておくかもしれない
        self.frame_state = []

        self.state = list(range(0, 8))

        # PIL画像オブジェクト参照用
        self.image = None

        # Tkinter画像オブジェクト参照用
        self.image_tk = None

        # 現在表示中のフレーム
        self.now = tkinter.IntVar()

        self.create_video("./input/input1.MP4")

    def create_video(self, path):
        '動画オブジェクトの生成を行う'

        # pathの動画から動画オブジェクト生成
        self.cap = cv2.VideoCapture(path)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f'{width=} {height=} {frame_count=}')

        self.frames = []
        self.frame_state = [0]*frame_count
        for i in tqdm(range(frame_count)):
            ret, img = self.cap.read()
            if ret == False:
                break
            # 画像をリサイズする　20分の1に圧縮
            if i % 20 != 0:
                continue
            rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            pil_image = pil_image.resize((round(width/4), round(height/4)), resample=3)
            self.frames.append(ImageTk.PhotoImage(pil_image))
        # セットする
        self.now.set(3)

    def set_vec_now(self, a):
        for i in range(8):
            state_ = self.now.get() + i - 4
            state_ = min( state_, len(self.frames)-1)
            state_ = max( state_, 0)
            self.state[i] = state_

    def next_frame(self):
        next = min(self.now.get()+1, len(self.frames)-1)
        self.now.set(next)

    def previous_frame(self):
        next = max(self.now.get()-1, 0)
        self.now.set(next)


class View():

    def __init__(self, app, model):

        self.master = app
        self.model = model

        # callbackを用意
        self.model.now.trace_add("write", self.draw_image)

        # アプリ内のウィジェットを作成
        self.create_widgets()

    def create_widgets(self):
        'アプリ内にウィジェットを作成・配置する'

        # キャンバスのサイズ
        canvas_width = 1200
        canvas_height = 900

        # キャンバスとボタンとタイトル配置するフレームの作成と配置
        self.main_frame = tkinter.Frame(
            self.master
        )
        self.main_frame.pack()

        # 上の表示を配置するフレームの作成と配置
        self.head_frame = tkinter.Frame(
            self.main_frame,
            height=200,
            width=700,
            bg="red"
        )
        self.head_frame.grid(column=1, row=1)

        # キャンバスを配置するフレームの作成と配置
        self.canvas_frame = tkinter.Frame(
            self.main_frame
        )
        self.canvas_frame.grid(column=1, row=2)

        # ユーザ操作用フレームの作成と配置
        self.operation_frame = tkinter.Frame(
            self.main_frame
        )
        self.operation_frame.grid(column=1, row=3)

        # キャンバスの配列
        self.canvas_paneles = [tkinter.Frame(
            self.canvas_frame,
            width=canvas_width/5.5,
            height=canvas_height/2,
            bg="#FFFFFF") for x in range(8)]
        # [self.canvas_paneles[x].pack(fill = 'x', padx=10, side = 'left') for x in range(7)]
        [self.canvas_paneles[x].grid(column=x, row=1) for x in range(1, 8)]

        # キャンバスごとのフレーム番号表示
        self.frame_index = [tkinter.Label(
            self.canvas_paneles[x],
            textvariable=self.model.now) for x in range(8)]
        [self.frame_index[x].pack() for x in range(8)]

        # キャンバスごとのフレーム表示
        self.frame = [tkinter.Canvas(
            self.canvas_paneles[x],
            width=canvas_width/5.5,
            height=canvas_height/2,
            bg="#FFFFFF") for x in range(8)]
        [self.frame[x].pack() for x in range(8)]

        # キャンパスごとのボタン表示
        self.state_button = [tkinter.Button(
            self.canvas_paneles[x],
            text="button") for x in range(8)]
        [self.state_button[x].pack() for x in range(8)]

        # ファイル読み込みボタンの作成と配置
        self.load_button = tkinter.Button(
            self.operation_frame,
            text="動画選択"
        )
        self.load_button.pack()

        # val = tkinter.IntVar()
        self.scale_bar = ttk.Scale(
            self.operation_frame,
            variable=self.model.now,
            orient=tkinter.HORIZONTAL,
            length=600,
            from_=0,
            to=len(self.model.frames)-1,
            # command=lambda e: self.draw_image()
        )
        self.scale_bar.pack()

        # グレーON/OFFボタンの作成と配置
        self.gray_button = tkinter.Button(
            self.operation_frame,
            text="Next Frame"
        )
        self.gray_button.pack(fill = 'x', padx=20, side = 'right')

        # フリップ/OFFボタンの作成と配置
        self.flip_button = tkinter.Button(
            self.operation_frame,
            text="Previous Frame"
        )
        self.flip_button.pack(fill = 'x', padx=20, side = 'left')

    def select_open_file(self, file_types):
        'オープンするファイル選択画面を表示'

        # ファイル選択ダイアログを表示
        file_path = tkinter.filedialog.askopenfilename(
            initialdir=".",
            filetypes=file_types
        )
        return file_path

    def draw_image(self, a, b, c):
        self.model.set_vec_now(self.model)
        '画像をキャンバスに描画'
        for i in range(len(self.canvas_paneles)):
            now = self.model.state[i]
            image = self.model.frames[now]
            if image is None:
                continue
            self.frame[i].delete('all')
            self.frame[i].create_image(
                0, 0,
                image=image,
                anchor=tkinter.NW,
                tag="image"
            )

class Controller():

    def __init__(self, app, model, view):
        self.master = app
        self.model = model
        self.view = view

        self.set_events()

    def set_events(self):
        '受け付けるイベントを設定する'

        # 動画選択ボタン押し下げイベント受付
        self.view.load_button['command'] = self.push_load_button

        # モノクロON/OFFボタン押し下げイベント受付
        self.view.gray_button['command'] = self.push_gray_button

        # フリップON/OFFボタン押し下げイベント受付
        self.view.flip_button['command'] = self.push_flip_button
        
    def push_load_button(self):
        '動画選択ボタンが押された時の処理'

        file_types = [
            ("MOVファイル", "*.mov"),
            ("MP4ファイル", "*.mp4"),
        ]

        # ファイル選択画面表示
        file_path = self.view.select_open_file(file_types)
        if len(file_path) != 0:
            # 動画オブジェクト生成
            self.model.create_video(file_path)

    def push_gray_button(self):
        self.model.next_frame()

    def push_flip_button(self):
        self.model.previous_frame()


app = tkinter.Tk()

app.title("らくらくトリセツ")

model = Model()
view = View(app, model)
controller = Controller(app, model, view)

app.mainloop()