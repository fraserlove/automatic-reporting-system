"""
EES Project Automatic Error Report Software - Development Version 1.5.0
Developed by Fraser Love on 13/02/19
Dependencies: Tkinter

Features
- Automatic CSV file creation
- Automatic additon of user entered values to CSV files
- Login with username and password
- Stylish GUI
- Hashed passwords and usernames for extra security
- Extra UI robustness enhancements
- Automatic email of reports
- Login cooldowns for extra security
- Automatic email of sucessfull and unsuccessfull login attempts
- Server login increasing robustness
- Enhanced UI displaying more useful data
- Client Side Storage of Information
- Ability to upload content
"""

from tkinter import *
import PIL.Image
import PIL.ImageTk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from flask import Flask
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from passlib.hash import pbkdf2_sha256
import datetime, csv, os, time, hashlib, uuid, smtplib, threading, urllib

def app():
    def initalise_app():
        root = Tk()
        root.overrideredirect(1)
        return root

    def close_window():
        root.destroy()

    def root_screen(root):
        tries = 3
        locked = True

        def navbar(root):
            nav = Frame(root, bg="#333333", width=1920, height=20)
            title = Label(nav, text="Automatic Report Software - Development Version", bg="#333333", fg="white")
            exit = Button(nav, text="Exit", fg="white", bg="#333333", borderwidth=0, height = 1, width = 5, activebackground="#333333", activeforeground="white", command=close_window)
            nav.place(x=0, y=0, anchor="nw")
            exit.place(x=1600, y=10, anchor="e")
            title.place(x=800, y=10, anchor="center")

        def gen_id():
            form_id = 1
            if os.path.isfile("data/data.csv"):
                file = open("data/data.csv", "r")
                for row in csv.reader(file):
                    form_id += 1
            return form_id

        def main(root):
            def destroy_widgit(widgit):
                widgit.destroy()

            def send_email(message, subject, login=False):
                email = sending_email.get()
                password = email_pass.get()
                send_to_email = recieving_email.get()

                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = send_to_email
                msg['Subject'] = subject

                msg.attach(MIMEText(message, 'plain'))
                if len(file_array) > 0 and login == False:
                    for i in range(0,len(file_array)):
                        attachment = open(file_array[i], "rb")
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload((attachment).read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', "attachment; filename= %s" % file_name_array[i])
                        msg.attach(part)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                text = msg.as_string()
                server.sendmail(email, send_to_email, text)
                server.quit()

            def get_entries(page, form_id, time_now, name, manufacturer, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge, description, message):
                if locked == False:
                    file = open("data/data.csv", "a", newline="")
                    writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
                    writer.writerow([form_id, time_now, name, manufacturer, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge, description])
                    file.close()
                    info = open("data/user_info.txt", "r+")
                    for row in info:
                        text = row.split(",")
                        if text[0] == username.get().lower():
                            text[2] = str(gen_id()-1)
                            text = ",".join(text)
                    info.close()
                    info = open("data/user_info.txt", "w")
                    info.write(text)
                    info.close()
                    send_email(message, '{}: Breakdown Report'.format(username.get()))
                    submit_display(page, "FORM ID {}: SUCESSFULLY SUBMITTED".format(gen_id()-2), "#42f456")
                if locked == True:
                    submit_display(page, "ERROR: FORM NOT SUBMITTED, YOU ARE NOT LOGGED IN", "red")

            def report_head(page):
                report_header = Label(page, text="REPORT", bg="#161616", fg="white", font=('Segoe UI', '18', 'bold'))
                report_header.place(x=480, y=30, anchor="center")

            def submit_display(page, string, colour):
                submit_text = Label(page, text=string, bg="#161616", fg=colour, font=('Segoe UI', '10'))
                submit_text.place(x=680, y=500, anchor="e")
                submit_text.after(3500, destroy_widgit, submit_text)

            def collect_time(page):
                time_now = datetime.datetime.now()
                time_now = time_now.strftime("%X") + " (" + time_now.strftime("%x") + ")"
                submit_time = Label(page, text="Time: {}".format(time_now), bg="#161616", fg="white", font=('Segoe UI', '13'))
                submit_time.place(x=10, y=70)
                return time_now

            def job_no(page):
                job_text = Label(page, text="Job Number: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                job_text.place(x=10, y=30)
                job_no_text = Label(page, text=str(gen_id()-1), bg="#161616", fg="white", font=('Segoe UI', '13'))
                job_no_text.place(x=110, y=30)

            def name_input(page):
                name_text = Label(page, text="Engineer Name: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                name_text.place(x=10, y=110)
                name_list = ("Engineer 1", "Engineer 2", "Engineer 3", "Engineer 4", "Engineer 5")
                name = StringVar()
                name.set("Select Name")
                name_set = OptionMenu(page, name, *name_list)
                name_set.configure(text="File", fg="white", bg="#474747", borderwidth=0, height = 1, width = 10, font=('Segoe UI', '10'), activebackground="#333333", activeforeground="white", highlightthickness=0, indicatoron=1)
                name_set.place(x=140, y=113)
                return name

            def machine_info(page):
                manufacturer = Label(page, text="Machine Manufacturer: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                manufacturer.place(x=10, y=150)
                manufacturer_list = ("MBF", "P.E.", "ROBINO", "TMG", "Logistics & Controls")
                manufacturer_name = StringVar()
                manufacturer_name.set("Select Manufacturer")
                manufacturer_set = OptionMenu(page, manufacturer_name, *manufacturer_list)
                manufacturer_set.configure(text="File", fg="white", bg="#474747", borderwidth=0, height = 1, width = 16, font=('Segoe UI', '10'), activebackground="#333333", activeforeground="white", highlightthickness=0, indicatoron=1)
                manufacturer_set.place(x=200, y=153)
                machine_model = StringVar()
                machine_model_input = Entry(page, textvariable=machine_model, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                machine_model_input.place(x=495, y=156)
                machine_model_text = Label(page, text="Machine Model: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                machine_model_text.place(x=360, y=150)
                machine_id = StringVar()
                machine_id_input = Entry(page, textvariable=machine_id, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                machine_id_input.place(x=815, y=156)
                machine_id_text = Label(page, text="Machine Serial No: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                machine_id_text.place(x=660, y=150)
                customer_name = StringVar()
                customer_name_input = Entry(page, textvariable=customer_name, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                customer_name_input.place(x=150, y=196)
                customer_name_text = Label(page, text="Customer Name: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                customer_name_text.place(x=10, y=190)
                contact_name = StringVar()
                contact_name_input = Entry(page, textvariable=contact_name, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                contact_name_input.place(x=385, y=196)
                contact_name_text = Label(page, text="Contact: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                contact_name_text.place(x=310, y=190)
                location = StringVar()
                location_input = Entry(page, textvariable=location, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                location_input.place(x=630, y=196)
                location_text = Label(page, text="Location: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                location_text.place(x=550, y=190)
                customer_charge_text = Label(page, text="Customer Charge: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                customer_charge_text.place(x=790, y=190)
                customer_charge_list = ("Yes", "No")
                customer_charge = StringVar()
                customer_charge.set("Select Y/N")
                customer_charge_set = OptionMenu(page, customer_charge, *customer_charge_list)
                customer_charge_set.configure(text="File", fg="white", bg="#474747", borderwidth=0, height = 1, width = 9, font=('Segoe UI', '10'), activebackground="#333333", activeforeground="white", highlightthickness=0, indicatoron=1)
                customer_charge_set.place(x=940, y=193)
                job_type_text = Label(page, text="Job Type: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                job_type_text.place(x=10, y=230)
                job_type = StringVar()
                job_type_1 = Radiobutton(page, text="Installation", value="Installation", variable=job_type, selectcolor='black', fg="white", bg="#161616", activebackground="#333333", activeforeground="white", highlightthickness=0,  font=('Segoe UI', '10'))
                job_type_2 = Radiobutton(page, text="Overhaul", value="Overhaul", variable=job_type, selectcolor='black', fg="white", bg="#161616", activebackground="#333333", activeforeground="white", highlightthickness=0,  font=('Segoe UI', '10'))
                job_type_3 = Radiobutton(page, text="Survey", value="Survey", variable=job_type, selectcolor='black', fg="white", bg="#161616", activebackground="#333333", activeforeground="white", highlightthickness=0,  font=('Segoe UI', '10'))
                job_type_4 = Radiobutton(page, text="Maintenance", value="Maintenance", variable=job_type, selectcolor='black', fg="white", bg="#161616", activebackground="#333333", activeforeground="white", highlightthickness=0,  font=('Segoe UI', '10'))
                job_type_5 = Radiobutton(page, text="Breakdown", value="Breakdown", variable=job_type, selectcolor='black', fg="white", bg="#161616", activebackground="#333333", activeforeground="white", highlightthickness=0,  font=('Segoe UI', '10'))
                job_type_6 = Radiobutton(page, text="Other", value="Other", variable=job_type, selectcolor='black', fg="white", bg="#161616", activebackground="#333333", activeforeground="white", highlightthickness=0,  font=('Segoe UI', '10'))
                job_type_1.place(x=92, y=233)
                job_type_2.place(x=192, y=233)
                job_type_3.place(x=284, y=233)
                job_type_4.place(x=358, y=233)
                job_type_5.place(x=467, y=233)
                job_type_6.place(x=568, y=233)
                extra_upload_text = Label(page, text=" - Pictures/Video/Documentation etc.", bg="#161616", fg="white", font=('Segoe UI', '10'))
                extra_upload_text.place(x=130, y=483)
                open_file_button = Button(page, text="Upload File", fg="white", bg="#474747", borderwidth=0, height = 1, width = 12, activebackground="#333333", activeforeground="white",  font=('Segoe UI', '12'), command=lambda:open_file(page))
                open_file_button.place(x=10, y=480)
                remove_button = Button(page, text="Remove", fg="white", bg="#474747", borderwidth=0, height = 1, width = 12, activebackground="#333333", activeforeground="white",  font=('Segoe UI', '12'), command=lambda:(remove(page, file_array)))
                remove_button.place(x=10, y=520)
                return manufacturer_name, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge

            def remove(page, array):
                global file_array, file_name_array
                canvas = Canvas(page, width=400, height=len(file_name_array)*20, bg="#161616", borderwidth=0, bd=0, highlightthickness=0, relief='ridge')
                canvas.place(x=130, y=520)
                file_array = []
                file_name_array = []

            def open_file(page):
                global file_text, attach_file, file_array
                file_text = askopenfilenames(filetypes=[("All files", "*.*")], initialdir="C:\\", title="Upload File")
                for entry in file_text:
                    entry = entry.split("(")
                    for file_name in entry:
                        file_array.append(file_name)
                        index = (file_name.rfind('/')+1)
                        file_name_array.append(file_name[index:])
                count = 0
                for entry in file_name_array:
                    show_text = []
                    for char in entry:
                        if len(show_text) < 40:
                            show_text.append(char)
                    show_text = "".join(show_text)
                    if len(entry) > 40:
                        show_text = show_text + "..."
                    file_text = Label(page, text="Uploaded: " + show_text, bg="#161616", fg="#42f456", font=('Segoe UI', '8'))
                    file_text.place(x=130, y=520+count*20)
                    count += 1
                if len(file_array) > 0:
                    if file_array[-1] == "":
                        del file_array[-1]
                        destroy_widgit(file_text)
                print(file_array)

            def note_input(page):
                description_text = Label(page, text="Description Of Work Carried Out: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                description_text.place(x=10, y=270)
                extra_text = Label(page, text=" - Issues, checks/testing done, conclusions, further actions/parts required", bg="#161616", fg="white", font=('Segoe UI', '10'))
                extra_text.place(x=270, y=273)
                description = Text(page, width = 100, height=10, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                description.place(x=10,y=310)

                return description

            def get_message(time_now, name, manufacturer_name, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge, description):
                return 'Emergency Breakdown Report from {}\n\n\tJob Number: {}\n\tSubmission Time: {}\n\tEngineer: {}\n\tManufacturer Name: {}\n\tMachine Model: {}\n\tMachine ID: {}\n\tCustomer Name: {}\n\tContact Name: {}\n\tLocation: {}\n\tJob Type: {}\n\tCustomer Charge: {} \n\tExtra Information: {}'.format(username.get(), gen_id(), time_now, name, manufacturer_name, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge, description)

            def submit_setup(page, time_now, name, manufacturer_name, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge, description):
                submit_button = Button(page, text="Submit", fg="white", bg="#474747", borderwidth=0, height = 1, width = 10, activebackground="#333333", activeforeground="white",  font=('Segoe UI', '15'), command=lambda:get_entries(page, gen_id()-1, time_now, name.get(), manufacturer_name.get(), machine_model.get(), machine_id.get(), customer_name.get(), contact_name.get(), location.get(), job_type.get(), customer_charge.get(), description.get("1.0","end-1c"), get_message(time_now, name.get(), manufacturer_name.get(), machine_model.get(), machine_id.get(), customer_name.get(), contact_name.get(), location.get(), job_type.get(), customer_charge.get(), description.get("1.0","end-1c"))))
                submit_button.place(x=697, y=480)

            def login_head(page):
                login_header = Label(page, text="LOGIN", bg="#161616", fg="white", font=('Segoe UI', '18', 'bold'))
                login_header.place(x=1340, y=30, anchor="center")

            def update_email(page, recieving_email, sending_email, email_pass):
                info = open("data/user_info.txt", "r+")
                text = ""
                for row in info:
                    text = row.split(",")
                    if text[0] == username.get().lower():
                        text[3] = recieving_email
                        text[4] = sending_email
                        text[5] = email_pass
                        text = ",".join(text)
                info.close()
                info = open("data/user_info.txt", "w")
                info.write(text)
                info.close()
                update_text = Label(page, text="Email Updated Sucessfully!", bg="#161616", fg="#42f456", font=('Segoe UI', '10'), width=23)
                update_text.place(x=1445, y=487, anchor="e")
                update_text.after(3000, destroy_widgit, update_text)

            def display_table(page):
                prevous_text = Label(page, text="LATEST REPORTS", bg="#161616", fg="white", font=('Segoe UI', '18', 'bold'))
                prevous_text.place(x=480, y=590, anchor="center")
                with open('data/data.csv') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    row_no = 0
                    for table_row in csv.reader(csv_file):
                        row_no += 1
                if row_no >= 2:
                    with open('data/data.csv') as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=',')
                        row_no = 0
                        active_row = 0
                        for table_row in csv.reader(csv_file):
                            font = ('Segoe UI', '10')
                            if row_no == 0:
                                font = ('Segoe UI', '10', 'bold')
                            if row_no + 6 > gen_id()-1 or row_no == 0:
                                for column in range(len(table_row)):
                                    if column == 11:
                                        continue
                                    elif column == 0:
                                        element = Label(page, text=table_row[column], bg="#161616", fg="white", font=font, width=20, anchor="w")
                                        element.place(x=10+column*110, y=630+active_row*30, anchor="w")
                                    elif column == 1:
                                        element = Label(page, text=table_row[column], bg="#161616", fg="white", font=font, width=20, anchor="w")
                                        element.place(x=(column*100)-10, y=630+active_row*30, anchor="w")
                                    elif column == 5:
                                        element = Label(page, text=table_row[column], bg="#161616", fg="white", font=font, width=20, anchor="w")
                                        element.place(x=70+column*110, y=630+active_row*30, anchor="w")
                                    elif column == 4:
                                        element = Label(page, text=table_row[column], bg="#161616", fg="white", font=font, width=20, anchor="w")
                                        element.place(x=70+column*110, y=630+active_row*30, anchor="w")
                                    else:
                                        element = Label(page, text=table_row[column], bg="#161616", fg="white", font=font, width=50, anchor="w")
                                        element.place(x=55+column*110, y=630+active_row*30, anchor="w")
                                active_row += 1
                            row_no += 1
                else:
                    table_error_text = Label(page, text="No Previous Reports To Be Displayed", bg="#161616", fg="red", font=('Segoe UI', '13'))
                    table_error_text.place(x=480, y=620, anchor="center")

            def login_panel(page, login_time):
                global recieving_email, sending_email, email_pass
                stats_header = Label(page, text="STATS/INFO", bg="#161616", fg="white", font=('Segoe UI', '18', 'bold'))
                stats_header.place(x=1340, y=200, anchor="center")
                latest_login = Label(page, text="Last Login: " + str(login_time), bg="#161616", fg="white", font=('Segoe UI', '13'))
                latest_login.place(x=1340, y=250, anchor="center")
                forms_sent = Label(page, text="Total Forms Sent: " + str(gen_id()-2), bg="#161616", fg="white", font=('Segoe UI', '13'))
                forms_sent.place(x=1340, y=280, anchor="center")
                recieving_email = StringVar()
                sending_email = StringVar()
                email_pass = StringVar()
                info = open("data/user_info.txt", "r+")
                for row in info:
                    text = row.split(",")
                    if text[0] == username.get().lower():
                        recieving_email.set(text[3])
                        sending_email.set(text[4])
                        email_pass.set(text[5])
                info.close()
                settings_header = Label(page, text="SETTINGS", bg="#161616", fg="white", font=('Segoe UI', '18', 'bold'))
                settings_header.place(x=1340, y=350, anchor="center")
                r_email_text = Label(page, text="Recieving Email: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                r_email_text.place(x=1280, y=400, anchor="e")
                s_email_text = Label(page, text="Your Email: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                s_email_text.place(x=1280, y=430, anchor="e")
                r_email_entry = Entry(page, textvariable=recieving_email, width=40, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                r_email_entry.place(x=1280, y=393)
                s_email_entry = Entry(page, textvariable=sending_email, width=40, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                s_email_entry.place(x=1280, y=423)
                pass_text = Label(page, text="Email Password: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                pass_text.place(x=1280, y=460, anchor="e")
                email_password = Entry(page, textvariable=email_pass, width=40, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb", show="•")
                email_password.place(x=1280, y=453)
                set_email = Button(page, text="Set Email", fg="white", bg="#474747", borderwidth=0, height = 1, width = 10, activebackground="#333333", activeforeground="white", command=lambda:update_email(page, recieving_email.get(), sending_email.get(), email_pass.get()))
                set_email.place(x=1447, y=478)
                display_table(page)

            def hash(password):
                hash_object = hashlib.sha256(password.encode())
                hex_dig = hash_object.hexdigest()
                return hex_dig

            def request_timeout(time_now):
                global to_wait, time_out
                time_out = 300  #In seconds
                if os.path.isfile("data/logins.txt"):
                    file = open("data/logins.txt","r")
                    for attempt in file:
                        to_wait = round(((float(attempt) + time_out) - time_now),5)
                        if time_now > float(attempt) + time_out:
                            return True
                        else:
                            return False
                    file.close()
                else:
                    return True

            def sign_in(page, username, password, username_text, password_text, username_input, password_input, login_button):
                nonlocal tries, locked
                if request_timeout(time.time()) == True and tries < 1:
                    tries = 3
                if request_timeout(time.time()) == True:
                    file = urllib.request.urlopen("http://81.153.109.26:3402/static/credentials.txt")
                    if locked == True:
                        for line in file:
                            line = line.decode("utf-8")
                            values = line.split(",")
                            for value in values:
                                value = value.encode("utf-8")
                            password = password.encode("utf-8")
                            username = username.encode("utf-8")
                            if pbkdf2_sha256.verify(password, values[1][:87]) and pbkdf2_sha256.verify(username, values[0]):
                                locked = False
                                destroy_widgit(username_text)
                                destroy_widgit(username_input)
                                destroy_widgit(password_text)
                                destroy_widgit(password_input)
                                destroy_widgit(login_button)
                        tries -= 1
                    file.close()
                    if locked == True:
                        tries_text = Label(page, text="Incorrect Username and Password: {} Tries Left".format(tries), bg="#161616", fg="red", font=('Segoe UI', '10'))
                        tries_text.place(x=1448, y=183, anchor="e")
                        tries_text.after(2000, destroy_widgit, tries_text)
                    if locked == False:
                        last_login = "First Time Logging In"
                        if os.path.isfile("data/user_info.txt"):
                            info = open("data/user_info.txt", "r+")
                            file_len = 0
                            for row in info:
                                file_len += 1
                                text = row.split(",")
                                if text[0] == username.decode("utf-8"):
                                    last_login = text[1]
                                    text[1] = str(datetime.datetime.now())
                                    text = ",".join(text)
                            if file_len > 0:
                                info.close()
                                info = open("data/user_info.txt", "w")
                                info.write(text)
                                info.close()
                            else:
                                info = open("data/user_info.txt", "w")
                                info.write(username.decode("utf-8") + "," + str(datetime.datetime.now()) + "," + "0" + "," + "" + "," + "" + "," + "")
                                info.close()
                        else:
                            info = open("data/user_info.txt", "w")
                            info.write(username.decode("utf-8") + "," + str(datetime.datetime.now()) + "," + "0" + "," + "" + "," + "" + "," + "")
                            info.close()
                        welcome_text = Label(page, text="Welcome {}".format(username.decode("utf-8")), bg="#161616", fg="white", font=('Segoe UI', '20'))
                        about_text = Label(page, text="Enter values for each field then press submit", bg="#161616", fg="white", font=('Segoe UI', '15'))
                        welcome_text.place(x=1340, y=90, anchor="center")
                        about_text.place(x=1340, y=120, anchor="center")
                        login_panel(page, last_login)
                        send_email("Security Alert: \n\n\tA sucessfull login attempt occured at {}".format(datetime.datetime.now()), "Security Alert: Sucessfull Login Attempt", True)
                    if locked == True and tries < 1:
                        file = open("data/logins.txt","w+")
                        file.write(str(time.time()))
                        file.close()
                if request_timeout(time.time()) == False:
                    tries_text = Label(page, text="Error: Out of Attempts, wait {:.2f}s".format(to_wait), bg="#161616", fg="red", font=('Segoe UI', '10'), width=60)
                    tries_text.place(x=1553, y=183, anchor="e")
                    tries_text.after(2000, destroy_widgit, tries_text)

            def login(page):
                global username
                username_text = Label(page, text="Username: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                username_text.place(x=1290, y=83, anchor='e')
                password_text = Label(page, text="Password: ", bg="#161616", fg="white", font=('Segoe UI', '13'))
                password_text.place(x=1290, y=113, anchor='e')
                username = StringVar()
                password = StringVar()
                username_input = Entry(page, textvariable=username, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb")
                username_input.place(x=1290, y=76)
                password_input = Entry(page, textvariable=password, width=25, bg="#474747", fg="white", highlightcolor="#161616", bd=0, highlightthickness="1",  highlightbackground="#dbdbdb", show="•")
                password_input.place(x=1290, y=106)
                login_button = Button(page, text="Login", fg="white", bg="#474747", borderwidth=0, height = 1, width = 10, activebackground="#333333", activeforeground="white", command=lambda:sign_in(page, username.get().lower(), password.get(), username_text, password_text, username_input, password_input, login_button), font=('Segoe UI', '12'))
                login_button.place(x=1347, y=136)

            def check_csv():
                if os.path.isfile("data/data.csv") == False:
                    file = open("data/data.csv", "a", newline="")
                    writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
                    writer.writerow(["Report ID", "Time/Date", "Engineer", "Manufacturer", "Machine Model", "Machine ID", "Customer", "Contact", "Location", "Job Type", "Customer Charge", "Description"])
                    file.close()

            def setup():
                page = Frame(root, bg="#161616", width = 1920, height = 1000)
                page.place(x=0, y=15, anchor="nw")
                check_csv()
                report_head(page)
                login_head(page)
                login(page)
                time_now = collect_time(page)
                job_no(page)
                name = name_input(page)
                manufacturer_name, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge = machine_info(page)
                description = note_input(page)
                submit_setup(page, time_now, name, manufacturer_name, machine_model, machine_id, customer_name, contact_name, location, job_type, customer_charge, description)

            setup()

        def about(root):
            bar = Frame(root, bg="#333333")
            bar.place(x=800, y=900, anchor="s", width=1600)
            info1 = Label(bar, text="Version 1.5.0", bg="#333333", fg="white")
            info2 = Label(bar, text="Developed by Fraser Love", bg="#333333", fg="white")
            info3 = Label(bar, text="Partners: Evolution BPS", bg="#333333", fg="white")
            info1.grid(row=0, column=0, padx=10)
            info2.grid(row=0, column=1, padx=10)
            info3.grid(row=0, column=2, padx=10)

        main(root)
        navbar(root)
        about(root)

    root = initalise_app()
    root_screen(root)
    x_pos = int(root.winfo_screenwidth()/2)-800
    y_pos = int(root.winfo_screenheight()/2)-450
    root.geometry("1600x900+" + str(x_pos) + "+" + str(y_pos))
    root.resizable(0, 0)
    root.mainloop()

file_name_array = []
file_array = []
app()
