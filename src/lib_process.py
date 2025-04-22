#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-*-coding:gb2312-*-

#Import Python Lib


import json

import requests
import os.path
import datetime
import sys
import aiofiles
import aiohttp
import logging
import importlib
import subprocess
import struct
#Lunar, Noted day Skill
import math
#Youtube Skill
import urllib
import numpy
#History Skill, #Funny Story
# import bs4
#Weather Skill
#Music
import os
# import concurrent.futures
#Youtube #Hass
#Speed Test
#News, Lottery skill
#Curency Rate, # Gold rate
# import urllib3
#Wikipedia Skill 
#Random
import random
# import usb.core
# import usb.util
#Schedule Skill
# import schedule
import time
#ZingMp3
import hashlib
import hmac
import hashlib
import shutil
import itertools
# import click
#Wakeupword
import numpy as np
# from openwakeword.model import Model
# import google.oauth2.credentials
import base64
import asyncio
import edge_tts
# import pyaudio
# import sounddevice
# import wave
import uuid    
import re
import argparse
import fcntl
import subprocess
# import imp
# import importlib
import threading
import socket
import colorsys
import queue
import ssl
# import imp
# import youtube_dl
# import spidev
#import as
# import xml.etree.ElementTree as ET
# import speech_recognition as sr
# import xml.dom.minidom as minidom
import pathlib2 as pathlib
#From import
from multiprocessing import Manager,Process
from math import ceil
from google.cloud import speech
from google.cloud import texttospeech                
# from flask_cors import CORS
# from flask import Flask, request, render_template, jsonify,send_from_directory
# from gtts import gTTS
from fuzzywuzzy import fuzz   
from os import listdir
# from html2text import HTML2Text
# from geopy.geocoders import Nominatim
# Base
from fuzzywuzzy import process
from urllib.parse import quote
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
# import paho.mqtt.client as mqtt
import websockets

# Đường dẫn các file cấu hình
CONFIG_FILE = "config.json"
SKILL_FILE = "skill.json"
ACTION_FILE = "action.json"
OBJECT_FILE = "object.json"
ADVERB_FILE = "adverb.json"

# Hàm load dữ liệu từ file JSON
def load_config(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Hàm lưu dữ liệu vào file JSON
async def save_config():
    async with aiofiles.open("config.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(config, indent=2, ensure_ascii=False))

# Các biến toàn cục dùng cho toàn hệ thống
config = load_config(CONFIG_FILE)
skill = load_config(SKILL_FILE)
action = load_config(ACTION_FILE)
objectt = load_config(OBJECT_FILE)
adverb = load_config(ADVERB_FILE)
