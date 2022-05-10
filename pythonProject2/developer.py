import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import cv2
import mysql.connector
from PIL import Image, ImageTk


class developer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x850+0+0")
        self.root.title("Face Recognition system")

        img_top = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\pexels-cátia-matos-1072179.jpg')
        img_top = img_top.resize((1530, 850), Image.ANTIALIAS)
        self.photoimg_top = ImageTk.PhotoImage(img_top)

        f_lbl = Label(self.root, image=self.photoimg_top)
        f_lbl.place(x=0, y=0, width=1530, height=850)

        title_lbl = Label(self.root, text="DEVELOPER ",
                          font=("times new roman", 35, "bold"), bg="green", fg="white")
        title_lbl.place(x=540, y=10, width=500, height=45)

        # frame

        main_frame = LabelFrame(f_lbl, bd=2, bg="black")
        main_frame.place(x=540, y=70, width=500, height=620)
        img_top1 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\profile2.jpg')
        img_top1 = img_top1.resize((550, 620), Image.ANTIALIAS)
        self.photoimg_top1 = ImageTk.PhotoImage(img_top1)

        f_lbl = Label(main_frame, image=self.photoimg_top1)
        f_lbl.place(x=0, y=0, width=550, height=620)

        # Developer info
        developer_label = Label(main_frame, text="Developed By : G M Gowrish ", font=("times new roman", 14, "bold"),
                                fg="white", bg="black")
        developer_label.place(x=130, y=550)

        developer_label = Label(main_frame, text="5th Sem BCA ", font=("times new roman", 14, "bold"),
                                fg="white", bg="black")
        developer_label.place(x=130, y=575)


if __name__ == "__main__":
    root = tkinter.Tk()
    obj = developer(root)
    root.mainloop()
