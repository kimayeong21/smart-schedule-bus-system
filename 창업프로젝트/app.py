# ==========================================================
# app.py — Smart Schedule & Bus Real-Time System (FINAL)
# nodeId 기반 실시간 조회 + 현재 버스 위치(/bus/where) 기능 포함
# ==========================================================

from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3
import requests
import urllib.parse
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# ----------------------------------------------------------
# Flask 설정
# ----------------------------------------------------------
app = Flask(__name__)
app.secret_key = "smart_bus_schedule_secret"

DB_FILE = "smartbus.db"
CITY_CODE = "33010"  # 청주시

SERVICE_KEY = urllib.parse.quote(
    "dc03c0f94d438e60f14a19e2d867743b4d91d9cc78299af0ee1016ee26c96fd9"
)

# ----------------------------------------------------------
# DB 연결
# ----------------------------------------------------------
def get_conn():
    return sqlite3.connect(DB_FILE)

# ----------------------------------------------------------
# DB 초기화
# ----------------------------------------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            name TEXT,
            role TEXT DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            date TEXT,
            place TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            detail TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_db()

# ----------------------------------------------------------
# 로그 저장
# ----------------------------------------------------------
def write_log(uid, action, detail):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (user_id, action, detail) VALUES (?, ?, ?)",
        (uid, action, detail)
    )
    conn.commit()
    conn.close()


# ==========================================================
# 메인 / 로그인 / 회원가입 / 로그아웃
# ==========================================================

@app.route("/")
def main_page():
    return render_template("main.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"].strip()
        p = request.form["password"].strip()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, role FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()
        conn.close()

        if not user:
            return render_template("login.html", error="❌ 아이디 또는 비밀번호 오류")

        session["user_id"] = user[0]
        session["username"] = user[1]
        session["role"] = user[2]

        write_log(user[0], "login", f"{u} 로그인")

        return redirect(url_for("admin_page" if user[2]=="admin" else "calendar"))

    return render_template("login.html")


@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        is_admin = "is_admin" in request.form

        role = "admin" if is_admin else "user"

        if is_admin:
            if not re.match(r"^[A-Z0-9]+$", username):
                return render_template("signup.html", error="관리자 ID는 대문자+숫자 조합입니다.")

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (name, username, password, role)
                VALUES (?, ?, ?, ?)
            """, (name, username, password, role))
            conn.commit()
            conn.close()

        except sqlite3.IntegrityError:
            return render_template("signup.html", error="이미 존재하는 아이디입니다.")

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        write_log(session["user_id"], "logout", "로그아웃")
    session.clear()
    return redirect(url_for("main_page"))


# ==========================================================
# 관리자 기능
# ==========================================================

@app.route("/admin")
def admin_page():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")


@app.route("/admin/users")
def admin_users():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, name, role FROM users")
    rows = cur.fetchall()
    conn.close()
    return render_template("admin_users.html", users=rows)


@app.route("/admin/user/<int:uid>")
def admin_user_detail(uid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, username, name, role FROM users WHERE id=?", (uid,))
    user = cur.fetchone()

    cur.execute("SELECT title, date, place FROM schedules WHERE user_id=?", (uid,))
    schedules = cur.fetchall()

    conn.close()

    return render_template("admin_user_detail.html", user=user, schedules=schedules)


@app.route("/admin/schedules")
def admin_schedules():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.name, schedules.title, schedules.date,
               schedules.place, schedules.id
        FROM schedules
        JOIN users ON users.id = schedules.user_id
        ORDER BY schedules.date
    """)
    items = cur.fetchall()
    conn.close()

    return render_template("admin_schedules.html", items=items)


@app.route("/admin/schedule/delete/<int:sid>")
def admin_schedule_delete(sid):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM schedules WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_schedules"))


@app.route("/admin/logs")
def admin_logs():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.name, logs.action, logs.detail, logs.time
        FROM logs
        JOIN users ON users.id = logs.user_id
        ORDER BY logs.time DESC
    """)
    logs = cur.fetchall()
    conn.close()

    return render_template("admin_logs.html", logs=logs)


# ==========================================================
# 일정 기능
# ==========================================================

@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, date, place FROM schedules WHERE user_id=?",
                (session["user_id"],))
    rows = cur.fetchall()
    conn.close()

    schedules = [{"id": r[0], "title": r[1], "date": r[2], "place": r[3]} for r in rows]

    return render_template("calendar.html",
                           username=session["username"],
                           schedules=schedules)


@app.route("/schedule", methods=["POST"])
def schedule_edit():
    if "user_id" not in session:
        return jsonify({"ok": False})

    act = request.form["action"]
    conn = get_conn()
    cur = conn.cursor()

    if act == "add":
        cur.execute("""
            INSERT INTO schedules (user_id, title, date, place)
            VALUES (?, ?, ?, ?)
        """, (
            session["user_id"],
            request.form["title"],
            request.form["date"],
            request.form["place"]
        ))

    elif act == "update":
        cur.execute("""
            UPDATE schedules SET title=?, date=?, place=?
            WHERE id=? AND user_id=?
        """, (
            request.form["title"],
            request.form["date"],
            request.form["place"],
            request.form["id"],
            session["user_id"]
        ))

    elif act == "delete":
        cur.execute("DELETE FROM schedules WHERE id=? AND user_id=?",
                    (request.form["id"], session["user_id"]))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ==========================================================
# 공통 API 요청(JSON 우선, 실패 시 XML)
# ==========================================================

def api_request(url, params):
    params["serviceKey"] = SERVICE_KEY
    params["_type"] = "json"
    try:
        r = requests.get(url, params=params, timeout=4)
        return r.json()
    except:
        return None


# ==========================================================
# routeId 조회
# ==========================================================

def get_route_id(bus_no):
    url = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList"
    params = {"cityCode": CITY_CODE, "routeNo": bus_no}

    data = api_request(url, params)
    try:
        item = data["response"]["body"]["items"]["item"]
        return item[0]["routeid"] if isinstance(item, list) else item["routeid"]
    except:
        pass

    # XML fallback
    try:
        xml = requests.get(url, params=params).text
        root = ET.fromstring(xml)
        for it in root.iter("item"):
            rid = it.findtext("routeid")
            if rid:
                return rid
    except:
        pass

    return None


# ==========================================================
# 출발/도착 정류장 정보
# ==========================================================

def get_route_info(route_id):
    url = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoItem"
    params = {"cityCode": CITY_CODE, "routeId": route_id}

    data = api_request(url, params)

    # JSON
    try:
        item = data["response"]["body"]["items"]["item"]
        return {"start": item.get("startnodenm"), "end": item.get("endnodenm")}
    except:
        pass

    # XML fallback
    try:
        xml = requests.get(url, params=params).text
        root = ET.fromstring(xml)
        for it in root.iter("item"):
            return {"start": it.findtext("startnodenm"), "end": it.findtext("endnodenm")}
    except:
        pass

    return {"start": None, "end": None}


# ==========================================================
# 경유 정류장 목록
# ==========================================================

def get_route_stations(route_id):
    url = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList"
    params = {"cityCode": CITY_CODE, "routeId": route_id}

    data = api_request(url, params)
    try:
        items = data["response"]["body"]["items"]["item"]
        if not isinstance(items, list):
            items = [items]
        return [{"nodeid": i["nodeid"], "nodenm": i["nodenm"]} for i in items]
    except:
        pass

    # XML fallback
    result = []
    try:
        xml = requests.get(url, params=params).text
        root = ET.fromstring(xml)
        for it in root.iter("item"):
            result.append({
                "nodeid": it.findtext("nodeid"),
                "nodenm": it.findtext("nodenm")
            })
    except:
        pass

    return result


# ==========================================================
# 정류장 도착 정보(nodeId 기반)
# ==========================================================

def get_arrival(node_id):
    url = "https://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList"
    params = {"cityCode": CITY_CODE, "nodeId": node_id}

    data = api_request(url, params)
    items = None

    # JSON
    try:
        items = data["response"]["body"]["items"]["item"]
    except:
        pass

    # XML fallback
    if items is None:
        try:
            xml = requests.get(url, params=params).text
            root = ET.fromstring(xml)
            items = []
            for it in root.iter("item"):
                items.append({
                    "routeno": it.findtext("routeno"),
                    "arrtime": it.findtext("arrtime")
                })
        except:
            return []

    if not isinstance(items, list):
        items = [items]

    results = []
    for it in items:
        bus = it["routeno"]
        sec = int(it["arrtime"])
        remain = sec // 60
        arrival_clock = (datetime.now() + timedelta(minutes=remain)).strftime("%H:%M")

        results.append({
            "bus": bus,
            "time": remain,
            "text": f"{bus}번 {remain}분 후 도착 (예정: {arrival_clock})"
        })

    return sorted(results, key=lambda x: x["time"])


# ==========================================================
# 버스 기본 페이지
# ==========================================================

@app.route("/bus")
def bus_page():
    return render_template("bus.html")


# ==========================================================
# 버스번호 검색 → 노선 & 정류장 목록 반환
# ==========================================================

@app.route("/bus/search")
def bus_search():
    bus_no = request.args.get("bus_no", "").strip()

    rid = get_route_id(bus_no)
    if not rid:
        return jsonify({"ok": False, "error": "해당 버스를 찾을 수 없습니다."})

    info = get_route_info(rid)
    stops = get_route_stations(rid)

    return jsonify({"ok": True, "info": info, "stops": stops})


# ==========================================================
# 정류장 실시간 조회 — nodeId 기반!
# ==========================================================

@app.route("/bus/arrival")
def bus_arrival():
    nodeid = request.args.get("nodeId")

    if not nodeid:
        return jsonify({"ok": True, "arrivals": []})

    arrivals = get_arrival(nodeid)
    return jsonify({"ok": True, "arrivals": [a["text"] for a in arrivals]})


# ==========================================================
# 🔥 현재 버스 위치 조회 — 가장 가까운 정류장 계산
# ==========================================================

@app.route("/bus/where")
def bus_where():
    bus_no = request.args.get("bus_no", "").strip()

    if not bus_no:
        return jsonify({"ok": False, "error": "버스 번호 필요"})

    rid = get_route_id(bus_no)
    if not rid:
        return jsonify({"ok": False, "error": "해당 버스를 찾을 수 없습니다."})

    stops = get_route_stations(rid)
    best = None

    for st in stops:
        nodeId = st["nodeid"]
        nodeNm = st["nodenm"]

        arrivals = get_arrival(nodeId)

        for a in arrivals:
            if a["bus"] == bus_no:
                if best is None or a["time"] < best["time"]:
                    best = {
                        "stop": nodeNm,
                        "time": a["time"],
                        "text": a["text"]
                    }

    return jsonify({"ok": True, "best": best})


# ==========================================================
# 전체 실시간 UI 페이지
# ==========================================================

@app.route("/bus/live-ui")
def bus_live_ui():
    return render_template("bus_live.html")


# ==========================================================
# 실행
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)
