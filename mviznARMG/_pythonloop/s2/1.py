#1.py

#quit()

try: 
    init
except:
    init=1

runcells=[]
phase=None
donotrun=0
if not donotrun:
    if init:
        print('init')
        phase='init'    
        runcells.extend([0]) 
    elif 0: #test
        phase='test'
    elif 1: #tinker
        phase='tinker'
        runcells.extend(['tinker'])

for cell in runcells:
    print(datetime.now(),'>>>>running',cell)
    if cell==0:
        runIfChanged2=RunIfChanged('_pythonloop/s2/2.py')
    elif cell==1:        
        hncdsyolo=YOLO('HNCDS/weights/HNCDS.weights')
    elif cell==2:
        _run('vcutils/taggerhelperfun.py')
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
        #_pythonloop/s2/2.py
        runIfChanged2.runifchanged(globals())

    print(datetime.now(),'>>>>ran',cell)

print(datetime.now(),'phase',phase)
init=0
