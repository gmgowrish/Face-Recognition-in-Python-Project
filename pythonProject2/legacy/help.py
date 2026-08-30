import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

import cv2


class help1:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x850+0+0")
        self.root.title("Face Recognition system")

        title_lbl = Label(self.root, text="Help Desk",
                          font=("times new roman", 35, "bold"), bg="royal blue", fg="gold")
        title_lbl.place(x=0, y=0, width=1530, height=45)

        img = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\helpdesk.jpg')
        img = img.resize((1530, 770), Image.ANTIALIAS)
        self.photoimg = ImageTk.PhotoImage(img)

        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=55, width=1530, height=770)

        developer_label = Label(f_lbl, text="Email:gmggowrish70199@gmail.com", font=("times new roman", 18, "bold"),
                                fg="green", bg="black")
        developer_label.place(x=550, y=120)


if __name__ == "__main__":
    root = tkinter.Tk()
    obj = help1(root)
    root.mainloop()
