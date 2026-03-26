# bussu.py
import urllib.parse
import requests

SERVICE_KEY = urllib.parse.quote(
    "dc03c0f94d438e60f14a19e2d867743b4d91d9cc78299af0ee1016ee26c96fd9"
)

# 청주시 도시코드 (네가 준 URL 기준)
CITY_CODE = "33010"

def _api_get(url, params):
    params = dict(params)
    params["serviceKey"] = SERVICE_KEY
    params["_type"] = "json"
    try:
        res = requests.get(url, params=params, timeout=7)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ API 오류:", e)
        return None


# 🚍 1) 버스번호 → 노선ID
def get_route_id(route_no):
    url = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList"
    data = _api_get(url, {"cityCode": CITY_CODE, "routeNo": route_no, "pageNo": 1, "numOfRows": 50})
    if not data:
        return None

    try:
        items = data["response"]["body"]["items"]["item"]
        if isinstance(items, list):
            return items[0]["routeid"]
        return items["routeid"]
    except Exception:
        return None


# 🚌 2) 노선ID → 상세정보
def get_route_info(route_id):
    url = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem"
    data = _api_get(url, {"cityCode": CITY_CODE, "routeId": route_id})
    if not data:
        return None
    try:
        return data["response"]["body"]["items"]["item"]
    except Exception:
        return None


# 🚏 3) 노선ID → 경유 정류장 목록
def get_route_stations(route_id):
    url = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList"
    data = _api_get(url, {"cityCode": CITY_CODE, "routeId": route_id, "pageNo": 1, "numOfRows": 300})
    if not data:
        return []

    try:
        items = data["response"]["body"]["items"]["item"]
        if not isinstance(items, list):
            items = [items]

        # nodeid / nodenm만 뽑아 UI에서 쓰기 편하게
        return [{"nodeid": i.get("nodeid"), "nodenm": i.get("nodenm")} for i in items]
    except Exception:
        return []


# ⏱ 4) 정류장ID → 실시간 도착정보
def get_arrival_info(node_id):
    url = "https://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList"
    data = _api_get(url, {"cityCode": CITY_CODE, "nodeId": node_id, "pageNo": 1, "numOfRows": 20})
    if not data:
        return []

    try:
        items = data["response"]["body"]["items"]["item"]
        if not isinstance(items, list):
            items = [items]

        arrivals = []
        for i in items:
            routeno = i.get("routeno", "N/A")
            arrtime_min = int(i.get("arrtime", 0)) // 60
            arrivals.append(f"{routeno}번 ({arrtime_min}분 후)")
        return arrivals
    except Exception:
        return []
