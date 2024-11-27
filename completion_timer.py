import time
import subprocess
import sys

class CompletionTimer:
    def __init__(self, countdown_time=5, script_name="main.py"):
        """
        กำหนดเวลาเริ่มต้นสำหรับการนับถอยหลัง
        :param countdown_time: เวลานับถอยหลัง (หน่วยวินาที)
        :param script_name: ชื่อไฟล์สคริปต์ Python ที่จะเปิดใหม่หลังนับถอยหลังเสร็จ
        """
        self.countdown_time = countdown_time
        self.script_name = script_name

    def start_and_restart(self):
        """
        เริ่มนับถอยหลังแล้วเปิด `main.py`
        """
        print(f"เริ่มนับถอยหลัง {self.countdown_time} วินาที...")
        
        # นับถอยหลังพร้อมแสดงเวลาที่เหลือ
        for remaining_time in range(self.countdown_time, 0, -1):
            print(f"เหลือเวลา: {remaining_time} วินาที")
            time.sleep(1)

        print("ครบเวลาแล้ว กำลังรันโปรแกรมใหม่...")

        # รัน main.py
        python = sys.executable  # ค้นหา Python interpreter ที่กำลังใช้งาน
        try:
            subprocess.Popen([python, self.script_name])  # เปิดไฟล์ main.py
            print(f"รัน {self.script_name} สำเร็จ")
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

# ตรวจสอบว่าไฟล์นี้ถูกเรียกใช้งานโดยตรงหรือไม่
if __name__ == "__main__":
    timer = CompletionTimer(countdown_time=5, script_name="main.py")
    timer.start_and_restart()
