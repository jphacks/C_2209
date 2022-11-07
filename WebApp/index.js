const fileInput = document.getElementById('filename');
const video = document.getElementById('video');
let videoWidth, videoHeight, videoRatio;
let stateOfFrame = [];
let prewviewMode = true;
let index = 0;



// FileInputのchangeイベントで呼び出す関数
const handleFileSelect = () => {
    var URL = URL || webkitURL;
    let videofile = fileInput.files[0];
    video.src = URL.createObjectURL(videofile);
    // document.getElementById('filename').innerHTML = video.src;
}

// ファイル選択時にhandleFileSelectを発火
fileInput.addEventListener('change', handleFileSelect);

// 編集モードとプレビューモードの切り替え
function modeChange() {
    prewviewMode = !prewviewMode;
    for(var i = 0;i < stateOfFrame.length; i++){
        if(prewviewMode){ // プレビューに変わったので
            if(stateOfFrame[i]) document.getElementById("allDiv" + (i)).hidden = false;
            else document.getElementById("allDiv" + (i)).hidden = true;
        }
        else{ // 編集モードに入ったので全てを表示
            document.getElementById("allDiv" + (i)).hidden = false;
        }
    }
    // モードの切り替え
    let mode = document.getElementsByClassName('mode');
    let modeChange = document.getElementsByClassName('modeChange');
    [mode[0].hidden, mode[1].hidden] = [mode[1].hidden, mode[0].hidden];
    console.log(modeChange.length);
    [modeChange[0].hidden, modeChange[1].hidden] = [modeChange[1].hidden, modeChange[0].hidden];
}

// ページ遷移を行う
function nextPage() {
    $.scrollify.next();
}

// フレームの選択/非選択の切り替え
function stateChange(i){
    stateOfFrame[i] = !stateOfFrame[i];
    const allDivi = document.getElementById("allDiv" + (i));
    if(prewviewMode) allDivi.hidden = true;
    const buttonElement = allDivi.childNodes[1].childNodes[0].childNodes;
    [buttonElement[0].hidden, buttonElement[1].hidden] = [buttonElement[1].hidden, buttonElement[0].hidden];
}

// opencv.jsの読み込みが終わってから動く関数
function onCvLoaded() {
    console.log('cv', cv); //debug用
    cv.onRuntimeInitialized = onReady;
}

// videoの再生時に処理を行う関数達
let streaming = true;
function onReady() {
    console.log('ready');
    let src, diff_src, pre_src;
    let cap;
    let pre_img_is_similar = false;
    const rate_similer = 0.95;
    
    video.controls = true;

    // videoタグに対して、再生・ポーズ・終了などのアクションに対して発火する関数をセットしている
    video.addEventListener('play', start);
    video.addEventListener('pause', pause);
    video.addEventListener('ended', stop);

    // 動画の再生時に発火する関数
    // processvideoを最後に呼んでいる
    function start() {
        if(!streaming) return;
        console.log('playing...');
        videoWidth  = video.videoWidth; // video本体の大きさ取得
        videoHeight = video.videoHeight;
        videoRatio = videoHeight/videoWidth;
        video.height = videoHeight; // videoElementの大きさを決める(capのため)
        video.width = videoWidth;
        video.playbackRate = 4.0;
        src      = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
        diff_src = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
        pre_src  = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
        cap = new cv.VideoCapture(video);
        setTimeout(processVideo, 0);
    }

    // 動画のポーズ時に発火する関数
    function pause() {
        // video.play();
        stop();
    }

    // 動画の終了時に発火する関数
    function stop() {
        console.log('paused or ended');
        streaming = false;
    }

    // 再生されている動画から画像を切り出す関数
    function processVideo() {
        if(!streaming) return;
        
        // 今videoで流れている画像をsrcにreadする処理
        // アイデア:ここの処理をsrc1とsrc2に交互に読み込めばコピーが起こらない
        cap.read(src);
        
        // diffをとる
        cv.absdiff(pre_src, src, diff_src);
        cv.bitwise_not(diff_src, diff_src);
        cv.cvtColor(diff_src, diff_src, cv.COLOR_RGBA2GRAY, 0);

        let channels = diff_src.channels(); //要素の次元
        let count = 0;
        let Lcount = 0;
        for (let y = 0; y < diff_src.rows; y+=10) {
            for (let x = 0; x < diff_src.cols; x+=10) {
                for (let c = 0; c < channels; ++c) {
                    if(diff_src.ucharPtr(y, x)[c] > 240){
                        count+=1;
                    }
                    Lcount+=1;
                }
            }
        }
        let similler = count/Lcount;
        if(similler < rate_similer && pre_img_is_similar){ // アニメーション始まり
            canvas_id = addCanvas(index, true);
            cv.imshow(canvas_id, pre_src);
            stateOfFrame.push(true);
            index++;
            pre_img_is_similar = false;
        }else if(similler >= rate_similer && !pre_img_is_similar){ // アニメーション終わり
            canvas_id = addCanvas(index, false);
            cv.imshow(canvas_id, src);
            stateOfFrame.push(false);
            index++;
            pre_img_is_similar = true;
        }
        
        pre_src = src.clone(); // 30フレームx10秒くらいやると落ちる, 6フレームx50秒くらいまで耐えられる
        setTimeout(processVideo, 0);
    }
}

// 「選択された画像の一覧画面」のところに<canvas>を追加する処理
function addCanvas(i, isSelected) {

    let parentnode = document.getElementsByClassName('canvases');

    // 一番外側のdiv要素
    let allDivElement = document.createElement('div');
    allDivElement.id = "allDiv" + (i);
    allDivElement.hidden = !isSelected; // 選択状態なら隠さない
    // ボタンのためのdiv
    let buttonDivElement = document.createElement('div');
    buttonDivElement.style="text-align:center";
    // ボタン
    let buttonElement = document.createElement('button');
    buttonElement.onclick = () => stateChange(i);
    buttonElement.className="buttonDiv";
    // 選択ボタン
    let checkboxElement = document.createElement('img');
    checkboxElement.src="assets/選択box.png";
    checkboxElement.hidden = !isSelected;
    // 未選択ボタン
    let noncheckboxElement = document.createElement('img');
    noncheckboxElement.src="assets/未選択box.png";
    noncheckboxElement.hidden = isSelected;

    // キャンバス
    let canvasElement = document.createElement('canvas');
    canvasElement.id = "canvas" + (i);
    canvasElement.style.width  = Math.round(videoWidth /4)+"px";
    canvasElement.style.height = Math.round(videoHeight/4)+"px";
    canvasElement.willReadFrequently = true;

    buttonElement.appendChild(checkboxElement);
    buttonElement.appendChild(noncheckboxElement);
    buttonDivElement.appendChild(buttonElement);
    allDivElement.appendChild(canvasElement);
    allDivElement.appendChild(buttonDivElement);
    parentnode[0].appendChild(allDivElement);

    return canvasElement.id;
}

// パワーポイントを作る関数
function makePPTX() {
    const allStart = performance.now();
    function Cm(n) {
        return n * 0.3937;
    }
    function Pt(n) {
        return n / 72;
    }

    //let startTime = performance.now();

    let pptx = new PptxGenJS();
    pptx.defineLayout({ name:'A4', width:11.7, height:8.3 });
    pptx.layout = 'A4';
    let slide = pptx.addSlide();

    let x = Cm(2.5);
    let y = Cm(0.5);
    let x2 = Cm(7.2);
    let y2 = Cm(4.25);
    let width = Cm(4.39);
    //let height = Cm(9.5);
    let height = width * videoRatio;
    let selectedImageData = [];
    let size = 28;

    // canvasに書かれたデータを読み取るコード
    for(let i=0; i<stateOfFrame.length; i++) {
        if(stateOfFrame[i]) {
            cvs = document.getElementById(`canvas${i}`);
            ctx = cvs.getContext('2d');
            imagedata = cvs.toDataURL("image/jpeg");
            selectedImageData.push(imagedata);
        }
    }

    //let endTime = performance.now();
    //console.log("キャンバスの取得時間:" + (endTime - startTime));
    
    for(let i = 0; i < selectedImageData.length; i++) {

        if (i % 8 === 0 && i!== 0){
            slide = pptx.addSlide();
            y = Cm(0.5);
            y2 = Cm(4.25)
        }

        //startTime = performance.now();
        
        slide.addImage({ path: "images/black.png", w: width+Cm(0.12), h: height+Cm(0.12), x: x-Cm(0.06), y: y-Cm(0.06) });
        slide.addImage({ data: selectedImageData[i], w: width, h: height, x: x, y: y });
        slide.addText(String(i+1), {x: x-Cm(1.5), y: y, w: Pt(size*2), h: Pt(size), color: "363636", fontSize: size});

        // endTime = performance.now();
        // console.log("画像・枠線・番号の追加時間：" + (endTime - startTime));

        if (i % 4 == 3){
            x = Cm(2.5);
            y += Cm(10);
            x2 = Cm(7.2)
            y2 += Cm(10)
        } else {
            x += Cm(7);
            if (i != selectedImageData.length-1){
            slide.addImage({ path: "images/arrow.png", w: Cm(2), h: Cm(2), x: x2, y: y2 });
            x2 += Cm(7) 
            }
        }

        // endTime = performance.now();
        // console.log("矢印込みの追加時間：" + (endTime - startTime));
    }

    //画像を２枚ずつパワポに出力
    //height = Cm(16);
    width = Cm(7.39);
    //let pre_imagedata = null;
    height = width * videoRatio;
    size = 36;
    y = Cm(2.5);

    for(let i=0;i<selectedImageData.length;i++){
        //console.log("--------２列---------");


        if (i === 0) {
            continue
        }

        slide = pptx.addSlide();

        // startTime = performance.now();
        
        x = ( 11.7/2 - width ) / 2
        slide.addImage({ path: "images/black.png", w: width+Cm(0.12), h: height+Cm(0.12), x: x-Cm(0.06), y: y-Cm(0.06) });
        slide.addImage({ data: selectedImageData[i-1], w: width, h: height, x: x, y: y });
        slide.addText(String(i),  {x: x-Cm(2.5), y: y, w:Pt(size*2), h:Pt(size), color: "363636", fontSize: size});

        slide.addImage({ path: "images/arrow.png", w: Cm(3.33), h: Cm(3.33), x: Cm(13.18), y: Cm(8.84) });
        
        x += (11.7/2)
        slide.addImage({ path: "images/black.png", w: width+Cm(0.12), h: height+Cm(0.12), x: x-Cm(0.06), y: y-Cm(0.06) });
        slide.addImage({ data: selectedImageData[i], w: width, h: height, x: x, y: y });
        slide.addText(String(i+1),{x: x-Cm(2.5), y: y, w:Pt(size*2), h:Pt(size), color: "363636", fontSize: size});

        // endTime = performance.now();
        // console.log("画像２枚・枠線・番号・矢印の追加時間：" + (endTime - startTime));
        
    }

    // パワポを保存
    pptx.writeFile({ fileName: "らくらくトリセツ.pptx" });
    // const allEnd = performance.now();
    // console.log("全実行時間：" + (allEnd - allStart));
}

// PDFを作る関数
function makePDF() {
    const allStart = performance.now();

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({orientation: "landscape"}); // 向きを指定する

    // 初期位置
    let x = 25;     // スマホ画像用
    let y = 5;
    let x2 = 72;    // 矢印画像用
    let y2 = 42.5;
    let width = 43.9;
    // let height = 95;
    let height = width * videoRatio;
    let selectedImageData = [];

    // フォントサイズの指定
    doc.setFontSize(27);

    // let startTime = performance.now();
    // canvasに書かれたデータを読み取るコード
    for(let i=0; i<stateOfFrame.length; i++) {
        if(stateOfFrame[i]) {
            cvs = document.getElementById(`canvas${i}`);
            ctx = cvs.getContext('2d');
            imagedata = cvs.toDataURL("image/jpeg");
            selectedImageData.push(imagedata);
        }
    }
    // let endTime = performance.now();
    // console.log("キャンバスの取得時間:" + (endTime - startTime));

    for(let i=0; i<selectedImageData.length; i++) {
        // console.log("--------４列---------");
        
        if (i % 8 === 0 && i !== 0){
            // ページを増やす
            doc.addPage({orientation: "landscape"});
            y = 5;
            y2 = 42.5;
        }

        // startTime = performance.now();

        doc.addImage('images/black.png', 'PNG', x-0.6, y-0.6, width+1.2, height+1.2);  // 画像の枠線用の黒画像を先に貼る
        doc.addImage(selectedImageData[i], 'JPEG', x, y, width, height);
        doc.text(String(i+1), x-13, y+10);  // 画像番号

        // endTime = performance.now();
        // console.log("画像・枠線・番号の追加時間：" + (endTime - startTime));

        if (i % 4 === 3){
            x = 25;
            y += 100;
            x2 = 72;
            y2 += 100;
        } else {
            x += 70;
            if(i != selectedImageData.length-1){
                doc.addImage('images/arrow.png', 'PNG', x2, y2, 20, 20);
                x2 += 70 
            }
        }

        // endTime = performance.now();
        // console.log("矢印込みの追加時間：" + (endTime - startTime));

    }

    // 画像を２枚ずつ連番で出力
    // height = 160;
    width = 73.9;
    height = width * videoRatio;
    y = 25;

    // フォントサイズの指定
    doc.setFontSize(35);  

    for(let i =0; i<selectedImageData.length; i++) {
        // console.log("--------２列---------");

        if (i === 0) {
            continue
        }

        //ページを増やす
        doc.addPage({orientation: "landscape"});

        // startTime = performance.now();

        // 左の画像
        x = ( 297/2 - width ) / 2;
        doc.addImage('images/black.png', 'PNG', x-0.8, y-0.8, width+1.6, height+1.6);  // 画像の枠線用の黒画像を先に貼る
        doc.addImage(selectedImageData[i-1], 'JPEG', x, y, width, height);
        doc.text(String(i), x-15, y+10);

        doc.addImage('images/arrow.png', 131.8, 88.4, 33.3, 33.3);

        // 右の画像
        x += 297/2
        doc.addImage('images/black.png', 'PNG', x-0.8, y-0.8, width+1.6, height+1.6);  // 画像の枠線用の黒画像を先に貼る
        doc.addImage(selectedImageData[i], 'JPEG', x, y, width, height);
        doc.text(String(i+1), x-15, y+10);

        // endTime = performance.now();
        // console.log("画像２枚・枠線・番号・矢印の追加時間：" + (endTime - startTime));
    }
        
    // addImage(imageData, format, x, y, width, height, alias, compression, rotation)
    // https://artskydj.github.io/jsPDF/docs/module-addImage.html
    // doc.addImage(imagedata, 'JPEG', 30, 30, 80, 160);

    doc.save("らくらくトリセツ.pdf");

    const allEnd = performance.now();
    console.log("全実行時間：" + (allEnd - allStart));
}