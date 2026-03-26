import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import folium
import uuid
from datetime import datetime

# ================================
# 🔧 고정 설정 (청주시)
# ================================
SERVICE_KEY = "dc03c0f94d438e60f14a19e2d867743b4d91d9cc78299af0ee1016ee26c96fd9"
CITY_NAME = "청주시"
CITY_CODE = "33010"   # 청주시 코드 (공공데이터 기준)
MAX_RETRY = 3


# ================================
# 🔧 HTML 파일 생성
# ================================
def generate_unique_filename(route_number):
    unique_id = uuid.uuid4().hex
    return f'cheongju_bus_map_{route_number}_{unique_id}.html'


# ================================
# 🔵 버스 routeId 조회
# ================================
def get_route_id(route_number):
    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList'
    params = {
        'serviceKey': SERVICE_KEY,
        '_type': 'xml',
        'cityCode': CITY_CODE,
        'routeNo': route_number
    }

    try:
        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, 'xml')
        routeid = soup.find('routeid')

        if routeid:
            return routeid.text
    except Exception as e:
        print("⚠ routeId 조회 오류:", e)

    return None


# ================================
# 🔵 GPS 좌표 가져오기
# ================================
def get_bus_stop_coordinates(route_id):
    coordinates = []

    params = {
        'serviceKey': SERVICE_KEY,
        'numOfRows': 800,
        'pageNo': 1,
        '_type': 'xml',
        'cityCode': CITY_CODE,
        'routeId': route_id
    }

    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'

    try:
        data = requests.get(url, params=params).text
        root = ET.fromstring(data)

        for item in root.iter("item"):
            try:
                lat = float(item.find('gpslati').text)
                lng = float(item.find('gpslong').text)
                name = item.find('nodenm').text
                coordinates.append((name, lat, lng))
            except:
                pass

    except Exception as e:
        print("⚠ GPS 조회 오류:", e)

    return coordinates


# ================================
# 🔵 노선 기본 정보
# ================================
def get_route_info(route_id):
    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem'
    params = {
        'serviceKey': SERVICE_KEY,
        '_type': 'xml',
        'cityCode': CITY_CODE,
        'routeId': route_id
    }

    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, 'xml')
    return soup


def print_route_info(soup):
    bus = soup.find('routeno')
    start = soup.find('startnodenm')
    end = soup.find('endnodenm')
    first = soup.find('startvehicletime')
    last = soup.find('endvehicletime')

    print("\n========= 🚌 노선 기본 정보 =========")
    print("노선번호:", bus.text)
    print("기점:", start.text)
    print("종점:", end.text)

    if first:
        t1 = datetime.strptime(first.text, "%H%M").strftime("%H:%M")
        print("첫차:", t1)
    if last:
        t2 = datetime.strptime(last.text, "%H%M").strftime("%H:%M")
        print("막차:", t2)
    print("====================================\n")


# ================================
# 🔵 경유 정류장 목록
# ================================
def get_via_stops(route_id):
    stops = []

    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    params = {
        'serviceKey': SERVICE_KEY,
        '_type': 'xml',
        'cityCode': CITY_CODE,
        'routeId': route_id
    }

    try:
        data = requests.get(url, params=params).text
        root = ET.fromstring(data)

        for idx, item in enumerate(root.iter("item"), start=1):
            name = item.find('nodenm').text
            stops.append(name)

    except Exception as e:
        print("⚠ 경유 정류장 오류:", e)

    return stops


# ================================
# 🗺 Folium 지도 생성
# ================================
def create_bus_map(coordinates, route_number):
    if not coordinates:
        print("⚠ 정류장 좌표 없음 — 지도 생성 불가")
        return

    first = coordinates[0]

    m = folium.Map(location=[first[1], first[2]], zoom_start=13)

    # 정류장 마커 표시
    for (name, lat, lng) in coordinates:
        folium.Marker([lat, lng], popup=name).add_to(m)

    # 경로선 추가
    line = [[lat, lng] for (_, lat, lng) in coordinates]
    folium.PolyLine(line, color='blue', weight=3).add_to(m)

    file_name = generate_unique_filename(route_number)
    m.save(file_name)

    print(f"📌 지도 저장 완료: {file_name}")


# ================================
# 🎯 메인 실행
# ================================
def main():
    print("====== 청주시 버스 정보 시스템 ======\n")

    while True:
        route_number = input("\n조회할 버스번호 입력 (종료: -1): ")

        if route_number == "-1":
            print("종료합니다.")
            break

        route_id = get_route_id(route_number)

        if not route_id:
            print("⚠ 해당 버스번호를 찾을 수 없습니다.\n")
            continue

        print(f"✔ routeId = {route_id}")

        # 노선 기본정보 조회
        info = get_route_info(route_id)
        print_route_info(info)

        # 정류장 목록
        stops = get_via_stops(route_id)
        print("🚌 경유 정류장 수:", len(stops))
        for i, s in enumerate(stops, 1):
            print(f"{i}. {s}")

        # GPS 좌표
        coords = get_bus_stop_coordinates(route_id)

        # 지도 생성
        create_bus_map(coords, route_number)


# ================================
# 실행
# ================================
if __name__ == "__main__":
    main()
