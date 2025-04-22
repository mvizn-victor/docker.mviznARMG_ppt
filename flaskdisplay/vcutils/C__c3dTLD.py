#version: 1.0.0

def load_di_pkl(difile):
    import pyrealsense2 as rs
    pkl=pickle.load(open(difile,'rb'))
    depth_intrinsic = rs.intrinsics()
    depth_intrinsic.width = pkl['width']
    depth_intrinsic.height = pkl['height']
    depth_intrinsic.ppx = pkl['ppx']
    depth_intrinsic.ppy = pkl['ppy']
    depth_intrinsic.fx = pkl['fx']
    depth_intrinsic.fy = pkl['fy']
    depth_intrinsic.model = pkl['model']
    depth_intrinsic.coeffs = pkl['coeffs']
    return depth_intrinsic

class C__c3d:
    #ha04, flip mode
    version=2
    def __init__(self,c3dname,jpgf1=None,flipim=0):
        #480,848
        self.flipim=flipim
        self.c3dname=c3dname
        self.baynum=c3dname[:1]
        
        try:
            self.di=load_di_pkl(f'/opt/captures/{c3dname}_.pkl')
        except:
            self.di=load_di_pkl(f'/opt/captures/defaultdi_.pkl')
        self.camsuffix=c3dname[-2:]
        if jpgf1 is None:
            d=f'/dev/shm/captures/{c3dname}'
            fs=sorted(glob.glob(f'{d}/*.jpg'))
            if len(fs)>=2:
                jpgf=fs[-2]
            else:
                jpgf=None
        else:
            #overwrite with specified image
            jpgf=jpgf1

        if jpgf is None:
            self.imdepth=np.zeros((960,848,3),np.uint8)
            self.im=np.zeros((480,848,3),np.uint8)
            self.ann=np.zeros((480,848,3),np.uint8)
            self.depth=np.zeros((480,848,3),np.uint8)
            self.deptharray=np.zeros((480,848),np.uint32)
        else:
            npzf=jpgf.replace('.jpg','.npz')
            self.imdepth=cv2.imread(jpgf)
            self.im=self.imdepth[:self.imdepth.shape[0]//2]
            self.ann=self.im.copy()
            self.depth=self.imdepth[self.imdepth.shape[0]//2:]
            with np.load(npzf) as tmpfile:
                self.deptharray=tmpfile['arr_0']
        self.imw=self.im.shape[1]
        self.imh=self.im.shape[0]
        if self.flipim:
            self.im=self.im[:,::-1].copy()
            self.ann=self.im.copy()
    def get_xyzmm(self,x,y,z):
        import pyrealsense2 as rs
        if self.flipim:
            x=self.imw-x
        xm,ym,zm=rs.rs2_deproject_pixel_to_point(self.di, [x, y], z/1000)
        xmm,ymm,zmm=int(xm*1000),int(ym*1000),int(zm*1000)
        if self.flipim:
            xmm=-xmm
        return xmm,ymm,zmm
    def map__rect_medianz(self,rect):
        x1,y1,w,h=rect
        x2,y2=x1+w,y1+h
        if self.flipim:
            x2=self.imw-x1
            x1=self.imw-x2
        if y1<0:
            y2=y2-y1
            y1=y1-y1
        if x1<0:
            x2=x2-x1
            x1=x1-x1
        depthh,depthw=self.deptharray.shape[:2]
        imh,imw=self.im.shape[:2]
        #print({'imh':imh,'imw':imw,'depthh':depthh,'depthw':depthw})
        y1=int(y1*depthh/imh)
        y2=int(y2*depthh/imh)
        x1=int(x1*depthw/imw)
        x2=int(x2*depthw/imw)
        v=self.deptharray[y1:y2,x1:x2]
        if np.sum(v!=0)==0:
            try:
                v[0,0]=1
            except:
                print('setv fail',x1,y1,x2,y2)
        medianz=np.median(v[v!=0])
        #medianz=np.percentile(v[v!=0],0.5)
        return medianz
