from datetime import datetime
import pytz

def get_jst_timestamp():
    """日本標準時（JST）の現在時刻を取得し、フォーマット"""
    tz_japan = pytz.timezone("Asia/Tokyo")
    return datetime.now(tz_japan).strftime("%Y-%m-%d %H:%M:%S")
