👀 Face Recognition Attendance System 📝
This is a Python-based application that uses face recognition technology to mark attendance for students. It incorporates a GUI, MySQL database integration, and various features to manage student data, mark attendance, generate reports, and analyze attendance records.

🚀 Getting Started
To run this project, follow these steps:

Clone the Repository

Copy code
git clone

```bash
git clone https://github.com/ikunalpn/Facial-Attendance-System.git
```

Install Dependencies
Make sure you have Python installed on your system. Then, install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

Set up MySQL Database
Install MySQL on your system if you haven't already.
Create a new database named sem6_project.
Import the provided SQL file to create the necessary tables.
Configure Database Connection
In the main.py file, locate the following lines and update them with your MySQL credentials:

```bash
db = MySQLdb.connect(
host="localhost",
user="your_username",
password="your_password",
database="sem6_project"
)
```

Run the Application

```bash
python main.py
```

The application will start, and you'll be prompted to log in or create a new user.

🔑 Key Features
👥 Add new students and capture their photos
📷 Mark attendance using face recognition technology
📊 Analyze attendance data with visualizations
📃 Generate attendance reports in PDF format
🔐 User authentication and authorization
📷 Sample Images

![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/login.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Main_Window.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Add_User.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Add_Student.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Mark_Attendance_Subject_Wise.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/All_Stats.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Student_Wise_Stat.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Generate_Report.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Subject_Wise_Report.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Modify_Student.png)
![Image Alt Text](https://github.com/ikunalpn/Facial-Attendance-System/blob/main/GUI_Screenshots/Update_Student.png)

🤝 Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

👏 Acknowledgments
face-recognition library for face recognition functionality
OpenCV for image and video processing
MySQL Connector/Python for MySQL database integration
Tkinter for creating the GUI
