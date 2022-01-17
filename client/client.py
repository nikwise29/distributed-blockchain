import socket
import logging
import json
import sys
import pathlib
import os
import time

from queue import PriorityQueue
from constants import *
from lamport_mutex_utils import *

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class Client:

    def __init__(self, host, port, client_dict):
        logger.info("Host : " + host)
        logger.info("Port :" + str(port))
        self.client_dict = client_dict

        self.timestamp = Timestamp(0, os.getpid())
        self.request_queue = PriorityQueue()

        # Testing the priority queue

        #self.request_queue.put(Timestamp(10, 1234))
        #self.request_queue.put(Timestamp(1, 4321))
        #self.request_queue.put(Timestamp(3, 3758))
        #self.request_queue.put(Timestamp(3, 2345))
        #self.request_queue.put(Timestamp(6, 9577))

        #while self.request_queue:
        #    logger.info(repr(self.request_queue.get()))

        self.start_client(host, port)
        
        # self.host = host
        # self.port = port

    @staticmethod
    def display_menu():
        print("a. Press 1 to make a new transaction.")
        print("b. Press 2 to get balance")
        print("c. Press 3 to quit")

    def get_response_from_server(self, msg_dict, client_socket):
        msg_str = json.dumps(msg_dict)
        logger.debug('Message sent to blockchain master : ' + msg_str)
        time.sleep(2)
        client_socket.sendall(msg_str.encode())
        data = client_socket.recv(1024).decode()
        logger.debug('Message received from blockchain master : ' + repr(data))
        return data

    def start_client(self, client_host, client_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

            client_socket.bind((client_host, client_port))
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            while True:
                self.display_menu()
                user_input = input("Client prompt >> ")
                if user_input == "1":
                    self.handle_transfer_transaction(client_socket)

                elif user_input == "2":
                    msg_dict = {'type': 'balance_transaction'}
                    response = self.get_response_from_server(msg_dict, client_socket)
                    logger.info("Your current balance is : $" + response)

                elif user_input == "3":
                    msg_dict = {'type': 'quit'}
                    self.get_response_from_server(msg_dict, client_socket)
                    logger.info("Bye..have a good one!")
                    break

                else:
                    logger.warning("Incorrect menu option. Please try again..")
                    continue

    def handle_transfer_transaction(self, client_socket):
        receiver_id = input("Enter receiver client id  >> ")
        # TODO : add check if receiver is available in the config list or not
        if receiver_id not in self.client_dict:
            logger.error("Client id does not exist. Please try again with a valid client id..")
            return
        receiver_addr = self.client_dict[receiver_id]['host'] + ":" + str(self.client_dict[receiver_id]['port'])
        amount = input("Enter the amount in $$ to be transferred to the above client  >> ")
        msg_dict = {'type': 'transfer_transaction', 'receiver': receiver_addr, 'amount': amount}
        response = self.get_response_from_server(msg_dict, client_socket)
        if response == '0':
            print("SUCCESS")
            # print("Your transaction executed successfully")
        elif response == '1':
            print("INCORRECT")
            # print("The transaction failed due to insufficient funds!")
        elif response == '2':
            print("INCORRECT")
            # print("The transaction failed due to an error. Try again after sometime !")


if __name__ == '__main__':

    client_id = sys.argv[1]
    with open(os.path.join(pathlib.Path(__file__).parent.resolve(),'config.json'), 'r') as config_file:
        config_dict = json.load(config_file)
        client_dict = config_dict["clients"]
        if client_id not in client_dict:
            logger.error("Invalid client id. Please check...")
        else:
            logger.info("Initiating client..")
            Client(client_dict[client_id]["host"], client_dict[client_id]["port"], client_dict)



