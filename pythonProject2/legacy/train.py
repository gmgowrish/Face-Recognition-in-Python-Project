import os
import tkinter
from tkinter import *
from tkinter import messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk


class Train:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x850+0+0")
        self.root.title("Face Recognition system")

        title_lbl = Label(self.root, text="TRAIN DATA SET ",
                          font=("times new roman", 35, "bold"), bg="blue", fg="yellow")
        title_lbl.place(x=0, y=0, width=1530, height=45)

        img_top = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\trainbg.jpg')
        img_top = img_top.resize((1530, 850), Image.ANTIALIAS)
        self.photoimg_top = ImageTk.PhotoImage(img_top)

        f_lbl = Label(self.root, image=self.photoimg_top)
        f_lbl.place(x=0, y=45, width=1530, height=850)
        # button
        b1_1 = Button(self.root, text="TRAIN DATA", command=self.train_classifier, cursor="hand2",
                      font=("times new roman", 30, "bold"), bg="black",
                      fg="orange")
        b1_1.place(x=500, y=370, width=530, height=70)

    def train_classifier(self):
        data_dir = "data"
        path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]

        faces = []
        ids = []
        for image in path:
            img = Image.open(image).convert("L")  # Gray scale image
            imageNp = np.array(img, 'uint8')
            id = int(os.path.split(image)[1].split('.')[1])

            faces.append(imageNp)
            ids.append(id)
            cv2.imshow("TRAINING", imageNp)
            cv2.waitKey(1) == 13
        ids = np.array(ids)

        # ++++++++++++++++++ TRAIN THE CLASSIFIER AND SAVE++++++++++++++
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces, ids)
        clf.write("classifier.xml")
        cv2.destroyAllWindows()
        messagebox.showinfo("Result", "Training Datasets completed", parent=self.root)


if __name__ == "__main__":
    root = tkinter.Tk()
    obj = Train(root)
    root.mainloop()
