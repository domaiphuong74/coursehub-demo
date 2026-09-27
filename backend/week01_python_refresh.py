print("CourseHub - Buoi 1")

students = [
{"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
{"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
]
courses = [
{
"code": "INT2204",
"name": "Co so du lieu Web va he thong thong tin",
"capacity": 3,
"enrolled": 2,
},
{
"code": "INT2205",
"name": "Khai pha du lieu",
"capacity": 2,
"enrolled": 2,
},
]
enrollments = [
{"student_id": "22000001", "course_code": "INT2204"}
]
for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")

def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    
print(find_course("INT2204"))