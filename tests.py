
import os
from dotenv import load_dotenv
from rich.console import Console
from utils.kreta import KretaUtils
from utils.date_utils import KretaDateUtils

load_dotenv()

kreta_user_id = os.getenv("KRETA_USER_ID")
kreta_password = os.getenv("KRETA_USER_PASSWORD")
kreta_klik_id = os.getenv("KRETA_KLIK_ID")

kreta_utils = KretaUtils(kreta_user_id, kreta_password, kreta_klik_id)
date_utils = KretaDateUtils()

#print(kreta_utils.get_student_data())
# print(kreta_utils.get_homework("2024-12-15", "2024-12-25"))
print(kreta_utils.get_lessons("2025-01-06", "2025-01-12"))
#print(kreta_utils.get_grades("2024-12-01", "2024-12-30"))
#print(kreta_utils.get_school_year_dates())