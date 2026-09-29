#2. Chạy chương trình Python đầu tiên trong project
print("CourseHub - Buoi 1")
#3. Mô phỏng dữ liệu bằng list và dictionary
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

#4. Duyệt dữ liệu và tính giá trị
for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")

#5. Tách xử lý thành hàm
def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None
print(find_course("INT2204"))

#6. Mô phỏng quy tắc đăng ký
def can_enroll(student_id, course_code):
    course = find_course(course_code)

    if course is None:
        return False, "Hoc phan khong ton tai"
    
    if course["enrolled"] >= course["capacity"]:
        return False, "Lop da du so luong"
    
    duplicated = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )
    if duplicated:
        return False, "Sinh vien da dang ky hoc phan nay"

    return True, "Co the dang ky"

print(can_enroll("22000002", "INT2204"))

#7. Xử lý dữ liệu nhập sai
try:
    limit = int(input("Nhap so luong hoc phan muon hien thi: "))
    print(courses[:limit])
except ValueError:
    print("So luong phai la so nguyen")

#8. Hàm tìm kiếm học phần
def search_courses(keyword):
    normalized = keyword.strip().lower()
    results = []

    for course in courses:
        code = course["code"].lower()
        name = course["name"].lower()
        if normalized in code or normalized in name:
            results.append(course)

    return results
print(search_courses("web"))

# 1. Hoàn thiện hàm đăng ký học phần
def enroll_student(student_id, course_code):
    student_exists = False

    for student in students:
        if student["id"] == student_id:
            student_exists = True
            break

    if not student_exists:
        print("Sinh vien khong ton tai")
        return

    can_register, message = can_enroll(student_id, course_code)

    if not can_register:
        print(message)
        return

    enrollments.append({
        "student_id": student_id,
        "course_code": course_code
    })

    course = find_course(course_code)
    course["enrolled"] = course["enrolled"] + 1

    print("Dang ky hoc phan thanh cong")

# 2. Kiểm tra chương trình
print("\n--- KIEM THU ---")

print("1. Dang ky thanh cong:")
enroll_student("22000002", "INT2204")

print("2. Dang ky trung:")
enroll_student("22000001", "INT2204")

print("3. Lop day:")
enroll_student("22000002", "INT2205")

print("4. Hoc phan khong ton tai:")
enroll_student("22000002", "INT9999")

print("5. Sinh vien khong ton tai:")
enroll_student("22000099", "INT2204")

# 3. Lưu thay đổi bằng Git/GitHub