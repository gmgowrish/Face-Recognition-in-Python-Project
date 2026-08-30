from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk  # pip install pillow
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk  # pip install pillow
from tkinter import messagebox
import mysql.connector
import re
import pyttsx3
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


def main():
    win = Tk()
    app = login_window(win)
    win.mainloop()


class login_window:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1552x840+0+0")

        # text_to-speech
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", self.voices[1].id)  # male 1 ,female 0

        img3 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\forest-1920.jpg')
        img3 = img3.resize((1552, 840), Image.ANTIALIAS)
        self.photoimg3 = ImageTk.PhotoImage(img3)

        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=0, width=1552, height=840)

        frame = Frame(self.root, bg="black")
        frame.place(x=610, y=170, width=340, height=450)

        img1 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\locked.png')
        img1 = img1.resize((100, 100), Image.ANTIALIAS)
        self.photoimg1 = ImageTk.PhotoImage(img1)

        img1 = Label(image=self.photoimg1, bg="black", borderwidth=0)
        img1.place(x=730, y=175, width=100, height=100)

        get_str = Label(frame, text="Get Started", font=("times new roman", 20, "bold"), fg="white", bg="black")
        get_str.place(x=95, y=100)

        # labels

        username = lbl = Label(frame, text="Username", font=("times new roman", 14, "bold"), fg="white", bg="black")
        username.place(x=70, y=155)

        self.txtuser = ttk.Entry(frame, font=("times new roman", 14, "bold"))
        self.txtuser.place(x=40, y=180, width=270)
        password = lbl = Label(frame, text="Password", font=("times new roman", 14, "bold"), fg="white", bg="black")
        password.place(x=70, y=225)

        self.txtpass = ttk.Entry(frame, font=("times new roman", 14, "bold"))
        self.txtpass.place(x=40, y=250, width=270)

        # ++++ icon images++++++

        img2 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\icons8-24.png')
        img2 = img2.resize((25, 25), Image.ANTIALIAS)
        self.photoimg2 = ImageTk.PhotoImage(img2)

        img2 = Label(image=self.photoimg2, bg="black", borderwidth=0)
        img2.place(x=650, y=323, width=25, height=25)
        # loblolly
        img4 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\icons8-64.png')
        img4 = img4.resize((25, 25), Image.ANTIALIAS)
        self.photoimg4 = ImageTk.PhotoImage(img4)

        img4 = Label(image=self.photoimg4, bg="black", borderwidth=0)
        img4.place(x=650, y=395, width=25, height=25)
        # login button
        loginbtn = Button(frame, command=self.login, text="Login", cursor="man", font=("times new roman", 14, "bold"),
                          bd=3,
                          relief=RIDGE, fg="white",
                          bg="red", activeforeground="white", activebackground="red")
        loginbtn.place(x=110, y=300, width=120, height=35)
        # Register button
        registerbtn = Button(frame, text="New User Register", command=self.rigister_window,
                             font=("times new roman", 10, "bold"), cursor="hand2", borderwidth=0,
                             fg="white",
                             bg="black", activeforeground="white", activebackground="black")
        registerbtn.place(x=15, y=350, width=160, height=35)
        # Forgetpassbutton
        registerbtn = Button(frame, text="Forget password", command=self.forget_password_window,
                             font=("times new roman", 10, "bold"), cursor="heart",
                             borderwidth=0,
                             fg="white",
                             bg="black", activeforeground="white", activebackground="black")
        registerbtn.place(x=10, y=380, width=160, )

    def rigister_window(self):
        self.new_window = Toplevel(self.root)
        self.app = Register(self.new_window)

    def login(self):
        if self.txtuser.get() == "" or self.txtpass.get() == "":
            messagebox.showerror("Error", "All field required")
        elif self.txtuser.get() == "kapu" and self.txtpass.get() == "ashu":
            messagebox.showinfo("success", "Welcome to code with ")
        else:
            conn = mysql.connector.connect(host="localhost", user="root", password="gmg70199",
                                           database=" register ")
            cur = conn.cursor()
            cur.execute("select * from ` register1` WHERE   ` email` = %s and  ` password`=%s", (

                self.txtuser.get(),
                self.txtpass.get()

            ))
            row = cur.fetchone()
            if row is None:
                self.engine.say("Invalid user name and password")
                self.engine.runAndWait()
                messagebox.showerror("Error", "Invalid user name and password")
            else:
                self.engine.say("Action only admin")
                self.engine.runAndWait()
                open_main = messagebox.askyesno("yes no", "Action only admin")
                if open_main > 0:
                    self.new_window = Toplevel(self.root)
                    self.app = face_recognition_system(self.new_window)
                else:
                    if not open_main:
                        return
            conn.commit()
            conn.close()
            # cursor = connection.cursor()

    # ===================================reset password=================
    def reset_pass(self):
        if self.comb_security_q.get() == "Select":
            messagebox.showerror("Error", "Select security question", parent=self.root2)
        elif self.security_a_entry.get() == "":
            messagebox.showerror("Error", "please enter the security answer", parent=self.root2)
        elif self.txt_newpass.get() == "":
            messagebox.showerror("Error", "please enter the new password", parent=self.root2)
        else:
            try:

                conn = mysql.connector.connect(host="localhost", user="root", password="gmg70199",
                                               database=" register ")
                cur = conn.cursor(buffered=True)
                qury = "select * from ` register1` WHERE   ` email` = %s and ` securityq`=%s and ` securitya`=%s "
                vlaue = (self.txtuser.get(), self.comb_security_q.get(), self.security_a_entry.get())
                cur.execute(qury, vlaue)
                row = cur.fetchone()
                if row is None:
                    messagebox.showerror("Error", "Please enter correct Answer", parent=self.root2)
                else:
                    # cur = conn.cur(buffered=True)
                    cur.execute("update ` register1` set ` password`=%s where ` email` = %s",
                                (self.txt_newpass.get(), self.txtuser.get()))

                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Info", "Your password has been rest,Please login new password",
                                        parent=self.root2)
                    self.reset()
                    self.root2.destroy()
            except Exception as es:
                messagebox.showerror("Error", f"Due To :{str(es)}", parent=self.root2)

    # ========================reset===============
    def reset(self):
        self.comb_security_q.current(0)
        self.txt_newpass.delete(0, END)
        self.txtuser.delete(0, END)
        self.security_a_entry.delete(0, END)
        self.txtpass.delete(0, END)

    # ==========================forget password===========================
    def forget_password_window(self):
        if self.txtuser.get() == "":
            messagebox.showerror("Error", "Place enter the Email to reset password")
        else:
            conn = mysql.connector.connect(host="localhost", user="root", password="gmg70199",
                                           database=" register ")
            cur = conn.cursor()
            query = "select * from ` register1` WHERE   ` email` = %s"
            value = (self.txtuser.get(),)
            cur.execute(query, value)
            row = cur.fetchone()
            # print(row)

            if row is None:
                messagebox.showerror("Error", "Please enter the valid user name")
            else:
                conn.close()
                self.root2 = Toplevel()
                self.root2.title("Forget Password")
                self.root2.geometry("340x450+610+170")
                self.root2.focus_force()
                self.root2.grab_set()
                l = Label(self.root2, text="Forget Password", font=("times new roman", 20, "bold"), fg="yellow",
                          bg="black")
                l.place(x=0, y=10, relwidth=1)
                security_q = Label(self.root2, text="Select Security Questions", font=("times new roman", 12),
                                   fg="black")
                security_q.place(x=50, y=80)

                self.comb_security_q = ttk.Combobox(self.root2,
                                                    font=("times new roman", 12), state="readonly", justify=CENTER)
                self.comb_security_q["values"] = ("Select", "Your Birth Place", "Your Girlfriend Name", "Your pet Name")
                self.comb_security_q.place(x=50, y=110, width=250)
                self.comb_security_q.current(0)

                security_a = Label(self.root2, text="Security Answer", font=("times new roman", 12),
                                   fg="black")
                security_a.place(x=50, y=150)

                self.security_a_entry = ttk.Entry(self.root2, font=("times new roman", 12))
                self.security_a_entry.place(x=50, y=180, width=250)
                # ________________________________________
                new_password1 = Label(self.root2, text="New Password", font=("times new roman", 12),
                                      fg="black")
                new_password1.place(x=50, y=220)

                self.txt_newpass = ttk.Entry(self.root2, font=("times new roman", 12))
                self.txt_newpass.place(x=50, y=250, width=250)

                btn = Button(self.root2, text="Reset Password", command=self.reset_pass, font=("times new roman", 12),
                             fg="yellow", bg="black")
                btn.place(x=110, y=320)


class Register:
    def __init__(self, root):
        self.root = root
        self.root.title("Register")
        self.root.geometry("1552x840+0+0")

        # text_to-speech
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", self.voices[0].id)  # male 1 ,female 0

        # ==================variables===============

        self.var_fname = StringVar()
        self.var_lname = StringVar()
        self.var_contact = StringVar()
        self.var_email = StringVar()
        self.var_securityq = StringVar()
        self.var_securitya = StringVar()
        self.var_pass = StringVar()
        self.var_confpass = StringVar()

        img3 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\register1.jpg')
        img3 = img3.resize((1552, 840), Image.ANTIALIAS)
        self.photoimg3 = ImageTk.PhotoImage(img3)

        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=0, width=1552, height=840)
        # left image
        img5 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\istockphoto.jpg')
        img5 = img5.resize((470, 550), Image.ANTIALIAS)
        self.photoimg5 = ImageTk.PhotoImage(img5)

        img5 = Label(self.root, image=self.photoimg5)
        img5.place(x=100, y=100, width=470, height=550)
        # ========= main frame =========
        frame = Frame(self.root)
        frame.place(x=570, y=100, width=800, height=550)

        register_lbl = Label(frame, text="REGISTER HERE", font=("times new roman", 20, "bold"), fg="black"
                             )
        register_lbl.place(x=20, y=20)

        # ========labels and entry ============

        # --------------------- row 1
        fname = Label(frame, text="First Name", font=("times new roman", 12), fg="black")
        fname.place(x=50, y=100)
        fname_entry = ttk.Entry(frame, textvariable=self.var_fname, font=("times new roman", 12))
        fname_entry.place(x=50, y=130, width=250)

        # callback and validation register
        validate_name = self.root.register(self.checkname)
        fname_entry.config(validate="key", validatecommand=(validate_name, "%P"))

        lname = Label(frame, text="Last Name", font=("times new roman", 12), fg="black")
        lname.place(x=370, y=100)

        lname_entry = ttk.Entry(frame, textvariable=self.var_lname, font=("times new roman", 12))
        lname_entry.place(x=370, y=130, width=250)
        # -------------row 2
        contact = Label(frame, text="Contact No", font=("times new roman", 12), fg="black")
        contact.place(x=50, y=170)

        contact_entry = ttk.Entry(frame, textvariable=self.var_contact, font=("times new roman", 12))
        contact_entry.place(x=50, y=200, width=250)

        # callback and validation register
        validate_contact = self.root.register(self.checkcontact)
        contact_entry.config(validate="key", validatecommand=(validate_contact, "%P"))

        email = Label(frame, text="Email", font=("times new roman", 12), fg="black")
        email.place(x=370, y=170)

        email_entry = ttk.Entry(frame, textvariable=self.var_email, font=("times new roman", 12))
        email_entry.place(x=370, y=200, width=250)

        # callback and validation register
        validate_email = self.root.register(self.checkemail)
        email_entry.config(validate="key", validatecommand=(validate_email, "%P"))

        # -------------row 3
        security_q = Label(frame, text="Select Security Questions", font=("times new roman", 12),
                           fg="black")
        security_q.place(x=50, y=240)
        self.comb_security_q = ttk.Combobox(frame, textvariable=self.var_securityq,
                                            font=("times new roman", 12), state="readonly", justify=CENTER)
        self.comb_security_q["values"] = ("Select", "Your Birth Place", "Your Girlfriend Name", "Your pet Name")
        self.comb_security_q.place(x=50, y=270, width=250)
        self.comb_security_q.current(0)

        security_a = Label(frame, text="Security Answer", font=("times new roman", 12),
                           fg="black")
        security_a.place(x=370, y=240)

        security_a_entry = ttk.Entry(frame, textvariable=self.var_securitya, font=("times new roman", 12))
        security_a_entry.place(x=370, y=270, width=250)

        validate_name = self.root.register(self.checkname)
        security_a_entry.config(validate="key", validatecommand=(validate_name, "%P"))

        # -----------------row4

        pswd = Label(frame, text="Password", font=("times new roman", 12), fg="black")
        pswd.place(x=50, y=310)

        txt_pswd = ttk.Entry(frame, textvariable=self.var_pass, font=("times new roman", 12))
        txt_pswd.place(x=50, y=340, width=250)

        validate_password = self.root.register(self.checkpassword)
        txt_pswd.config(validate="key", validatecommand=(validate_password, "%P"))

        confirm_pswd = Label(frame, text="Confirm Password", font=("times new roman", 12),
                             fg="black")
        confirm_pswd.place(x=370, y=310)

        txt_confirm_pswd = ttk.Entry(frame, textvariable=self.var_confpass, font=("times new roman", 12))
        txt_confirm_pswd.place(x=370, y=340, width=250)

        # ======================================checkbutton
        self.var_check = IntVar()
        checkbtn = Checkbutton(frame, variable=self.var_check, text="I Agree The Terms & Condition ",
                               font=("times new roman", 12),
                               fg="black", onvalue=1, offvalue=0)
        checkbtn.place(x=50, y=380)

        self.check_lbl = Label(frame, text="", font=("arial", 12), fg="red")
        self.check_lbl.place(x="220", y="410")

        # ======================== button++++++++++++++++++++++++++++++++

        b1 = Button(frame, text="Registration Now->", command=self.validation, font=("times new roman", 15, "bold"),
                    bg="blue", fg="white", bd=0, cursor="hand2")
        b1.place(x=50, y=450, width=200)

        b2 = Button(frame, text="Sign Up", command=self.return_login, font=("times new roman", 15, "bold"), bg="blue",
                    fg="white", bd=0,
                    cursor="hand2")
        b2.place(x=420, y=450, width=150)

    # call back function

    def checkname(self, name):
        if name.isalnum():
            return True
        if name == "":
            return True
        else:
            self.engine.say("NOt Allowed" + name[-1])
            self.engine.runAndWait()
            messagebox.showwarning("Invalid", "NOt Allowed" + name[-1])
            return False

    # check contact

    def checkcontact(self, contact):
        if contact.isdigit():
            return True
        if len(str(contact)) == 0:
            return True
        else:
            self.engine.say("Invalid Entry")
            self.engine.runAndWait()
            messagebox.showerror("Invalid", "Invalid Entry")
            return False

    # check password
    # pattern = r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z](?=.*[^a-bA-B0-9]))"

    def checkpassword(self, password):

        if len(password) <= 5:
            if re.match(r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z](?=.*[^a-bA-B0-9]))", password) is None:
                return True
            else:
                self.engine.say("Enter valid password (eg:Name%123) ")
                self.engine.runAndWait()
                messagebox.showwarning("Invalid", "Enter valid password (eg:Name%123)")
                return False
        else:
            self.engine.say("Length try to exceed")
            self.engine.runAndWait()
            messagebox.showerror("Invalid", "Length try to exceed")
            return False

    # check email
    # pattern = r'\b[A-Za-z0-9._%+-]+-\_\.@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    def checkemail(self, email):

        if len(email) <= 20:
            if re.match(r'\b[A-Za-z0-9._%+-]+-\_\.@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email) is None:
                return True
            else:
                self.engine.say("Invalid email enter valid user email (eg:Name1234@gmail.com)")
                self.engine.runAndWait()
                messagebox.showerror("Alert", "Invalid email enter valid user email (eg:Name1234@gmail.com)")
                return False
        else:
            self.engine.say(" email length is exceed ")
            self.engine.runAndWait()
            messagebox.showerror("Invalid", "email length is exceed")
            return False

    # validation

    def validation(self):
        x = y = 0
        if self.var_fname.get() == '':
            self.engine.say("Please Enter Your First Name")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Your First Name ", parent=self.root)

        elif self.var_lname.get() == '':
            self.engine.say("Please Enter Your Last Name")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Your Last Name ", parent=self.root)

        elif self.var_contact.get() == '' or len(self.var_contact.get()) != 10:
            self.engine.say("Please Enter Your 10 digits Contact number")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Your 10 digits Contact no. ", parent=self.root)

        elif self.var_email.get() == '':
            self.engine.say("Please Enter Your Email")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Your Email ", parent=self.root)

        elif self.var_securityq.get() == 'Select your Question':
            self.engine.say("Please Select your Question ")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Select your Question ", parent=self.root)

        elif self.var_securitya.get() == '':
            self.engine.say("Please Enter Security Answer ")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Security Answer ", parent=self.root)

        elif self.var_pass.get() == '':
            self.engine.say("Please Enter Your password ")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Your password ", parent=self.root)

        elif self.var_confpass.get() == '':
            self.engine.say("Please Enter Your confirm password")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Please Enter Your confirm password ", parent=self.root)
        elif self.var_pass.get() != self.var_confpass.get():
            self.engine.say("Password & confirm password must be same")
            self.engine.runAndWait()
            messagebox.showerror("Error", "Password & confirm password must be same", parent=self.root)
        elif self.var_email.get() is not None and self.var_pass.get() is not None:
            x = self.checkemail(self.var_email.get())
            y = self.checkpassword(self.var_pass.get())
        if (x == True) and (y == True):
            if self.var_check.get() == 0:
                self.engine.say("Please Agree our term and condition")
                self.engine.runAndWait()
                self.check_lbl.config(text="(*>﹏<*) Please Agree Our Term & Condition (*>﹏<*)", fg="red")
            # ===================== function declaration ===========

            else:

                try:
                    conn = mysql.connector.connect(host="localhost", user="root", password="gmg70199",
                                                   database=" register ")
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM ` register1` WHERE   ` email` = %s", (self.var_email.get(),))
                    row = cur.fetchone()
                    print(row)
                    if row is not None:
                        self.engine.say("email already exist")
                        self.engine.runAndWait()
                        messagebox.showerror("Error", "Email Already Exist", parent=self.root)
                    cur.execute(
                        "insert into ` register1` values(%s,%s,%s,%s,%s,%s,%s)",
                        (
                            self.var_fname.get(),
                            self.var_lname.get(),
                            self.var_contact.get(),
                            self.var_email.get(),
                            self.var_securityq.get(),
                            self.var_securitya.get(),
                            self.var_pass.get()

                        ))
                    conn.commit()
                    conn.close()
                    self.engine.say(
                        f"Checked Register Successful username:{self.var_fname.get()} and password:{self.var_pass.get()}")
                    self.engine.runAndWait()
                    self.check_lbl.config(text="(❁´◡`❁) CHECKED (❁´◡`❁)", fg="green")
                    messagebox.showinfo("Success",
                                        f"Register Successful username:{self.var_fname.get()} and password:{self.var_pass.get()} ",
                                        parent=self.root)
                except Exception as es:
                    messagebox.showerror("Error", f"Due To :{str(es)}", parent=self.root)

    def return_login(self):
        self.root.destroy()


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
    main()
