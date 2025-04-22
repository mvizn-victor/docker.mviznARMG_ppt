import tensorflow as tf
import numpy as np
import glob, os, shutil
import cv2
from collections import Counter
def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph


def read_tensor_from_image_file(sess, file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(
        file_reader, channels=3, name="png_reader")
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(
        tf.image.decode_gif(file_reader, name="gif_reader"))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
  else:
    image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  #sess = tf.Session()
  result = sess.run(normalized)

  return result

def tensor_from_cvimg_old(sess, cvimg, input_height=299, input_width=299, input_mean=0, input_std=255):
    # from https://stackoverflow.com/questions/34484148/feeding-image-data-in-tensorflow-for-transfer-learning/34497833#34497833
    if 1:
        cvimg_nparray = np.array(cvimg)[:, :, ::-1]
        image_reader = tf.convert_to_tensor(cvimg_nparray, dtype=tf.float32)
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        result = sess.run(normalized)
        #print(result,file=open('/tmp/method1','w'))
    if 0:
        # Format for the Mul:0 Tensor
        img2 = cv2.resize(cvimg, dsize=(input_height, input_width), interpolation=cv2.INTER_LINEAR)
        # Numpy array
        np_image_data = np.asarray(img2)
        # maybe insert float convertion here - see edit remark!
        np_image_data=(np_image_data-input_mean)/input_std #cv2.normalize(np_image_data.astype('float'), None, -0.5, .5, cv2.NORM_MINMAX)
        np_final = np.expand_dims(np_image_data, axis=0)
        result=np_final
        #print(result,file=open('/tmp/method2','w'))
    #os.system('killall python')
    return result

def tensor_from_cvimg(sess, cvimg, input_height=299, input_width=299, input_mean=0, input_std=255):
    # from https://stackoverflow.com/questions/34484148/feeding-image-data-in-tensorflow-for-transfer-learning/34497833#34497833
    if 0:
        cvimg_nparray = np.array(cvimg)[:, :, 0:3]
        image_reader = tf.convert_to_tensor(cvimg_nparray, dtype=tf.float32)
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        result = sess.run(normalized)
        #print(result,file=open('/tmp/method1','w'))
    if 1:
        # Format for the Mul:0 Tensor
        img2 = cv2.resize(cvimg[:,:,::-1], dsize=(input_height, input_width), interpolation=cv2.INTER_LINEAR)
        # Numpy array
        np_image_data = np.asarray(img2)
        # maybe insert float convertion here - see edit remark!
        np_image_data=(np_image_data-input_mean)/input_std #cv2.normalize(np_image_data.astype('float'), None, -0.5, .5, cv2.NORM_MINMAX)
        np_final = np.expand_dims(np_image_data, axis=0)
        result=np_final
        #print(result,file=open('/tmp/method2','w'))
    #os.system('killall python')
    return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


#model_file = "/home/mvizn/Code/mViznRTG/config/top/top.pb"
#label_file = "/home/mvizn/Code/mViznRTG/config/top/top.labels"
model_file = "/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.pb"
label_file = "/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.labels"
input_layer = "Placeholder"
output_layer = "final_result"
graph = load_graph(model_file)
input_name = "import/" + input_layer
output_name = "import/" + output_layer
input_operation = graph.get_operation_by_name(input_name)
output_operation = graph.get_operation_by_name(output_name)
labels = load_labels(label_file)


def get_top_res(sess, cv_img):
    t = tensor_from_cvimg(sess, cv_img)
    tfresults = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t})
    tfresults = np.squeeze(tfresults)
    top_k = tfresults.argsort()[-5:][::-1]
    return(labels[top_k[0]], tfresults[top_k[0]])

def get_top_res_file(sess,f):
    t = read_tensor_from_image_file(sess,f)
    tfresults = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t})
    tfresults = np.squeeze(tfresults)
    top_k = tfresults.argsort()[-5:][::-1]
    return(labels[top_k[0]], tfresults[top_k[0]])


if __name__ == "__main__":
    resall=[]
    with tf.Session(graph=graph) as sess:
        for NP in 'np':
            for img_file in glob.glob(f'/mnt/908b5279-0ff3-48ce-83be-f0f3a7d2926d/tophits_0d97/phase3/{NP}/*'):
                im=cv2.imread(img_file)
                t1=tensor_from_cvimg(sess,im)
                t2=tensor_from_cvimg_old(sess,im)
                tfresults = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t1})
                tfresults = np.squeeze(tfresults)
                top_k = tfresults.argsort()[-5:][::-1]
                res1=[NP]
                if labels[top_k[0]]  == 'p':
                    res1.append('p')
                if labels[top_k[0]]  == 'n':
                    res1.append('n')
                tfresults = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t2})
                tfresults = np.squeeze(tfresults)
                top_k = tfresults.argsort()[-5:][::-1]
                if labels[top_k[0]]  == 'p':
                    res1.append('p')
                if labels[top_k[0]]  == 'n':
                    res1.append('n')
                resall.append(tuple(res1))
                if len(resall)%100==0:
                    print(Counter(resall))
