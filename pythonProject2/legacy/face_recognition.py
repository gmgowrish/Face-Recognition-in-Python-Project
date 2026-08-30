from tkinter import *

import cv2
import mysql.connector
from time import strftime
from datetime import datetime
from PIL import Image, ImageTk


class Face_recognition:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x850+0+0")
        self.root.title("Face Recognition system")

        img3 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\bg1.jpg')
        img3 = img3.resize((1530, 850), Image.ANTIALIAS)
        self.photoimg3 = ImageTk.PhotoImage(img3)

        bg_img = Label(self.root, image=self.photoimg3)
        bg_img.place(x=0, y=0, width=1530, height=850)

        # first image
        img = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\face_s1.jpeg')
        img = img.resize((650, 830), Image.ANTIALIAS)
        self.photoimg = ImageTk.PhotoImage(img)

        f_lbl = Label(self.root, image=self.photoimg)
        f_lbl.place(x=0, y=0, width=650, height=830)
        # second image
        img2 = Image.open(r'C:\Users\gmg\PycharmProjects\pythonProject2\image\face_s2.jpeg')
        img2 = img2.resize((880, 830), Image.ANTIALIAS)
        self.photoimg2 = ImageTk.PhotoImage(img2)

        f_lbl = Label(self.root, image=self.photoimg2)
        f_lbl.place(x=650, y=0, width=880, height=830)

        b1_1 = Button(f_lbl, text="Face Recognition", command=self.face_recog, cursor="hand2",
                      font=("times new roman", 15, "bold"), bg="darkgreen",
                      fg="white")
        b1_1.place(x=340, y=740, width=200, height=40)

    # ==========================attendance==========================
    def mark_attendance(self, i, r, n, d):
        with open("gmg.csv", "r+", newline="") as f:
            myDataList = f.readlines()  # readline is not same to readlines
            name_list = []
            for line in myDataList:
                entry = line.split(",")
                name_list.append(entry[0])
            if (i not in name_list) and (r not in name_list) and (n not in name_list) and (d not in name_list):
                now = datetime.now()
                d1 = now.strftime("%d/%m/%Y")
                dtstring = now.strftime("%H:%M:%S")
                f.writelines(f"\n{i},{r},{n},{d},{dtstring},{d1},Present")

    # ++++++++++++++++++++++++++++++++++++++++===face recognition+++++++++++

    def face_recog(self):
        def draw_boundray(img, classifier, scaleFactor, minNeighbors, color, text, clf):
            gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)

            coord = []

            for (x, y, w, h) in features:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                id, predict = clf.predict(gray_image[y:y + h, x:x + w])
                confidence = int((100 * (1 - predict / 300)))

                conn = mysql.connector.connect(host="localhost", user="root", password="gmg70199",
                                               database=" face_recogizer")
                my_cursor = conn.cursor()

                my_cursor.execute("select Name from student where `Student id`=" + str(id))
                n = my_cursor.fetchone()
                n = "+".join(n)

                my_cursor.execute("select Roll from student where `Student id`=" + str(id))
                r = my_cursor.fetchone()
                r = "+".join(r)

                my_cursor.execute("select Dep from student where `Student id`= " + str(id))
                d = my_cursor.fetchone()
                d = "+".join(d)

                my_cursor.execute("select  `Student id` from student where `Student id`= " + str(id))
                i = my_cursor.fetchone()
                i = "+".join(i)

                if confidence > 77:
                    cv2.putText(img, f"ID:{i}", (x, y - 80), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                    cv2.putText(img, f"Roll:{r}", (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                    cv2.putText(img, f"Name:{n}", (x, y - 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)
                    cv2.putText(img, f"Department:{d}", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255),
                                3)
                    self.mark_attendance(i, r, n, d)
                else:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    cv2.putText(img, "Unknown Face ", (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255),
                                3)

                coord = [x, y, w, y]

            return coord

        def recognize(img, clf, faceCascade):
            coord = draw_boundray(img, faceCascade, 1.1, 10, (255, 25, 255), "Face", clf)
            return img

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")

        video_cap = cv2.VideoCapture(0)

        while True:
            ret, img = video_cap.read()
            img = recognize(img, clf, faceCascade)
            cv2.imshow("Welcome To face Recognition", img)

            if cv2.waitKey(1) == 13:
                break
        video_cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root: Tk = Tk()
    obj = Face_recognition(root)
    root.mainloop()
