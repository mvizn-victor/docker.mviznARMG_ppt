#version:1
from time import sleep, time, process_time
from memcachehelper import memcacheRW as mcrw
from config import config


def get_resp():
    t1 = process_time()
    resp_arr = ['%010d'%0, '..','%010d'%0, '..','%010d'%0, '..','%010d'%0, '..','%010d'%0, 'F',0, 'F',0, 'F']
    for i in range(7):
        p_res = mcrw.raw_read('p%s'%(i+1))
        t_res = '%010d'%mcrw.raw_read(f'cam{i+1}lastrawupdate')
        resp_arr[2*i]=t_res
        #w_res = mcrw.raw_read('w%s' % (i+1))
        camok_res = mcrw.raw_read('cam%dok'%(i+1)) # set in framesharer
        p_tstamp = float(p_res['tstamp'])
        if camok_res == 0:
            if i < 4:
                resp_arr[2*i+1] = 'XX'
            else:
                resp_arr[2*i+1] = 'X'
        elif (time()-p_tstamp) > config.config['inferdelaytolerance']:
            if i < 4:
                resp_arr[2*i+1] = 'ZZ'
            else:
                resp_arr[2*i+1] = 'Z'
        else :     #dont use stale res
            p_arr = p_res['results']
            p_arr.sort()
            #print(i, p_tstamp, p_arr)
            if len(p_arr)>0:
                if i < 4:
                    p_arr[0]=max(0,p_arr[0])
                    resp_arr[2*i+1] = str(int(p_arr[0])).zfill(2)
                else:
                    resp_arr[2*i+1] = 'T'
    if config.verbose:
        print("MC read took:", (process_time() - t1) * 1000, 'ms')
    return resp_arr

    #exit()
    #sleep(0.1)

if __name__ == '__main__':
    while True:
        resp_arr = get_resp()
        print(resp_arr)
        sleep(0.1)