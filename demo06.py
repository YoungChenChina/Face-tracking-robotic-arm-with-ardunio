'''
2018.8.14
更新内容：动态人脸识别框
锁定一个人脸后将识别框缩小在当前人脸的范围内

'''

# coding=utf-8
import cv2
import dlib
import serial
import time
import math
 
bias_x = 0.07
bias_y = 0.08
bias_detect_area = 1
resize = 0.65


def get_detect_area(face_pos, width, height):

    # print('width:', width, 'height', height)

    center = [(face_pos[0] + face_pos[1]) * 0.5, (face_pos[2] + face_pos[3]) * 0.5]
    # print('center:', center)
    d_width = face_pos[1]  - face_pos[0]
    d_height = face_pos[3] - face_pos[2]
    
    d_left = center[0] - bias_detect_area * d_width
    d_right = center[0] + bias_detect_area * d_width
    d_top = center[1] - bias_detect_area * d_height
    d_bottom = center[1] + bias_detect_area * d_height

    # print('face_pos:', face_pos)

    if(d_left < 0):
        d_left = 0
    if(d_right > width):
        d_right = width
    if(d_top < 0):
        d_top = 0
    if(d_bottom > height):
        d_bottom = height

    detect_area = []

    detect_area = [int(d_left), int(d_right), int(d_top), int(d_bottom)]
    # print('detect_area:',detect_area)
    return detect_area    



ser = serial.Serial()
ser.baudrate = 9600 #波特率
ser.port = 'COM3' #端口
print(ser)
ser.open()#打开串口
# print(ser.is_open)#检验串口是否打开

# 初始化dlib人脸检测器
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('shape_predictor_5_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')
# 初始化显示窗口
win = dlib.image_window()

# opencv load camera

cap = cv2.VideoCapture(0)

cap.set(3,1080)
cap.set(4,720)

width = cap.get(3)
height = cap.get(4)

# print(width)
# print(height)

# self_tracking tag
right_tag = 0
left_tag = 0
count = 0
renew_edge_count = 0

# face area
face_pos = []     #[left, right, top, bottom]

#detect area
detect_area = [] #[left, right, top, bottom]


judge_person = 1

init_former = 1

while cap.isOpened():

    ret, cv_img = cap.read()
    if cv_img is None:
        break

    img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (0, 0), fx=resize, fy=resize)
    height, width = img.shape[:2]
    # print(width, '\t', height)


    if(init_former == 1):

        dets = detector(img,0)

        if(len(dets) == 0):
            continue
        else:
            init_former = 0

            face_pos = [dets[0].left(), dets[0].right(), dets[0].top(), dets[0].bottom()]
            
            detect_area = get_detect_area(face_pos, width, height)
            former_pos_x = 0.5*( dets[0].left() + dets[0].right() )
            former_pos_y = 0.5*( dets[0].top() + dets[0].bottom() )
            former_facearea = math.pow((dets[0].right()-dets[0].left())*(dets[0].top()-dets[0].bottom()),2)


    else:
        img_d = img[detect_area[2]:detect_area[3], detect_area[0]:detect_area[1]]
        dets_d = detector(img_d, 0)
        if(len(dets_d) != 0):

            renew_edge_count = 0

            # dets = detector(img,0)
            # print('dets_d')
            # img = img_d
            cv2.rectangle(img, (detect_area[0],detect_area[2]), (detect_area[1],detect_area[3]), (0,255,0), 4)

            right_tag = 0
            left_tag = 0

            axis_x = 0
            axis_y = 0

            x_motion = 0
            y_motion = 0            

            face_left = 0
            face_right = 0
            face_top = 0
            face_bottom = 0

            face_left = dets_d[0].left() + detect_area[0]
            face_right = dets_d[0].right() + detect_area[0]
            face_top = dets_d[0].top() + detect_area[2]
            face_bottom = dets_d[0].bottom() + detect_area[2]

            axis_x = (face_left + face_right)*0.5
            axis_y = (face_top + face_bottom)*0.5


            if(axis_x > (0.5*width + width*bias_x)):
                x_motion = 1
                right_tag = 1
            elif(axis_x < (0.5*width - width*bias_x)):
                x_motion = 2
                left_tag = 1

            if(axis_y > (0.5*height + height*bias_y)):
                y_motion = 1
            elif(axis_y < (0.5*height - height*bias_y)):
                y_motion = 2

            motion_data = str(x_motion) + str(y_motion)
            # print(motion_data)
            motion_data = bytes(motion_data, encoding = "utf8")
            ser.write(motion_data) 

            face_pos = [face_left, face_right, face_top, face_bottom]
            detect_area = get_detect_area(face_pos, width, height)

            win.clear_overlay()                                   

        else:


            # 检测人脸
            dets = detector(img, 0)

            axis_x = 0
            axis_y = 0
            x_motion = 0
            y_motion = 0

            # self searching for face depending on last appearance
            if(len(dets) == 0):

                count += 1

                if(count > 1):
                    count = 0


                    if(right_tag == 1):
                        x_motion = 1

                        motion_data = str(x_motion) + str(y_motion)
                        # print(motion_data)
                        motion_data = bytes(motion_data, encoding = "utf8")
                        ser.write(motion_data)
                        
                    elif(left_tag == 1):
                        x_motion = 2

                        motion_data = str(x_motion) + str(y_motion)
                        # print(motion_data)
                        motion_data = bytes(motion_data, encoding = "utf8")
                        ser.write(motion_data) 

            else:

                distance = []
                axis = []
                area = []
                face = []

                renew_edge_count += 1

                #print("Number of faces detected: {}".format(len(dets)))
                for i, d in enumerate(dets):

                    if(init_former == 1):
                        former_pos_x = 0.5*( d.left() + d.right() )
                        former_pos_y = 0.5*( d.top() + d.bottom() )
                        init_former = 0
                        former_facearea = math.pow((d.right()-d.left())*(d.top()-d.bottom()),2)

                    right_tag = 0
                    left_tag = 0
                    #print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                        #i, d.left(), d.top(), d.right(), d.bottom()))
                    axis_x = 0.5*( d.left() + d.right() )
                    axis_y = 0.5*( d.top() + d.bottom() )

                    axis.append([axis_x,axis_y])
                    face.append([d.left(), d.right(), d.top(), d.bottom()])

                    # print('x:',axis_x, '    y:', axis_y)

                    dis = math.sqrt(math.pow(former_pos_x - axis_x , 2) + math.pow(former_pos_y - axis_y , 2))
                    distance.append(dis)

                    ar = math.pow(math.pow((d.right()-d.left())*(d.top()-d.bottom()),2)-former_facearea,2)
                    area.append(ar)



                if(area.index(min(area))==distance.index(min(distance))):
                    axis_x = axis[distance.index(min(distance))][0]
                    axis_y = axis[distance.index(min(distance))][1]

                    former_pos_x = axis_x
                    former_pos_y = axis_y

                    if(renew_edge_count == 3):
                        renew_edge_count = 0
                        face_pos = face[distance.index(min(distance))]
                        detect_area = get_detect_area(face_pos, width, height)                     


                if(axis_x > (0.5*width + width*bias_x)):
                    x_motion = 1
                    right_tag = 1
                elif(axis_x < (0.5*width - width*bias_x)):
                    x_motion = 2
                    left_tag = 1

                if(axis_y > (0.5*height + height*bias_y)):
                    y_motion = 1
                elif(axis_y < (0.5*height - height*bias_y)):
                    y_motion = 2

                motion_data = str(x_motion) + str(y_motion)
                # print(motion_data)
                motion_data = bytes(motion_data, encoding = "utf8")
                ser.write(motion_data) 

                # shape = sp(img, d)
                # face_descriptor = facerec.compute_face_descriptor(img, shape,1)

        win.clear_overlay()
        # win.add_overlay(dets)




    win.set_image(img)



cap.release()