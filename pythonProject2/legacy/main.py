import tkinter.messagebox
from tkinter import *
from tkinter import Tk
from PIL import Image, ImageTk
import os
import tkinter
from time import strftime
from datetime import datetime
from student import Student
from train import Train
from face_recognition import Face_recognition
from attendance import attendance
from developer import developer
from help import help1


class face_recognition_system:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition system")
        # first image
        img = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\facere.jpg')
        img = img.resize((765, 135), Image.ANTIALIAS)
        self.photoimg = ImageTk.PhotoImage(img)

        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=0, width=765, height=135)
        # second image

        img1 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\images (1).jpeg')
        img1 = img1.resize((765, 135), Image.ANTIALIAS)
        self.photoimg1 = ImageTk.PhotoImage(img1)

        f_lbl = Label(self.root, image=self.photoimg1)
        f_lbl.place(x=765, y=0, width=765, height=135)

        # bg image

        img3 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\bgimg3.jpg')
        img3 = img3.resize((1530, 710), Image.ANTIALIAS)
        self.photoimg3 = ImageTk.PhotoImage(img3)

        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=130, width=1530, height=710)

        title_lbl = Label(bg_img, text="FACE RECOGNITION ATTENDANCE SYSTEM SOFTWARE",
                          font=("times new roman", 35, "bold"), bg="royal blue", fg="yellow")
        title_lbl.place(x=0, y=0, width=1530, height=45)

        # ================= Time =====================
        def time():
            string = strftime("%H:%M:%S %p")
            lbl.config(text=string)
            lbl.after(1000, time)

        lbl = Label(title_lbl, font=('times new roman ', 12, 'bold'), background='royal blue', foreground='black')
        lbl.place(x=0, y=0, width=110, height=50)
        time()

        # student button
        img4 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\stu1.jpeg')
        img4 = img4.resize((220, 220), Image.ANTIALIAS)
        self.photoimg4 = ImageTk.PhotoImage(img4)

        b1 = Button(bg_img, image=self.photoimg4, command=self.student_details, cursor="hand2")
        b1.place(x=200, y=100, width=220, height=220)

        b1_1 = Button(bg_img, text="Student Details", command=self.student_details, cursor="hand2",
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=200, y=300, width=220, height=40)

        #  Detect face button
        img5 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\face_detectioniconicon.jpg')
        img5 = img5.resize((220, 220), Image.ANTIALIAS)
        self.photoimg5 = ImageTk.PhotoImage(img5)

        b1 = Button(bg_img, image=self.photoimg5, cursor="hand2", command=self.face_data)
        b1.place(x=500, y=100, width=220, height=220)

        b1_1 = Button(bg_img, text="Face Detector", cursor="hand2", command=self.face_data,
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=500, y=300, width=220, height=40)

        #  Attendance face button
        img6 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\attwnnfa.jpg')
        img6 = img6.resize((220, 220), Image.ANTIALIAS)
        self.photoimg6 = ImageTk.PhotoImage(img6)

        b1 = Button(bg_img, image=self.photoimg6, command=self.attendance_data, cursor="hand2")
        b1.place(x=800, y=100, width=220, height=220)

        b1_1 = Button(bg_img, text="Attendance", command=self.attendance_data, cursor="hand2",
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=800, y=300, width=220, height=40)

        #  Help Desk button
        img7 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\helpdesksoftware.png')
        img7 = img7.resize((220, 220), Image.ANTIALIAS)
        self.photoimg7 = ImageTk.PhotoImage(img7)

        b1 = Button(bg_img, image=self.photoimg7, cursor="hand2", command=self.help_data)
        b1.place(x=1100, y=100, width=220, height=220)

        b1_1 = Button(bg_img, text="Help Desk", cursor="hand2", command=self.help_data,
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=1100, y=300, width=220, height=40)

        #  Train face button
        img8 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\drivetrain_approach.jpg')
        img8 = img8.resize((220, 220), Image.ANTIALIAS)
        self.photoimg8 = ImageTk.PhotoImage(img8)

        b1 = Button(bg_img, image=self.photoimg8, cursor="hand2", command=self.train_data)
        b1.place(x=200, y=380, width=220, height=220)

        b1_1 = Button(bg_img, text="Train Data", cursor="hand2", command=self.train_data,
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=200, y=580, width=220, height=40)

        #   Photos face button
        img9 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\phots.jpg')
        img9 = img9.resize((220, 220), Image.ANTIALIAS)
        self.photoimg9 = ImageTk.PhotoImage(img9)

        b1 = Button(bg_img, image=self.photoimg9, cursor="hand2", command=self.open_img)
        b1.place(x=500, y=380, width=220, height=220)

        b1_1 = Button(bg_img, text="Photos", cursor="hand2", command=self.open_img,
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=500, y=580, width=220, height=40)

        #    Developer button
        img10 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\developer-programming-.jpg')
        img10 = img10.resize((220, 220), Image.ANTIALIAS)
        self.photoimg10 = ImageTk.PhotoImage(img10)

        b1 = Button(bg_img, image=self.photoimg10, cursor="hand2", command=self.developer_data, )
        b1.place(x=800, y=380, width=220, height=220)

        b1_1 = Button(bg_img, text="Developer", cursor="hand2", command=self.developer_data,
                      font=("times new roman", 15, "bold"), bg="purple",
                      fg="white")
        b1_1.place(x=800, y=580, width=220, height=40)

        #    exit-button
        img11 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\exit1.jpg')
        img11 = img11.resize((220, 220), Image.ANTIALIAS)
        self.photoimg11 = ImageTk.PhotoImage(img11)

        b1 = Button(bg_img, image=self.photoimg11, command=self.iExit, cursor="hand2")
        b1.place(x=1100, y=380, width=220, height=220)

        b1_1 = Button(bg_img, text=" Exit", cursor="hand2", command=self.iExit, font=("times new roman", 15, "bold"),
                      bg="purple",
                      fg="white")
        b1_1.place(x=1100, y=580, width=220, height=40)

    def open_img(self):
        os.startfile("data")

    # exit button
    def iExit(self):
        self.iExit = tkinter.messagebox.askyesno(" FAce Recognition", "Are you sure exit this project",
                                                 parent=self.root)
        if self.iExit > 0:
            self.root.destroy()
        else:
            return

            # ******************* function ***************

    def student_details(self):
        self.new_window = Toplevel(self.root)
        self.app = Student(self.new_window)

    def train_data(self):
        self.new_window = Toplevel(self.root)
        self.app = Train(self.new_window)

    def face_data(self):
        self.new_window = Toplevel(self.root)
        self.app = Face_recognition(self.new_window)

    def attendance_data(self):
        self.new_window = Toplevel(self.root)
        self.app = attendance(self.new_window)

    def developer_data(self):
        self.new_window = Toplevel(self.root)
        self.app = developer(self.new_window)

    def help_data(self):
        self.new_window = Toplevel(self.root)
        self.app = help1(self.new_window)


if __name__ == "__main__":
    root: Tk = Tk()
    obj = face_recognition_system(root)
    root.mainloop()
