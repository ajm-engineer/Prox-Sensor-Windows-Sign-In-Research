#!/usr/bin/env python3   # you also will need to pip3 install pyscard
import argparse
import json
import sys
import time

from smartcard.Exceptions import NoCardException, SmartcardException
from smartcard.System import readers
from smartcard.util import toHexString

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
CONTACTLESS_HINTS = ("contactless", "picc", "nfc")


def pick_reader(all_readers, choice):
    if choice is None:
        for r in all_readers:
            if any(h in str(r).lower() for h in CONTACTLESS_HINTS):
                return r
        return all_readers[0]
    if choice.isdigit():
        i = int(choice)
        if i >= len(all_readers):
            sys.exit(f"No reader with index {i}. Use --list to see the readers.")
        return all_readers[i]
    for r in all_readers:
        if choice.lower() in str(r).lower():
            return r
    sys.exit(f'No reader matching "{choice}". Use --list to see the readers.')


def read_card(reader):
    conn = reader.createConnection()
    conn.connect()
    try:
        data, sw1, sw2 = conn.transmit(GET_UID)
        atr = toHexString(conn.getATR())
    finally:
        conn.disconnect()
    uid = toHexString(data) if (sw1, sw2) == (0x90, 0x00) else None
    return uid, atr, f"{sw1:02X} {sw2:02X}"


def main():
    ap = argparse.ArgumentParser(description="Print the UID and ATR of contactless cards and tags tapped on a PC/SC reader.")
    ap.add_argument("--list", action="store_true", help="List the connected readers and exit")
    ap.add_argument("--reader", help="Reader index or part of its name (default: first contactless reader)")
    ap.add_argument("--once", action="store_true", help="Exit after the first card")
    ap.add_argument("--json", action="store_true", help="Print one JSON object per card")
    ap.add_argument("--interval", type=float, default=0.3, help="Seconds between checks (default 0.3)")
    args = ap.parse_args()

    try:
        all_readers = readers()
    except SmartcardException as e:
        sys.exit(f"Couldn't list readers: {e}. On Linux, make sure the pcscd service is running.")
    if not all_readers:
        sys.exit("No PC/SC readers found. Check that the reader is connected, enabled and has a driver installed.")
    if args.list:
        for i, r in enumerate(all_readers):
            print(f"[{i}] {r}")
        return

    reader = pick_reader(all_readers, args.reader)
    if not args.json:
        print(f"Using: {reader}\nTap a card. Press Ctrl C to stop.\n")

    last = None
    while True:
        try:
            uid, atr, status = read_card(reader)
        except NoCardException:
            last = None
        except SmartcardException:
            last = None
        else:
            if (uid, atr) != last:
                last = (uid, atr)
                stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
                if args.json:
                    print(json.dumps({"time": stamp, "reader": str(reader), "uid": uid, "atr": atr, "status": status}), flush=True)
                else:
                    shown = uid or f"not returned (reader status {status})"
                    print(f"{stamp}  UID: {shown}  |  ATR: {atr}", flush=True)
                if args.once:
                    return
        time.sleep(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
