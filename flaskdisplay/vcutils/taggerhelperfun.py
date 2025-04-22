#version: 1.0.0

class Tagger:
    def parse_mp4(mp4):
        mp4_sp=mp4.split('/')
        DATE=mp4_sp[-2]
        TIME=mp4_sp[-1].split('-')[1].split('.')[0].replace('_','-')
        g=G()
        g.DATE=DATE
        g.TIME=TIME
        g.TIME2=TIME.replace('-','_')
        g.DATETIME=f'{DATE}_{TIME}'
        g.CRANE=mp4_sp[-5]
        g.CAM=mp4_sp[-1].split('-')[0]
        return g
    def get_mp4(captureshome,CRANE,DATETIME,CAM):
        DATE,TIME=DATETIME.split('_')
        TIME2=TIME.replace('-','_')
        return f'{captureshome}/{CRANE}/captures/vids/{DATE}/{CAM}-{TIME2}.mp4'
    def myvstack(list_im):
        Htotal=0
        Wmax=0
        for im in list_im:
            H,W=im.shape[:2]
            Htotal+=H
            Wmax=max(W,Wmax)
        collage=np.zeros((Htotal,Wmax,3),dtype=np.uint8)
        currH=0
        for im in list_im:
            H,W=im.shape[:2]
            collage[currH:currH+H,0:W]=im
            currH+=H   
        return collage 
    def myhstack(list_im):
        Wtotal=0
        Hmax=0
        for im in list_im:
            H,W=im.shape[:2]
            Wtotal+=W
            Hmax=max(H,Hmax)
        collage=np.zeros((Hmax,Wtotal,3),dtype=np.uint8)
        currW=0
        for im in list_im:
            H,W=im.shape[:2]
            collage[0:H,currW:currW+W]=im
            currW+=W    
        return collage
    def print_yolocolor(yolo):
        print(list(zip(yolo.classes,'roygbiv'*10)))

    def yolodraw(im,yolo):
        res=yolo.infer(im)
        for label,prob,box in zip(*res):
            cv2.rectangle(im,box,color=rainbowbgr[yolo.classes.index(label)%7],thickness=2)
            #putText(im,f'{prob:0.2f}',(box[0],box[1]),shadow=True)
            putText(im,f'{label}',(box[0],box[1]),shadow=True)
        return res
        
    def yolodrawres(im,res,classes):    
        for label,prob,box in zip(*res):
            cv2.rectangle(im,box,color=rainbowbgr[classes.index(label)%7],thickness=2)
            #putText(im,f'{prob:0.2f}',(box[0],box[1]),shadow=True)
            putText(im,f'{label}',(box[0],box[1]),shadow=True)
        return res

    def getfilesize(f):
        return os.stat(f).st_size    

    def tag_grep(srcfolder,label):
        cmd=f"grep '^{label},' {srcfolder}/imgs.label/*"
        print(os.popen(cmd).read())

    def tag_delete(srcfolder):
        for f in glob.glob(f'{srcfolder}/imgs/*.jpg'):
            os.unlink(f)
        for f in glob.glob(f'{srcfolder}/imgs.label/*.jpg.txt'):
            os.unlink(f)

    def tag_rename(srcfolder,destfolder,fromto):
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            if os.path.exists(flab):
                fjpgbase=f.split('/')[-1]
                fbase=fjpgbase.replace('.jpg','')
                im=cv2.imread(f)            
                fjpgout=f'{destfolder}/imgs/{fbase}.jpg'
                flabout=f'{destfolder}/imgs.label/{fbase}.jpg.txt'
                cv2.imwrite(makedirsf(fjpgout),im)
                with open(makedirsf(flabout),'w') as Flabout:
                    for line in open(flab):
                        if line=='':break
                        name,x1,x2,y1,y2=line.split(',')
                        if name in fromto:
                            name=fromto[name]
                        x1,x2,y1,y2=map(float,[x1,x2,y1,y2])
                        Flabout.write(f'{name},{x1},{x2},{y1},{y2}\n')               

    def tag_empty(srcfolder):
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            open(makedirsf(flab),'w')                    

    def tag_countlabels(srcfolder):
        from collections import defaultdict
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        labcount=defaultdict(int)
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            if not os.path.exists(flab):
                labcount['skipped']+=1
                continue
            labcount['labeled']+=1
            for line in open(flab):
                if line=='':break
                name,_,_,_,_=line.split(',')
                labcount[name]+=1
        return labcount
    def tag_filter(srcfolder,destfolder,wanted,exclude=[]):
        """
        after exclude, all label left must be in wanted, otherwise discard
        """
        D2=destfolder
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            if not os.path.exists(flab):
                continue
            fjpgbase=f.split('/')[-1]
            fbase=fjpgbase.replace('.jpg','')            
            all_label_in_wanted=1
            outline=[]
            for line in open(flab):
                if line=='':break
                name,other=line.split(',',1)
                if name in exclude:continue
                if name not in wanted:
                    all_label_in_wanted=0
                    break
                outline.append(f'{name},{other}')
            if not all_label_in_wanted:continue
            fjpgout=makedirsf(f'{D2}/imgs/{fbase}.jpg')
            flabout=makedirsf(f'{D2}/imgs.label/{fbase}.jpg.txt')
            if fjpgout!=f:
                shutil.copy(f,fjpgout)
            open(flabout,'w').write(''.join(outline))
    def tag_reflect(srcfolder,destfolder,reflect='I,H,V,HV'):
        reflect=reflect.split(',')
        D2=destfolder
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            if os.path.exists(flab):
                fjpgbase=f.split('/')[-1]
                fbase=fjpgbase.replace('.jpg','')
                im=cv2.imread(f)
                if 'I' in reflect:
                    fjpgout=makedirsf(f'{D2}/imgs/{fbase}__I.jpg')
                    flabout=makedirsf(f'{D2}/imgs.label/{fbase}__I.jpg.txt')
                    cv2.imwrite(fjpgout,im)
                    with open(flabout,'w') as Flabout:
                        for line in open(flab):
                            if line=='':break
                            name,x1,x2,y1,y2=line.split(',')
                            x1,x2,y1,y2=map(float,[x1,x2,y1,y2])
                            Flabout.write(f'{name},{x1},{x2},{y1},{y2}\n')
                if 'HV' in reflect:
                    fjpgout=makedirsf(f'{D2}/imgs/{fbase}__HV.jpg')
                    flabout=makedirsf(f'{D2}/imgs.label/{fbase}__HV.jpg.txt')
                    cv2.imwrite(fjpgout,im[::-1,::-1])
                    with open(flabout,'w') as Flabout:
                        for line in open(flab):
                            if line=='':break
                            name,x1,x2,y1,y2=line.split(',')
                            x1,x2,y1,y2=map(float,[x1,x2,y1,y2])
                            Flabout.write(f'{name},{1-x2},{1-x1},{1-y2},{1-y1}\n')
                if 'H' in reflect:
                    fjpgout=makedirsf(f'{D2}/imgs/{fbase}__H.jpg')
                    flabout=makedirsf(f'{D2}/imgs.label/{fbase}__H.jpg.txt')
                    cv2.imwrite(fjpgout,im[:,::-1])
                    with open(flabout,'w') as Flabout:
                        for line in open(flab):
                            if line=='':break
                            name,x1,x2,y1,y2=line.split(',')
                            x1,x2,y1,y2=map(float,[x1,x2,y1,y2])
                            Flabout.write(f'{name},{1-x2},{1-x1},{y1},{y2}\n')

                if 'V' in reflect:
                    fjpgout=makedirsf(f'{D2}/imgs/{fbase}__V.jpg')
                    flabout=makedirsf(f'{D2}/imgs.label/{fbase}__V.jpg.txt')
                    cv2.imwrite(fjpgout,im[::-1])
                    with open(flabout,'w') as Flabout:
                        for line in open(flab):
                            if line=='':break
                            name,x1,x2,y1,y2=line.split(',')
                            x1,x2,y1,y2=map(float,[x1,x2,y1,y2])
                            Flabout.write(f'{name},{x1},{x2},{1-y2},{1-y1}\n')
    def tag_move(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            fjpgbase=f.split('/')[-1]
            fbase=fjpgbase.replace('.jpg','')
            if os.path.exists(flab) and open(flab).read()!='':
                fjpgout=makedirsf(f'{D2}/imgs/{fbase}.jpg')
                flabout=makedirsf(f'{D2}/imgs.label/{fbase}.jpg.txt')
                shutil.move(f,fjpgout)
                shutil.move(flab,flabout)
                n-=1
                if n==0:
                    break
    def tag_move_empty(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        print(len(list_f))
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            fjpgbase=f.split('/')[-1]
            fbase=fjpgbase.replace('.jpg','')
            if os.path.exists(flab) and open(flab).read()=='':
                fjpgout=makedirsf(f'{D2}/imgs/{fbase}.jpg')
                flabout=makedirsf(f'{D2}/imgs.label/{fbase}.jpg.txt')            
                shutil.move(f,fjpgout)
                shutil.move(flab,flabout)
                n-=1
                if n==0:
                    break                
    def tag_copynonempty(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=f[:-4]+'.jpg.txt'
            #flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            fjpgbase=f.split('/')[-1]
            fbase=fjpgbase[:-4]
            if os.path.exists(flab) and open(flab).read()!='':
                fjpgout=makedirsf(f'{D2}/imgs/{fbase}.jpg')
                flabout=makedirsf(f'{D2}/imgs.label/{fbase}.jpg.txt')
                shutil.copy(f,fjpgout)
                shutil.copy(flab,flabout)
                n-=1
                if n==0:
                    break

    def tag_copyuntagged(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=f[:-4]+'.jpg.txt'
            #flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            flab=f.replace('.jpg','.jpg.txt').replace('imgs','imgs.label')
            fjpgbase=f.split('/')[-1]
            fbase=fjpgbase[:-4]
            if not os.path.exists(flab):
                fjpgout=makedirsf(f'{D2}/imgs/{fbase}.jpg')
                flabout=makedirsf(f'{D2}/imgs.label/{fbase}.jpg.txt')
                shutil.copy(f,fjpgout)
                #shutil.copy(flab,flabout)
                n-=1
                if n==0:
                    break                

    def darknetdir_to_tagtraindir(darknetdir,tagtraindir):
        l__imf=glob.glob(f'{darknetdir}/imgs/*.jpg')
        
        namesfile=glob.glob(f'{darknetdir}/*.names')[0]
        
        classes=open(namesfile).read().split()

        def tagtrain_to_darknet(labelfname,outlabelfname,classes):
            with open(outlabelfname,'w') as outf:
                for line in open(labelfname):
                    if line.strip()=='':continue
                    tagname,xmin,xmax,ymin,ymax = line.strip().split(',')
                    try:
                        tagname=classes.index(tagname)
                    except:
                        continue
                    xmin=max(float(xmin),0)
                    xmax=max(float(xmax),0)
                    ymin=max(float(ymin),0)
                    ymax=max(float(ymax),0)
                    outf.write(f'{tagname} {(xmin+xmax)/2} {(ymin+ymax)/2} {xmax-xmin} {ymax-ymin}\n')    
        def darknet_to_tagtrain(inlabelfname, outlabelfname, classes):
            with open(makedirsf(outlabelfname), 'w') as outf:
                for line in open(inlabelfname):
                    if line.strip() == '':
                        continue
                    items = line.strip().split()
                    if len(items) != 5:
                        continue
                    tag_index, x_center, y_center, width, height = items
                    try:
                        tag_index = int(tag_index)
                        tagname = classes[tag_index]
                    except (ValueError, IndexError):
                        continue
                    x_center = float(x_center)
                    y_center = float(y_center)
                    width = float(width)
                    height = float(height)
                    xmin = x_center - width / 2
                    xmax = x_center + width / 2
                    ymin = y_center - height / 2
                    ymax = y_center + height / 2
                    outf.write(f'{tagname},{xmin},{xmax},{ymin},{ymax}\n')
        #tagtraindir='/home/mvizn/raid/rtg-train-uploads/ad4fc994-6833-4bbe-be6e-c2f565ce1624/4d18851e-7f4c-468c-8000-fe639808ec20-d1e10a30-ba57-4395-9f03-e1c71460ac91'
        for imf in l__imf:
            darknetlabelf=imf[:-4]+'.txt'
            tagtrainlabelf=f"{tagtraindir}/imgs.label/{os.path.basename(imf[:-4]+'.jpg.txt')}"
            darknet_to_tagtrain(darknetlabelf,tagtrainlabelf,classes)
            shutil.copy(imf,makedirsf(f'{tagtraindir}/imgs/{os.path.basename(imf)}'))   
