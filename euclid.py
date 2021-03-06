#-------------------------------------------------------------------------------
# Euclid - Labelling tool
# Create and label bounding boxes
#    prabindh@yahoo.com, 2017
#        Initial code taken from github.com/puzzledqs/BBox-Label-Tool
#        Significantly modified to add more image types, image folders, labelling saves, and format, and format selection
#        Currently supports Kitti and YOLO(darknet) output formats
# Python 2.7
# pip install pillow
# pip install image
# Python 3
# Python 3 + Pillow on Ubuntu, do the below
# sudo apt-get install python-imaging-tk
# sudo apt-get install python3-pil.imagetk
#
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# The DetectNet/ Kitti Database format
# Taken from https://github.com/NVIDIA/DIGITS/blob/master/digits/extensions/data/objectDetection/README.md#label-format
# All values (numerical or strings) are separated via spaces,
# each row corresponds to one object. The 15 columns represent:
#
#Values    Name      Description
#----------------------------------------------------------------------------
#   1    type         Describes the type of object: 'Car', 'Van', 'Truck',
#                     'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram',
#                     'Misc' or 'DontCare'
#   1    truncated    Float from 0 (non-truncated) to 1 (truncated), where
#                     truncated refers to the object leaving image boundaries
#   1    occluded     Integer (0,1,2,3) indicating occlusion state:
#                     0 = fully visible, 1 = partly occluded
#                     2 = largely occluded, 3 = unknown
#   1    alpha        Observation angle of object, ranging [-pi..pi]
#   4    bbox         2D bounding box of object in the image (0-based index):
#                     contains left, top, right, bottom pixel coordinates
#   3    dimensions   3D object dimensions: height, width, length (in meters)
#   3    location     3D object location x,y,z in camera coordinates (in meters)
#   1    rotation_y   Rotation ry around Y-axis in camera coordinates [-pi..pi]
#   1    score        Only for results: Float, indicating confidence in
#                     detection, needed for p/r curves, higher is better.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# The YOLO format
# All values (numerical or strings) are separated via spaces,
# each row corresponds to one object. The 5 columns represent:
#
#Values    Name      Description
#----------------------------------------------------------------------------
#   1    Class ID     Describes the class number of object, as an integer number (0 based)
#   1    Center_X     Float from 0 to 1, X coordinate of b-box center, normalised to image width
#   1    Center_Y     Float from 0 to 1, Y coordinate of b-box center, normalised to image height
#   1    Bbox_Width   Float from 0 to 1, Width of b-box, normalised to image width
#   1    Bbox_Height  Float from 0 to 1, Height of b-box, normalised to image height
#-------------------------------------------------------------------------------
import sys
if sys.version_info[0] < 3:
    from Tkinter import *
    import tkMessageBox
    import tkFileDialog
else:
    from tkinter import *
    from tkinter import messagebox as tkMessageBox
    from tkinter import filedialog as tkFileDialog
from PIL import Image, ImageTk
import os
import glob
import random

    
# Usage
USAGE = " \
1. Select a Directory of images in bottom control panel \n \
2. Click Load \n \
3. The first image in the directory should load, along with existing labels if any. \n \
4. Select a Class label to be used for next bounding box, in class-control panel \n \
5. After the image is loaded, press x key, or mouseclick to draw bounding boxes over the image \n \
6. Click Save in the File Navigation panel in bottom, to save the bounding boxes \n \
7. Labels are saved in folder named LabelData in same directory as the images \n \
8. Can use Left/Right arrows for navigating prev/next images \n \
Note: Default is KITTI format \
"


# Object Classes (No spaces in name)
CLASSES = ['Class0', 'Class1', 'Class2', 'Class3', 'Class4', 'Class5', 'Class6', 'Class7', 'Class8', 'Class9', 'Class10', 'Class11', 'Class12', 'Class13']

class Euclid():

    #set class label 
    def setClass0(self):
        self.currClassLabel=0;
        self.currClassLabelDisplayString.set('Current Class = 0')
    def setClass1(self):
        self.currClassLabel=1;
        self.currClassLabelDisplayString.set('Current Class = 1')        
    def setClass2(self):
        self.currClassLabel=2;
        self.currClassLabelDisplayString.set('Current Class = 2')        
    def setClass3(self):
        self.currClassLabel=3;
        self.currClassLabelDisplayString.set('Current Class = 3')                
    def setClass4(self):
        self.currClassLabel=4;
        self.currClassLabelDisplayString.set('Current Class = 4')
    def setClass5(self):
        self.currClassLabel=5;
        self.currClassLabelDisplayString.set('Current Class = 5')        
    def setClass6(self):
        self.currClassLabel=6;
        self.currClassLabelDisplayString.set('Current Class = 6')        
    def setClass7(self):
        self.currClassLabel=7;
        self.currClassLabelDisplayString.set('Current Class = 7')        
    def setClass8(self):
        self.currClassLabel=8;
        self.currClassLabelDisplayString.set('Current Class = 8')        
    def setClass9(self):
        self.currClassLabel=9;
        self.currClassLabelDisplayString.set('Current Class = 9')    
    def setClass10(self):
        self.currClassLabel=10;
        self.currClassLabelDisplayString.set('Current Class = 10')          
    def setClass11(self):
        self.currClassLabel=11;
        self.currClassLabelDisplayString.set('Current Class = 11')          
    def setClass12(self):
        self.currClassLabel=12;
        self.currClassLabelDisplayString.set('Current Class = 12')          
    def setClass13(self):
        self.currClassLabel=13;
        self.currClassLabelDisplayString.set('Current Class = 13')          
    def setClassN(self, N):
        self.currClassLabel=N;
        self.currClassLabelDisplayString.set('Current Class = '+ str(N))  

    def askDirectory(self):
      self.imageDir = tkFileDialog.askdirectory()
      self.SavePathToConfig(self.imageDir)
      self.entry.insert(0, self.imageDir)
      self.loadDir(self)
        
    def SavePathToConfig(self, newPath):
        #config file
        configFile = open(os.path.join(sys.path[0], "euclidconfig.txt"), "a+")
        lines = configFile.readlines()
        if(len(lines) > 10):
            configFile.close()
            configFile = open(os.path.join(sys.path[0], "euclidconfig.txt"), "w+")
            configFile.write(newPath + "\n")
            configFile.close()
        else:
            configFile.write(newPath + "\n")
            configFile.close()

    def AddFileToTrainingList(self, newFile):
        #training file
        trainfile = open(os.path.join(sys.path[0], "train.txt"), "a+")
        trainfile.write(newFile + "\n")
        trainfile.close()
        
    def TestClassEntry(self,inStr,i,acttyp):
        ind=int(i)
        if acttyp == '1': #insert
            if not inStr[ind].isdigit():
                return False
        
        self.setClassN(int(inStr))
        return True


    def loadDir(self, dbg = False):
        self.imageDir = self.entry.get()
        self.parent.focus()
        if not os.path.isdir(self.imageDir):
            tkMessageBox.showerror("Folder error", message = "The specified directory doesn't exist!")
            return        
        self.SavePathToConfig(self.imageDir)
         #get image list
        imageFileTypes = ('*.JPEG', '*.JPG', '*.PNG') # the tuple of file types
        self.imageList = []
        for files in imageFileTypes:
            self.imageList.extend(glob.glob(os.path.join(self.imageDir, files.lower())) )
            if (False == self.is_windows):
                self.imageList.extend(glob.glob(os.path.join(self.imageDir, files)) )
            
        if len(self.imageList) == 0:
            tkMessageBox.showerror("File not found", message = "No images (png, jpeg, jpg) found in folder!")
            self.updateStatus( 'No image files found in the specified dir!')
            return
        # Change title
        self.parent.title("Euclid Labeller (" + self.imageDir + ") " + str(len(self.imageList)) + " images")


        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(self.imageDir + '/LabelData')
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.updateStatus( '%d images loaded from %s' %(self.total, self.imageDir))
        self.loadImageAndLabels()

        
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("Euclid Labeller (Press F1 for Help)")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = TRUE, height = TRUE)
        self.is_windows = hasattr(sys, 'getwindowsversion')


        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.imagename = ''
        self.labelfilename = ''
        self.currLabelMode = 'YOLO' #'KITTI' #'YOLO' # Other modes TODO
        self.imagefilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0
        self.currentMouseX = 0;
        self.currentMouseY = 0;

        #colors
        self.redColor = self.blueColor = self.greenColor = 128
        
        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.currClassLabel = 0
        self.classLabelList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------

        # main panel for labeling
        self.imagePanelFrame = Frame(self.frame)
        self.imagePanelFrame.grid(row = 0, column = 0, rowspan = 4, padx = 5, sticky = W+N)

        self.imageLabel = Label(self.imagePanelFrame, text = 'Image View')
        self.imageLabel.grid(row = 0, column = 0,  sticky = W+N)        
        self.mainPanel = Canvas(self.imagePanelFrame, cursor='tcross', borderwidth=2, background='light blue')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("n", self.nextImage)    
        self.parent.bind("x", self.selectPointXY)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Escape> to cancel current bbox
        self.parent.bind("<F1>", self.showHelp)  # press <F1> to show help
        self.parent.bind("<Left>", self.prevImage) # press 'Left Arrow' to go backforward
        self.parent.bind("<Right>", self.nextImage) # press 'Right Arrow' to go forward
        self.mainPanel.grid(row = 1, column = 0, rowspan = 4, sticky = W+N)

        # Boundingbox info panel
        self.bboxControlPanelFrame = Frame(self.frame)
        self.bboxControlPanelFrame.grid(row = 0, column = 1, sticky = E)

        self.lb1 = Label(self.bboxControlPanelFrame, text = 'Bounding box / Label list')
        self.lb1.grid(row = 0, column = 0,  sticky = W+N)
        self.listbox = Listbox(self.bboxControlPanelFrame, width = 40, height = 12,  background='white')
        self.listbox.grid(row = 1, column = 0, sticky = N)
        self.btnDel = Button(self.bboxControlPanelFrame, text = 'Delete', command = self.delBBox)
        self.btnDel.grid(row = 2, column = 0, sticky = W+E+N)
        self.btnClear = Button(self.bboxControlPanelFrame, text = 'Clear All', command = self.clearBBox)
        self.btnClear.grid(row = 3, column = 0, sticky = W+E+N)

	    #Class labels selection
        # control panel for label navigation
        CLASSHANDLERS = [self.setClass0, self.setClass1, self.setClass2, self.setClass3, self.setClass4, 
                self.setClass5, self.setClass6, self.setClass7, self.setClass8, self.setClass9, self.setClass10, self.setClass11, self.setClass12, self.setClass13]

        self.labelControlPanelFrame = Frame(self.frame)
        self.labelControlPanelFrame.grid(row = 0, column = 2, padx = 5, sticky = N+E)
        self.classLabelText = Label(self.labelControlPanelFrame, text = 'Select class before drawing box')
        self.classLabelText.grid(row = 0, column = 0, sticky = W+E+N)

        count = 0
        for classLabel in CLASSES:
            classBtn = Button(self.labelControlPanelFrame, text = classLabel, command = CLASSHANDLERS[count])
            classBtn.grid(row = 1+count, column = 0, sticky = N+W)
            count = count + 1
        #Provide entry fields
        self.ClassEntry = Entry(self.labelControlPanelFrame, validate="key")
        self.ClassEntry.grid(row = 1+count, column = 0, sticky = N)
        self.ClassEntry['validatecommand'] = (self.ClassEntry.register(self.TestClassEntry),'%P','%i','%d')
        #Display current label
        self.currClassLabelDisplayString = StringVar()
        self.currClassLabelDisplayString.set('Current Class = 0')
        self.currClassLabelDisplay = Label(self.labelControlPanelFrame, textvariable = self.currClassLabelDisplayString)
        self.currClassLabelDisplay.grid(row = 2+count, column = 0, sticky = W+E+N)            

        # dir entry & load File control panel
        self.FileControlPanelFrame = Frame(self.frame)
        self.FileControlPanelFrame.grid(row = 5, column = 0, sticky = W)

        self.FileControlPanelLabel = Label(self.FileControlPanelFrame, text = '1. Select a directory (or) Enter input path, and click Load')
        self.FileControlPanelLabel.grid(row = 0, column = 0,  sticky = W+N)
        
        self.browserBtn = Button(self.FileControlPanelFrame, text = "Select Dir", command = self.askDirectory)
        self.browserBtn.grid(row = 1, column = 0, sticky = N)        
        
        self.entry = Entry(self.FileControlPanelFrame)
        self.entry.grid(row = 1, column = 1, sticky = N)
        self.ldBtn = Button(self.FileControlPanelFrame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 1, column = 2, sticky = N)
        
        self.FormatLabel = Label(self.FileControlPanelFrame, text = '2. Format Selection')
        self.FormatLabel.grid(row = 2, column = 0, sticky = W+N)
        self.isYoloCheckBox = IntVar()
        self.isYoloCheckBox.set(0)    
        self.yoloCheckBox = Radiobutton(self.FileControlPanelFrame, variable=self.isYoloCheckBox, value=1, text="Yolo Format")
        self.yoloCheckBox.grid(row = 3, column = 0, sticky = N)
        self.kittiCheckBox = Radiobutton(self.FileControlPanelFrame, variable=self.isYoloCheckBox, value=0, text="KITTI Format")
        self.kittiCheckBox.grid(row = 3, column = 1, sticky = N)
       
            
            
        
        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 6, column = 0, columnspan = 2, sticky = W+N)
        self.navLabel = Label(self.ctrPanel, text = '3. File Navigation')
        self.navLabel.pack(side = LEFT, padx = 5, pady = 3)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.saveLabelBtn = Button(self.ctrPanel, text = 'Save Current Boxes/Labels', command = self.saveLabel)
        self.saveLabelBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)
        self.progLabel = Label(self.ctrPanel, text = "Progress: [  0   /  0  ]")
        self.progLabel.pack(side = LEFT, padx = 5)

        # Status panel for image navigation
        self.statusPanel = Frame(self.frame)
        self.statusPanel.grid(row = 7, column = 0, columnspan = 3, sticky = W)
        self.statusText = StringVar()
        self.statusLabel = Label(self.statusPanel, textvariable = self.statusText)
        self.statusLabel.grid(row = 0, column = 0, sticky = W+E+N)
        self.updateStatus("Directory not selected.")

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)




    def loadImageAndLabels(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.imagefilename = imagepath
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "Progress: [ %04d / %04d ]" %(self.cur, self.total))
        self.updateStatus("Loaded file " + imagepath)
        
        if self.tkimg.width() > 1024 or self.tkimg.height() > 1024:
            tkMessageBox.showwarning("Too large image", message = "Image dimensions not suited for Deep Learning frameworks!")
            
        # load labels
        self.clearBBox()
        self.classLabelList = []
        lastPartFileName, lastPartFileExtension = os.path.splitext(os.path.split(imagepath)[-1])      
        self.imagename = lastPartFileName
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    bbox_cnt = len(line)
                    tmp = [elements.strip() for elements in line.split()]
                    
                    if(len(tmp) > 5):
                        self.currLabelMode='KITTI'
                        bbTuple = (int(float(tmp[4])),int(float(tmp[5])), int(float(tmp[6])),int(float(tmp[7])) )
                        self.classLabelList.append(CLASSES.index(tmp[0]))
                        
                    else:
                        self.currLabelMode='YOLO'
                        bbTuple = self.GetBoundariesFromYoloFile(float(tmp[1]),float(tmp[2]), float(tmp[3]),float(tmp[4]), 
                                                            self.tkimg.width(), self.tkimg.height() )
                        self.classLabelList.append(tmp[0])                        
                    
                    self.bboxList.append( bbTuple  )
                    #color set
                    currColor = '#%02x%02x%02x' % (self.redColor, self.greenColor, self.blueColor)
                    self.greenColor = (self.greenColor + 45) % 255
                    # currColor = setColor(tmp[0])

                    tmpId = self.mainPanel.create_rectangle(int(bbTuple[0]), int(bbTuple[1]), \
                                                            int(bbTuple[2]), int(bbTuple[3]), \
                                                            width = 2, \
                                                            outline = currColor)
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d) [%s]' %(int(bbTuple[0]), int(bbTuple[1]), \
                                                            int(bbTuple[2]), int(bbTuple[3]), tmp[0]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = currColor)

    def setColor(colorId):
        if(colorId == 0):
            self.redColor = 255;
            self.greenColor = 0;
            self.blueColor = 0;
        elif(colorId == 1):
            self.redColor = 0;
            self.greenColor = 255;
            self.blueColor = 0;
        elif(colorId == 2):
            self.redColor = 0;
            self.greenColor = 0;
            self.blueColor = 255;
        elif(colorId == 3):
            self.redColor = 255;
            self.greenColor = 255;
            self.blueColor = 0;
        elif(colorId == 4):
            self.redColor = 255;
            self.greenColor = 0;
            self.blueColor = 255;
        else:
            self.redColor = 0;
            self.greenColor = 255;
            self.blueColor = 255;
        return '#%02x%02x%02x' % (self.redColor, self.greenColor, self.blueColor)


    def GetBoundariesFromYoloFile(self, centerX, centerY, width, height, imageWidth, imageHeight):
        topLeftX = (int)(centerX*imageWidth - (width*imageWidth)/2)
        topLeftY = (int)(centerY*imageHeight - (height*imageHeight)/2)
        bottomRightX = (int)(centerX*imageWidth + (width*imageWidth)/2)
        bottomRightY = (int)(centerY*imageHeight + (height*imageHeight)/2)
        return topLeftX, topLeftY, bottomRightX, bottomRightY    

    def convert2Yolo(self, image, boxCoords):
        
        invWidth = 1./image[0]
        invHeight = 1./image[1]
        x = invWidth * (boxCoords[0] + boxCoords[2])/2.0
        y = invHeight * (boxCoords[1] + boxCoords[3])/2.0
        boxWidth = invWidth * (boxCoords[2] - boxCoords[0])
        boxHeight = invHeight * (boxCoords[3] - boxCoords[1])
        return (x,y,boxWidth,boxHeight)
                

    def saveLabel(self):
        if self.labelfilename == '': 
            return            
        if(len(self.bboxList) == 0):
            return
        if self.isYoloCheckBox.get() == 0:
            self.currLabelMode = 'KITTI'
        else:
            self.currLabelMode = 'YOLO'
            
        if self.currLabelMode == 'KITTI':
            with open(self.labelfilename, 'w') as f:
                labelCnt=0
                ##class1 0 0 0 x1,y1,x2,y2 0,0,0 0,0,0 0 0  
                # fields ignored by DetectNet: alpha, scenario, roty, occlusion, dimensions, location.
                for bbox in self.bboxList:
                    f.write('%s' %CLASSES[self.classLabelList[labelCnt]])               
                    f.write(' 0.0 0 0.0 ')
                    #f.write(str(bbox[0])+' '+str(bbox[1])+' '+str(bbox[2])+' '+str(bbox[3]))
                    f.write('%.2f %.2f %.2f %.2f' % (bbox[0], bbox[1], bbox[2], bbox[3]))                 
                    f.write(' 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 ')
                    f.write('\n')
                    labelCnt = labelCnt+1
            self.updateStatus ('Label Image No. %d saved' %(self.cur))
        elif self.currLabelMode == 'YOLO':
            with open(self.labelfilename, 'w') as f:
                labelCnt=0
                labelList=[]
                ##class1 center_box_x_ratio center_box_y_ratio width_ratio height_ratio
                for bbox in self.bboxList:                
                    yoloOut = self.convert2Yolo(
                                [self.tkimg.width(), self.tkimg.height()], 
                                [bbox[0], bbox[1], bbox[2], bbox[3]]
                                );
                    f.write('%s' %self.classLabelList[labelCnt])  
                    labelList.append(self.classLabelList[labelCnt])             
                    f.write(' %.7f %.7f %.7f %.7f' % (yoloOut[0], yoloOut[1], yoloOut[2], yoloOut[3]))                 
                    f.write('\n')
                    #tkMessageBox.showinfo("Save Info", message = self.classLabelList[labelCnt])
                    labelCnt = labelCnt+1
                print labelList
            self.updateStatus ('Label Image No. %d saved' %(self.cur))
            self.AddFileToTrainingList(self.imagefilename);
        else:
            tkMessageBox.showerror("Labelling error", message = 'Unknown Label format')
        

    def selectPointXY(self, event):
        self.handleMouseOrXKey(self.currentMouseX, self.currentMouseY)

    def mouseClick(self, event):
        self.handleMouseOrXKey(event.x, event.y)

    def handleMouseOrXKey(self, xCoord, yCoord):
        if self.imagefilename == '':
            return
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = xCoord, yCoord
        else:
            #Got a new BB, store the class label also
            x1, x2 = min(self.STATE['x'], xCoord), max(self.STATE['x'], xCoord)
            y1, y2 = min(self.STATE['y'], yCoord), max(self.STATE['y'], yCoord)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.classLabelList.append(self.currClassLabel)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)[Class %d]' %(x1, y1, x2, y2 , self.currClassLabel))
            # #color set
            currColor = '#%02x%02x%02x' % (self.redColor, self.greenColor, self.blueColor)
            self.redColor = (self.redColor + 25) % 255     
            # currColor = setColor(self.currClassLabel)    
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = currColor)
        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        if self.imagefilename == '':
            return
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if event.x > self.tkimg.width():
                return
            if event.y > self.tkimg.height():
                return
                
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            #color set
            currColor = '#%02x%02x%02x' % (self.redColor, self.greenColor, self.blueColor)
            self.blueColor = (self.blueColor + 35) % 255                
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = currColor)
        #Save current xy
        self.currentMouseX = event.x;
        self.currentMouseY = event.y;

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def showHelp(self, event):
        tkMessageBox.showinfo("Help", USAGE)


    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        self.classLabelList.pop(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.classLabelList = []

    def prevImage(self, event = None):
        self.saveLabel()    
        if self.cur > 1:
            self.cur -= 1
            self.loadImageAndLabels()
        else:
            self.updateStatus("No more previous files!")
            tkMessageBox.showwarning("Labelling complete", message = "No previous file to label!")

    def nextImage(self, event = None):
        self.saveLabel()
        if self.cur < self.total:
            self.cur += 1
            self.loadImageAndLabels()
        else:
            self.updateStatus("No more next files!")
            tkMessageBox.showwarning("Labelling complete", message = "No next file to label!")

    def gotoImage(self):
        if self.idxEntry.get() == '':
            return
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.cur = idx
            self.loadImageAndLabels()

    def updateStatus(self, newStatus):
        self.statusText.set("Status: " + newStatus)
    
if __name__ == '__main__':
    root = Tk()
    tool = Euclid(root)
    root.mainloop()

