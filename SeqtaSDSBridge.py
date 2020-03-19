###########################################################################################################
###########################################################################################################
##                                            SeqtaToSDS                                                ##
##                                          Jacob Curulli                                                ##
## This code is shared as is, under Creative Commons Attribution Non-Commercial 4.0 License              ##
## Permissions beyond the scope of this license may be available at http://creativecommons.org/ns        ##
###########################################################################################################

# Read Me
# This script will likely not work out of the box and will need to be customised
# 1.    The approvedClassesCSV is a list of classes in Seqta that will be exported,
#       the list is checked against the 'name' column in the public.classunit table.
# 2.    A directory called 'sds' will need to be created in the root of where the script is run.
# 3.    This script allows for an admin user to be added to every class (section)

# import required modules
# psycopg2 isn't usually included with python and may need to be installed separately
# see www.psycopg.org for instructions

import psycopg2
import csv
import os.path
import configparser
from datetime import datetime

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# read config file for seqta database connection details
db_user=config['db']['user']
db_port=config['db']['port']
db_password=config['db']['password']
db_database=config['db']['database']
db_host=config['db']['host']
db_sslmode=config['db']['sslmode']

# read config file for school details
teamsAdminUsername=config['school']['teamsAdminUsername']
teamsAdminFirstName=config['school']['teamsAdminFirstName']
teamsAdminLastName=config['school']['teamsAdminLastName']
teamsAdminID=config['school']['teamsAdminID']
schoolName =config['school']['schoolName']
schoolSISId=config['school']['schoolSISId']
classTermName=config['school']['classTermName']

# declare some variables here so we can make sure they are present
staffList = set()
studentList = set()
classArray = tuple()
currentYear = datetime.now().year
print("current year is:", currentYear)

# file locations, this can be changed to suit your environment
csvApprovedClasses = "approved_classes.csv"
csvSchoolFilename = "sds/School.csv"
csvSectionFileName = "sds/Section.csv"
csvStudentFileName = "sds/Student.csv"
csvTeacherFileName = "sds/Teacher.csv"
csvTeacherRosterFileName = "sds/TeacherRoster.csv"
csvStudentEnrollmentFileName = "sds/StudentEnrollment.csv"

# remove the csv files if they already exist. This is a messy way of doing it but I learnt python 2 days ago so whatever
if os.path.exists(csvSchoolFilename):
    os.remove(csvSchoolFilename)
if os.path.exists(csvSectionFileName):
    os.remove(csvSectionFileName)
if os.path.exists(csvStudentFileName):
    os.remove(csvStudentFileName)
if os.path.exists(csvTeacherFileName):
    os.remove(csvTeacherFileName)
if os.path.exists(csvTeacherRosterFileName):
    os.remove(csvTeacherRosterFileName)
if os.path.exists(csvStudentEnrollmentFileName):
    os.remove(csvStudentEnrollmentFileName)

try:
    # Import CSV file for approved class lists
    with open(csvApprovedClasses, newline='', encoding='utf-8-sig') as csvfile:
        classList = list(csv.reader(csvfile))
        print (type(classList))
        print (classList)
        print ("Number of classes imported from csv: ",classList.count())

except:
    print("***************************")
    print("Error importing csv file")

# Open connection to Seqta
try:
    connection = psycopg2.connect(user=db_user,
                                  port=db_port,
                                  password=db_password,
                                  database=db_database,
                                  host = db_host,
                                  sslmode = db_sslmode)
    cursor = connection.cursor()
    print(connection.get_dsn_parameters(), "\n")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

# Fetch data for classlists
try:
    for i in classList:
        className = str(('[%s]' % ', '.join(map(str, (i))))[1:-1])
        print ("**")
        print (className)
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()

        # Lookup classID from Class name in Seqta
        sq_classUnitQuery = "SELECT * FROM public.classunit WHERE name = (%s);"
        cursor.execute(sq_classUnitQuery,(className,))
        classUnitPull = cursor.fetchall()
        print("Getting class information for:", (className))
        for row in classUnitPull:
            classUnitID = row[0]
            classSubjectID = row[4]
            classTermID = row[7]

        print("Class unit ID (classUnitID) is:", classUnitID)
        print("Class subject ID (classSubjectID) is:", classSubjectID)
        print("Class term ID (classTermID) is:", classTermID)

        # Check if class has a staff member or students
        # If they don't we need to stop processing the class and drop it gracefully


        # Get subject description for Class
        sq_classSubjectQuery = "SELECT * FROM subject WHERE id = (%s);"
        cursor.execute(sq_classSubjectQuery, (classSubjectID,))
        classSubjectPull = cursor.fetchall()
        for row in classSubjectPull:
            classSubjectDescription = row[3]
            classSubjectName = row[2]
        classTeamName = (className + " - " + classSubjectDescription)
        print("Class subject Description (classSubjectDescription) is:", classSubjectDescription)
        print("Class team name (classTeamName) is:", classTeamName)
        print("Class subject Name (classSubjectName) is:", classSubjectName)

        # Get StaffID in this classUnit
        sq_staffIDQuery = "SELECT staff from public.classinstance WHERE classunit = (%s);"
        cursor.execute(sq_staffIDQuery, (classUnitID,))
        staffID_pre = cursor.fetchone()
        staffID = int(staffID_pre[0])
        print("Staff ID is:", (staffID))
        # Write to teacher ID list
        staffList.add(staffID)

        # Get Student ID's for this classUnit
        sq_studentIDListQuery = "SELECT student from \"classunitStudent\" WHERE classunit = (%s) and removed is NULL;"
        cursor.execute(sq_studentIDListQuery, (classUnitID,))
        studentIDArray = tuple([r[0] for r in cursor.fetchall()])
        print("List of students in class name:", className)
        print(studentIDArray)
        for row in studentIDArray:
            studentList.add(row)

        # Check if the csv section file exists
        csvSectionFileExists = os.path.isfile(csvSectionFileName)
        # Write to the section csv file
        with open(csvSectionFileName, 'a', newline='') as csvSection:
            writer = csv.writer(csvSection)
            # If the csv doesn't exist already we'll need to put in the headers
            if not csvSectionFileExists:
                writer.writerow(["SIS ID", "School SIS ID", "Section Name", "Section Number", "Term SIS ID", "Term Name", "Course SIS ID", "Course Name", "Course Description"])
            writer.writerow([(classUnitID), (schoolSISId), (classTeamName), (classUnitID), (classTermID), (classTermName), (classUnitID), (classSubjectName), (classSubjectDescription)])
            print ("Writing class section row:")

        # Check if the csv teacher roster file exists
        csvTeacherRosterFileExists = os.path.isfile(csvTeacherRosterFileName)
        # Write to the teacher roster csv file
        with open(csvTeacherRosterFileName, 'a', newline='') as csvTeacherRoster:
            writer = csv.writer(csvTeacherRoster)
        # If the csv doesn't exist already we'll need to put in the headers
            if not csvTeacherRosterFileExists:
                    writer.writerow(["Section SIS ID", "SIS ID"])
            writer.writerow([(classUnitID), (staffID)])
            # Also include the Teams Admin account as a teacher
            writer.writerow([(classUnitID), (teamsAdminID)])
            print("Written staff to roster")
        # Check if the csv student enrollment file exists
        csvStudentEnrollmentFileNameExists = os.path.isfile(csvStudentEnrollmentFileName)
        # Write to the student enrollment csv file
        with open(csvStudentEnrollmentFileName, 'a', newline='') as csvStudentEnrollment:
            writer = csv.writer(csvStudentEnrollment)
            # If the csv doesn't exist already we'll need to put in the headers
            if not csvStudentEnrollmentFileNameExists:
                writer.writerow(["Section SIS ID", "SIS ID"])
            for studentInArray in studentIDArray:
                writer.writerow([(classUnitID), (studentInArray)])
except:
    print("")
    print("***************************")
    print("Error fetching class list data")
    print("")

# Now we will fetch the staff information
try:
    print("Print the staff lists now")
    print(staffList)

    for staff in staffList:

        # Now get the staff information
        sq_staffQuery = "SELECT * from public.staff WHERE id = (%s);"
        cursor.execute(sq_staffQuery, (staff,))
        staffPull = cursor.fetchall()
        for row in staffPull:
            staffFirstName = row[4]
            staffLastName = row[7]
            staffUsername = row[21]

        print("Staff First Name (staffFirstName) is:", staffFirstName)
        print("Staff Last Name (staffLastName) is:", staffLastName)
        print("Staff username (staffUsername) is:", staffUsername)
        print("Staff ID is (staff) is:", staff)

        # Now we write this information to the Teacher.csv file
        # Check if the csv teacher file exists
        csvTeacherFileNameExists = os.path.isfile(csvTeacherFileName)
        # Write to the teacher csv file
        with open(csvTeacherFileName, 'a', newline='') as csvTeacher:
            writer = csv.writer(csvTeacher)
            # If the csv doesn't exist already we'll need to put in the headers
            if not csvTeacherFileNameExists:
                writer.writerow(["SIS ID", "School SIS ID", "First Name", "Last Name", "Username", "Teacher Number"])
                # Also include the Teams Admin user as a teacher
                writer.writerow(
                    [(teamsAdminID), (schoolSISId), (teamsAdminFirstName), (teamsAdminLastName), (teamsAdminUsername),
                     (teamsAdminID)])
            writer.writerow([(staff), (schoolSISId), (staffFirstName), (staffLastName), (staffUsername), (staff)])
except:
    print("something went wrong getting the staff data")

# Now we will fetch the student information
try:
    print("Print the student lists now")
    print(studentList)

    for student in studentList:

        # Now get the student information
        sq_studentQuery = "SELECT * from student WHERE id = (%s) AND status = 'FULL';"
        cursor.execute(sq_studentQuery, (student,))
        studentPull = cursor.fetchall()
        for row in studentPull:
            studentFirstName = row[3]
            studentLastName = row[6]
            studentUsername = row[47]

        print("Student First Name (studentFirstName) is:", studentFirstName)
        print("Student Last Name (studentLastName) is:", studentLastName)
        print("Student username (studentUsername) is:", studentUsername)
        print("Student ID is (student) is:", student)

        # Now we write this information to the Student.csv file
        # Check if the csv Student file exists
        csvStudentFileNameExists = os.path.isfile(csvStudentFileName)
        # Write to the student enrollment csv file
        with open(csvStudentFileName, 'a', newline='') as csvStudent:
            writer = csv.writer(csvStudent)
            # If the csv doesn't exist already we'll need to put in the headers
            if not csvStudentFileNameExists:
                writer.writerow(["SIS ID", "School SIS ID", "First Name", "Last Name", "Username", "Student Number"])
            writer.writerow([(student), (schoolSISId), (studentFirstName), (studentLastName), (studentUsername), (student)])
except:
    print("something went wrong getting the student data")

# write the School.csv file
try:
    with open('sds/School.csv', 'a', newline='') as csvSchool:
        writer = csv.writer(csvSchool)
        writer.writerow(["SIS ID","Name"])
        writer.writerow([(schoolSISId),(schoolName)])
except:
    print("something went wrong writing the school csv file")

finally:
    # closing database connection.
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")