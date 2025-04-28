#version:1
import pylibmc

mc = pylibmc.Client(["localhost"], binary=True, behaviors={"tcp_nodelay": True})


def write(camid, tstamp, results=None):
    """
    Write yolo results to memcache with camid as key
    :param camid:
    :param tstamp:
    :param results:
    :return: 0 on success
    """

    try:
        mc.set(camid, {'tstamp': tstamp, 'results': results})
    except Exception as e:
        print(e)
        return(1)
    return(0)


def read(camid):

    """
    Returns memcached result for particular camera
    :param camid:
    :return: [tstamp, resultsarray]
    """

    yolores = mc.get(camid)
    return(yolores['tstamp'], yolores['results'])


def raw_read(key,default=None):
    v = mc.get(key)
    if v is None:
        return default
    else:
        return v
        
def raw_write(key,value):
    return mc.set(key,value)
