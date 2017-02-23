# *-* conding: utf-8 -*-
from pylearn2.utils import serial
import h5py
import numpy as np
import sys
import os
import glob
import sys
import yaml
import Image
import scipy.misc
import hickle as hkl
ex = '.bmp' #such as :'bmp' or 'jpg' et.al

#---------------------make image txt type: image_filename table---------------------------#
def make_image_txt(paths,flag=False):#if True means label is useful
    print 'making train.txt,val.txt,test.txt........'
    train_img_dir = paths['train_img_dir']
    misc_dir = paths['misc_dir']
    train_label_file=paths['train_label_file']
    tar_label_dir = paths['tar_label_dir']
    
    traintxt_filename = os.path.join(misc_dir, 'image_all.txt')
    sorted_train_dirs = sorted([name for name in os.listdir(train_img_dir) if ex in name])
# generate train.txt and label.npy
    if flag:
    	with open(train_label_file, 'r') as f:
        	train_labels = f.readlines()    	
        assert len(train_labels) == len(sorted_train_dirs), \
               'train data: Numbers of images and labels should be the same.'
        final_labels = []
        for label in train_labels:
	    final_labels.append(label)#find 
        np.save(tar_label_dir+'label_all.npy',np.float32(final_labels))#note: if labels is float else remove 'float32'

    	with open(traintxt_filename, 'w') as f:
        	for ind in range(len(sorted_train_dirs)):
	    	    str_write =sorted_train_dirs[ind] + ' ' + \
	        	    str(float(train_labels[ind])) + '\n'              #note: int or float 
	    	    f.write(str_write)
    else:
    	with open(traintxt_filename, 'w') as f:
           for ind in range(len(sorted_train_dirs)):
	       str_write =sorted_train_dirs[ind]+ '\n'  #note: int or float 
	       f.write(str_write)
#---------------------make image data to npy out: image_data.npy---------------------------#
#read picture
def get_img(img_name,img_width=256,img_height=256):
    if ex == '.raw':
    	target_shape = (img_width,img_height)
    	f = open(img_name, "rb")
    	rawdata = f.read()
    	im=Image.fromstring('F',target_shape,rawdata,"raw",'F;32F')
    	pix=np.array(im.getdata())
    	pix = pix.reshape(img_width,img_height)
    else:#'jpg or bmp'
        target_shape = (img_height,img_width, 3)
        pix = scipy.misc.imread(img_name)  # x*x*3 img.shape(512,640,3)
        assert pix.dtype == 'uint8', img_name
        # assert False
        if len(pix.shape) == 2:
            pix = scipy.misc.imresize(pix, (img_height,ing_width))
            pix = np.asarray([pix, pix, pix])
        else:
            if pix.shape[2] > 3:
                pix = pix[:, :, :3]
            pix = scipy.misc.imresize(pix, target_shape)
            pix = np.rollaxis(pix, 2)#3*x*x pix.shape(3,512,640)
        if pix.shape[0] != 3:
            print img_name
    return pix
#save image data to npy def:one gpu
def save_batches(file_list, tar_dir,name,img_width=256,img_height=256,flag_avg=True):
    if not os.path.exists(tar_dir):
        os.makedirs(tar_dir)
#this is the problem
    if ex == '.raw':
       img_batch = np.zeros((img_width,img_height,len(file_list)),np.float32)
    else:
       img_batch = np.zeros((3,img_height,img_width,len(file_list)),np.uint8)
    batch_count = 0
    count = 0
    for file_name in file_list:
        img_batch[:, :, :,count % len(file_list)] =get_img(file_name,img_width=img_width,img_height=img_height)
        count += 1
    img_mean = img_batch.mean(axis=3)
    hkl.dump(img_batch, os.path.join(tar_dir,name), mode='w')
    return img_mean
def make_image_data(paths):
    misc_dir = paths['misc_dir']
    train_img_dir = paths['train_img_dir']
    img_width = paths['img_width']
    img_height = paths['img_height']
    tar_train_dir = paths['tar_train_dir']
    train_filenames = np.asarray(sorted(glob.glob(train_img_dir + '*'+ex)))

    print 'making training data..................'
    img_mean=save_batches(train_filenames,tar_train_dir,'image_all.hkl',img_width=img_width,img_height=img_height)
    np.save(misc_dir+'img_all_mean.npy',img_mean)
#---------------------start 1.make txt 2.make image data 3.make image lable---------------------------#
def get_config(filename=None, reload=False):
    if filename is None:
        raise Exception(
            'Configuration has not been loaded previously, filename parameter is required')
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(curr_dir, 'config.yaml')
    with open(filename) as f:
        config = yaml.load(f)
    return config

if __name__ == '__main__':
#reading globe config.yam
    conf_file = sys.argv[1] if len(sys.argv) > 1 else None
    conf = get_config(conf_file)
    enable_label = conf['enable_label']#make txt  true or false means label is useful or dis use
    make_image_txt(conf,enable_label)
    make_image_data(conf)#make image data
    

