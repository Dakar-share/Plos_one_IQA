import numpy as np
import hickle as hkl
import scipy.misc
import time
root = './data/image_all/'
a = hkl.load(root+'image_all.hkl')
P = 3
Q = 3
C = 10.0
a = np.asarray(a,dtype='f')

for k in range(a.shape[3]):
   #start = time.clock()
   for i in range(P,a.shape[2]):
      for j in range(Q,a.shape[1]):
         u = np.mean(a[:,(j-Q):(j+Q),(i-P):(i+P),k])
         s = np.sqrt(np.sum(np.square(a[:,(j-Q):(j+Q),(i-P):(i+P),k]-u)))
         a[:,j,i,k]=(a[:,j,i,k]-u)/(s+C)
   #end = time.clock()
   print 'picnumber: u,s,a',k,u,s, a[:,j,i,k]
   #print "this pic time:",(end-start)

print "Done....."
np.save(root+'image_all_lcn.npy',a[:,Q:,P:,:])
scipy.misc.imshow(a[:,Q:,P:,2])