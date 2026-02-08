# Centauri Carbon – OctoPrint Bridge

This project provides a **minimal OctoPrint-compatible API bridge** for the **Elegoo Centauri Carbon**.

It allows you to **upload G-code over the network from slicers that only support OctoPrint**
(e.g. Bambu Studio).

⚠️ **This is NOT a real OctoPrint server.**  
It is a lightweight shim that implements just enough of the OctoPrint API to satisfy slicers and
translates file uploads to the Centauri Carbon native protocol (SDCP / HTTP).

---

## What This Does

- ✅ Use **OctoPrint** as printer type in your slicer
- ✅ Upload **G-code over LAN**
- ✅ Works with **Bambu Studio / Orca forks**
- ✅ Runs on **Raspberry Pi or any Linux host**
- ✅ No cloud, no Elegoo Link, no slicer changes

---

## What This Does NOT Do

- ❌ Not a full OctoPrint implementation
- ❌ No webcam, no live progress, no terminal
- ❌ No USB/serial printer control
- ❌ Not safe to expose to the internet

---

## Architecture

The slicer believes it is talking to OctoPrint version 1.1 or newer.

The bridge receives the standard OctoPrint file upload request and forwards the file
to the Centauri Carbon using the printer native upload endpoint.

Flow:

Slicer (OctoPrint mode)
-> HTTP multipart upload
-> POST /api/files/local

OctoPrint Bridge (running on Raspberry Pi or Linux)
-> Translates request
-> SDCP HTTP upload

Elegoo Centauri Carbon
-> POST http://PRINTER_IP:3030/uploadFile/upload

---

## Requirements
- Any machine on the same local network as the printer
- Linux, macOS, or Windows
- One of the following:
	- Docker with Docker Compose
	- OR Python 3.10+ with pip (for running directly without containers)
- Elegoo Centauri Carbon with a known IP address
