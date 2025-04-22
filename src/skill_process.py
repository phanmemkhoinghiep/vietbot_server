# !/usr/bin/python
# -*- coding: utf-8 -*-
#Processing
from lib_process import requests,fuzz,datetime,math,fuzz,random,re, os, logging, config, skill, objectt, action

weather_session = requests.Session()
music_cache = {}

import google.generativeai as genai
genai.configure(api_key=skill["gemini"]["api"])
gemini_model = genai.GenerativeModel(skill["gemini"]["model"])


if config["logging_type"] =='INFO':
    logging.basicConfig(level=logging.INFO) 
else:
    logging.basicConfig(
        level=logging.DEBUG,  # Bật DEBUG cho toàn bộ ứng dụng
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("server_debug.log", encoding='utf-8', mode='a')
        ]
    )       

logger = logging.getLogger("AudioServer")

def similarity_check(new_data, cached_data):
    # Use token_sort_ratio for comparing the similarity
    similarity_ratio =fuzz.token_sort_ratio(new_data, cached_data)
    return similarity_ratio >= skill["ơcache_compare_result"]  # Adjust the threshold as needed

def get_current_date():
    answer=datetime.date.today()- datetime.timedelta(days=1),datetime.date.today(),datetime.date.today() + datetime.timedelta(days=1),datetime.date.today() + datetime.timedelta(days=2),datetime.date.today() + datetime.timedelta(days=5)    
    return answer
tomorrow_str=f"{get_current_date()[2]:%d}"
next_day_str=f"{(get_current_date()[3]):%d}"
next_5day_str=f"{(get_current_date()[4]):%d}"
def what_time(opt):
    if opt == 'TIME':
        answer= 'Bây giờ là ' + str(datetime.datetime.today().strftime('%H')) + ' giờ ' + str(datetime.datetime.today().strftime('%M')) + ' phút '
    elif opt == 'DAY':
        answer= 'Hôm nay là ngày ' + f"{(get_current_date()[1]):%D}"
    elif opt == 'MONTH':
        answer= 'Tháng này là tháng ' + f"{(get_current_date()[1]):%m}"
    elif opt == 'YEAR':
        answer='Năm nay là năm ' + f"{(get_current_date()[1]):%Y}"
    return answer
def solar_day(opt):
    today = get_current_date()[1]
    yesterday = get_current_date()[0]
    tomorrow = get_current_date()[2]
    next_day = get_current_date()[3]
    weekdays_vietnamese = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy','Chủ Nhật']
    today_weekday = weekdays_vietnamese[today.weekday()]
    yesterday_weekday = weekdays_vietnamese[yesterday.weekday()]
    tomorrow_weekday = weekdays_vietnamese[tomorrow.weekday()]
    next_day_weekday = weekdays_vietnamese[next_day.weekday()]
    if opt == 'YESTERDAY':
        answer='Hôm qua là ' + yesterday_weekday + ' ngày ' + yesterday.strftime('%d/%m/%Y')
    elif opt == 'TODAY':
        answer='Hôm nay là ' + today_weekday + ' ngày ' + today.strftime('%d/%m/%Y')
    elif opt == 'TOMORROW':
        answer='Ngày mai là ' + tomorrow_weekday + ' ngày ' + tomorrow.strftime('%d/%m/%Y')
    elif opt == 'NEXT_DAY':
        answer='Ngày kia là ' + next_day_weekday + ' ngày ' + next_day.strftime('%d/%m/%Y')
    return answer
def lunar_day(opt):
    def jdFromDate(dd, mm, yy):
        a = (14 - mm) // 12
        y = yy + 4800 - a
        m = mm + 12 * a - 3
        jd = dd + ((153 * m + 2) // 5) \
             + 365 * y + (y // 4) - (y // 100) \
             + (y // 400) - 32045
        if jd < 2299161:
            jd = dd + ((153 * m + 2) // 5) \
                 + 365 * y + (y // 4) - 32083
        return jd
    def jdToDate(jd):
        if jd > 2299160:
            # After 5/10/1582, Gregorian calendar
            a = jd + 32044
            b = (4 * a + 3) // 146097
            c = a - (b * 146097) // 4
        else:
            b = 0
            c = jd + 32082
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153
        day = e - ((153 * m + 2) // 5) + 1
        month = m + 3 - 12 * (m // 10)
        year = b * 100 + d - 4800 + (m // 10)
        return [day, month, year]
    def NewMoon(k):
        # Time in Julian centuries from 1900 January 0.5
        T = k / 1236.85
        T2 = T * T
        T3 = T2 * T
        dr =math.pi / 180.
        jd1 = 2415020.75933 + 29.53058868 * k \
            + 0.0001178 * T2 - 0.000000155 * T3
        jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)

        # Mean new moon
        M = 359.2242 + 29.10535608 * k \
            - 0.0000333 * T2 - 0.00000347 * T3

        # Sun's mean anomaly
        Mpr = 306.0253 + 385.81691806 * k \
            + 0.0107306 * T2 + 0.00001236 * T3

        # Moon's mean anomaly
        F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 \
            - 0.00000239 * T3

        # Moon's argument of latitude
        C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) \
            + 0.0021 * math.sin(2 * dr * M)
        C1 -= 0.4068 * math.sin(Mpr * dr) \
            + 0.0161 * math.sin(dr * 2 * Mpr)
        C1 -= 0.0004 * math.sin(dr * 3 * Mpr)
        C1 += 0.0104 * math.sin(dr * 2 * F) \
            - 0.0051 * math.sin(dr * (M + Mpr))
        C1 -= 0.0074 * math.sin(dr * (M - Mpr)) \
            + 0.0004 * math.sin(dr * (2 * F + M))
        C1 -= 0.0004 * math.sin(dr * (2 * F - M)) \
            - 0.0006 * math.sin(dr * (2 * F + Mpr))
        C1 += 0.0010 * math.sin(dr * (2 * F - Mpr)) \
            + 0.0005 * math.sin(dr * (2 * Mpr + M))

        if T < -11:
            deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 \
                - 0.00000845 * T3 - 0.000000081 * T * T3
        else:
            deltat = -0.000278 + 0.000265 * T + 0.000262 * T2

        jd_new = jd1 + C1 - deltat
        return jd_new
    def SunLongitude(jdn):
      '''def SunLongitude(jdn): Compute the longitude of the sun at any time. Parameter: floating number jdn, the number of days since 1/1/4713 BC noon.'''
      T = (jdn - 2451545.0 ) / 36525.
      ## Time in Julian centuries
      ## from 2000-01-01 12:00:00 GMT
      T2 = T * T
      dr = math.pi / 180.  ## degree to radian
      M = 357.52910 + 35999.05030*T \
          - 0.0001559*T2 - 0.00000048*T*T2
      ## mean anomaly, degree
      L0 = 280.46645 + 36000.76983*T + 0.0003032*T2
      ## mean longitude, degree
      DL = (1.914600 - 0.004817*T - 0.000014*T2) \
              * math.sin(dr*M)
      DL += (0.019993 - 0.000101*T) *math.sin(dr*2*M) \
                + 0.000290*math.sin(dr*3*M)
      L = L0 + DL  ## true longitude, degree
      L = L * dr
      L = L - math.pi*2*(int(L / (math.pi*2)))
      #### Normalize to (0, 2*math.pi)
      return L
    def getSunLongitude(dayNumber, timeZone):
      '''def getSunLongitude(dayNumber, timeZone):  Compute sun position at midnight of the day with the given Julian day number. The time zone if the time difference between local time and UTC: 7.0 for UTC+7:00. The function returns a number between 0 and 11.  From the day after March equinox and the 1st major term after March equinox, 0 is returned. After that, return 1, 2, 3 ...'''
      return int( \
        SunLongitude(dayNumber - 0.5 - timeZone/24.) \
        / math.pi*6)
    def getNewMoonDay(k, timeZone):
      '''def getNewMoonDay(k, timeZone): Compute the day of the k-th new moon in the given time zone. The time zone if the time difference between local time and UTC: 7.0 for UTC+7:00.'''
      return int(NewMoon(k) + 0.5 + timeZone / 24.)
    def getLunarMonth(yy, timeZone):
      '''def getLunarMonth(yy, timeZone):  Find the day that starts the luner month 11of the given year for the given time zone.'''
      # off = jdFromDate(31, 12, yy) \
      #            - 2415021.076998695
      off = jdFromDate(31, 12, yy) - 2415021.
      k = int(off / 29.530588853)
      nm = getNewMoonDay(k, timeZone)
      sunLong = getSunLongitude(nm, timeZone)
      #### sun longitude at local midnight
      if (sunLong >= 9):
        nm = getNewMoonDay(k - 1, timeZone)
      return nm
    def getLeapMonthOffset(a11, timeZone):
      '''def getLeapMonthOffset(a11, timeZone): Find the index of the leap month after the month starting on the day a11.'''
      k = int((a11 - 2415021.076998695) \
                  / 29.530588853 + 0.5)
      last = 0
      i = 1  ## start with month following lunar month 11
      arc = getSunLongitude( \
                    getNewMoonDay(k + i, timeZone), timeZone)
      while True:
        last = arc
        i += 1
        arc = getSunLongitude( \
                          getNewMoonDay(k + i, timeZone), \
                          timeZone)
        if  not (arc != last and i < 14):
          break
      return i - 1
    def S2L(dd, mm, yy, timeZone = 7):
      '''def S2L(dd, mm, yy, timeZone = 7): Convert solar date dd/mm/yyyy to the corresponding lunar date.'''
      dayNumber = jdFromDate(dd, mm, yy)
      k = int((dayNumber - 2415021.076998695) \
                    / 29.530588853)
      monthStart = getNewMoonDay(k + 1, timeZone)
      if (monthStart > dayNumber):
        monthStart = getNewMoonDay(k, timeZone)
      # alert(dayNumber + " -> " + monthStart)
      a11 = getLunarMonth(yy, timeZone)
      b11 = a11
      if (a11 >= monthStart):
        lunarYear = yy
        a11 = getLunarMonth(yy - 1, timeZone)
      else:
        lunarYear = yy + 1
        b11 = getLunarMonth(yy + 1, timeZone)
      lunarDay = dayNumber - monthStart + 1
      diff = int((monthStart - a11) / 29.)
      lunarLeap = 0
      lunarMonth = diff + 11
      if (b11 - a11 > 365):
        leapMonthDiff = \
            getLeapMonthOffset(a11, timeZone)
        if (diff >= leapMonthDiff):
          lunarMonth = diff + 10
          if (diff == leapMonthDiff):
            lunarLeap = 1
      if (lunarMonth > 12):
        lunarMonth = lunarMonth - 12
      if (lunarMonth >= 11 and diff < 4):
        lunarYear -= 1
      return \
          [ lunarDay, lunarMonth, lunarYear, lunarLeap ]
    def L2S(lunarD, lunarM, lunarY, lunarLeap, tZ=7):
        if lunarM < 11:
            a11 = getLunarMonth(lunarY - 1, tZ)
            b11 = getLunarMonth(lunarY, tZ)
        else:
            a11 = getLunarMonth(lunarY, tZ)
            b11 = getLunarMonth(lunarY + 1, tZ)
        k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
        off = (lunarM - 11) % 12

        if b11 - a11 > 365:
            leapOff = getLeapMonthOffset(a11, tZ)
            leapM = (leapOff - 2) % 12

            if lunarLeap != 0 and lunarM != leapM:
                return [0, 0, 0]
            elif lunarLeap != 0 or off >= leapOff:
                off += 1
        monthStart = getNewMoonDay(k + off, tZ)
        return jdToDate(monthStart + lunarD - 1) 
    days_offset = {
        'YESTERDAY': -1,
        'TODAY': 0,
        'TOMORROW': 1,
        'NEXT_DAY': 2
    }
    current_date = get_current_date()[1]
    # Check if opt is 'THIS MONTH'
    if opt == 'THIS MONTH':
        lunar_date = S2L(current_date.day, current_date.month, current_date.year)
        list_thang = ["tháng Giêng", "tháng Hai", "tháng Ba", "tháng Tư", "tháng Năm", "tháng Sáu", "tháng Bảy", "tháng Tám", "tháng Chín", "tháng Mười", "tháng Mười một", "tháng Chạp"]
        return list_thang[lunar_date[1] - 1]
    if opt not in days_offset:
        return "Ngày đưa vào không đúng"
    dd = current_date + datetime.timedelta(days=days_offset[opt])
    day_names = {
        'YESTERDAY': 'Hôm qua',
        'TODAY': 'Hôm nay',
        'TOMORROW': 'Ngày mai',
        'NEXT_DAY': 'Ngày kia'
    }
    day_name = day_names[opt]
    lunar_date = S2L(dd.day, dd.month, dd.year)
    list_thang = ["tháng Giêng", "tháng Hai", "tháng Ba", "tháng Tư", "tháng Năm", "tháng Sáu", "tháng Bảy", "tháng Tám", "tháng Chín", "tháng Mười", "tháng Mười một", "tháng Chạp"]
    ngay_am = str(lunar_date[0])
    thang_am = list_thang[lunar_date[1] - 1]
    can = ['Canh', 'Tân', 'Nhâm', 'Quý', 'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ']
    chi = ['Thân', 'Dậu', 'Tuất', 'Hợi', 'Tí', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi']
    nam_am = can[lunar_date[2] % 10] + ' ' + chi[lunar_date[2] % 12]
    ss = lunar_date[0]  # I assume ss is derived from lunar_date
    if ss == 1:
        return day_name + ' là mùng một '  + thang_am + ' năm ' + nam_am
    elif 1 < ss < 11:
        return day_name + ' là mùng ' + ngay_am + ' ' + thang_am + ' năm ' + nam_am + ', còn ' + str(15 - ss) + " ngày nữa là đến rằm"
    elif 11< ss < 15:
        return day_name + ' là ' + ngay_am + ' ' + thang_am + ' năm ' + nam_am +  ', còn ' + str(15 - ss) + " ngày nữa là đến rằm"
    elif 15 < ss < 31:
        return day_name + ' là ' + ngay_am + ' ' + thang_am + ' năm ' + nam_am +  ', còn ' + str(31 - ss) + " ngày nữa là đến mùng một"
    elif ss == 15:
            return day_name + ' là rằm ' + thang_am + ' năm ' + nam_am
    else:
        return day_name + ' là ' + ngay_am + ' ' + thang_am + ' năm ' + nam_am

# def get_location_from_place(place):
    # """Lấy tọa độ (lat, lon) từ tên địa điểm."""
    # try:
        # url = f"http://api.openweathermap.org/geo/1.0/direct?q={place}&limit=1&appid={skill["weather"]["openweathermap_key"]}"
        # response = weather_session.get(url)
        # response.raise_for_status()
        # data = response.json()
        # if data:
            # return data[0]['lat'], data[0]['lon']
        # else:
            # return None, None
    # except requests.RequestException as e:
        # logger.warning(f"Error fetching location: {e}")
        # return None, None

# def get_weather_data(lat, lon, endpoint):
    # """Lấy dữ liệu thời tiết từ API OpenWeatherMap."""
    # try:
        # url = f"https://api.openweathermap.org/data/2.5/{endpoint}?lat={lat}&lon={lon}&lang=vi&appid={skill["weather"]["openweathermap_key"]}"
        # response = weather_session.get(url)
        # response.raise_for_status()
        # return response.json()
    # except requests.RequestException as e:
        # logger.warning('left',f"Error weather data: {e}")
        # return None

# def format_weather_response(data, day, prefix_msg):
    # """Định dạng phản hồi thời tiết."""
    # temp = str(round(data['main']['temp'] + skill["temp_delta", 2))
    # description = data['weather'][0]['description']
    # humidity = str(data['main']['humidity'])
    # pressure = str(data['main']['pressure'])
    # wind_speed = str(data['wind']['speed'])
    # pop = str(round(data.get('pop', 0) * 100, 2))  # Tỉ lệ mưa, mặc định 0 nếu không có
    # return f"{prefix_msg} {description} nhiệt độ trung bình {temp} độ C, độ ẩm {humidity}%, áp suất khí quyển {pressure} Pa, tốc độ gió {wind_speed} mét/giây, tỉ lệ mưa {pop}%."

# def weather_process(day):
    # """Xử lý thời tiết theo ngày."""
    # lat, lon = get_location_from_place(global_vars.user_place_covert)
    # if not lat or not lon:
        # return f"Không tìm thấy tọa độ của địa điểm '{global_vars.user_place}'."    
    # if day == 'YESTERDAY':
        # return f"Thời tiết {global_vars.user_place} hôm qua đã biết"    
    # if day == 'TODAY':
        # data = get_weather_data(lat, lon, "weather")
        # if data:
            # return format_weather_response(data, day, f"Thời tiết {global_vars.user_place} hôm nay:")
        # return f"Không thể lấy dữ liệu thời tiết cho {global_vars.user_place} hôm nay."
    # # Dự báo thời tiết
    # data = get_weather_data(lat, lon, "forecast")
    # if not data:
        # return f"Không thể lấy dữ liệu thời tiết cho {global_vars.user_place}."
    # # Lấy thời điểm mục tiêu
    # if day == 'TOMORROW':
        # target_date = (datetime.datetime.now() +datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        # prefix_msg = f"Thời tiết {global_vars.user_place} ngày mai:"
    # elif day == 'NEXT_DAY':
        # target_date = (datetime.datetime.now() +datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        # prefix_msg = f"Thời tiết {global_vars.user_place} ngày kia:"
    # elif day == 'NEXT_WEEK':
        # target_date = (datetime.datetime.now() +datetime.timedelta(days=5)).strftime('%Y-%m-%d')
        # prefix_msg = f"Thời tiết {global_vars.user_place} tuần tới:"
    # else:
        # return f"Ngày '{day}' không hợp lệ."
    # # Tìm dữ liệu dự báo phù hợp
    # for item in data.get('list', []):
        # if item['dt_txt'].startswith(target_date):
            # return format_weather_response(item, day, prefix_msg)    
    # return f"Không tìm thấy dữ liệu thời tiết cho ngày {target_date}."
# # Note: Functions like get_location_from_place, tomorrow_str, next_day_str, next_5day_str are assumed to be defined elsewhere in your code.

def local_music(data):
    global music_cache
    song_path_list = os.listdir('mp3/')    
    for cached_data, cached_result in music_cache.items():
        if similarity_check(data, cached_data):
            return cached_result
    music_compare_result=[]
    words = data.split()
    data = ' '.join(word for word in words if word not in action["play"] and word not in objectt["music"] )
    for i in range(len(song_path_list)):
        match_ratio= fuzz.token_sort_ratio(data, song_path_list[i].replace('.mp3','').lower())
        music_compare_result.append(match_ratio)
    # print(music_compare_result)    
    if max(music_compare_result) > skill["local_compare_percent"]:
        song_path=song_path_list[music_compare_result.index(max(music_compare_result))]
        return 'mp3/'+song_path
    else:
        return ''       

def gemini_process(data):
    chat = gemini_model.start_chat()
    response = chat.send_message(data)
    return response.text

if __name__ == '__main__':  
    pass