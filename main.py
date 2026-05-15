import serial
import time

COM_PORT = "COM14"
BAUD_RATE = 9600
RECEIVER_ADDRESS = 2
SEND_MODE = "AT"


VALID_COMMANDS = {
    "C1": "Turn cameras ON",
    "C0": "Turn cameras OFF",
    "T1": "Turn Teensy ON",
    "T2": "Turn Teensy OFF",
}

def open_serial():
    ser = serial.Serial(
        port=COM_PORT,
        baudrate=BAUD_RATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.2,
        write_timeout=1.0,
    )
    time.sleep(0.5)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def read_available(ser):
    time.sleep(0.2)
    data = b""
    while ser.in_waiting:
        data += ser.read(ser.in_waiting)
        time.sleep(0.05)
    if data:
        print(data.decode(errors="replace").strip())

def send_command(ser, cmd):
    cmd = cmd.strip().upper()
    if cmd not in VALID_COMMANDS:
        print("Invalid command.")
        print("Valid commands: C1, C0, T1, T2")
        return
    if SEND_MODE.upper() == "AT":
        message = f"AT+SEND={RECEIVER_ADDRESS},{len(cmd)},{cmd}\r\n"
    elif SEND_MODE.upper() == "RAW":
        message = f"{cmd}\r\n"
    else:
        raise ValueError("SEND_MODE must be 'AT' or 'RAW'.")
    print(f"Sending {cmd}: {VALID_COMMANDS[cmd]}")
    ser.write(message.encode("ascii"))
    ser.flush()
    read_available(ser)

def main():
    print("DX-LR02 Remote Start Sender")
    print("--------------------------")
    print(f"COM port: {COM_PORT}")
    print(f"Baud: {BAUD_RATE}")
    print(f"Mode: {SEND_MODE}")
    print()
    print("Commands:")
    print("  C1 = cameras ON")
    print("  C0 = cameras OFF")
    print("  T1 = Teensy ON")
    print("  T2 = Teensy OFF")
    print("  q  = quit")
    print()
    with open_serial() as ser:
        print("Serial opened.")
        print("Testing module with AT...")
        ser.write(b"AT\r\n")
        ser.flush()
        read_available(ser)
        while True:
            cmd = input("> ").strip()
            if cmd.lower() in ["q", "quit", "exit"]:
                print("Exiting.")
                break
            send_command(ser, cmd)

if __name__ == "__main__":
    main()