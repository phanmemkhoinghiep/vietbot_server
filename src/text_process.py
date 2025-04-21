# !/usr/bin/python
# -*- coding: utf-8 -*-
# Processing
from lib_process import re,random
import skill_process
# import hass_process
from global_vars import objectt, skill

    
def text_process(data):
    # answer='Không có câu trả lời từ các skill của vietbot trong tình huống này'
    answer=''
    music_link=''
    
    if any(item["value"] in data for item in objectt["what_time"]):
        answer=skill_process.what_time('TIME')
    elif any(item["value"] in data for item in objectt["what_month"]):
        answer=skill_process.what_time('MONTH')
    elif any(item["value"] in data for item in objectt["what_year"]):
        answer=skill_process.what_time('YEAR')
    elif any(item["value"] in data for item in objectt["lunar_day"]):        
        if any(item["value"] in data for item in objectt["yesterday"]):
            answer=skill_process.lunar_day('YESTERDAY')
        elif any(item["value"] in data for item in objectt["obj_today"]):                         
            answer=skill_process.lunar_day('TODAY')
        elif any(item["value"] in data for item in objectt["obj_tomorrow"]):                         
            answer=skill_process.lunar_day('TOMORROW')
        elif any(item["value"] in data for item in objectt["obj_next_day"]):                         
            answer=skill_process.lunar_day('NEXT_DAY')
        elif any(item["value"] in data for item in objectt["obj_what_month"]):                         
            answer=skill_process.lunar_day('THIS_MONTH')
        else:
            answer=skill_process.lunar_day('TODAY')
    # elif any(item in data for item in global_vars.obj_weather):   
        # try:
            # if any(item in data for item in global_vars.obj_yesterday): 
                # answer=skill_process.weather_process('YESTERDAY')
            # elif any(item in data for item in global_vars.obj_today):   
                # answer=skill_process.weather_process('TODAY')
            # elif any(item in data for item in global_vars.obj_tomorrow):             
                # answer=skill_process.weather_process('TOMORROW')
            # elif any(item in data for item in global_vars.obj_next_day):             
                # answer=skill_process.weather_process('NEXT_DAY')
            # elif any(item in data for item in global_vars.obj_next_week):             
                # answer=skill_process.weather_process('NEXT_WEEK')            
            # else:
                # answer=skill_process.weather_process('TODAY')
        # except:
            # answer=global_vars.weather_error
    elif any(item["value"] in data for item in objectt["music"]):               
        try:
            music_link=skill_process.local_music(data)           
        except:
            answer=skill['music']['error_answer']            
    else:
        try:        
            answer = skill_process.gemini_process(data)
        except:
            answer=skill['gemini']['error_answer']     
            
    return answer,music_link

if __name__ == '__main__': 
    data='thời tiết hôm nay thế nào'    
    print(text_process(data))