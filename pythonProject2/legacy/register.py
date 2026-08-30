from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk  # pip install pillow
from tkinter import messagebox
import mysql.connector
import re
import pyttsx3


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
        img1 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\istockphoto.jpg')
        img1 = img1.resize((470, 550), Image.ANTIALIAS)
        self.photoimg1 = ImageTk.PhotoImage(img1)

        img1 = Label(image=self.photoimg1)
        img1.place(x=100, y=100, width=470, height=550)
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

        b2 = Button(frame, text="Sign Up", font=("times new roman", 15, "bold"), bg="blue", fg="white", bd=0,
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
                self.check_lbl.config(text="`(*>﹏<*)′ Please Agree Our Term & Condition `(*>﹏<*)′", fg="red")
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
                        messagebox.showerror("Error", "Email Already Exist")
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


if __name__ == "__main__":
    root: Tk = Tk()
    obj = Register(root)
    root.mainloop()
