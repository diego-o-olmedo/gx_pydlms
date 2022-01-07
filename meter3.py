import select, socket, os, sys, queue, logging, threading
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader

from gurux_common.enums import TraceLevel
from gurux_dlms.objects import GXDLMSObjectCollection
from meter2 import MeterTest

class Meter(threading.Thread):
    def run(self):
        meter = MeterTest(
            "-r ln -i WRAPPER -c 17 -s 1 -a Low -P tisretem01 -h 194.163.161.91 -p 5001 -t Verbose -o C:\\Users\\User\\Desktop\\Gx\device2.xml -g \"0.0.42.0.0.255:2;0.0.40.0.0.255:2\"")
        meter.main()
class Server():
    def __init__(self, host='194.163.161.91', port=5001, recv_buffer=4096):
        self.host = host
        self.port = port
        self.recv_buffer = recv_buffer
        # Sockets from which we expect to read
        self.inputs = []
        # Sockets to which we expect to write
        self.outputs = []
        # Outgoing message queues (socket:Queue)
        self.message_queues = {}

    def bind(self):
        try:
            # Create a TCP/IP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setblocking(0) # non blocking socket
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            # add server socket object to the list of readable connections
            self.inputs.append(self.server_socket)

            logging.info("Chat server listenning on port: {}, host: {}".format(self.port, self.host))

        except socket.error as error:
            logging.warning(error)
            logging.warning("Couldn't connect to the remote host: {}".format(self.host))
            sys.exit(1)

    # broadcast chat messages to all connected clients exept the socket in arg
    def broadcast(self, sock, data):
        for s in self.inputs:
            # send the message only to peer
            if not (s is self.server_socket) and not (s is sock):
                # Add output channel for response
                if s not in self.outputs:
                    self.outputs.append(s)

                self.message_queues[s].put(data)

    def run(self):
        self.bind()

        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            for s in readable:
                if s is self.server_socket:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = self.server_socket.accept()
                    connection.setblocking(0) # non blocking socket
                    self.inputs.append(connection)

                    self.message_queues[connection] = queue.Queue()

                    logging.info('Client (%s, %s) connected' % client_address)
                    if client_address[0] != '194.163.161.91':
                        thread = Meter()
                        thread.daemon = True
                        thread.start()
                        # meter = MeterTest("-r ln -i WRAPPER -c 17 -s 1 -a Low -P tisretem01 -h 194.163.161.91 -p 5001 -t Verbose -o C:\\Users\\User\\Desktop\\Gx\device2.xml -g \"0.0.42.0.0.255:2;0.0.40.0.0.255:2\"")
                        # meter.main()
                        # POST_request()
                        # addtask('Time_1', '0.0.1.1.0.101')
                        # r = requests.post('http://194.163.161.91:64881/api/task/AddTask', json=djson)
                # a message from a client on a new connection
                else:
                    try:

                        data = s.recv(self.recv_buffer)

                        if data:
                            # A readable client socket has data
                            logging.info('Received "%s" from %s' % (data, s.getpeername()))

                            self.broadcast(s, data)
                        else:
                            # Interpret empty result as closed connection
                            logging.warning('Closing {} after reading no data'.format(client_address))

                            # Stop listening for input on the connection
                            if s in self.outputs:
                                self.outputs.remove(s)
                            self.inputs.remove(s)
                            s.close()

                            # Remove message queue
                            del self.message_queues[s]
                    except:
                        continue

            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except queue.Empty:
                    logging.warning('Output queue for {} is empty'.format(s.getpeername()))
                    self.outputs.remove(s)
                else:
                    try:
                        logging.info('Sending "%s" to %s' % (next_msg, s.getpeername()))
                        s.send(next_msg)
                    except:
                        s.close()



            for s in exceptional:
                logging.warning('Handling exceptional condition for {}'.format(s.getpeername()))

                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()

                # Remove message queue
                del self.message_queues[s]

if __name__ == "__main__":
    server = Server()
    server.run()