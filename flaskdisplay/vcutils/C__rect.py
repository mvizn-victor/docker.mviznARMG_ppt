#version: 1.0.0

class C__rect:
    """
    inputformat:
    x1y1wh
    x1y1x2y2
    xcycwh

    outputformat:
    xcyc
    x1y1x2y2
    x1y1wh
    xcycwh
    expand
    xcycexpand
    int -> round off x1 y1 x2 y2 and convert to integer
    """
    __version__=3
    def __init__(self,rect,format='x1y1wh'):
        if format=='x1y1wh':
            self.x1,self.y1,self.w,self.h=rect
        elif format=='x1y1x2y2':
            self.x1,self.y1,self.x2,self.y2=rect
            self.w=self.x2-self.x1
            self.h=self.y2-self.y1
        elif format=='xcycwh':
            self.xc,self.yc,self.w,self.h=rect
            self.x1=self.xc-self.w/2
            self.y1=self.yc-self.h/2
    def int(self):
        self.x1,self.y1,self.w,self.h=map(lambda x:int(round(x)),[self.x1,self.y1,self.w,self.h])
        return self
    def xcyc(self):
        xc=self.x1+self.w/2
        yc=self.y1+self.h/2
        return xc,yc
    def x1y1x2y2(self):
        x1=self.x1
        y1=self.y1
        x2=self.x1+self.w
        y2=self.y1+self.h
        return x1,y1,x2,y2
    def x1y1wh(self):
        x1=self.x1
        y1=self.y1
        w=self.w
        h=self.h
        return x1,y1,w,h
    def xcycwh(self):
        xc=self.x1+self.w/2
        yc=self.y1+self.h/2
        w=self.w
        h=self.h
        return xc,yc,w,h
    #version=2
    def expand(self,x1,y1,x2,y2):
        ax1,ay1,ax2,ay2=self.x1y1x2y2()
        ax1=ax1-x1
        ay1=ay1-y1
        ax2=ax2+x2
        ay2=ay2+y2
        return C__rect((ax1,ay1,ax2,ay2),format='x1y1x2y2')
    def xcycexpand(self,x1,y1,x2,y2):
        axc,ayc=self.xcyc()
        ax1=axc-x1
        ay1=ay1-y1
        ax2=ax2+x2
        ay2=ay2+y2
        return C__rect((ax1,ay1,ax2,ay2),format='x1y1x2y2')
    def __str__(self):
        return f'{self.x1} {self.y1} {self.w} {self.h}'
    def __repr__(self):
        return f'{self.x1} {self.y1} {self.w} {self.h}'
def croprect_im(im,rect):
    """
    make sure rect is integer
    """
    x1,y1,w,h=rect
    x2,y2=x1+w,y1+h
    return im[max(0,y1):y2,max(0,x1):x2]
