import csv
import hashlib
from tkinter import simpledialog, ttk
from tkinter.ttk import Combobox
import mysql.connector as MySQLdb
import cv2
import numpy as np
import face_recognition
import pickle
import os
from datetime import datetime as dt
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import datetime
from tkcalendar import DateEntry
from tkinter import Canvas
# Colors
BG_COLOR = "#F0F8FF"
FRAME_COLOR = "#34495e"
BUTTON_COLOR = "#007FFF"
BUTTON_HOVER_COLOR = "#d35400"
TEXT_COLOR = "black"
ENTRY_COLOR = "#bdc3c7"

# Fonts
TITLE_FONT = ("Arial", 18, "bold")
BUTTON_FONT = ("Arial", 12, "bold")
LABEL_FONT = ("Arial", 12)
FONT_FG = "#007FFF"
path = 'Training_images'
classNames = [] 
last_attendance_time = {}  

# MySQL database connection
db = MySQLdb.connect(
    host="localhost",
    user="root",
    password="root",
    database="sem6_project"
)
cursor = db.cursor()

# Create the student table
create_table_query = """
CREATE TABLE IF NOT EXISTS student (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    year VARCHAR(10) NOT NULL,
    branch VARCHAR(50) NOT NULL,
    division VARCHAR(10) NOT NULL,
    roll_no VARCHAR(10) NOT NULL 
)
"""
cursor.execute(create_table_query)


create_subject_table_query = """
CREATE TABLE IF NOT EXISTS subject (
    subject_id VARCHAR(50),
    subject_name VARCHAR(50) PRIMARY KEY
)
"""
cursor.execute(create_subject_table_query)



attendance_table_query = """
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20),
    student_name VARCHAR(50),
    date DATE,
    time TIME,
    subject_name VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (subject_name) REFERENCES subject(subject_name)
);
"""
cursor.execute(attendance_table_query)

create_user_table_query = """
CREATE TABLE IF NOT EXISTS user (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
)
"""
cursor.execute(create_user_table_query)

def generate_pkl():
    global encodeListKnown
    images = []
    myList = os.listdir(path)
    print(myList)

    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])  

    print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    encodeListKnown = findEncodings(images)
    print('Encoding Complete')

    with open('encoded_faces.pkl', 'wb') as file:
        pickle.dump(encodeListKnown, file)

    
try:
    with open('encoded_faces.pkl', 'rb') as file:
        model = pickle.load(file)
except FileNotFoundError:
    model = None

def add_new_student():
    add_student_window = Toplevel(root)
    add_student_window.title("Add New Student")
    add_student_window.minsize(400,300)
    add_student_window.config(bg=BG_COLOR)

    # Create entry fields for student details
    student_id_label = Label(add_student_window, text="Student ID:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_id_label.pack(pady=15)
    student_id_entry = Entry(add_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_id_entry.pack(pady=5)

    student_name_label = Label(add_student_window, text="Name:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_name_label.pack(pady=5)
    student_name_entry = Entry(add_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_name_entry.pack(pady=5)

    student_year_label = Label(add_student_window, text="Year:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_year_label.pack(pady=5)

    # Combobox for selecting the year
    year_combobox = Combobox(add_student_window, values=["FE", "SE", "TE", "BE"], font=LABEL_FONT)
    year_combobox.pack(pady=5)

    student_branch_label = Label(add_student_window, text="Branch:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_branch_label.pack(pady=5)

    # Combobox for selecting the branch
    branch_combobox = Combobox(add_student_window, values=["Computer", "IT", "AIDS"], font=LABEL_FONT)
    branch_combobox.pack(pady=5)

    student_div_label = Label(add_student_window, text="Division:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_div_label.pack(pady=5)
    student_div_entry = Entry(add_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_div_entry.pack(pady=5)

    student_roll_label = Label(add_student_window, text="Roll No.:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_roll_label.pack(pady=5)
    student_roll_entry = Entry(add_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_roll_entry.pack(pady=5)

    def save_student_details():
        student_id = student_id_entry.get()
        student_name = student_name_entry.get()
        student_year = year_combobox.get()
        student_branch = branch_combobox.get()  # Retrieve selected branch from combobox
        student_div = student_div_entry.get()
        student_roll = student_roll_entry.get()

        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
        if file_path:
            student_image = cv2.imread(file_path)
            file_name = os.path.join(path, f"{student_name}.jpg")
            cv2.imwrite(file_name, student_image)
            messagebox.showinfo("Success", f"Image for {student_name} saved successfully!")
            update_training_images()

            # Insert student details into the database
            insert_query = "INSERT INTO student (student_id, name, year, branch, division, roll_no) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (student_id, student_name, student_year, student_branch, student_div, student_roll)
            cursor.execute(insert_query, values)
            db.commit()

        add_student_window.destroy()

    save_button = Button(add_student_window, text="Save", command=save_student_details, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    save_button.pack(pady=10)

def update_training_images():
    global classNames
    classNames = []
    images = []
    myList = os.listdir(path)

    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    generate_pkl()

def update_attendance_csv(student_id, student_name, date, time, attendance_file):
    file_exists = os.path.exists(attendance_file)
    with open(attendance_file, 'a', newline='') as csvfile:
        fieldnames = ['Student ID', 'Student Name', 'Date', 'Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header only if the file doesn't exist
        if not file_exists:
            writer.writeheader()

        # Write the attendance data
        writer.writerow({'Student ID': student_id, 'Student Name': student_name, 'Date': date, 'Time': time})


def mark_attendance(name, classNames, subject_name):
    global last_attendance_time
    now = dt.now()
    dtString = now.strftime('%Y-%m-%d %H:%M:%S')
    name_key = name.lower()  # Use lowercase name as the key

    # Check if the name is in the dictionary and if it's been less than 1 minute since the last attendance
    if name_key in last_attendance_time and (now - last_attendance_time[name_key]).total_seconds() < 100:
        return  # Skip marking attendance if it's been less than 1 minute

    # Fetch student_id from student table based on student_name
    cursor.execute("SELECT student_id FROM student WHERE name = %s", (name,))
    student_id = cursor.fetchone()
    if student_id:
        student_id = student_id[0]
    else:
        # If student not found, skip marking attendance
        return

    # Insert attendance record into the attendance table
    insert_query = "INSERT INTO attendance (student_id, student_name, date, time, subject_name) VALUES (%s, %s, %s, %s, %s)"
    values = (student_id, name, dtString.split()[0], dtString.split()[1], subject_name)
    cursor.execute(insert_query, values)
    db.commit()

    global attendance_file

    folder_name = "CSV File"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    # Update attendance CSV file with subject-specific file name
    attendance_file = f"{folder_name}/{subject_name}_{dtString.split()[0]}_{dtString.split()[1].replace(':', '')}.csv"
    update_attendance_csv(student_id, name, dtString.split()[0], dtString.split()[1], attendance_file)
    last_attendance_time[name_key] = now 
     
def start_face_recognition(subject_name):
    generate_pkl()
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX  # Set the font for displaying text

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        facesCurFrame = face_recognition.face_locations(frame, model='cnn')
        encodesCurFrame = face_recognition.face_encodings(frame, facesCurFrame)

        for faceLoc, encodeFace in zip(facesCurFrame, encodesCurFrame):
            matches = face_recognition.compare_faces(model, encodeFace)
            faceDis = face_recognition.face_distance(model, encodeFace)
            matchIndex = np.argmin(faceDis)

            y1, x2, y2, x1 = faceLoc
            if matches[matchIndex]:
                if matchIndex >= 0 and matchIndex < len(classNames):
                    name = classNames[matchIndex].upper()
                    mark_attendance(name, classNames, subject_name)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle for known faces

                    # Display the name below the green rectangle
                    cv2.putText(frame, name, (x1, y2 + 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
                else:
                    print("No match found in the database.")
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red rectangle for unknown faces
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red rectangle for unknown faces

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        cam_label.imgtk = imgtk
        cam_label.configure(image=imgtk)

        root.update()

    cap.release()
    cv2.destroyAllWindows()

def select_subject():
    select_subject_window = Toplevel(root)
    select_subject_window.title("Marking Attendance")
    select_subject_window.config(bg=BG_COLOR)
    
    # Center the window on the screen
    window_width = 1550
    window_height = 870
    screen_width = select_subject_window.winfo_screenwidth()
    screen_height = select_subject_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    select_subject_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    subject_label = Label(select_subject_window, text="Select Subject For Marking Attendance:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    subject_label.pack(pady=10)

    global subject_combobox
    subject_combobox = Combobox(select_subject_window, values=["System Programming & Compiler Construction", "Cryptogrphy & System Security ", "Artificial Intelligence", "Internet of Things", "Mobile Computing"], font=LABEL_FONT, width=40)
    subject_combobox.pack(pady=5)

    

    # Create a frame for the attendance list and face preview
    attendance_frame = Frame(select_subject_window, bg=FRAME_COLOR)
    attendance_frame.pack(side=RIGHT, padx=10, pady=10)

    # Create a label to display the face preview
    global face_preview_label
    face_preview_label = Label(attendance_frame, bg=FRAME_COLOR)

    def start_face_recognition_for_subject():
        selected_subject = subject_combobox.get()
        if selected_subject:
            # Fetch the subject_name from the subject table
            cursor.execute("SELECT subject_name FROM subject WHERE subject_name = %s", (selected_subject,))
            subject_name = cursor.fetchone()
            if subject_name:
                subject_name = subject_name[0]
                start_face_recognition(subject_name)
            else:
                messagebox.showerror("Error", f"Subject '{selected_subject}' not found in the database.")
        else:
            messagebox.showerror("Error", "Please select a subject.")

    
    def select_image_and_recognize():
        selected_subject = subject_combobox.get()
        if selected_subject:
            # Fetch the subject_name from the subject table
            cursor.execute("SELECT subject_name FROM subject WHERE subject_name = %s", (selected_subject,))
            subject_name = cursor.fetchone()
            if subject_name:
                subject_name = subject_name[0]

                generate_pkl()
                file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
                if file_path:
                    image = cv2.imread(file_path)
                    facesCurFrame = face_recognition.face_locations(image, model='cnn')
                    encodesCurFrame = face_recognition.face_encodings(image, facesCurFrame)

                    font = cv2.FONT_HERSHEY_SIMPLEX  # Set the font for displaying text

                    for faceLoc, encodeFace in zip(facesCurFrame, encodesCurFrame):
                        matches = face_recognition.compare_faces(model, encodeFace)
                        faceDis = face_recognition.face_distance(model, encodeFace)
                        matchIndex = np.argmin(faceDis)

                        y1, x2, y2, x1 = faceLoc
                        if matches[matchIndex]:
                            if matchIndex >= 0 and matchIndex < len(classNames):
                                name = classNames[matchIndex].upper()
                                mark_attendance(name, classNames, subject_name)

                                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle for known faces
                                # Display the name below the green rectangle
                                cv2.putText(image, name, (x1, y2 + 30), font, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
                            else:
                                print("No match found in the database.")
                                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red rectangle for unknown faces
                        else:
                            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red rectangle for unknown faces

                    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    imgtk = ImageTk.PhotoImage(image=img)
                    cam_label.imgtk = imgtk
                    cam_label.configure(image=imgtk)
            else:
                messagebox.showerror("Error", f"Subject '{selected_subject}' not found in the database.")
        else:
            messagebox.showerror("Error", "Please select a subject.")
    # Create the "Capture Live" button
    start_face_recognition_button = Button(select_subject_window, text="Capture Live From Camera", command=start_face_recognition_for_subject, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    start_face_recognition_button.pack(pady=5)

    # Create the "Select Image" button
    select_image_button = Button(select_subject_window, text="Select Image From Device", command=select_image_and_recognize, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    select_image_button.pack(pady=5)

    # Create a frame for the webcam feed
    cam_frame = Frame(select_subject_window, bg=FRAME_COLOR, height=500,  width=850)
    cam_frame.pack(side=BOTTOM, padx=10, pady=10)

    # Create a label to display the webcam feed
    global cam_label
    cam_label = Label(cam_frame, bg=FRAME_COLOR)
    cam_label.pack()

    # Add hover effect for buttons
    def on_enter(event):
        event.widget.config(bg=BUTTON_HOVER_COLOR)

    def on_leave(event):
        event.widget.config(bg=BUTTON_COLOR)

    start_face_recognition_button.bind("<Enter>", on_enter)
    start_face_recognition_button.bind("<Leave>", on_leave)
    select_image_button.bind("<Enter>", on_enter)
    select_image_button.bind("<Leave>", on_leave)


def show_attendance_analysis():
    # Fetch attendance data from the database
    cursor.execute("SELECT s.name, a.date, a.subject_name FROM attendance a JOIN student s ON a.student_id = s.student_id")
    attendance_data = cursor.fetchall()

    # Create a pandas DataFrame from the attendance data
    attendance_df = pd.DataFrame(attendance_data, columns=['name', 'date', 'subject'])

    # Create a new window for attendance analysis
    analysis_window = Toplevel(root)
    analysis_window.title("Attendance Analysis")
    analysis_window.config(bg=BG_COLOR)
    analysis_window.state('zoomed')

    # Create a notebook (tabbed interface)
    notebook = ttk.Notebook(analysis_window)
    notebook.pack(pady=10, fill=BOTH, expand=True)

    # Create a tab for student-wise stats
    student_stats_tab = ttk.Frame(notebook)
    notebook.add(student_stats_tab, text="Student-wise Stats")

    # Create a frame for the analysis plots and student combobox in the student stats tab
    student_stats_frame = Frame(student_stats_tab, bg=FRAME_COLOR)
    student_stats_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

    student_label = Label(student_stats_frame, text="Select Student:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    student_label.pack(side=TOP, pady=5)

    # Create a dropdown menu to select a student in the student stats tab
    student_combobox = Combobox(student_stats_frame, values=sorted(attendance_df['name'].unique()), font=LABEL_FONT)
    student_combobox.pack(side=TOP, pady=5)

    # Create a canvas with scrollbar for the analysis plots in the student stats tab
    student_stats_canvas = Canvas(student_stats_frame, bg=FRAME_COLOR)
    student_stats_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    student_analysis_frame = Frame(student_stats_canvas, bg=FRAME_COLOR)
    student_analysis_frame_window = student_stats_canvas.create_window((0, 0), window=student_analysis_frame, anchor="nw")

    def on_student_analysis_tab_select(event):
        if notebook.index(notebook.select()) == notebook.index(student_stats_tab):
            student_stats_canvas.itemconfigure(student_analysis_frame_window, width=1200)
        else:
            student_stats_canvas.itemconfigure(student_analysis_frame_window, width=800)

    notebook.bind("<<NotebookTabChanged>>", on_student_analysis_tab_select)

    def show_student_analysis(attendance_df):
        for widget in student_analysis_frame.winfo_children():
            widget.destroy()

        selected_student = student_combobox.get()
        student_attendance = attendance_df[attendance_df['name'] == selected_student]

        # Create a figure for the student attendance by subject
        fig5 = plt.Figure(figsize=(6, 6), dpi=100)
        ax5 = fig5.add_subplot(111)
        attendance_by_subject = student_attendance.groupby('subject').size()
        ax5.pie(attendance_by_subject.values, labels=attendance_by_subject.index, autopct='%1.1f%%')
        ax5.axis('equal')
        ax5.set_title(f'Attendance by Subject for {selected_student}')

        # Create a canvas to display the attendance by subject plot
        canvas5 = FigureCanvasTkAgg(fig5, master=student_analysis_frame)
        canvas5.draw()
        canvas5.get_tk_widget().pack(padx=10, pady=10, fill=BOTH, expand=True)

    student_combobox.bind('<<ComboboxSelected>>', lambda event: show_student_analysis(attendance_df))
def generate_pdf_report(date=None, subject=None):
    # Fetch attendance data from the database
    if date and subject:
        cursor.execute("SELECT s.name, a.student_id, a.date, a.time, a.subject_name FROM attendance a JOIN student s ON a.student_id = s.student_id WHERE a.date = %s AND a.subject_name = %s ORDER BY a.date, a.time", (date, subject))
    else:
        cursor.execute("SELECT s.name, a.student_id, a.date, a.time, a.subject_name FROM attendance a JOIN student s ON a.student_id = s.student_id ORDER BY a.date, a.time")
    attendance_data = cursor.fetchall()

    # Get the current date and time
    current_date = datetime.date.today()
    current_time = datetime.datetime.now().strftime("%I-%M-%p")


    reports_folder = "PDF Reports"
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)

    # Create a PDF file
    if date and subject:
        pdf_file_name = f"{reports_folder}/{subject.replace(' ', '_')}_Attendance_Report_{date}_{current_time.replace(':', '')}.pdf"
    else:
        pdf_file_name = f"{reports_folder}/Attendance_Report_{current_date.strftime('%Y-%m-%d')}_{current_time.replace(':', '')}.pdf"
    doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)
    elements = []

    # Add the title and date/time to the PDF
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    date_time_style = styles["BodyText"]
    title = "Attendance Report"
    if date and subject:
        date_time = f"{date} ({subject})"
    else:
        date_time = f"{current_date.strftime('%Y-%m-%d')} {current_time}"
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(date_time, date_time_style))

    # Create the table for attendance data
    data = [["Name", "Student ID", "Date", "Time", "Subject"]]
    for record in attendance_data:
        data.append(record)

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('FONTSIZE', (0, 0), (-1, 0), 14),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Add the table to the PDF elements
    elements.append(table)

    # Generate the PDF file
    doc.build(elements)

    messagebox.showinfo("Success", f"Attendance report saved as {pdf_file_name}")

def generate_report_window():
    report_window = Toplevel(root)
    report_window.title("Generate Report")
    report_window.config(bg=BG_COLOR)
    window_width = 400
    window_height = 300
    screen_width = report_window.winfo_screenwidth()
    screen_height = report_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    report_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def generate_all_subjects_report():
        report_window.destroy()
        generate_pdf_report()

    def generate_by_date_and_subject():
        date_window = Toplevel(report_window)
        date_window.title("Select Date and Subject")
        date_window.config(bg=BG_COLOR)
        window_width = 400
        window_height = 300
        screen_width = date_window.winfo_screenwidth()
        screen_height = date_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        date_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        report_window.deiconify()

        # Create a frame for the date picker and subject dropdown
        date_subject_frame = Frame(date_window, bg=BG_COLOR)
        date_subject_frame.pack(pady=10)

        # Create the date picker
        date_label = Label(date_subject_frame, text="Select Date:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        date_label.grid(row=0, column=0, padx=5, pady=5)

        date_entry = DateEntry(date_subject_frame, date_pattern='yyyy-mm-dd', background=ENTRY_COLOR, foreground=TEXT_COLOR, font=LABEL_FONT)
        date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Create the subject dropdown
        subject_label = Label(date_subject_frame, text="Select Subject:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        subject_label.grid(row=1, column=0, padx=5, pady=5)

        cursor.execute("SELECT subject_name FROM subject")
        subjects = [subject[0] for subject in cursor.fetchall()]
        subject_combobox = Combobox(date_subject_frame, values=subjects, font=LABEL_FONT)
        subject_combobox.grid(row=1, column=1, padx=5, pady=5)

        def generate_report():
            selected_date = date_entry.get_date().strftime('%Y-%m-%d')
            selected_subject = subject_combobox.get()
            if selected_subject:
                date_window.destroy()
                report_window.destroy()
                generate_pdf_report(selected_date, selected_subject)

        generate_button = Button(date_window, text="Generate Report", command=generate_report, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
        generate_button.pack(pady=10)

    all_subjects_button = Button(report_window, text="Generate All Subject Report", command=generate_all_subjects_report, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    all_subjects_button.pack(padx=10, pady=10)

    by_date_and_subject_button = Button(report_window, text="Generate Report by Date and Subject", command=generate_by_date_and_subject, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    by_date_and_subject_button.pack(pady=10)


def login():
    login_window = Toplevel(root)
    login_window.title("Login")
    login_window.config(bg=BG_COLOR)

    # Set the window size and position it at the center
    window_width = 1550
    window_height = 870
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")


    title_label = Label(login_window, text="Facial Attendance System", bg=BG_COLOR, fg="#007FFF", font=("Arial", 24, "bold"))
    title_label.place(x=window_width // 2, y=50, anchor="center")

    image_path = "assets/login.jpg"
    image = Image.open(image_path)

    # Resize the image
    new_width, new_height = 700, 680
    resized_image = image.resize((new_width, new_height))

    # Create the PhotoImage object from the resized image
    photo = ImageTk.PhotoImage(resized_image)

    # Create a label to display the image
    image_label = Label(login_window, image=photo, bg="white")
    image_label.image = photo  # Keep a reference to the image to prevent garbage collection

    # Position the image at the center-left side of the window
    image_x = (window_width - new_width) // 4
    image_y = (window_height - new_height) // 2
    image_label.place(x=image_x - 100, y=image_y, width=new_width, height=new_height)

    # Calculate the center position for the labels and entries to the right of the image
    center_x = image_x + new_width + 100
    center_y = image_y + new_height // 2

    signin_label = Label(login_window, text="Sign In", bg=BG_COLOR, fg="#007FFF", font=("Aerial",20,"bold"))
    signin_label.place(x=center_x + 120, y=center_y - 170, anchor="center")

    username_label = Label(login_window, text="Username:", bg=BG_COLOR, fg="black", font=("Aerial",14))
    username_label.place(x=center_x + 45, y=center_y - 100, anchor="e")
    username_entry = Entry(login_window, bg=ENTRY_COLOR, fg="black", font=LABEL_FONT)
    username_entry.place(x=center_x + 60, y=center_y - 100, anchor="w")

    password_label = Label(login_window, text="Password:", bg=BG_COLOR, fg="black", font=("Aerial",14))
    password_label.place(x=center_x + 45, y=center_y - 50, anchor="e")
    password_entry = Entry(login_window, show="*", bg=ENTRY_COLOR, fg="black", font=LABEL_FONT)
    password_entry.place(x=center_x + 60 , y=center_y - 50, anchor="w")

    def validate_login():
        entered_username = username_entry.get()
        entered_password = password_entry.get()

        cursor.execute("SELECT username, password FROM user WHERE username = %s", (entered_username,))
        result = cursor.fetchone()

        if result:
            stored_username, stored_password_hash = result
            entered_password_hash = hashlib.sha256(entered_password.encode()).hexdigest()

            if entered_password_hash == stored_password_hash:
                login_window.destroy()
                root.deiconify()
            else:
                messagebox.showerror("Login Failed", "Incorrect username or password.")
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    login_button = Button(login_window, text="Login", command=validate_login, bg="#007FFF", fg=TEXT_COLOR, font=BUTTON_FONT)
    login_button.place(x=center_x + 125, y=center_y, anchor="center")

    login_window.mainloop()

def add_user():
    add_user_window = Toplevel(root)
    add_user_window.title("Add User")
    add_user_window.config(bg=BG_COLOR)

    window_width = 300
    window_height = 200
    screen_width = add_user_window.winfo_screenwidth()
    screen_height = add_user_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    add_user_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    username_label = Label(add_user_window, text="Username:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    username_label.pack(pady=5)
    username_entry = Entry(add_user_window, bg=ENTRY_COLOR, fg="black", font=LABEL_FONT)
    username_entry.pack(pady=5)

    password_label = Label(add_user_window, text="Password:", bg=BG_COLOR, fg="black", font=LABEL_FONT)
    password_label.pack(pady=5)
    password_entry = Entry(add_user_window, show="*", bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
    password_entry.pack(pady=5)

    def save_user():
        username = username_entry.get()
        password = password_entry.get()

        # Hash the password using SHA-256
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Insert the user into the database
        insert_user_query = "INSERT INTO user (username, password) VALUES (%s, %s)"
        try:
            cursor.execute(insert_user_query, (username, password_hash))
            db.commit()
            messagebox.showinfo("Success", "User added successfully!")
            add_user_window.destroy()
        except MySQLdb.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")

    save_button = Button(add_user_window, text="Save", command=save_user, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    save_button.pack(pady=10)


def show_registered_students():
    registered_students_window = Toplevel(root)
    registered_students_window.title("Modify Registered Students")
    registered_students_window.config(bg=BG_COLOR)

    # Fetch student data from the database
    cursor.execute("SELECT student_id, name, year, branch, division, roll_no FROM student")
    student_data = cursor.fetchall()

    # Create a treeview to display student data
    student_tree = ttk.Treeview(registered_students_window, columns=("ID", "Name", "Year", "Branch", "Division", "Roll No."), show="headings")
    student_tree.heading("ID", text="Student ID")
    student_tree.heading("Name", text="Name")
    student_tree.heading("Year", text="Year")
    student_tree.heading("Branch", text="Branch")
    student_tree.heading("Division", text="Division")
    student_tree.heading("Roll No.", text="Roll No.")

    # Insert student data into the treeview
    for student in student_data:
        student_tree.insert("", "end", values=student)

    student_tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

    # Add a scrollbar to the treeview
    scrollbar = ttk.Scrollbar(registered_students_window, orient=VERTICAL, command=student_tree.yview)
    student_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Function to update student details
    def update_student():
        selected_item = student_tree.selection()
        if selected_item:
            student_id = student_tree.item(selected_item)['values'][0]
            update_student_window = Toplevel(registered_students_window)
            update_student_window.title("Update Student Details")
            update_student_window.config(bg=BG_COLOR)

            # Fetch current student details from the database
            cursor.execute("SELECT name, year, branch, division, roll_no FROM student WHERE student_id = %s", (student_id,))
            student_details = cursor.fetchone()

            # Create entry fields for updating student details
            name_label = Label(update_student_window, text="Name:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            name_label.grid(row=0, column=0, padx=10, pady=10)
            name_entry = Entry(update_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            name_entry.grid(row=0, column=1, padx=10, pady=10)
            name_entry.insert(0, student_details[0])

            year_label = Label(update_student_window, text="Year:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            year_label.grid(row=1, column=0, padx=10, pady=10)
            year_combobox = Combobox(update_student_window, values=["FE", "SE", "TE", "BE"], font=LABEL_FONT)
            year_combobox.grid(row=1, column=1, padx=10, pady=10)
            year_combobox.set(student_details[1])

            branch_label = Label(update_student_window, text="Branch:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            branch_label.grid(row=2, column=0, padx=10, pady=10)
            branch_combobox = Combobox(update_student_window, values=["Computer", "IT", "AIDS"], font=LABEL_FONT)
            branch_combobox.grid(row=2, column=1, padx=10, pady=10)
            branch_combobox.set(student_details[2])

            division_label = Label(update_student_window, text="Division:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            division_label.grid(row=3, column=0, padx=10, pady=10)
            division_entry = Entry(update_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            division_entry.grid(row=3, column=1, padx=10, pady=10)
            division_entry.insert(0, student_details[3])

            roll_no_label = Label(update_student_window, text="Roll No.:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            roll_no_label.grid(row=4, column=0, padx=10, pady=10)
            roll_no_entry = Entry(update_student_window, bg=ENTRY_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            roll_no_entry.grid(row=4, column=1, padx=10, pady=10)
            roll_no_entry.insert(0, student_details[4])

            def save_updated_details():
                updated_name = name_entry.get()
                updated_year = year_combobox.get()
                updated_branch = branch_combobox.get()
                updated_division = division_entry.get()
                updated_roll_no = roll_no_entry.get()

                # Update student details in the database
                update_query = "UPDATE student SET name = %s, year = %s, branch = %s, division = %s, roll_no = %s WHERE student_id = %s"
                values = (updated_name, updated_year, updated_branch, updated_division, updated_roll_no, student_id)
                cursor.execute(update_query, values)
                db.commit()

                # Update the treeview with the new details
                student_tree.item(selected_item, values=(student_id, updated_name, updated_year, updated_branch, updated_division, updated_roll_no))

                update_student_window.destroy()

            save_button = Button(update_student_window, text="Save", command=save_updated_details, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
            save_button.grid(row=5, column=1, padx=10, pady=10)

        else:
            messagebox.showwarning("Warning", "Please select a student to update.")

    # Function to delete a student
    def delete_student():
        selected_item = student_tree.selection()
        if selected_item:
            student_id = student_tree.item(selected_item)['values'][0]
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the student with ID {student_id}?")
            if confirm:
                try:
                    # Fetch the student's name from the database
                    cursor.execute("SELECT name FROM student WHERE student_id = %s", (student_id,))
                    student_name = cursor.fetchone()[0]

                    # Delete the attendance records for the student
                    delete_attendance_query = "DELETE FROM attendance WHERE student_id = %s"
                    cursor.execute(delete_attendance_query, (student_id,))

                    # Delete the student from the student table
                    delete_student_query = "DELETE FROM student WHERE student_id = %s"
                    cursor.execute(delete_student_query, (student_id,))

                    # Delete the student's image from the Training_images folder
                    image_path = os.path.join(path, f"{student_name}.jpg")
                    if os.path.exists(image_path):
                        os.remove(image_path)

                    db.commit()
                    student_tree.delete(selected_item)
                    messagebox.showinfo("Success", f"Student '{student_name}' deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please select a student to delete.")
    # Add buttons for update and delete operations
    button_frame = Frame(registered_students_window, bg=BG_COLOR)
    button_frame.pack(pady=10)

    update_button = Button(button_frame, text="Update", command=update_student, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    update_button.pack(side=LEFT, padx=5)

    delete_button = Button(button_frame, text="Delete", command=delete_student, bg=BUTTON_COLOR, fg=TEXT_COLOR, font=BUTTON_FONT)
    delete_button.pack(side=LEFT, padx=5)

root = Tk()
root.title("Face Recognition Attendance System")
root.config(bg=BG_COLOR)



bg_image = Image.open("assets/main_bg.jpg")
bg_image = bg_image.resize((1550, 1550), resample=Image.Resampling.BICUBIC)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def create_square_button(root, text, command, image_path):
    square_size = 250
    square = Canvas(root, width=square_size, height=square_size)
    square.pack(pady=0,padx=0)

    image = Image.open(image_path)
    image_tk = ImageTk.PhotoImage(image)
    square.create_image(square_size // 2, square_size // 2, image=image_tk)
    square.image = image_tk  # Keep a reference to the image to prevent garbage collection

    label = Label(root, text=text, fg=TEXT_COLOR, font=("Aerial",16, "bold"))
    label.pack(padx=0,pady=0)

    square.bind("<Button-1>", lambda event: command())
    return square

buttons_frame = Frame(root)
buttons_frame.place(relx=0.5, rely=0.44, anchor="center")

button_frames = []
for _ in range(6):
    button_frame = Frame(buttons_frame)
    button_frame.pack(side=LEFT, padx=1)
    button_frames.append(button_frame)


add_student_button = create_square_button(button_frames[0], "Add New Student", add_new_student, "assets/student.png")
select_subject_button = create_square_button(button_frames[1], "Mark Attendance\nFor Subject", select_subject, "assets/select_sub.png")
show_analysis_button = create_square_button(button_frames[2], "Show Analysis", show_attendance_analysis, "assets/show_analysis.png")
generate_report_button = create_square_button(button_frames[3], "Generate Master Report", generate_report_window, "assets/report.png")
add_user_button = create_square_button(button_frames[4], "Add User", add_user, "assets/add_user.png")
show_students_button = create_square_button(button_frames[5], "Modify Registered \n Students", show_registered_students, "assets/reg_student.png")

def logout():
    root.withdraw()
    login()

logout_button = Button(root, text="Logout", command=logout, bg="red", fg="white", font=("Arial", 12, "bold"))
logout_button.place(relx=0.95, rely=0.02, anchor="ne")

root_window_width = 1550
root_window_height = 870
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (root_window_width // 2)
y = (screen_height // 2) - (root_window_height // 2)
root.geometry(f"{root_window_width}x{root_window_height}+{x}+{y}")

root.state('zoomed') 
root.withdraw()  


login()