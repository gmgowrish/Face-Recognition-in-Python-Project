import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import cv2
import mysql.connector
from PIL import Image, ImageTk
import os
import csv
from tkinter import filedialog

mydata = []


class attendance:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x850+0+0")
        self.root.title("Face Recognition system")
        # ++++++++++ variables ++++++++
        self.var_atten_id = StringVar()
        self.var_atten_roll = StringVar()
        self.var_atten_name = StringVar()
        self.var_atten_dep = StringVar()
        self.var_atten_time = StringVar()
        self.var_atten_date = StringVar()
        self.var_atten_attendance = StringVar()

        # first image
        img = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\attenadance-management2.png')
        img = img.resize((800, 200), Image.ANTIALIAS)
        self.photoimg = ImageTk.PhotoImage(img)

        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=0, width=800, height=200)
        # second image

        img1 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\Attendance-management1.jpg')
        img1 = img1.resize((800, 200), Image.ANTIALIAS)
        self.photoimg1 = ImageTk.PhotoImage(img1)

        f_lbl = Label(self.root, image=self.photoimg1)
        f_lbl.place(x=800, y=0, width=800, height=200)

        img3 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\bgimg3.jpg')
        img3 = img3.resize((1530, 700), Image.ANTIALIAS)
        self.photoimg3 = ImageTk.PhotoImage(img3)

        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=200, width=1530, height=640)

        title_lbl = Label(bg_img, text="ATTENDANCE MANAGEMENT SYSTEM",
                          font=("times new roman", 35, "bold"), bg="silver", fg="black")
        title_lbl.place(x=0, y=0, width=1530, height=50)

        main_frame = Frame(bg_img, bd=2)
        main_frame.place(x=10, y=55, width=1510, height=580)
        # left frame
        left_frame = LabelFrame(main_frame, bd=2, relief=RIDGE, text=" Student Attendance Details",
                                font=("times new roman", 19, "bold"))
        left_frame.place(x=10, y=0, width=730, height=560)

        img_left = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\su1.jpeg')
        img_left = img_left.resize((720, 130), Image.ANTIALIAS)
        self.photoimg_left = ImageTk.PhotoImage(img_left)

        f_lbl = Label(left_frame, image=self.photoimg_left)
        f_lbl.place(x=5, y=0, width=720, height=130)

        left_inside_frame = Frame(left_frame, relief=RIDGE, bd=2)
        left_inside_frame.place(x=3, y=135, width=720, height=390)

        # labels or entries
        # attendance id
        attendance_id_label = Label(left_inside_frame, text="AttendanceID:", font=("times new roman", 12, "bold"),
                                    bg="white")
        attendance_id_label.grid(row=0, column=0, padx=4, pady=8, sticky=W)

        attendance_id_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_id,
                                        font=("times new roman", 12, "bold"))
        attendance_id_entry.grid(row=0, column=1, padx=4, pady=8, sticky=W)

        # roll
        roll_label = Label(left_inside_frame, text="Roll:", font=("times new roman", 12, "bold"),
                           bg="white")
        roll_label.grid(row=0, column=2, padx=4, pady=8, sticky=W)

        roll_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_roll,
                               font=("times new roman", 12, "bold"))
        roll_entry.grid(row=0, column=3, padx=4, pady=8, sticky=W)

        #  name
        name_label = Label(left_inside_frame, text="Name:", font=("times new roman", 12, "bold"),
                           bg="white")
        name_label.grid(row=1, column=0, padx=4, pady=8, sticky=W)

        name_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_name,
                               font=("times new roman", 12, "bold"))
        name_entry.grid(row=1, column=1, padx=4, pady=8, sticky=W)

        #  Department
        dep_label = Label(left_inside_frame, text="Department:", font=("times new roman", 12, "bold"),
                          bg="white")
        dep_label.grid(row=1, column=2, padx=4, pady=8, sticky=W)

        dep_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_dep,
                              font=("times new roman", 12, "bold"))
        dep_entry.grid(row=1, column=3, padx=4, pady=8, sticky=W)

        #  time
        time_label = Label(left_inside_frame, text="Time:", font=("times new roman", 12, "bold"),
                           bg="white")
        time_label.grid(row=2, column=0, padx=4, pady=8, sticky=W)

        time_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_time,
                               font=("times new roman", 12, "bold"))
        time_entry.grid(row=2, column=1, padx=4, pady=8, sticky=W)

        #  date
        date_label = Label(left_inside_frame, text="Date:", font=("times new roman", 12, "bold"),
                           bg="white")
        date_label.grid(row=2, column=2, padx=4, pady=8, sticky=W)

        date_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_date,
                               font=("times new roman", 12, "bold"))
        date_entry.grid(row=2, column=3, padx=4, pady=8, sticky=W)

        #  attendance
        attendance_label = Label(left_inside_frame, text="Attendance:", font=("times new roman", 12, "bold"),
                                 bg="white")
        attendance_label.grid(row=3, column=0, padx=4, pady=8, sticky=W)
        attendance_entry = ttk.Entry(left_inside_frame, width=20, textvariable=self.var_atten_attendance,
                                     font=("times new roman", 12, "bold"))
        attendance_entry.grid(row=3, column=1, padx=4, pady=8, sticky=W)

        # buttons frame
        btn_frame = Frame(left_inside_frame, bd=2, relief=RIDGE, bg="white")
        btn_frame.place(x=0, y=350, width=715, height=35)
        #  import csv
        save_btn = Button(btn_frame, text="Import csv", command=self.ImportCsv, width=25,
                          font=("times new roman", 12, "bold"),
                          bg="blue", fg="white")
        save_btn.grid(row=0, column=0)
        # export csv
        update_btn = Button(btn_frame, text="Export csv", command=self.exportCsv, width=25,
                            font=("times new roman", 12, "bold"), bg="blue",
                            fg="white")
        update_btn.grid(row=0, column=1)

        # reset
        reset_btn = Button(btn_frame, text="Reset", width=28,command=self.reset_data,
                           font=("times new roman", 12, "bold"), bg="blue",
                           fg="white")
        reset_btn.grid(row=0, column=3)

        # right frame
        Right_frame = LabelFrame(main_frame, bd=2, relief=RIDGE, text="Attendance  Details",
                                 font=("times new roman", 19, "bold"))
        Right_frame.place(x=780, y=0, width=710, height=560)
        table_frame = Frame(Right_frame, bd=2, relief=RIDGE, bg="white")
        table_frame.place(x=5, y=5, width=700, height=445)

        # ========================scroll bar table===============
        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)

        self.AttendanceReportTable = ttk.Treeview(table_frame, columns=(
            "id", "roll", "name", "department", "time", "date", "attendance"), xscrollcommand=scroll_x.set,
                                                  yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)

        scroll_x.config(command=self.AttendanceReportTable.xview)
        scroll_y.config(command=self.AttendanceReportTable.yview)

        self.AttendanceReportTable.heading("id", text="Attendance ID")
        self.AttendanceReportTable.heading("roll", text="Roll")
        self.AttendanceReportTable.heading("name", text="Name")
        self.AttendanceReportTable.heading("department", text="Department")
        self.AttendanceReportTable.heading("time", text="Time")
        self.AttendanceReportTable.heading("date", text="Date")
        self.AttendanceReportTable.heading("attendance", text="Attendance")

        self.AttendanceReportTable["show"] = "headings"
        self.AttendanceReportTable.column("id", width=100)
        self.AttendanceReportTable.column("roll", width=100)
        self.AttendanceReportTable.column("name", width=100)
        self.AttendanceReportTable.column("department", width=100)
        self.AttendanceReportTable.column("time", width=100)
        self.AttendanceReportTable.column("date", width=100)
        self.AttendanceReportTable.column("attendance", width=100)

        self.AttendanceReportTable.pack(fill=BOTH, expand=1)

        self.AttendanceReportTable.bind("<ButtonRelease>", self.get_cursor)

    # ++++++++++++++++++++++++++++++++++++ fetch data +++++++++++++++++++++++++++++++++++
    def fetch_data(self, rows):
        self.AttendanceReportTable.delete(*self.AttendanceReportTable.get_children())
        for i in rows:
            self.AttendanceReportTable.insert("", END, values=i)

    # import csv
    def ImportCsv(self):
        global mydata
        mydata.clear()
        fln = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open CSV",
                                         filetypes=(("CSV File", "*csv"), ("All File", "*.*")), parent=self.root)
        with open(fln) as myfile:
            csvread = csv.reader(myfile, delimiter=",")
            for i in csvread:
                mydata.append(i)
            self.fetch_data(mydata)

    # export csv
    def exportCsv(self):
        try:
            if len(mydata) < 1:
                messagebox.showerror("No Data", "No Data found to export", parent=self.root)
                return False
            fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Open CSV",
                                               filetypes=(("CSV File", "*csv"), ("All File", "*.*")), parent=self.root)
            with open(fln, mode="w", newline="") as myfile:
                exp_write = csv.writer(myfile, delimiter=",")
                for i in mydata:
                    exp_write.writerow(i)
                messagebox.showinfo("Data Export", "Your data exported to " + os.path.basename(fln) + "Successfully")
        except Exception as es:

            messagebox.showerror("Error", f"Due To:{str(es)}", parent=self.root)

    def get_cursor(self, event=""):
        cursor_row = self.AttendanceReportTable.focus()
        content = self.AttendanceReportTable.item(cursor_row)
        rows = content["values"]
        self.var_atten_id.set(rows[0])
        self.var_atten_roll.set(rows[1])
        self.var_atten_name.set(rows[2])
        self.var_atten_dep.set(rows[3])
        self.var_atten_time.set(rows[4])
        self.var_atten_date.set(rows[5])
        self.var_atten_attendance.set(rows[6])

    def reset_data(self):
        self.var_atten_id.set("")
        self.var_atten_roll.set("")
        self.var_atten_name.set("")
        self.var_atten_dep.set("")
        self.var_atten_time.set("")
        self.var_atten_date.set("")
        self.var_atten_attendance.set("")



if __name__ == "__main__":
    root = tkinter.Tk()
    obj = attendance(root)
    root.mainloop()
