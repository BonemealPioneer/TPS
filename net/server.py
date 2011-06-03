import socket
import thread
import logging
import select
import struct

from connectioninfo import ConnectionInfo
from messagehandlerservice import MessageHandlerService
from message import Message

HEADER_FORMAT = '<i' # little endian integer
PROTOCOL_VERSION = 3
SERVER_VERSION = "Terraria" + str(PROTOCOL_VERSION)
MESSAGE_TYPE_FORMAT = '<B' # little endian byte (char)

log = logging.getLogger()

class NetworkState:
  Starting = 0
  Running = 1
  Closing = 2
  Closed = 3
  Error = 4

class ConnectionManager:

  def __init__(self, world):
    self.__connections = []
    self.locker = thread.allocate_lock()
    self.world = world

  def connectionCount(self):
    connectionCount = 0
    self.locker.acquire()
    connectionCount = len(self.__connections)
    self.locker.release()
    return connectionCount

  def addConnection(self, connection):
    self.locker.acquire()
    self.__connections.append(connection)
    self.locker.release()

  def removeConnection(self, connection):
    connection.socket.shutdown(socket.SHUT_RDWR)
    connection.socket.close()
    self.locker.acquire()
    self.__connections.remove(connection)
    self.locker.release()

  def getListOfSocketsForSelect(self):
    result = []
    self.locker.acquire()
    for ci in self.__connections:
      result.append(ci.socket)
    self.locker.release()
    return result

  def findConnection(self, socket):
    result = None
    self.locker.acquire()
    for ci in self.__connections:
      if ci.socket == socket:
        result = ci
        break
    self.locker.release()
    return result

  def getNewClientId(self):
    clientId = 0
    idList = []
    self.locker.acquire()
    # get a list of the clientIds
    for ci in self.__connections:
      idList.append(ci.clientNumber)      
    self.locker.release()
    # now we just want to find the next available id
    while clientId in idList:
      clientId += 1
    return clientId

class TerrariaServer:

  def __init__(self, listenAddr, listenPort, password=None):
    self.listenAddress = listenAddr
    self.listenPort = listenPort
    self.password = password
    self.networkState = NetworkState.Closed
    self.connectionManager = ConnectionManager()
    self.messageHandlerService = MessageHandlerService(self)

  def __setupSocket(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.bind((self.listenAddress, self.listenPort))
      self.socket.listen(5)
      log.debug("Server listening on " + str(self.listenAddress))
      self.networkState = NetworkState.Running
    except Exception as ex:
      log.error(ex)
      self.networkState = NetworkState.Error

  def __doProtocol(self, connection):
    log.debug("Got data from socket...doing protocol goodness")
    try:
      header = connection.socket.recv(4) # first 4 bytes tell us the message length
      if len(header) == 0:
        self.connectionManager.removeConnection(connection)
      msgLen = struct.unpack(HEADER_FORMAT, header)[0] # unpack returns a tuple 
      connection.data = connection.socket.recv(msgLen)
      # Now get the rest of the message from the client....
      log.debug("Got message with " + str(msgLen) + " size")
      # first byte of the data is the message Type
      messageType = struct.unpack(MESSAGE_TYPE_FORMAT, connection.data[0])[0]
      message = Message(messageType)
      message.appendRaw(connection.data[1:])
      log.debug("Processing message...")
      self.messageHandlerService.processMessage(message, connection)
    except Exception as ex:
      log.error(ex)
      self.connectionManager.removeConnection(connection)

  def __readThread(self):
    while self.networkState == NetworkState.Running:
      socketList = self.connectionManager.getListOfSocketsForSelect()
      socketsToRead, socketsToWrite, socketsWithError = select.select(socketList, [], socketList, 0)
      for serr in socketsWithError:
        self.connectionManager.removeConnection(self.connectionManager.findConnection(serr))
      for s in socketsToRead:
        self.__doProtocol(self.connectionManager.findConnection(s))

  def __mainLoop(self):
    while self.networkState == NetworkState.Running:
      (clientsock, clientaddr) = self.socket.accept()
      # New connection here
      log.debug("New connection from " + str(clientaddr))
      connection = ConnectionInfo(clientsock, clientaddr, self.connectionManager.getNewClientId())
      log.debug("Client id: " + str(connection.clientNumber))
      self.connectionManager.addConnection(connection)

  def start(self):
    log.debug("Server starting up...")
    self.__setupSocket()
    # set up a thread to read from the clients sockets
    thread.start_new_thread(self.__readThread, ())
    self.__mainLoop()
     