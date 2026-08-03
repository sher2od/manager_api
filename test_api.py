"""
Manager API - To'liq API Test Skripti
Barcha endpointlarni test qiladi va natijalarni chiroyli ko'rsatadi.
"""
import json
import urllib.request
import urllib.error
import urllib.parse
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8001/api"

# Test natijalarini saqlash
results = []

def log(status, test_name, detail=""):
    icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    results.append((status, test_name, detail))
    print(f"  {icon} {test_name}")
    if detail:
        print(f"     -> {detail}")

def api_request(method, path, data=None, token=None):
    """API so'rov yuborish"""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = response.read().decode("utf-8")
            return response.status, json.loads(resp_data) if resp_data else {}
    except urllib.error.HTTPError as e:
        resp_data = e.read().decode("utf-8")
        try:
            return e.code, json.loads(resp_data)
        except:
            return e.code, {"raw": resp_data}
    except urllib.error.URLError as e:
        return 0, {"error": str(e)}

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ============================================================
# 1. SERVER HEALTH CHECK
# ============================================================
section("1. SERVER HEALTH CHECK")

status, data = api_request("GET", "/")
if status > 0:
    log("PASS", "Server ishlayapti", f"Status: {status}")
else:
    log("FAIL", "Server ishlamayapti", str(data))
    print("\n⛔ Server ishlamayapti! Testlarni to'xtatamiz.")
    sys.exit(1)

# ============================================================
# 2. AUTHENTICATION TESTS
# ============================================================
section("2. AUTHENTICATION - Ro'yxatdan o'tish va Login")

# 2.1 Admin user yaratish (test uchun)
admin_data = {
    "username": "test_admin",
    "email": "admin@test.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "Admin"
}
status, data = api_request("POST", "/register/", admin_data)
if status == 201:
    admin_id = data.get("id")
    log("PASS", "Admin foydalanuvchi ro'yxatdan o'tdi", f"ID: {admin_id}")
elif status == 400:
    log("WARN", "Admin foydalanuvchi allaqachon mavjud", str(data))
else:
    log("FAIL", "Admin foydalanuvchi yaratishda xato", f"Status: {status}, {data}")

# 2.2 Manager user yaratish
manager_data = {
    "username": "test_manager",
    "email": "manager@test.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "Manager"
}
status, data = api_request("POST", "/register/", manager_data)
if status == 201:
    manager_id = data.get("id")
    log("PASS", "Manager foydalanuvchi ro'yxatdan o'tdi", f"ID: {manager_id}")
elif status == 400:
    log("WARN", "Manager foydalanuvchi allaqachon mavjud", str(data))
else:
    log("FAIL", "Manager foydalanuvchi yaratishda xato", f"Status: {status}, {data}")

# 2.3 Employee user yaratish
employee_data = {
    "username": "test_employee",
    "email": "employee@test.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "Employee"
}
status, data = api_request("POST", "/register/", employee_data)
if status == 201:
    employee_id = data.get("id")
    log("PASS", "Employee foydalanuvchi ro'yxatdan o'tdi", f"ID: {employee_id}")
elif status == 400:
    log("WARN", "Employee foydalanuvchi allaqachon mavjud", str(data))
else:
    log("FAIL", "Employee foydalanuvchi yaratishda xato", f"Status: {status}, {data}")

# 2.4 Invalid registration (parol qisqa)
invalid_user = {
    "username": "",
    "email": "bad@test.com",
    "password": "123"
}
status, data = api_request("POST", "/register/", invalid_user)
if status == 400:
    log("PASS", "Noto'g'ri ro'yxatdan o'tish rad etildi (400)", str(data)[:100])
else:
    log("FAIL", "Noto'g'ri ma'lumotlar qabul qilindi", f"Status: {status}")

# 2.5 Login - Token olish
section("3. TOKEN - JWT Authentication")

status, data = api_request("POST", "/token/", {
    "username": "test_admin",
    "password": "TestPass123!"
})
if status == 200 and "access" in data:
    admin_token = data["access"]
    log("PASS", "Admin login muvaffaqiyatli", f"Token: {admin_token[:30]}...")
    if "username" in data:
        log("PASS", "Token javobda username mavjud", f"username: {data['username']}")
    if "role" in data:
        log("PASS", "Token javobda role mavjud", f"role: {data['role']}")
else:
    admin_token = None
    log("FAIL", "Admin login muvaffaqiyatsiz", f"Status: {status}, {data}")

# Manager login
status, data = api_request("POST", "/token/", {
    "username": "test_manager",
    "password": "TestPass123!"
})
if status == 200 and "access" in data:
    manager_token = data["access"]
    log("PASS", "Manager login muvaffaqiyatli", f"role: {data.get('role', 'N/A')}")
else:
    manager_token = None
    log("FAIL", "Manager login muvaffaqiyatsiz", f"Status: {status}, {data}")

# Employee login
status, data = api_request("POST", "/token/", {
    "username": "test_employee",
    "password": "TestPass123!"
})
if status == 200 and "access" in data:
    employee_token = data["access"]
    log("PASS", "Employee login muvaffaqiyatli", f"role: {data.get('role', 'N/A')}")
else:
    employee_token = None
    log("FAIL", "Employee login muvaffaqiyatsiz", f"Status: {status}, {data}")

# Noto'g'ri parol bilan login
status, data = api_request("POST", "/token/", {
    "username": "test_admin",
    "password": "WrongPassword"
})
if status == 401:
    log("PASS", "Noto'g'ri parol bilan login rad etildi (401)")
else:
    log("FAIL", "Noto'g'ri parol bilan login xato", f"Status: {status}")

# ============================================================
# 4. USERS MANAGEMENT TESTS
# ============================================================
section("4. USERS MANAGEMENT")

# 4.1 Foydalanuvchilar ro'yxati (admin token bilan)
if admin_token:
    status, data = api_request("GET", "/users/", token=admin_token)
    if status == 200:
        log("PASS", "Foydalanuvchilar ro'yxati (admin)", f"Jami: {len(data) if isinstance(data, list) else 'N/A'}")
    else:
        log("FAIL", "Foydalanuvchilar ro'yxati (admin)", f"Status: {status}, {data}")

# 4.2 Employee token bilan - ruxsat yo'q bo'lishi kerak
if employee_token:
    status, data = api_request("GET", "/users/", token=employee_token)
    if status == 403:
        log("PASS", "Employee foydalanuvchilar ro'yxatini ko'ra olmaydi (403)")
    else:
        log("FAIL", "Employee ruxsatsiz foydalanuvchilarni ko'ra oldi", f"Status: {status}")

# 4.3 Token siz so'rov - 401 bo'lishi kerak
status, data = api_request("GET", "/users/")
if status == 401:
    log("PASS", "Autentifikatsiyasiz so'rov rad etildi (401)")
else:
    log("FAIL", "Autentifikatsiyasiz so'rov qabul qilindi", f"Status: {status}")

# 4.4 Assign manager role (admin bilan)
# Avval employee ID ni topamiz
if admin_token:
    status, users_data = api_request("GET", "/users/", token=admin_token)
    employee_user = None
    if status == 200 and isinstance(users_data, list):
        for u in users_data:
            if u.get("username") == "test_manager":
                employee_user = u
                break
    
    if employee_user:
        status, data = api_request("POST", f"/users/{employee_user['id']}/assign-manager/", token=admin_token)
        if status == 200:
            log("PASS", "Manager roli tayinlandi", str(data))
        else:
            log("FAIL", "Manager roli tayinlashda xato", f"Status: {status}, {data}")

# ============================================================
# 5. PROJECTS TESTS
# ============================================================
section("5. PROJECTS - Loyihalar boshqaruvi")

# Avval manager login qilsin (yangilangan role bilan)
status, data = api_request("POST", "/token/", {
    "username": "test_manager",
    "password": "TestPass123!"
})
if status == 200:
    manager_token = data["access"]

project_id = None

# 5.1 Loyiha yaratish (manager bilan)
if manager_token:
    project_data = {
        "title": "Test Loyiha",
        "description": "Bu test uchun yaratilgan loyiha",
        "end_date": "2026-12-31"
    }
    status, data = api_request("POST", "/projects/", project_data, token=manager_token)
    if status == 201:
        project_id = data.get("id")
        log("PASS", "Loyiha yaratildi (manager)", f"ID: {project_id}, Title: {data.get('title')}")
    else:
        log("FAIL", "Loyiha yaratishda xato", f"Status: {status}, {data}")

# 5.2 Loyihalar ro'yxati
if manager_token:
    status, data = api_request("GET", "/projects/", token=manager_token)
    if status == 200:
        count = len(data) if isinstance(data, list) else data.get("count", "N/A")
        log("PASS", "Loyihalar ro'yxati", f"Jami: {count}")
    else:
        log("FAIL", "Loyihalar ro'yxati", f"Status: {status}")

# 5.3 Bitta loyiha detail
if manager_token and project_id:
    status, data = api_request("GET", f"/projects/{project_id}/", token=manager_token)
    if status == 200:
        log("PASS", "Loyiha detail", f"Title: {data.get('title')}")
    else:
        log("FAIL", "Loyiha detail", f"Status: {status}")

# 5.4 Loyiha yangilash (PATCH)
if manager_token and project_id:
    status, data = api_request("PATCH", f"/projects/{project_id}/", 
                                {"title": "Yangilangan Loyiha"}, token=manager_token)
    if status == 200:
        log("PASS", "Loyiha yangilandi (PATCH)", f"Yangi title: {data.get('title')}")
    else:
        log("FAIL", "Loyiha yangilash", f"Status: {status}, {data}")

# 5.5 Employee loyiha yarata olmaydi
if employee_token:
    status, data = api_request("POST", "/projects/", 
                                {"title": "Employee Loyiha"}, token=employee_token)
    if status == 403:
        log("PASS", "Employee loyiha yarata olmaydi (403)")
    else:
        log("FAIL", "Employee loyiha yaratdi - bu xato!", f"Status: {status}")

# ============================================================
# 6. TASKS TESTS
# ============================================================
section("6. TASKS - Vazifalar boshqaruvi")

task_id = None

# 6.1 Task yaratish (manager bilan)
if manager_token and project_id:
    # Employee ID topamiz
    status, users = api_request("GET", "/users/", token=manager_token)
    assignee_id = None
    if status == 200 and isinstance(users, list):
        for u in users:
            if u.get("username") == "test_employee":
                assignee_id = u.get("id")
                break
    
    task_data = {
        "title": "Test Vazifa",
        "description": "Bu test uchun yaratilgan vazifa",
        "project": project_id,
        "assignee": assignee_id,
        "status": "new",
        "priority": "high",
        "deadline": "2026-12-31T23:59:59Z"
    }
    status, data = api_request("POST", "/tasks/", task_data, token=manager_token)
    if status == 201:
        task_id = data.get("id")
        log("PASS", "Task yaratildi (manager)", f"ID: {task_id}, Title: {data.get('title')}")
    else:
        log("FAIL", "Task yaratishda xato", f"Status: {status}, {data}")

# 6.2 Task ro'yxati (manager - barchani ko'radi)
if manager_token:
    status, data = api_request("GET", "/tasks/", token=manager_token)
    if status == 200:
        count = len(data) if isinstance(data, list) else data.get("count", "N/A")
        log("PASS", "Tasks ro'yxati (manager - all)", f"Jami: {count}")
    else:
        log("FAIL", "Tasks ro'yxati", f"Status: {status}")

# 6.3 Task ro'yxati (employee - faqat o'ziga tayinlangan)
if employee_token:
    status, data = api_request("GET", "/tasks/", token=employee_token)
    if status == 200:
        count = len(data) if isinstance(data, list) else data.get("count", "N/A")
        log("PASS", "Tasks ro'yxati (employee - assigned only)", f"Jami: {count}")
    else:
        log("FAIL", "Tasks ro'yxati (employee)", f"Status: {status}")

# 6.4 Employee task yarata olmaydi
if employee_token and project_id:
    status, data = api_request("POST", "/tasks/", {
        "title": "Employee Task",
        "description": "Bu yaratilmasligi kerak",
        "project": project_id,
        "status": "new",
        "priority": "low",
        "deadline": "2026-12-31T23:59:59Z"
    }, token=employee_token)
    if status == 403:
        log("PASS", "Employee task yarata olmaydi (403)")
    else:
        log("FAIL", "Employee task yaratdi - bu xato!", f"Status: {status}, {data}")

# 6.5 Task status yangilash
if manager_token and task_id:
    status, data = api_request("PATCH", f"/tasks/{task_id}/", 
                                {"status": "in_progress"}, token=manager_token)
    if status == 200:
        log("PASS", "Task status yangilandi", f"Yangi status: {data.get('status')}")
    else:
        log("FAIL", "Task status yangilash", f"Status: {status}, {data}")

# 6.6 Task detail
if manager_token and task_id:
    status, data = api_request("GET", f"/tasks/{task_id}/", token=manager_token)
    if status == 200:
        log("PASS", "Task detail", f"Title: {data.get('title')}, Status: {data.get('status')}")
    else:
        log("FAIL", "Task detail", f"Status: {status}")

# ============================================================
# 7. COMMENTS TESTS
# ============================================================
section("7. COMMENTS - Izohlar")

comment_id = None

# 7.1 Izoh yozish (employee bilan)
if employee_token and task_id:
    status, data = api_request("POST", "/comments/", {
        "task": task_id,
        "content": "Bu test izoh - Employee tomonidan"
    }, token=employee_token)
    if status == 201:
        comment_id = data.get("id")
        log("PASS", "Izoh yozildi (employee)", f"ID: {comment_id}")
    else:
        log("FAIL", "Izoh yozishda xato", f"Status: {status}, {data}")

# 7.2 Izoh yozish (manager bilan)
if manager_token and task_id:
    status, data = api_request("POST", "/comments/", {
        "task": task_id,
        "content": "Bu test izoh - Manager tomonidan"
    }, token=manager_token)
    if status == 201:
        log("PASS", "Izoh yozildi (manager)", f"ID: {data.get('id')}")
    else:
        log("FAIL", "Izoh yozishda xato (manager)", f"Status: {status}, {data}")

# 7.3 Izohlar ro'yxati
if employee_token:
    status, data = api_request("GET", "/comments/", token=employee_token)
    if status == 200:
        count = len(data) if isinstance(data, list) else data.get("count", "N/A")
        log("PASS", "Izohlar ro'yxati", f"Jami: {count}")
    else:
        log("FAIL", "Izohlar ro'yxati", f"Status: {status}")

# 7.4 Izoh detail
if employee_token and comment_id:
    status, data = api_request("GET", f"/comments/{comment_id}/", token=employee_token)
    if status == 200:
        log("PASS", "Izoh detail", f"Content: {data.get('content', '')[:50]}")
    else:
        log("FAIL", "Izoh detail", f"Status: {status}")

# 7.5 Token siz izoh - 401
status, data = api_request("POST", "/comments/", {"task": 1, "content": "test"})
if status == 401:
    log("PASS", "Autentifikatsiyasiz izoh rad etildi (401)")
else:
    log("FAIL", "Autentifikatsiyasiz izoh xatosi", f"Status: {status}")

# ============================================================
# 8. API SCHEMA / DOCS
# ============================================================
section("8. API DOCUMENTATION")

try:
    req_schema = urllib.request.Request(f"{BASE_URL}/schema/")
    with urllib.request.urlopen(req_schema) as response:
        if response.status == 200:
            log("PASS", "OpenAPI Schema mavjud", f"Status: {response.status}")
        else:
            log("FAIL", "OpenAPI Schema", f"Status: {response.status}")
except Exception as e:
    log("FAIL", "OpenAPI Schema", str(e))

# Swagger UI
req = urllib.request.Request(f"{BASE_URL}/docs/")
try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            log("PASS", "Swagger UI mavjud", f"Status: {response.status}")
        else:
            log("FAIL", "Swagger UI", f"Status: {response.status}")
except Exception as e:
    log("FAIL", "Swagger UI", str(e))

# ============================================================
# 9. EDGE CASES
# ============================================================
section("9. EDGE CASES - Chegaraviy holatlar")

# 9.1 Mavjud bo'lmagan endpoint
status, data = api_request("GET", "/nonexistent/")
if status == 404:
    log("PASS", "Mavjud bo'lmagan endpoint 404 qaytaradi")
else:
    log("FAIL", "Mavjud bo'lmagan endpoint", f"Status: {status}")

# 9.2 Mavjud bo'lmagan ID bilan so'rov
if manager_token:
    status, data = api_request("GET", "/tasks/99999/", token=manager_token)
    if status == 404:
        log("PASS", "Mavjud bo'lmagan task ID 404 qaytaradi")
    else:
        log("FAIL", "Mavjud bo'lmagan task ID", f"Status: {status}")

# 9.3 Noto'g'ri ma'lumot bilan task yaratish
if manager_token:
    status, data = api_request("POST", "/tasks/", {
        "title": "",
        "description": ""
    }, token=manager_token)
    if status == 400:
        log("PASS", "Noto'g'ri ma'lumot bilan task yaratish rad etildi (400)")
    else:
        log("FAIL", "Validatsiya xatosi", f"Status: {status}, {data}")

# ============================================================
# 10. CLEANUP - Test ma'lumotlarini o'chirish
# ============================================================
section("10. DELETE OPERATIONS")

# 10.1 Izoh o'chirish
if manager_token and comment_id:
    status, data = api_request("DELETE", f"/comments/{comment_id}/", token=manager_token)
    if status == 204:
        log("PASS", "Izoh o'chirildi (DELETE)")
    else:
        log("FAIL", "Izoh o'chirish", f"Status: {status}")

# 10.2 Task o'chirish
if manager_token and task_id:
    status, data = api_request("DELETE", f"/tasks/{task_id}/", token=manager_token)
    if status == 204:
        log("PASS", "Task o'chirildi (DELETE)")
    else:
        log("FAIL", "Task o'chirish", f"Status: {status}")

# 10.3 Project o'chirish
if manager_token and project_id:
    status, data = api_request("DELETE", f"/projects/{project_id}/", token=manager_token)
    if status == 204:
        log("PASS", "Loyiha o'chirildi (DELETE)")
    else:
        log("FAIL", "Loyiha o'chirish", f"Status: {status}")

# ============================================================
# SUMMARY
# ============================================================
section("UMUMIY NATIJA")

passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
warned = sum(1 for r in results if r[0] == "WARN")
total = len(results)

print(f"\n  [PASS] Muvaffaqiyatli: {passed}")
print(f"  [FAIL] Muvaffaqiyatsiz: {failed}")
print(f"  [WARN] Ogohlantirish: {warned}")
print(f"  [TOTAL] Jami testlar: {total}")
print(f"\n  Natija: {'BARCHA TESTLAR OTDI!' if failed == 0 else 'BAZI TESTLAR MUVAFFAQIYATSIZ'}")

if failed > 0:
    print(f"\n  Muvaffaqiyatsiz testlar:")
    for r in results:
        if r[0] == "FAIL":
            print(f"     - {r[1]}: {r[2]}")

print(f"\n{'='*60}\n")

