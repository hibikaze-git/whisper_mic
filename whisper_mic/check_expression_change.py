import argparse
import threading
import time
from typing import List
from pythonosc import dispatcher, osc_server, udp_client


client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

LAST_EXPRESSION_CHANGE_TIME = time.time()
LAST_EXPRESSION_NUM = 0


def printdata(address: str, *osc_arguments: List[str]):
    print(address + "  " + str(osc_arguments[0]))

    if "FaceEmo_SYNC_EM_EMOTE" in address:
        global LAST_EXPRESSION_CHANGE_TIME
        global LAST_EXPRESSION_NUM
        LAST_EXPRESSION_CHANGE_TIME = time.time()
        LAST_EXPRESSION_NUM = int(osc_arguments[0])


def check_expression_change_time():
    while True:
        global LAST_EXPRESSION_CHANGE_TIME
        global LAST_EXPRESSION_NUM
        elapsed_time = time.time() - LAST_EXPRESSION_CHANGE_TIME
        if elapsed_time > 15 and LAST_EXPRESSION_NUM != 0:
            global client
            client.send_message("/avatar/parameters/FaceEmo_SYNC_EM_EMOTE", 0)

        time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9001, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/*", printdata)

    check_thread = threading.Thread(target=check_expression_change_time)
    check_thread.setDaemon(True)
    check_thread.start()

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

    check_thread.join()
