'''
Created on Jun 3, 2012

@author: redwards
'''

import Image

def show():
    fileName = raw_input("What is the name of the image file? ")
    showImage(fileName)

def showImage(fn):
    picture = Image.open(fn)
    picture.show();
   # width, height = picture.size()
    #pix = picture.getPixels()



show()