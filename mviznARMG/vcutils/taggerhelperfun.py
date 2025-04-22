#version: 1.0.2
#1.0.1
# added tag1_rmlabels
# added tag1_replacelabels
# use staticmethod decorator
# added diff_tag
# use replace_suffix instead of replace
#1.0.2
# fileorderbymodearg
# made self sufficient, reduce dependency on taggerhelper
#1.0.3
# optimal pairing assignment and auxiliary helpers

##tag format 1: parse_tag_file format proposed by "chatgpt" for difftag
# {'p': [(2034, 1973, 2152, 2209)], 't': [(1004, 2937, 1430, 3399)]}
##tag format 2: [('p', 0.94054747, array([2034, 1973,  119,  236], dtype=int32)),
#            ('t', 0.9847761, array([1004, 2937,  427,  462], dtype=int32))]
##tag format 3: tagger app string format
#   p,0.8106815464328417,0.8577122359505779,0.5802941176470588,0.6497058823529411\n
#   t,0.40015942606616184,0.5699481865284974,0.8638235294117647,0.9997058823529412\n

from io import StringIO
from PIL import Image, ImageDraw
import os
import hashlib
import math
from typing import Union, List, Dict, Tuple

try:
    from .helperfun import *
    #print('from .helperfun import *')
except:
    try:
        from vcutils.helperfun import *        
        #print('from vcutils.helperfun import *')
    except:
        pass
from io import StringIO
import traceback
def geterrorstring(e):
    sio=StringIO()
    print("An exception occurred:", e,file=sio)
    print("\nStack trace:",file=sio)
    print(traceback.format_exc(),file=sio)
    return sio.getvalue()
0
class Tagger:
    @staticmethod
    def build_autotag_index(list_images, autotag_folder, d__imhw):
        """
        Build a lookup of golden (autotag) boxes per image and label.
        Returns: { fbase: { label: [box1, box2, ...], ... }, ... }
        """
        autotag_index = defaultdict(lambda: defaultdict(list))
        for f in list_images:
            fbase = os.path.basename(f)
            if f not in d__imhw:
                d__imhw[f] = Tagger.getimhw(f)
            h, w = d__imhw[f]
            tag_file = os.path.join(autotag_folder, fbase + '.txt')
            tags = Tagger._parse_tag_file(tag_file, width=w, height=h)
            if not tags:
                continue
            for label, boxes in tags.items():
                autotag_index[fbase][label].extend(boxes)
        return autotag_index

    @staticmethod
    def is_autotag(fbase, label, box, autotag_index, iou_threshold=0.99):
        """
        Check if a given box matches any autotag box (within IoU threshold).
        """
        auto_boxes = autotag_index.get(fbase, {}).get(label, [])
        if not auto_boxes:
            return False
        ious = Tagger._batch_iou([box], auto_boxes)[0]
        return np.any(ious >= iou_threshold)
    
    def merge_tag_dicts_by_iou(dict1, dict2, iou_threshold=0.5):
        def calc_iou(boxA, boxB):
            xA = max(boxA[0], boxB[0])
            yA = max(boxA[1], boxB[1])
            xB = min(boxA[2], boxB[2])
            yB = min(boxA[3], boxB[3])

            interArea = max(0, xB - xA) * max(0, yB - yA)
            if interArea == 0:
                return 0.0

            boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
            boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
            return interArea / float(boxAArea + boxBArea - interArea)

        def merge_boxes(box1, box2):
            # Simple merge strategy: average the coordinates
            return tuple(int((a + b) / 2) for a, b in zip(box1, box2))        
        merged = {}

        all_keys = set(dict1.keys()) | set(dict2.keys())

        for key in all_keys:
            boxes1 = dict1.get(key, [])
            boxes2 = dict2.get(key, [])
            used2 = [False] * len(boxes2)
            result = []

            for b1 in boxes1:
                matched = False
                for i, b2 in enumerate(boxes2):
                    if not used2[i] and calc_iou(b1, b2) > iou_threshold:
                        result.append(merge_boxes(b1, b2))
                        used2[i] = True
                        matched = True
                        break
                if not matched:
                    result.append(b1)

            # Add unmatched boxes from dict2
            for i, b2 in enumerate(boxes2):
                if not used2[i]:
                    result.append(b2)

            merged[key] = result

        return merged
    
    
    @staticmethod
    def convert_tag_format(
        data: Union[Dict[str, List[Tuple[int, int, int, int]]], List[Tuple[str, float, np.ndarray]], str],
        from_format: int,
        to_format: int,
        image_width: int = None,
        image_height: int = None
    ) -> Union[Dict[str, List[Tuple[int, int, int, int]]], List[Tuple[str, float, np.ndarray]], str]:
        
        """
        # Format 1 data
        format1_data = {
            'p': [(2034, 1973, 2152, 2209)],
            't': [(1004, 2937, 1430, 3399)]
        }

        # Convert Format 1 -> Format 2
        format2 = convert_tag_format(format1_data, from_format=1, to_format=2)

        # Convert Format 2 -> Format 3 (need width and height)
        format3 = convert_tag_format(format2, from_format=2, to_format=3, image_width=2550, image_height=3400)

        # Convert back from Format 3 -> Format 1
        format1_again = convert_tag_format(format3, from_format=3, to_format=1, image_width=2550, image_height=3400)
        """        
        if from_format == 3:
            # Parse format 3 string into format 2
            lines = data.strip().splitlines()
            format2 = []
            for line in lines:
                parts = line.strip().split(',')
                label = parts[0]
                x1, x2 = float(parts[1]), float(parts[2])
                y1, y2 = float(parts[3]), float(parts[4])
                if image_width is None or image_height is None:
                    raise ValueError("image_width and image_height are required for format 3 conversion")
                abs_x1 = int(round(x1 * image_width))
                abs_x2 = int(round(x2 * image_width))
                abs_y1 = int(round(y1 * image_height))
                abs_y2 = int(round(y2 * image_height))
                array = np.array([abs_x1, abs_y1, abs_x2 - abs_x1, abs_y2 - abs_y1], dtype=np.int32)
                confidence = 1.0  # Confidence not provided in format 3, assume 1.0
                format2.append((label, confidence, array))
            if to_format == 2:
                return format2
            data = format2
            from_format = 2  # continue conversion to format 1

        if from_format == 2:
            if to_format == 1:
                # Format 2 -> Format 1
                result = {}
                for label, _, arr in data:
                    x, y, w, h = arr
                    box = (x, y, x + w, y + h)
                    if label not in result:
                        result[label] = []
                    result[label].append(box)
                return result
            elif to_format == 3:
                # Format 2 -> Format 3
                if image_width is None or image_height is None:
                    raise ValueError("image_width and image_height are required for format 3 conversion")
                lines = []
                for label, confidence, arr in data:
                    x, y, w, h = arr
                    x1 = x / image_width
                    x2 = (x + w) / image_width
                    y1 = y / image_height
                    y2 = (y + h) / image_height
                    lines.append(f"{label},{x1},{x2},{y1},{y2}\n")
                return "".join(lines)

        if from_format == 1:
            if to_format == 2:
                format2 = []
                for label, boxes in data.items():
                    for box in boxes:
                        x1, y1, x2, y2 = box
                        arr = np.array([x1, y1, x2 - x1, y2 - y1], dtype=np.int32)
                        confidence = 1.0  # Not provided in format 1
                        format2.append((label, confidence, arr))
                return format2
            elif to_format == 3:
                data = Tagger.convert_tag_format(data, 1, 2)
                return Tagger.convert_tag_format(data, 2, 3, image_width, image_height)

        raise ValueError("Unsupported conversion path or missing image dimensions")
    
    #OPTIMAL PAIRING RELATED
    @staticmethod
    def get__d__fbase__index(l__f):
        d__fbase__index={}
        for i,f in enumerate(l__f):
            fbase=os.path.basename(f)
            d__fbase__index[fbase]=i
        return d__fbase__index

    @staticmethod
    def compute_pair_keyfun(num_images, N):
        """
        Compute a set2 ordering for num_images with N taggers when num_images is not
        necessarily an exact multiple of N.

        This function partitions the images into N nearly equal blocks for set1,
        computes a target tagger for each image using a cyclic shift, and then
        sorts images by a key derived from the target tagger and their original index.

        Note: For a guaranteed overlap every set1 block should have at least N-1 images.
        """
        if N < 2:
            raise ValueError("At least 2 taggers are required.")
        if num_images < N:
            raise ValueError("Number of images must be at least N.")

        from bisect import bisect
        # Compute boundaries for set1 blocks.
        boundaries = [int(j * num_images // N) for j in range(N)] + [num_images]

        # List to hold (key, image_index) pairs.
        key_image_pairs = []
        d__key={}
        for j in range(N):
            start = boundaries[j]
            end = boundaries[j+1]
            M_j = end - start
            for i in range(start, end):
                # r: index within the block.
                r = i - start
                # Compute target tagger b using a cyclic shift.
                # Note: This works best if M_j >= N-1.
                b = (j + (r % (N-1)) + 1) % N
                # Use a tuple key (b, i) to sort.
                #key = (b, i)
                #key = (b,myhash(str(i)),i) #randomise within block
                key = (b,i-boundaries[bisect(boundaries,i)-1],i) #try to pair with early images from each block in set1
                #key = (b,r,i) #try to pair with early images from each block in set1
                #key_image_pairs.append((key, i))
                d__key[i]=key
        keyfun=lambda i:d__key[i]
        return keyfun

    @staticmethod
    def gettaggername(i,num_images,taggernames):
        taggernames=sorted(x.upper() for x in taggernames)
        N=len(taggernames)
        from bisect import bisect
        boundaries = [int(j * num_images // N) for j in range(N)] + [num_images]
        taggeri=bisect(boundaries,i)
        return taggernames[taggeri-1]

    @staticmethod
    def printtaggerlink(num_images,taggernames,url):
        N=len(taggernames)
        boundaries = [int(j * num_images // N) for j in range(N)] + [num_images]
        taggernames=sorted(x.upper() for x in taggernames)
        for i,taggername in enumerate(taggernames):
            print(taggername,':',f'{url}/{boundaries[i]+1} to {boundaries[i+1]}')

    @staticmethod
    def computeorder(L):
        return [i for i, _ in sorted(enumerate(L), key=lambda x: x[1])]

    @staticmethod
    def get_sorted_ranks(lst):
        """
        Given a list of numbers, returns a new list of the same length where each element is
        the rank (i.e., the sorted order index) of the corresponding element in the original list.
        
        For example:
            Input: [43622436, 1523, 3646]
            Sorted order: [1523, 3646, 43622436]
            Output: [2, 0, 1]  # because 43622436 is 3rd (index 2), 1523 is 1st (index 0), 3646 is 2nd (index 1)
        """
        # First, compute the indices that would sort the list (argsort).
        sorted_indices = sorted(range(len(lst)), key=lambda i: lst[i])
        
        # Next, create a list to store the rank for each element.
        ranks = [0] * len(lst)
        for rank, index in enumerate(sorted_indices):
            ranks[index] = rank
        return ranks

    @staticmethod
    def fileorderbymodearg(l__f,mode=None,arg=None):
        """
        hashtagger1
        file already of the form 57acbad7bda7bdbed_ix__....
        H=57acbad7bda7bdbed
        naturalsort(myhash(H+'tagger1')+fbase)
        """        
        if mode is None:
            mode='natural'
        if arg is None:
            arg=''
        if mode=='natural':
            key=lambda fbase:''
        if mode=='hashchunk':
            l__f=natural_sort(l__f)
            d__fbase__key={}
            for i,sublf in enumerate(chunk_string(l__f,5)):
                for f in sublf:
                    fbase=os.path.basename(f)
                    d__fbase__key[fbase]=myhash(f'chunk{i}')
            key=lambda fbase:d__fbase__key[fbase]

        if mode=='hashchunkpair':

            l__f=natural_sort(l__f)
            d__fbase__key={}
            numchunks=len(chunk_string(l__f,5))
            d__fbase__chunki={}
            for i,sublf in enumerate(chunk_string(l__f,5)):
                for f in sublf:
                    fbase=os.path.basename(f)
                    d__fbase__chunki[fbase]=i

            ld__chunki__key=list(myhash(f'chunk{i}') for i in range(numchunks))
            ld__chunki__rchunki=Tagger.get_sorted_ranks(ld__chunki__key)
            #sort by key already then extract index
            N=int(arg)
            map__rchunki__key=Tagger.compute_pair_keyfun(numchunks,N)
            ld__rchunki__rrchunki=Tagger.get_sorted_ranks(list(map(map__rchunki__key,range(numchunks))))
            d__fbase__key={}
            for f in l__f:
                fbase=os.path.basename(f)
                chunki=d__fbase__chunki[fbase]
                rchunki=ld__chunki__rchunki[chunki]
                d__fbase__key[fbase]=map__rchunki__key(rchunki)
            key=lambda fbase:d__fbase__key[fbase]
        if mode=='hashH':
            def key(fbase):
                H=fbase.split('_')[0]
                return myhash(H)
        if mode=='hash':
            key=lambda fbase:myhash(fbase+str(arg))
        return list(v for k,v in sorted(((key(os.path.basename(f)),natural_sort_key(f)),f) for f in l__f))

    @staticmethod
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
        
    @staticmethod
    def get_mp4(captureshome,CRANE,DATETIME,CAM):
        DATE,TIME=DATETIME.split('_')
        TIME2=TIME.replace('-','_')
        return f'{captureshome}/{CRANE}/captures/vids/{DATE}/{CAM}-{TIME2}.mp4'
        
    @staticmethod
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
        
    @staticmethod
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
    @staticmethod
    def print_yolocolor(yolo):
        print(list(zip(yolo.classes,'roygbiv'*10)))

    @staticmethod
    def yolodraw(im,yolo):
        res=yolo.infer(im)
        for label,prob,box in zip(*res):
            cv2.rectangle(im,box,color=rainbowbgr[yolo.classes.index(label)%7],thickness=2)
            #putText(im,f'{prob:0.2f}',(box[0],box[1]),shadow=True)
            putText(im,f'{label}',(box[0],box[1]),shadow=True)
        return res
        
    @staticmethod
    def yolodrawres(im,res,classes):    
        for label,prob,box in zip(*res):
            cv2.rectangle(im,box,color=rainbowbgr[classes.index(label)%7],thickness=2)
            #putText(im,f'{prob:0.2f}',(box[0],box[1]),shadow=True)
            putText(im,f'{label}',(box[0],box[1]),shadow=True)
        return res

    @staticmethod
    def getfilesize(f):
        return os.stat(f).st_size    

    @staticmethod
    def tag_grep(srcfolder,label):
        cmd=f"grep '^{label},' {srcfolder}/imgs.label/*"
        print(os.popen(cmd).read())

    @staticmethod
    def tag_delete(srcfolder):
        for f in glob.glob(f'{srcfolder}/imgs/*.jpg'):
            os.unlink(f)
        for f in glob.glob(f'{srcfolder}/imgs.label/*.jpg.txt'):
            os.unlink(f)

    @staticmethod
    def tag_rename(srcfolder,destfolder,fromto):
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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

    @staticmethod
    def tag_empty(srcfolder):
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
            open(makedirsf(flab),'w')                    

    @staticmethod
    def tag_countlabels(srcfolder):
        from collections import defaultdict
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        labcount=defaultdict(int)
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
            if not os.path.exists(flab):
                labcount['skipped']+=1
                continue
            labcount['labeled']+=1
            for line in open(flab):
                if line=='':break
                name,_,_,_,_=line.split(',')
                labcount[name]+=1
        return labcount
        
    @staticmethod
    def tag1_rmlabels(f,labels):
        """
        f is imagefile in tagging make sure .jpg only appear once
        labels will be removed
        """
        sio=StringIO()
        from collections import defaultdict
        flab=f.replace('.jpg','.jpg.txt').replace('/imgs/','/imgs.label/')
        if not os.path.exists(flab):
            return
        for line in open(flab):
            if line=='':break
            name,_,_,_,_=line.split(',')
            if name not in labels:
                print(line.strip(),file=sio)
        print(sio.getvalue())
        #open(flab,'w').write(sio.getvalue())
    
    @staticmethod
    def tag1_replacelabels(f,yolores,labels,imhw=None):
        """
        f is imagefile in tagging make sure .jpg only appear once
        yolores is output of yolo.infer
        labels will be removed and replaced by yolores
        imhw if provided skips reading f to get imh and imw
        """
        sio=StringIO()
        from collections import defaultdict
        flab=f.replace('.jpg','.jpg.txt').replace('/imgs/','/imgs.label/')
        if not os.path.exists(flab):
            return
        if imhw is None:
            try:
                with Image.open(f) as img:
                    width, height = img.size
                    imhw=height,width
            except FileNotFoundError:
                print(f"Error: Image file not found: {image_path}")
                return 0
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                return 0
        imh,imw=imhw
        zipres=list(zip(*yolores))
        #first remove all labels
        for line in open(flab):
            if line=='':break
            name,_,_,_,_=line.split(',')
            if name not in labels:
                print(line.strip(),file=sio)
        #then add all labels from yolores
        for name,_,rect in zipres:
            if name in labels:
                x1,y1,w,h=rect
                x2=x1+w
                y2=y1+h
                _x1=x1/imw
                _x2=x2/imw
                _y1=y1/imh
                _y2=y2/imh
                print(f'{name},{_x1},{_x2},{_y1},{_y2}',file=sio)
        #print(sio.getvalue())
        open(flab,'w').write(sio.getvalue())
        return 1
        
    @staticmethod
    def tag_filter(srcfolder,destfolder,wanted,exclude=[]):
        """
        after exclude, all label left must be in wanted, otherwise discard
        """
        D2=destfolder
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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

    @staticmethod    
    def tag_reflect(srcfolder,destfolder,reflect='I,H,V,HV'):
        reflect=reflect.split(',')
        D2=destfolder
        list_f=sorted(glob.glob(f'{srcfolder}/imgs/*.jpg'))
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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
                            
    @staticmethod
    def tag_move(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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
                    
    @staticmethod
    def tag_move_empty(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        print(len(list_f))
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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

    @staticmethod
    def tag_copynonempty(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=f[:-4]+'.jpg.txt'
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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

    @staticmethod
    def tag_copyuntagged(srcfolder,destfolder,n):
        import random
        list_f=glob.glob(f'{srcfolder}/imgs/*.jpg')
        random.shuffle(list_f)
        D2=destfolder
        for f in list_f:
            flab=f[:-4]+'.jpg.txt'
            flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
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

    @staticmethod
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

    @staticmethod
    def tag_movef(f,destfolder):
        destfolder_im=destfolder+'/imgs/'
        destfolder_lab=destfolder+'/imgs.label/'
        flab=replace_suffix(f, '.jpg', '.jpg.txt').replace('/imgs/','/imgs.label/')
        try:
            shutil.move(f,makedirsf(f'{destfolder_im}/'))
        except:
            pass
        try:
            shutil.move(flab,makedirsf(f'{destfolder_lab}/'))
        except:
            pass
        return 1

    @staticmethod
    def getyoloweights(groupname):       
        return f'/home/mvizn/Code/mViznRTGTrain/Config/{groupname}/{groupname}.weights'
    
    @staticmethod
    def tag_genautotagfolder(tagtraindir,yolo,overwrite=None,suffix=None):
        """
        if overwrite is 0 do nothing when file exists
        """
        if overwrite is None:
            overwrite=0
        l__imgfile=sorted(glob.glob(f'{tagtraindir}/imgs/*.jpg'))
        N=len(l__imgfile)
        progress=Progress(1,1.1)
        T=time.time()
        for i,imgfile in enumerate(l__imgfile):            
            progress.print('elapse:',int(time.time()-T),i,'/',N)
            autotagfile=Tagger.getautotagfile(imgfile,suffix)
            if not overwrite and os.path.exists(autotagfile):
                continue
            autotagstring=Tagger.getautotagstring(imgfile,yolo)
            open(makedirsf(autotagfile),'w').write(autotagstring)
        
    @staticmethod
    def getautotagfile(imgfile,suffix=None):
        if suffix is None:
            suffix='autotag'
        return replace_suffix(imgfile,'.jpg','.jpg.txt').replace('/imgs/',f'/imgs.{suffix}/')
    
    @staticmethod
    def getlabelfile(imgfile):
        return replace_suffix(imgfile,'.jpg','.jpg.txt').replace('/imgs/','/imgs.label/')

    @staticmethod
    def convertF2toF3(zipyolores,imw,imh):
        from io import StringIO
        f=StringIO()
        for name,prob,rect in zipyolores:
            x1,y1,w,h=rect[0]
            x2=x1+w
            y2=y1+h
            f.write(f'{name},{x1/width},{x2/width},{y1/height},{y2/height}\n')
        return f.getvalue()

    @staticmethod
    def convertF2toF1(zipyolores):
        from io import StringIO
        f=StringIO()
        for name,prob,rect in zipyolores:
            x1,y1,w,h=rect[0]
            x2=x1+w
            y2=y1+h
            f.write(f'{name},{x1/width},{x2/width},{y1/height},{y2/height}\n')
        return f.getvalue()    
    
    @staticmethod
    def getautotagstring(imgfile,yolo):
        """
            imgfile can also be cv2 image
            convert to format 3
        """
        if type(imgfile) is str:            
            frame = cv2.imread(imgfile)
        else:
            frame=imgfile
        height=frame.shape[0]
        width=frame.shape[1]
        #sem.acquire()
        #sem.release()
        #labelfile = Tagger.getautotagfile(imgfile)
        from io import StringIO
        f=StringIO()
        results=yolo.inferold(frame)
        for result in results:
            name = result[0]
            if type(name) == bytes:
                name = name.decode('utf8')
            prob = result[1]
            xc = int(result[2][0])
            yc = int(result[2][1])
            boxh = int(result[2][3] / 2)
            boxw = int(result[2][2] / 2)
            x1 = max(0,xc - boxw)
            y1 = max(0,yc - boxh)
            x2 = min(width,xc + boxw)
            y2 = min(height,yc + boxh)
            f.write(f'{name},{x1/width},{x2/width},{y1/height},{y2/height}\n')
        return f.getvalue()

    """
    diff_tags and helper functions
    """

    @staticmethod
    def _calculate_average_box(box_a, box_b):
        is_a_valid = any(c != 0 for c in box_a)
        is_b_valid = any(c != 0 for c in box_b)

        if is_a_valid and is_b_valid:
            return tuple(int(round((a + b) / 2.0)) for a, b in zip(box_a, box_b))
        elif is_a_valid:
            return box_a
        elif is_b_valid:
            return box_b
        else:
            return (0, 0, 0, 0)


    @staticmethod
    def _parse_tag_string(s, width=None, height=None, imf=None):
        if imf is not None:
            width,height=Tagger.getimhw(imf)            

        tags = {}

        if width is None or height is None or width <= 0 or height <= 0:
            return None

        try:
            for i, line in enumerate(s.strip().split('\n')):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) != 5:
                    continue

                label = parts[0].strip()
                try:
                    nx1, nx2 = float(parts[1]), float(parts[2])
                    ny1, ny2 = float(parts[3]), float(parts[4])

                    x1 = int(round(min(nx1, nx2) * width))
                    x2 = int(round(max(nx1, nx2) * width))
                    y1 = int(round(min(ny1, ny2) * height))
                    y2 = int(round(max(ny1, ny2) * height))

                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(width, x2)
                    y2 = min(height, y2)

                    box = (x1, y1, x2, y2)
                    tags.setdefault(label, []).append(box)

                except ValueError:
                    continue
        except IOError:
            return {}

        return tags
    
    @staticmethod
    def _parse_tag_file(filepath, width=None, height=None, imf=None):
        if imf is not None:
            width,height=Tagger.getimhw(imf)            

        tags = {}

        if not os.path.exists(filepath):
            return None

        if width is None or height is None or width <= 0 or height <= 0:
            return None

        try:
            with open(filepath, 'r') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(',')
                    if len(parts) != 5:
                        continue

                    label = parts[0].strip()
                    try:
                        nx1, nx2 = float(parts[1]), float(parts[2])
                        ny1, ny2 = float(parts[3]), float(parts[4])

                        x1 = int(round(min(nx1, nx2) * width))
                        x2 = int(round(max(nx1, nx2) * width))
                        y1 = int(round(min(ny1, ny2) * height))
                        y2 = int(round(max(ny1, ny2) * height))

                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(width, x2)
                        y2 = min(height, y2)

                        box = (x1, y1, x2, y2)
                        tags.setdefault(label, []).append(box)

                    except ValueError:
                        continue
        except IOError:
            return {}

        return tags

    @staticmethod
    def _batch_iou(boxes_a, boxes_b):
        """
        Vectorized IoU computation for all box pairs.
        Returns:
            iou_matrix: 2D numpy array of shape (len(boxes_a), len(boxes_b))
        """
        if not boxes_a or not boxes_b:
            return np.zeros((len(boxes_a), len(boxes_b)), dtype=np.float32)

        a = np.array(boxes_a, dtype=np.float32)  # (N, 4)
        b = np.array(boxes_b, dtype=np.float32)  # (M, 4)

        ax1, ay1, ax2, ay2 = a[:, 0][:, None], a[:, 1][:, None], a[:, 2][:, None], a[:, 3][:, None]
        bx1, by1, bx2, by2 = b[:, 0][None, :], b[:, 1][None, :], b[:, 2][None, :], b[:, 3][None, :]

        # Intersection coords
        inter_x1 = np.maximum(ax1, bx1)
        inter_y1 = np.maximum(ay1, by1)
        inter_x2 = np.minimum(ax2, bx2)
        inter_y2 = np.minimum(ay2, by2)

        inter_area = np.maximum(0, inter_x2 - inter_x1) * np.maximum(0, inter_y2 - inter_y1)

        area_a = (ax2 - ax1) * (ay2 - ay1)  # Shape (N, 1)
        area_b = (bx2 - bx1) * (by2 - by1)  # Shape (1, M)

        union_area = area_a + area_b - inter_area

        # Avoid division by zero
        iou = np.where(union_area > 0, inter_area / union_area, 0)

        return iou

    @staticmethod
    def _diff_tags(tags_a,tags_b):
        diffs = []
        zero_box = (0, 0, 0, 0)
        if tags_a is None or tags_b is None:
            return None
        all_labels = set(tags_a.keys()) | set(tags_b.keys())

        for label in all_labels:
            boxes_a = tags_a.get(label, [])
            boxes_b = tags_b.get(label, [])

            matched_a = set()
            matched_b = set()

            if boxes_a and boxes_b:
                iou_matrix = Tagger._batch_iou(boxes_a, boxes_b)
                match_candidates = [
                    (i, j, iou_matrix[i, j])
                    for i in range(iou_matrix.shape[0])
                    for j in range(iou_matrix.shape[1])
                    if iou_matrix[i, j] > 0
                ]
                match_candidates.sort(key=lambda x: x[2], reverse=True)

                for idx_a, idx_b, iou in match_candidates:
                    if idx_a not in matched_a and idx_b not in matched_b:
                        matched_a.add(idx_a)
                        matched_b.add(idx_b)
                        box_a = boxes_a[idx_a]
                        box_b = boxes_b[idx_b]
                        avg_box = Tagger._calculate_average_box(box_a, box_b)
                        diffs.append((label, box_a, box_b, avg_box, float(iou)))

            for idx_a, box_a in enumerate(boxes_a):
                if idx_a not in matched_a:
                    avg_box = Tagger._calculate_average_box(box_a, zero_box)
                    diffs.append((label, box_a, zero_box, avg_box, 0.0))

            for idx_b, box_b in enumerate(boxes_b):
                if idx_b not in matched_b:
                    avg_box = Tagger._calculate_average_box(zero_box, box_b)
                    diffs.append((label, zero_box, box_b, avg_box, 0.0))
        return diffs
        
    @staticmethod
    def diff_tags(image_path, file_a_path, file_b_path, file_c_path=None):
        diffs = []
        zero_box = (0, 0, 0, 0)

        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception:
            return None

        tags_a = Tagger._parse_tag_file(file_a_path, width, height)
        tags_b = Tagger._parse_tag_file(file_b_path, width, height)
        if file_c_path is not None:
            if tags_a is None and tags_b is not None:
                tags_a = Tagger._parse_tag_file(file_c_path, width, height)
            if tags_b is None and tags_a is not None:
                tags_b = Tagger._parse_tag_file(file_c_path, width, height)
                
        return Tagger._diff_tags(tags_a,tags_b)
    
    @staticmethod
    def showdiff(diff_item, image_path, file_a_path=None, file_b_path=None, file_c_path=None, zoom=0, hide=0):
        """
        Draws diff visualization with strict edge-drawing order for clarity in overlaps.
        Drawing order:
            1. Cyan (file B) left/top
            2. Pink (file A) right/bottom
            3. Cyan (file B) right/bottom
            4. Pink (file A) left/top
            5. Blue (diff B) left/top
            6. Red (diff A) right/bottom
            7. Blue (diff B) right/bottom
            8. Red (diff A) left/top
        Special case:
            - If both box_a and box_b == (0,0,0,0), draws box_c in yellow
        """
        label, box_a, box_b, box_c, iou = diff_item
        boxes = []

        if box_a != (0, 0, 0, 0):
            boxes.append(box_a)
        if box_b != (0, 0, 0, 0):
            boxes.append(box_b)
        if not boxes and box_c != (0, 0, 0, 0):
            boxes.append(box_c)

        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error: Could not read image at {image_path}")
                return None
            h, w = img.shape[:2]
            
            tags_c = Tagger._parse_tag_file(file_c_path, w, h).get(label,[]) if os.path.exists(file_c_path) else None
            tags_a = Tagger._parse_tag_file(file_a_path, w, h).get(label,[]) if os.path.exists(file_a_path) else None
            tags_b = Tagger._parse_tag_file(file_b_path, w, h).get(label,[]) if os.path.exists(file_b_path) else None
            if tags_a is None:
                tags_a=tags_c
            if tags_b is None:
                tags_b=tags_c                
            print('tags_a',tags_a)
            print('tags_b',tags_b)
            print('tags_c',tags_c)

            # Zoom calculation
            x1_crop, y1_crop, x2_crop, y2_crop = 0, 0, w, h
            if zoom > 0 and boxes:
                min_x = int(min(box[0] for box in boxes))
                min_y = int(min(box[1] for box in boxes))
                max_x = int(max(box[2] for box in boxes))
                max_y = int(max(box[3] for box in boxes))
                box_w = max_x - min_x
                box_h = max_y - min_y
                pad_x = int(box_w * 0.25 / zoom)
                pad_y = int(box_h * 0.25 / zoom)

                x1_crop = max(0, min_x - pad_x)
                y1_crop = max(0, min_y - pad_y)
                x2_crop = min(w, max_x + pad_x)
                y2_crop = min(h, max_y + pad_y)

                img = img[y1_crop:y2_crop, x1_crop:x2_crop]

            def adjust(box):
                return (
                    int(box[0] - x1_crop),
                    int(box[1] - y1_crop),
                    int(box[2] - x1_crop),
                    int(box[3] - y1_crop),
                )

            def draw_edges(img, box, color, edges):
                if hide: return
                x1, y1, x2, y2 = adjust(box)
                if 'top' in edges:
                    cv2.line(img, (x1, y1), (x2, y1), color, 3)
                if 'bottom' in edges:
                    cv2.line(img, (x1, y2), (x2, y2), color, 3)
                if 'left' in edges:
                    cv2.line(img, (x1, y1), (x1, y2), color, 3)
                if 'right' in edges:
                    cv2.line(img, (x2, y1), (x2, y2), color, 3)

            # COLORS
            CYAN   = (255, 255, 0)
            PINK   = (203, 192, 255)
            BLUE   = (255, 0, 0)
            RED    = (0, 0, 255)
            YELLOW = (0, 255, 255)

            # 1. Cyan left/top
            for box in tags_b:
                if box != box_b:
                    draw_edges(img, box, CYAN, ['left', 'top'])

            # 2. Pink right/bottom
            for box in tags_a:
                if box != box_a:
                    draw_edges(img, box, PINK, ['right', 'bottom'])

            # 3. Cyan right/bottom
            for box in tags_b:
                if box != box_b:
                    draw_edges(img, box, CYAN, ['right', 'bottom'])

            # 4. Pink left/top
            for box in tags_a:
                if box != box_a:
                    draw_edges(img, box, PINK, ['left', 'top'])

            # Handle special case
            if box_a == (0, 0, 0, 0) and box_b == (0, 0, 0, 0) and box_c != (0, 0, 0, 0):
                draw_edges(img, box_c, YELLOW, ['left', 'top', 'right', 'bottom'])

            # 5. Blue left/top
            if box_b != (0, 0, 0, 0):
                draw_edges(img, box_b, BLUE, ['left', 'top'])

            # 6. Red right/bottom
            if box_a != (0, 0, 0, 0):
                draw_edges(img, box_a, RED, ['right', 'bottom'])

            # 7. Blue right/bottom
            if box_b != (0, 0, 0, 0):
                draw_edges(img, box_b, BLUE, ['right', 'bottom'])

            # 8. Red left/top
            if box_a != (0, 0, 0, 0):
                draw_edges(img, box_a, RED, ['left', 'top'])

            return img, (x1_crop, y1_crop, x2_crop, y2_crop)

        except Exception as e:
            print(geterrorstring(e))            
            raise KeyboardInterrupt
            return None

    @staticmethod
    def getimhw(f):
        with Image.open(f) as img:
            width, height = img.size
            return height,width

    @staticmethod
    def merge_images_and_tags(d__imf__tag, commonemptyfbase, merge_folder):
        """
        Copies images and generates tag files in a merged folder structure using
        a comma-separated normalized format as expected by _parse_tag_file.

        For each image in d__imf__tag:
          - Copies the image into merge_folder/imgs/
          - Loads the image to obtain its width and height.
          - Writes a tag file in merge_folder/imgs.label/ with lines formatted as:
                {label},{normalized_x1},{normalized_x2},{normalized_y1},{normalized_y2}
            where normalized_x1 = x1/image_width, etc.

        Then, for each label filename in commonemptyfbase (which are not present as keys
        in d__imf__tag):
          - The corresponding image filename is derived by stripping the trailing ".txt"
            from the label filename.
          - The image is copied to merge_folder/imgs/ and an empty tag file is created in
            merge_folder/imgs.label/ with the given label filename.

        Args:
            d__imf__tag (dict or defaultdict(list)):
                Mapping from full image paths to a list of tuples: (label, (x1, y1, x2, y2))
            commonemptyfbase (set):
                Set of label file names (e.g. "imagename.jpg.txt") that should be created empty.
            merge_folder (str):
                Parent folder under which "imgs" and "imgs.label" subfolders will be created.
        """
        print('merge_images_and_tags',{'d__imf__tag':f'{len(d__imf__tag)} d__imf__tag','commonemptyfbase':f'{len(commonemptyfbase)} commonemptyfbase','merge_folder':merge_folder})

        # Define destination directories
        imgs_dir = os.path.join(merge_folder, 'imgs')
        labels_dir = os.path.join(merge_folder, 'imgs.label')
        os.makedirs(imgs_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)

        # Set to track image basenames that have been processed from d__imf__tag
        processed_img_basenames = set()

        # Process images with tag data from d__imf__tag
        for full_img_path, tag_list in d__imf__tag.items():
            if not os.path.isfile(full_img_path):
                print(f"Warning: Image not found: {full_img_path}")
                continue

            img_filename = os.path.basename(full_img_path)
            processed_img_basenames.add(img_filename)
            # Create a label filename by appending ".txt" to the image filename
            label_filename = img_filename + ".txt"
            dest_img_path = os.path.join(imgs_dir, img_filename)

            # Copy image to destination folder
            try:
                shutil.copy2(full_img_path, dest_img_path)
            except Exception as e:
                print(f"Error copying {full_img_path} to {dest_img_path}: {e}")
                continue

            # Load image with OpenCV to determine dimensions
            img = cv2.imread(full_img_path)
            if img is None:
                print(f"Warning: Could not load image {full_img_path}")
                continue
            h, w = img.shape[:2]

            # Open the tag file for writing
            label_file_path = os.path.join(labels_dir, label_filename)
            try:
                with open(label_file_path, 'w') as f:
                    for tag_entry in tag_list:
                        label, box = tag_entry  # box is (x1, y1, x2, y2)
                        normalized_x1 = box[0] / w
                        normalized_x2 = box[2] / w
                        normalized_y1 = box[1] / h
                        normalized_y2 = box[3] / h
                        # Write in comma-separated normalized format
                        f.write(f"{label},{normalized_x1:.6f},{normalized_x2:.6f},{normalized_y1:.6f},{normalized_y2:.6f}\n")
            except Exception as e:
                print(f"Error writing tag file {label_file_path}: {e}")
                continue

        # Determine a source folder to locate images that are in commonemptyfbase.
        # We use one of the keys in d__imf__tag if available; otherwise, we fallback to CWD.
        if d__imf__tag:
            sample_key = next(iter(d__imf__tag))
            source_folder = os.path.dirname(sample_key)
        else:
            source_folder = os.getcwd()

        # Process images with empty tag files
        for empty_label_fname in commonemptyfbase:
            # Expecting a file name like "imagename.jpg.txt"
            if not empty_label_fname.endswith('.txt'):
                print(f"Warning: Label file name does not end with '.txt': {empty_label_fname}")
                continue
            image_basename = empty_label_fname[:-4]  # remove the trailing ".txt"
            if image_basename in processed_img_basenames:
                # Already processed via d__imf__tag; skip it.
                continue

            full_img_path = os.path.join(source_folder, image_basename)
            if not os.path.isfile(full_img_path):
                print(f"Warning: Could not find image for empty label file: {empty_label_fname} (expected: {full_img_path})")
                continue

            # Copy the image to the destination imgs folder
            dest_img_path = os.path.join(imgs_dir, image_basename)
            try:
                shutil.copy2(full_img_path, dest_img_path)
            except Exception as e:
                print(f"Error copying {full_img_path} to {dest_img_path}: {e}")
                continue

            # Create an empty tag file with the given label file name
            label_file_path = os.path.join(labels_dir, empty_label_fname)
            try:
                open(label_file_path, 'w').close()
            except Exception as e:
                print(f"Error creating empty label file {label_file_path}: {e}")
                continue

        print(f"Done. Processed {len(d__imf__tag)} images with tags and {len(commonemptyfbase)} empty tag files.")

    @staticmethod
    def compute_accuracy(imgs_folder, golden_folder, pred_folder, iou_threshold=0.5):
        """
        Compare golden labels (ground truth) in `golden_folder` against predicted labels
        in `pred_folder` for images under `imgs_folder`. All label files are in format 3,
        one per image: <label>,x1_norm,x2_norm,y1_norm,y2_norm per line.
        
        Returns a metrics dict:
          {
            'num_images': int,
            'per_class': { label: {tp, fp, fn, precision, recall, f1}, ... },
            'micro': {precision, recall, f1},
            'macro': {precision, recall, f1}
          }
        """
        # Prepare metrics containers
        metrics = {'num_images': 0, 'per_class': {}, 'micro': {}, 'macro': {}}
        counts = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
        
        # Collect all image files
        image_files = sorted(glob.glob(os.path.join(imgs_folder, '*.jpg')))
        
        for img_path in image_files:
            metrics['num_images'] += 1
            base = os.path.basename(img_path)
            gt_file = os.path.join(golden_folder, base + '.txt')
            pred_file = os.path.join(pred_folder, base + '.txt')
            
            # Parse tags (format 3) into absolute boxes
            tags_gt = Tagger._parse_tag_file(gt_file, imf=img_path) or {}
            tags_pred = Tagger._parse_tag_file(pred_file, imf=img_path) or {}
            
            # Compare per label
            for label in set(tags_gt) | set(tags_pred):
                gt_boxes = tags_gt.get(label, [])
                pred_boxes = tags_pred.get(label, [])
                
                if gt_boxes and pred_boxes:
                    # Compute IoU matrix
                    iou_mat = Tagger._batch_iou(gt_boxes, pred_boxes)
                    # Greedy matching above threshold
                    pairs = [
                        (iou_mat[i, j], i, j)
                        for i in range(iou_mat.shape[0])
                        for j in range(iou_mat.shape[1])
                        if iou_mat[i, j] >= iou_threshold
                    ]
                    pairs.sort(key=lambda x: x[0], reverse=True)
                    
                    matched_gt = set()
                    matched_pred = set()
                    for _, i_idx, j_idx in pairs:
                        if i_idx not in matched_gt and j_idx not in matched_pred:
                            matched_gt.add(i_idx)
                            matched_pred.add(j_idx)
                            counts[label]['tp'] += 1
                    
                    # Unmatched ground-truth = false negatives
                    counts[label]['fn'] += len(gt_boxes) - len(matched_gt)
                    # Unmatched predictions = false positives
                    counts[label]['fp'] += len(pred_boxes) - len(matched_pred)
                else:
                    # All GT are FN; all preds are FP
                    counts[label]['fn'] += len(gt_boxes)
                    counts[label]['fp'] += len(pred_boxes)
        
        # Aggregate and compute metrics
        sum_tp = sum(v['tp'] for v in counts.values())
        sum_fp = sum(v['fp'] for v in counts.values())
        sum_fn = sum(v['fn'] for v in counts.values())
        
        # Per-class
        for label, c in counts.items():
            tp, fp, fn = c['tp'], c['fp'], c['fn']
            prec = tp / (tp + fp) if tp + fp else 0.0
            rec  = tp / (tp + fn) if tp + fn else 0.0
            f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
            metrics['per_class'][label] = {
                'tp': tp, 'fp': fp, 'fn': fn,
                'precision': prec, 'recall': rec, 'f1': f1
            }
        
        # Micro-averaged
        micro_prec = sum_tp / (sum_tp + sum_fp) if (sum_tp + sum_fp) else 0.0
        micro_rec  = sum_tp / (sum_tp + sum_fn) if (sum_tp + sum_fn) else 0.0
        micro_f1   = 2 * micro_prec * micro_rec / (micro_prec + micro_rec) if (micro_prec + micro_rec) else 0.0
        metrics['micro'] = {
            'precision': micro_prec,
            'recall': micro_rec,
            'f1': micro_f1
        }
        
        # Macro-averaged
        precs = [m['precision'] for m in metrics['per_class'].values()]
        recs  = [m['recall']    for m in metrics['per_class'].values()]
        macro_prec = sum(precs) / len(precs) if precs else 0.0
        macro_rec  = sum(recs)  / len(recs)  if recs  else 0.0
        macro_f1   = 2 * macro_prec * macro_rec / (macro_prec + macro_rec) if (macro_prec + macro_rec) else 0.0
        metrics['macro'] = {
            'precision': macro_prec,
            'recall': macro_rec,
            'f1': macro_f1
        }
        
        return metrics
