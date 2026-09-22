import can
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Any


# ── EMS CAN config ──────────────────────────────────────────────────────────
CAN_INTERFACE = 'pcan'
CAN_CHANNEL   = 'PCAN_USBBUS1'
CAN_BITRATE   = 250000

REQ_ID  = 0x18DA00FA   # Tester → EMS  (DA=00, SA=FA)
RESP_ID = 0x18DAFA00   # EMS → Tester  (DA=FA, SA=00)
FC_ID   = REQ_ID       # Flow Control: Tester sends TO ECU = REQ_ID


app = FastAPI(title = 'read dtc,VIN,EMS from EMS via UDS protocol')

# ── ISO-TP session ───────────────────────────────────────────────────────────
dtc_dict = {
    "P000F": "pressure relief valve is open",
    "P0016": "DFC for camshaft offset angle exceeded",
    "P0071": "DFC for environment temperature plausibility check function",
    "P0072": "SRC low for Environment Temperature",
    "P0073": "SRC High for Environment Temperature",
    "P0078": "No load error on exhaust flap low pressure",
    "P0079": "Short circuit to ground error on exhaust flap low pressure",
    "P0080": "Short circuit to battery error on exhaust flap low pressure",
    "P0087": "minimum rail pressure exceeded",
    "P0088": "maximum rail pressure exceeded",
    "P0112": "Diagnostic fault check for SRC low in engine inlet valve air temperature upstream sensor",
    "P0113": "Diagnostic fault check for SRC high in engine inlet valve air temperature upstream sensor",
    "P0118": "SRC High for Engine coolant temperature(down stream)",
    "P0122": "Signal Range Check Low for APP1",
    "P0123": "Signal Range Check High for APP1",
    "P018F": "pressure relief valve reached maximun allowed opening count",
    "P0191": "maximum positive deviation of rail pressure exceeded",
    "P0192": "Sensor voltage below lower limit",
    "P0193": "Sensor voltage above upper limit",
    "P0194": "maximum negative rail pressure deviation with metering unit on lower limit is exceeded",
    "P0201": "open load",
    "P0202": "open load",
    "P0203": "open load",
    "P0204": "open load",
    "P0215": "Injection cut off demand (ICO) for shut off coordinator",
    "P0219": "Overspeed detection in component engine protection",
    "P0222": "Signal Range Check Low for APP2",
    "P0223": "Signal Range Check High for APP2",
    "P0237": "Diagnostic fault check for SRC low in air pressure upstream of intake valve sensor",
    "P0238": "Diagnostic fault check for SRC high in air pressure upstream of intake valve sensor",
    "P0251": "open load of metering unit output",
    "P0262": "general short circuit",
    "P0265": "general short circuit",
    "P0268": "general short circuit",
    "P0271": "general short circuit",
    "P0297": "Maximum threshold error for vehicle speed",
    "P02EE": "short circuit Low Side to High Side",
    "P02EF": "short circuit Low Side to High Side",
    "P02F0": "short circuit Low Side to High Side",
    "P02F1": "short circuit Low Side to High Side",
    "P0335": "DFC for crankshaft signal diagnose - no signal",
    "P0339": "DFC for crankshaft signal diagnose - disturbed signal",
    "P0340": "DFC for camshaft signal diagnose - no signal",
    "P0344": "DFC for camshaft signal diagnose - disturbed signal",
    "P0501": "Plausibility defect for vehicle speed",
    "P0504": "Plausibility check for Brake",
    "P0520": "Maximum oil pressure error in plausibility check",
    "P0522": "Minimum oil pressure error in plausibility check",
    "P0615": "No load error",
    "P0616": "Short circuit to ground error",
    "P0617": "Short circuit to battery error",
    "P062D": "short circuit",
    "P062E": "short circuit",
    "P062F": "EEP Erase Error based on the error for more blocks",
    "P0641": "Error Sensor supplies 1",
    "P0651": "Error Sensor supplies 2",
    "P0668": "SRC low for ECU temperature sensor",
    "P0669": "SRC high for ECU temperature sensor",
    "P0697": "Error Sensor supplies 3",
    "P072A": "Plausibility check for Gbx SCG",
    "P081D": "Plausibility check for Gbx SCB",
    "P0830": "Plausibility check for Clutch",
    "P1003": "setpoint of metering unit in overrun mode not plausible",
    "P1004": "setpoint of metering unit in idle mode not plausible",
    "P1005": "maximum rail pressure exceeded (second stage)",
    "P100F": "pressure relief valve reached maximun allowed open time",
    "P1010": "short circuit to battery in the high side of the MeUn",
    "P1011": "short circuit to ground in the high side of the MeUn",
    "P1012": "short circuit to battery of metering unit output",
    "P1013": "short circuit to ground of metering unit output",
    "P1014": "over teperature of device driver of metering unit",
    "P1020": "pressure relief valve is forced to open; perform pressure increase",
    "P1021": "pressure relief valve is forced to open; perform pressure shock",
    "P102E": "Dosing Valve is blocked",
    "P102F": "Error in dosing valve plausibility at low voltage",
    "P103B": "Error of Urea Tank Level Sensor with Physical Range Check low",
    "P103C": "Error of Urea Tank Level Sensor evaluation with Physical Range Check high",
    "P1041": "Physical Range Check low for Urea Temperature Sensor",
    "P1042": "Physical Range Check high for Urea Temperature Sensor",
    "P1043": "Error Tank temperature sensor plausibility min threshold",
    "P1044": "Error Tank temperature sensor plausibility max threshold",
    "P104D": "General backflow line plausability error",
    "P104E": "General pressure check error",
    "P104F": "Pressure stabilisation error",
    "P1068": "Plausibility Check for air pressure at the upstream of intake valve sensor",
    "P1069": "Plausibility Check for air pressure at the upstream of intake valve sensor",
    "P1070": "Over temperature error on exhaust flap low pressure",
    "P1088": "No load error on highside powerstage for Urea back flow pump",
    "P1089": "Over temperature error on highside powerstage for Urea back flow pump",
    "P108A": "Short circuit to ground error on highside powerstage for Urea back flow pump",
    "P108B": "Short circuit to battery error on highside powerstage for Urea back flow pump",
    "P108C": "No load error on low powerstage for Urea back flow pump",
    "P108D": "Over temperature error on low powerstage for Urea back flow pump",
    "P108E": "Short circuit to ground error on low powerstage for Urea back flow pump",
    "P108F": "Short circuit to battery error on low powerstage for Urea back flow pump",
    "P10E8": "Low threshold for pressure sensor plausibility",
    "P10E9": "high threshold for pressure sensor plausibility",
    "P1116": "defect fault check for Absolute plausibility test",
    "P1117": "defect fault check for dynamic plausibility test",
    "P1190": "rail pressure raw value is below minimum offset",
    "P1191": "rail pressure raw value is above maximum offset",
    "P1201": "DFC for NOx availability diagnosis for sensor 2.",
    "P1330": "Short circuit to battery error at acuator relay",
    "P1332": "Short circuit to ground error at actuator relay",
    "P1350": "Powerstage diagnosis could be disabled due to high Battery voltage",
    "P1351": "Powerstage diagnosis could be disabled due to low Battery voltage",
    "P1420": "DFC for Evaluation of both Temperature Ranges",
    "P1500": "Signal error for vehicle speed over CAN",
    "P1600": "Diagnostic fault check to report the NTP error in ADC monitoring",
    "P1601": "Diagnostic fault check to report the ADC test error",
    "P1602": "Diagnostic fault check to report the error in Voltage ratio in ADC monitoring",
    "P1610": "Diagnostic fault check to report multiple error while checking the complete ROM-memory",
    "P1611": "Loss of synchronization sending bytes to the MM from CPU.",
    "P1612": "Over temperature error on ECU powerstage for Starter",
    "P1620": "Diagnostic fault check to report errors in query-/response-communication",
    "P1621": "Diagnostic fault check to report errors in SPI-communication",
    "P1630": "DFC to set a torque limitation once an error is detected before MoCSOP's error reaction is set",
    "P1631": "Wrong set response time",
    "P1632": "Too many SPI errors during MoCSOP execution.",
    "P1633": "Diagnostic fault check to report the error in undervoltage monitoring",
    "P1634": "Diagnostic fault check to report that WDA is not working correct",
    "P1635": "OS timeout in the shut off path test. Failure setting the alarm task period.",
    "P1636": "Diagnostic fault check to report that the positive test failed",
    "P1637": "Diagnostic fault check to report the timeout in the shut off path test",
    "P1638": "Diagnostic fault check to report the error in overvoltage monitoring",
    "P1639": "Diagnostic fault check to report the error due to Over Run",
    "P1650": "No load error",
    "P1651": "No load error",
    "P1652": "Short circuit to battery error",
    "P1653": "Short circuit to ground error",
    "P16C0": "Visibility of SoftwareResets in DSM",
    "P16C1": "Visibility of SoftwareResets in DSM",
    "P16C2": "Visibility of SoftwareResets in DSM",
    "P16E0": "Diagnostic fault check to report \"WDA active\" due to errors in query-/response communication",
    "P16E1": "Diagnostic fault check to report \"ABE active\" due to undervoltage detection",
    "P16E2": "Diagnostic fault check to report \"ABE active\" due to overvoltage detection",
    "P16E3": "Diagnostic fault check to report \"WDA/ABE active\" due to unknown reason",
    "P16F0": "Reported SPI and COM-Errors of a Cy146",
    "P16F1": "SPI/COM-Errors of the Cy320",
    "P16F2": "CY33X is defect",
    "P16F3": "Reported MSC-Errors of a R2S2",
    "P16F4": "Error during read/write operation",
    "P203C": "DFC for SRC low error of the urea tank level sesnor",
    "P203D": "DFC for SRC high error of the urea tank level sesnor",
    "P203F": "Status of tank level",
    "P2044": "SRC low for Urea temperature sensor",
    "P2045": "SRC high for Urea temperature sensor",
    "P204C": "SRC low for Urea Pump Module Pressure Sensor",
    "P204D": "SRC high for Urea Pump Module Pressure Sensor",
    "P204F": "Monitoring of the time until the dosing release is given",
    "P208A": "No load error on powerstage for urea pump motor",
    "P208C": "Short circuit to ground error on powerstage for urea pump motor",
    "P208D": "Short circuit to battery error on powerstage for urea pump motor",
    "P20E8": "Physical Range Check low for Urea Pump Module Pressure Sensor",
    "P20E9": "Physical Range Check high for Urea Pump Module Pressure Sensor",
    "P20F4": "Urea tank sensor indicates too high fill level",
    "P20F5": "Urea tank sensor indicates too low fill level",
    "P2135": "In case of dual analog accelerator pedal, it is the plausibility check between APP1 and APP2 and in case of potentiometer switch accelerator pedal, it is the plausibility check between APP1 and idle switch",
    "P2200": "0",
    "P2228": "SRC low for Environment Pressure",
    "P2229": "SRC High for Environment Pressure",
    "P2507": "SRC low for battery voltage sensor",
    "P2508": "SRC high for battery voltage sensor",
    "P2533": "Defective T50 switch",
    "P268C": "check of missing injector adjustment value programming",
    "P268D": "check of missing injector adjustment value programming",
    "P268E": "check of missing injector adjustment value programming",
    "P268F": "check of missing injector adjustment value programming",
    "P3000": "error passive CAN A",
    "P3002": "BusOff error CAN A",
    "P3048": "Short circuit to ground error in high side powerstage of Urea dosing valve actuator",
    "P3049": "Over temperature error on powerstage of Urea dosing valve actuator",
    "P304A": "Monitoring of Pressure Build Up Malfuntion",
    "P304B": "Short circuit to battery error in powerstage of Urea dosing valve actuator",
    "P304C": "Short circuit to ground error in powerstage of Urea dosing valve actuator",
    "P304D": "Short circuit to battery error in high side powerstage of Urea dosing valve actuator",
    "P305B": "Error Urea tank temperature is overheated",
    "P3080": "Error SCR catalyst upstream temperature sensor plausibility max threshold",
    "P3081": "Error SCR catalyst upstream temperature sensor plausibility min threshold",
    "P3085": "Pump Motor Speed Deviation",
    "P3086": "Permanent Pump Motor Speed Deviation",
    "P3087": "Pump motor not available for actuation",
    "P3088": "Over temperature error on powerstage for urea pump motor",
    "P308B": "Defective pressure reduction",
    "P3099": "Diagnostic Fault Check for Supply Module temperature Duty cycle in failure range",
    "P309A": "Diagnostic Fault Check for Supply Module temperature Duty cycle in failure range",
    "P309B": "Diagnostic Fault Check for Supply Module temperature Duty cycle in failure range",
    "P309C": "Diagnostic Fault Check for Supply Module temperature Duty cycle in failure range",
    "P30E8": "Underpressure monitoring in METERING CONTROL",
    "P30E9": "Overpressure monitoring in METERING CONTROL",
    "P30EA": "Monitoring of over pressure",
    "P30EE": "DFC for Evaluation of Temprature Range 1",
    "P30EF": "DFC for Evaluation of Temprature Range 2",
    "P3109": "Timeout Error of CAN-Transmit-Frame INCON",
    "P3201": "DFC for peak plausibility check for NOx sensor downstream of SCR Cat",
    "P3202": "DFC for Stuck in range error check for NOx sensor downstream of SCR Cat",
    "U0113": "Acknowledgement message error for DM19Ds CAN message on exceeding the maximum limit of Ack message reception",
    "U0155": "Timeout Error of CAN-Receive-Frame Dash Display",
    "U0423": "DFC for DLC Error of CAN-Receive-Frame Dash Display",
    "U129A": "DLC Error of CAN-Receive-Frame AT1O1",
    "U129B": "Timeout Error of CAN-Receive-Frame AT1O1",
    "U129C": "DFC for AT1OGC2Rx Frame Timeout error",
    "U129E": "DFC for AT1OGC1Rx Frame Timeout Error",
    "U1423": "DFC for DLC Error of CAN-Receive-Frame VDHR",
    "U159D": "SAE J1939 error for Aftertreatment 1 Outlet Gas NOx Sensor Heater Ratio message.",
    "U159E": "SAE J1939 error for NOx Concentration Downstream message",
    "U3100": "Timeout Error of CAN-send-Frame ACK",
    "U3102": "Timeout Error of CAN-Transmit-Frame DLCC1",
    "U3103": "Timeout Error of CAN-Transmit-Frame EEC1",
    "U3104": "Timeout Error of CAN-Transmit-Frame EEC2",
    "U3105": "Timeout Error of CAN-Transmit-Frame EEC3",
    "U3106": "Timeout Error of CAN-Transmit-Frame EFL_P1",
    "U3107": "Timeout Error of CAN-Transmit-Frame EngTemp",
    "U3108": "Timeout Error of CAN-Transmit-Frame FlEco",
    "U310A": "Timeout Error of CAN-Transmit-Frame FlC",
    "U310B": "Timeout Error of CAN-Receive-Frame VDHR",
    "U310F": "Timeout DFC for NOxSensGlbReqTx.",
    "U3110": "Timeout DFC for TxPGNRQ."
}

IQA_ALPHABET = {
    0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I',   # A-I (7,8 confirmed)
    20:'W',                                                          # confirmed
    23:'0',24:'1',25:'2',26:'3',27:'4',28:'5',29:'6',30:'7',31:'8', # digits (1,4,7 confirmed)
    # 9,10,11,12,13,14,15,16,17,18,19,21,22 -> UNKNOWN (J-Z with exclusions)
}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # your Vite/React origin
    allow_methods=["GET"],
    allow_headers=["*"],
)

class IsoTpSession:
    def __init__(self, bus, req_id, resp_id, fc_id):
        self.bus     = bus
        self.req_id  = req_id
        self.resp_id = resp_id
        self.fc_id   = fc_id

    def send(self, payload: bytes):
        try:
            msg = can.Message(
                arbitration_id=self.req_id,
                data=payload.ljust(8, b'\x00'),
                is_extended_id=True
            )
            self.bus.send(msg)
            print(f">> {payload.hex().upper()}")
        except can.CanError as e:
            print(f"!! Send error: {e}")
            raise

    def _safe_recv(self, timeout: float) -> can.Message | None:
        """Wraps bus.recv() to catch PCAN driver-level exceptions gracefully."""
        try:
            return self.bus.recv(timeout=timeout)
        except Exception as e:
            print(f"!! bus.recv() exception (PCAN driver): {e}")
            return None

    def recv(self, timeout: float = 5.0) -> bytes | None:
        start = time.time()

        while time.time() - start < timeout:
            msg = self._safe_recv(timeout=0.5)

            if msg is None or msg.arbitration_id != self.resp_id:
                continue

            data = msg.data
            print(f"<< {data.hex().upper()}")

            # NRC 0x78 — response pending, reset timer
            if len(data) >= 4 and data[1] == 0x7F and data[3] == 0x78:
                print("... ECU busy (0x78), waiting")
                start = time.time()
                continue

            pci = data[0] & 0xF0  

            # Single Frame
            if pci == 0x00:
                length = data[0] & 0x0F 
                return bytes(data[1:1 + length])

            # First Frame — multi-frame response
            elif pci == 0x10:
                total_len = ((data[0] & 0x0F) << 8) | data[1]
                payload   = bytearray(data[2:])
                print(f"[ISO-TP] Multi-frame start, total={total_len} bytes")

                # Flow Control: Tester → ECU, so use fc_id = REQ_ID
                fc = can.Message(
                    arbitration_id=self.fc_id,
                    data=bytes([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                    is_extended_id=True
                )
                self.bus.send(fc)
                print(">> Flow Control sent")

                # Collect consecutive frames
                expected_seq = 1
                cf_timeout   = 2.0   # wider window — EMS may have inter-frame delay

                while len(payload) < total_len:
                    cf = self._safe_recv(timeout=cf_timeout)

                    if cf is None:
                        print(f"!! CF timeout — collected {len(payload)}/{total_len} bytes")
                        break

                    if cf.arbitration_id != self.resp_id:
                        continue

                    print(f"<< CF {cf.data.hex().upper()}")

                    if (cf.data[0] & 0xF0) == 0x20:
                        seq = cf.data[0] & 0x0F

                        if seq != expected_seq:
                            print(f"!! CF seq error: expected {expected_seq}, got {seq} — aborting")
                            return None

                        remaining = total_len - len(payload)
                        payload.extend(cf.data[1: 1 + min(7, remaining)])
                        expected_seq = (expected_seq + 1) % 16
                        print(f"   progress: {len(payload)}/{total_len} bytes")

                if len(payload) < total_len:
                    print(f"!! Incomplete frame: got {len(payload)}/{total_len} bytes")
                    return None

                return bytes(payload[:total_len])

        print("!! Session timeout — no response from EMS")
        return None

# ── DTC parser ───────────────────────────────────────────────────────────────

def parse_dtcs_json(data: bytes | None) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if not data or data[0] != 0x59:
        return output
    dtc_bytes = data[3:]
    if len(dtc_bytes) < 4:
        return output

    seen = set()
    prefix = {0x00: "P", 0x01: "C", 0x02: "B", 0x03: "U"}
    for i in range(0, len(dtc_bytes) - 3, 4):
        b1, b2, b3, b4 = dtc_bytes[i:i+4]
        if (b1 == 0xFF and b2 == 0xFF) or (b1 == 0x00 and b2 == 0x00):
            continue
        dtc = f"{prefix.get(b1, 'P')}{b2:02X}{b3:02X}"
        if dtc in seen:
            continue
        seen.add(dtc)
        output.append({
            "code": dtc,                                  # NOTE: "code", not "dtc"
            "status": f"0x{b4:02X}",
            "description": dtc_dict.get(dtc, "Unknown DTC"),
            "severity": classify_status(b4),
        })
    return output

def conversion(slot: bytes) -> str | None:
    if not any(slot[:5]):                 # all-zero -> unused slot
        return None
    word = int.from_bytes(slot[:4], byteorder='big')
    bits = f"{word:032b}"[:30]            # chars 1-6 (drop 2 pad bits)
    idx = [int(bits[i:i+5], 2) for i in range(0, 30, 5)]
    idx.append(slot[4] >> 3)              # char 7 from byte 4 (drop 3 pad bits)
    return ''.join(IQA_ALPHABET.get(i, '?') for i in idx)          

def  read_iqa_data(data: bytes | None) -> list | None:
    if data[:3] != bytes([0x62, 0x04, 0x18]):
        raise ValueError(f"Not a 62 0418 response: {data[:3].hex()}")
    code : list = []
    
    payload = data[3:]
    for i in range(0, len(payload), 8):
        slot = payload(data[i:i+8])
        if len(slot) < 5:
            break
        converted = conversion(slot)
        if converted is not None:
            code.append(converted)
    return code

        
    
def classify_status(status: int) -> str:
    """
    ISO 14229-1 §D.2 — status byte is a bitmask:
      bit 0  testFailed
      bit 2  pendingDTC
      bit 3  confirmedDTC
    """
    confirmed   = bool(status & 0x08)
    test_failed = bool(status & 0x01)
    pending     = bool(status & 0x04)

    if confirmed and test_failed:
        return 'high'
    elif confirmed or pending:
        return 'medium'
    else:
        return 'low'


def parse_dtcs(data: bytes | None):
    if not data:
        print("No DTC data received")
        return

    if data[0] != 0x59:
        print(f"Unexpected SID: 0x{data[0]:02X} (expected 0x59)") 
        return

    dtc_bytes = data[3:]

    if len(dtc_bytes) < 4:
        print("No DTCs present in EMS")
        return

    seen   = set()
    high   = []
    medium = []
    low    = []

    for i in range(0, len(dtc_bytes), 4):
        if i + 4 > len(dtc_bytes):
            break

        b1, b2, b3, b4 = dtc_bytes[i], dtc_bytes[i+1], dtc_bytes[i+2], dtc_bytes[i+3]

        if (b1 == 0xFF and b2 == 0xFF) or (b1 == 0x00 and b2 == 0x00):
            continue

        if f"{b1:02X}" == "00":
            dtc = f"P{b2:02X}{b3:02X}"
        if f"{b1:02X}" == "01":
            dtc = f"C{b2:02X}{b3:02X}"
        if  f"{b1:02X}" == "02":    
            dtc = f"B{b2:02X}{b3:02X}"
        if f"{b1:02X}" == "03":
            dtc = f"U{b2:02X}{b3:02X}"    
   
        status = b4

        if dtc in seen:
            continue
        seen.add(dtc)

        bucket = classify_status(status)
        entry  = (dtc, status)

        if bucket == 'high':
            high.append(entry)
        elif bucket == 'medium':
            medium.append(entry)
        else:
            low.append(entry)

    print("\n========== EMS DTC SUMMARY ==========\n")

    print(f"HIGH   — Confirmed + active ({len(high)}):")
    for dtc, st in high:
        if dtc in dtc_dict:
            desc = dtc_dict[dtc]
            print(f"  DTC {dtc}  status=0x{st:02X}  bits={st:08b}  — {desc}")
        else : 
            print(f"  DTC {dtc}  status=0x{st:02X}  bits={st:08b} ")

    print(f"\nMEDIUM — Confirmed or pending ({len(medium)}):")
    for dtc, st in medium:
        if dtc in dtc_dict:
            desc = dtc_dict[dtc]
            print(f"  DTC {dtc}  status=0x{st:02X}  bits={st:08b}  — {desc}")
        else :     
            print(f"  DTC {dtc}  status=0x{st:02X}  bits={st:08b}")

    print(f"\nLOW    — Not currently active ({len(low)}):")
    for dtc, st in low:
        if dtc in dtc_dict:
            desc = dtc_dict[dtc]
            print(f"  DTC {dtc}  status=0x{st:02X}  bits={st:08b}  — {desc}")
        else :     
            print(f"  DTC {dtc}  status=0x{st:02X}  bits={st:08b}")

    total = len(high) + len(medium) + len(low)
    print(f"\nTotal DTCs: {total}  (high={len(high)}, medium={len(medium)}, low={len(low)})")
    print("=====================================\n")
    return 


# ── Main ─────────────────────────────────────────────────────────────────────
@app.get("/scan") 
def main():
    bus = can.Bus(
        interface=CAN_INTERFACE,
        channel=CAN_CHANNEL,
        bitrate=CAN_BITRATE
    )

    session = IsoTpSession(bus, REQ_ID, RESP_ID, FC_ID)

    try:
        print("\n[1] Extended Diagnostic Session")
        session.send(b'\x02\x10\x03')
        session.recv()

        print("Read VIN")
        session.send(b'\x03\x22\xF1\x90')
        VIN_res = session.recv()
        VIN_read = VIN_res[3:].decode('utf-8')
        print (f"VIN : '{VIN_read}")

        print("Read ESN")
        session.send(b'\x03\x22\xF1\x57')
        ESN_res = session.recv()
        ESN_read = ESN_res[3:].decode('utf-8')
        print (f"VIN : '{ESN_read}")

        print("\n[3] Read Pending DTCs (0x19 02 04)")
        session.send(b'\x03\x19\x02\x04')
        dtc_data = session.recv()

        print("\n[4] Read IQA values (0x22 04 81)")
        session.send(b'\x03\x22\x04\x81')
        iqa = session.recv()
        physical_iqa = read_iqa_data(iqa)
        print(f"Physical IQA: {physical_iqa}")

        print("\n[5] Read_engine_cal_id:")
        session.send(b'\x03\x22\xF1\x8A')
        cal_id_res = session.recv()
        cal_id = cal_id_res[3:].decode('utf-8')
        print(f"Calibration ID: {cal_id}")


        parse_dtcs(dtc_data)
        return {"status": "scan complete", "vin": VIN_read, "esn": ESN_read,"dtcs": parse_dtcs_json(dtc_data) , "iqa": physical_iqa, "cal_id" : cal_id}
    

    finally:
        bus.shutdown()
        print("Bus shutdown complete")

if __name__ == "__main__":
    main()


