# NFC UID Reader

A basic command-line tool that prints the UID (serial number) and ATR of every contactless card or NFC tag tapped on a PC/SC reader. It works with USB readers and with the contactless readers built into many business laptops, on Windows, macOS and Linux.

It's useful for checking what a card reports, comparing cards, and seeing which chip a reader picks when a card or tag holds more than one.

## Features

- Lists all connected readers and picks the first contactless one automatically
- Choose a reader by its number or part of its name
- Prints each new card once, with a timestamp, and again after it's removed and re-tapped
- Optional JSON output, one object per card, for logging or piping into other tools
- Reports when a reader refuses the UID request instead of failing silently

## Requirements

- Python 3.9 or newer
- A PC/SC-compatible reader with its driver installed
- `pip install -r requirements.txt` (installs pyscard)
- Linux only: the `pcscd` service must be running (`sudo apt install pcscd`)

## Usage

```bash
python uid_reader.py --list
python uid_reader.py
python uid_reader.py --reader 1
python uid_reader.py --reader contactless --json
python uid_reader.py --once
```

Example output:

```
Using: ACS ACR1252 1S CL Reader PICC 0
Tap a card. Press Ctrl+C to stop.

2026-01-15T14:02:11  UID: 04 A2 2B 1C 5E 61 80  |  ATR: 3B 8F 80 01 80 4F 0C A0 00 00 03 06 03 00 03 00 00 00 00 68
```

## Options

| Option | Description |
| --- | --- |
| `--list` | List the connected readers and exit |
| `--reader` | Reader number from `--list`, or part of its name |
| `--once` | Exit after the first card |
| `--json` | Print one JSON object per card: time, reader, uid, atr, status |
| `--interval` | Seconds between checks (default 0.3) |

## How it works

When a card is present, the tool connects to it and sends the standard PC/SC "Get Data" command (`FF CA 00 00 00`), which asks the reader for the card's UID. The ATR (Answer To Reset) is the reader's description of the card, and it differs between chip types. If the reader answers with anything other than success (`90 00`), the tool prints the status code it returned.

## Notes

- Some readers don't support the UID command, and some cards and phones return a new random UID on every tap. This is a security feature I will crack later.
- **A UID is not a secret.** It can be read by anyone nearby and copied onto a beater card, so it shouldn't be the only thing protecting access to anything.
- Built-in laptop readers often need the manufacturer's driver, and sometimes need to be enabled in the BIOS. I used Dell Latitude laptops E7470 for testing.

## Disclaimer

This software is provided "as is", without warranty of any kind. The author is not responsible for any damage, loss or misuse resulting from its use. Only read cards and tags that you own or have permission to read, and probably don't use this tool to copy credentials, gain unauthorized access, or break any law or policy.

## License

MIT. See [LICENSE](LICENSE).
