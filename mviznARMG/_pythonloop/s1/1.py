#1.py

#quit()

try: 
    init 
except:
    init=1

runcells=[]
phase=None
donotrun=1
if not donotrun:
    if init:
        phase='init'    
        runcells.extend([0]) 
        runcells.extend([1])
    elif 0: #test
        phase='test'
        runcells.extend([2])
        runcells.extend([3])
    elif 1: #tinker
        phase='tinker'
        runcells.extend(['tinker'])

for cell in runcells:
    print('>>>>running',cell)
    if cell==0:
        from vcutils.C__flaskdisplay import *
        fd=C__flaskdisplay('001')
        from paddleocr import PaddleOCR, draw_ocr
        from PIL import Image

        # Initialize PaddleOCR model
        ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use English model
        pass
    elif cell==1: 
        hncdsyolo=YOLO('HNCDS/weights/HNCDS.weights')
    elif cell==2:
        ipyrun('vcutils/taggerhelperfun.py',globals())
        im=cv2.imread('PMNRS/sample/1.jpg')
        imcp=im.copy()
        res=(hncdsyolo.infer(im))
        print(res)
        for label,prob,rect in zip(*res):
            x1,y1,w,h=rect
            x2,y2=x1+w,y1+h
            pass
        imcrop=im[y1:y2,x1:x2]
        Tagger.yolodrawres(imcp,res,hncdsyolo.classes)
        #fd.imswk(imcp,1);
        fd.imswk(imcrop,1)        
    elif cell==3:
        # Run OCR on an image
        img_rgb = cv2.cvtColor(imcrop, cv2.COLOR_BGR2RGB)

        # Run OCR
        results = ocr.ocr(img_rgb, cls=True)

        print(results)        
        print("HERE")
        # Display recognized text
        for line in results[0]:
            box, (text, confidence) = line
            print(f"Detected Text: {text}, Confidence: {confidence:.2f}")

        # Optional: visualize
        #image = Image.open(img_path).convert('RGB')
        boxes = [line[0] for line in results[0]]
        txts = [line[1][0] for line in results[0]]
        scores = [line[1][1] for line in results[0]]
        im_show = draw_ocr(img_rgb, boxes, txts, scores, font_path='fonts/simfang.ttf')
        im_show = Image.fromarray(im_show)
        im_show.save('result.jpg')
        imout=cv2.imread('result.jpg')
        fd.imswk(imout,1)
    elif cell=='tinker':
        os.system('ls CLPS/sample/2020-01-09/15-00-29/')
        l__f=sorted(glob.glob('CLPS/sample/2020-01-09/15-00-29/*.jpg'))
        res=procimage('clpsmaskrcnn',cv2.imread(l__f[0]))
        print(res)
    print('>>>>ran',cell)

print('phase',phase)

init=0