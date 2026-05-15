import serial
import time
import threading

COM_PORT = "COM3"
BAUD_RATE = 9600
RECEIVER_ADDRESS = 2
SEND_MODE = "AT"

VALID_COMMANDS = {
    "C1": "Turn cameras ON",
    "C0": "Turn cameras OFF",
    "T1": "Turn Teensy ON",
    "T2": "Turn Teensy OFF",
}

rxn_wheel_state = None
serial_running = True


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


def parse_received_text(text):
    global rxn_wheel_state

    text = text.strip()

    if not text:
        return

    print(text)

    if "RXN1" in text:
        if rxn_wheel_state is not True:
            rxn_wheel_state = True
            print()
            print("================================")
            print("REACTION WHEEL: ON")
            print("================================")
            print()

    elif "RXN0" in text:
        if rxn_wheel_state is not False:
            rxn_wheel_state = False
            print()
            print("================================")
            print("REACTION WHEEL: OFF")
            print("================================")
            print()


def serial_reader_thread(ser):
    buffer = ""

    while serial_running:
        try:
            while ser.in_waiting:
                c = ser.read(1).decode(errors="replace")

                if c == "\n" or c == "\r":
                    if buffer.strip():
                        parse_received_text(buffer)
                        buffer = ""
                else:
                    buffer += c

                    if len(buffer) > 300:
                        parse_received_text(buffer)
                        buffer = ""

            time.sleep(0.05)

        except serial.SerialException as e:
            print(f"Serial error: {e}")
            break


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


def print_status():
    if rxn_wheel_state is True:
        print("REACTION WHEEL: ON")
    elif rxn_wheel_state is False:
        print("REACTION WHEEL: OFF")
    else:
        print("REACTION WHEEL: UNKNOWN")


def main():
    global serial_running

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
    print("  status = show reaction wheel state")
    print("  q  = quit")
    print()

    with open_serial() as ser:
        print("Serial opened.")
        print("Testing module with AT...")

        reader = threading.Thread(target=serial_reader_thread, args=(ser,), daemon=True)
        reader.start()

        ser.write(b"AT\r\n")
        ser.flush()

        while True:
            cmd = input("> ").strip()

            if cmd.lower() in ["q", "quit", "exit"]:
                print("Exiting.")
                serial_running = False
                time.sleep(0.2)
                break

            if cmd.lower() == "status":
                print_status()
                continue

            send_command(ser, cmd)


if __name__ == "__main__":
    main()