import time
import threading
import serial

# Thay đổi ở đây
use_serial = True  # Đặt False nếu không muốn mở serial

# Cấu hình cổng COM
arduinoPort = "COM4"
qtPort = "COM1"
baudrate = 9600  # Tốc độ baud của thiết bị
interval = 0.02  # Thời gian giữa các lần gửi (giây)

# Biến toàn cục để lưu dữ liệu
shared_data = ""
data_lock = threading.Lock()

# Hàm nhận dữ liệu từ Arduino
def receive_from_arduino():
    global shared_data
    try:
        if use_serial:
            arduinoSerial = serial.Serial(arduinoPort, baudrate, timeout=1)
            print(f"Đã mở cổng {arduinoPort} với baudrate {baudrate}")
        else:
            print("Chạy giả lập - Không mở cổng Arduino")

        while True:
            # Đọc dữ liệu dòng theo dòng
            if use_serial and arduinoSerial.in_waiting > 0:
                data = arduinoSerial.readline().decode('utf-8').strip()
                with data_lock:
                    shared_data = data
            time.sleep(0.01)

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if use_serial and 'arduinoSerial' in locals() and arduinoSerial.is_open:
            arduinoSerial.close()
            print(f"Đã đóng cổng {arduinoPort}")

# Hàm gửi dữ liệu đến Qt
def send_to_qt():
    global shared_data
    try:
        if use_serial:
            qtSerial = serial.Serial(qtPort, baudrate, timeout=1)
            print(f"Đã mở cổng {qtPort} với baudrate {baudrate}")
        else:
            print("Chạy giả lập - Không mở cổng Qt")

        while True:
            # Gửi dữ liệu hiện tại nếu có
            with data_lock:
                data_to_send = shared_data

            if data_to_send:
                if use_serial:
                    qtSerial.write((data_to_send + '\n').encode())
                    print(f"{data_to_send}")
                else:
                    print(f"Gửi giả lập: {data_to_send}")

            time.sleep(interval)

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if use_serial and 'qtSerial' in locals() and qtSerial.is_open:
            qtSerial.close()
            print(f"Đã đóng cổng {qtPort}")

# Tạo và chạy các luồng
try:
    arduino_thread = threading.Thread(target=receive_from_arduino, daemon=True)
    qt_thread = threading.Thread(target=send_to_qt, daemon=True)

    arduino_thread.start()
    qt_thread.start()

    # Giữ chương trình chạy cho đến khi có yêu cầu dừng
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nĐã dừng chương trình theo yêu cầu người dùng.")
