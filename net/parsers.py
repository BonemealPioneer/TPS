from struct import calcsize, unpack
import logging

from messages import ConnectionRequestMessage, PlayerInfoMessage, PlayerHpMessage, PlayerManaMessage, \
    PlayerBuffMessage, PlayerInventoryMessage, RequestWorldDataMessage, TileBlockRequestMessage, SpawnMessage, \
    PlayerUpdateMessage, LoginWithPassword, Message

logger = logging.getLogger()


def parseConnectionRequest(rawMessage, session):
    message = ConnectionRequestMessage()
    message_length = unpack(Message.byteFormat,
        rawMessage[:Message.byteFormatLen])[0]  
    rawMessage = rawMessage[Message.byteFormatLen:]

    if len(rawMessage) is not message_length:
        message.clientVersion = None
        return message

    message.clientVersion = rawMessage
    return message

messageLookup = {
    ConnectionRequestMessage.MESSAGE_TYPE: parseConnectionRequest,
    LoginWithPassword.MESSAGE_TYPE: (lambda m, s: LoginWithPassword(s).deserialize(m)),
    PlayerInfoMessage.MESSAGE_TYPE: (lambda m, s: PlayerInfoMessage(s).deserialize(m)),
    PlayerHpMessage.MESSAGE_TYPE: (lambda m, s: PlayerHpMessage(s).deserialize(m)),
    PlayerManaMessage.MESSAGE_TYPE: (lambda m, s: PlayerManaMessage(s).deserialize(m)),
    PlayerBuffMessage.MESSAGE_TYPE: (lambda m, s: PlayerBuffMessage(s).deserialize(m)),
    PlayerInventoryMessage.MESSAGE_TYPE: (lambda m, s: PlayerInventoryMessage(s).deserialize(m)),
    RequestWorldDataMessage.MESSAGE_TYPE: (lambda m, s: RequestWorldDataMessage().deserialize(m)),
    TileBlockRequestMessage.MESSAGE_TYPE: (lambda m, s: TileBlockRequestMessage().deserialize(m)),
    PlayerUpdateMessage.MESSAGE_TYPE: (lambda m, s: PlayerUpdateMessage(s).deserialize(m)),
    SpawnMessage.MESSAGE_TYPE: (lambda m, s: SpawnMessage(s).deserialize(m))
}


class BinaryMessageParser(object):
    """
    A class to parse binary messages into higher level
    messages.
    """
    messageTypeFormat = "<B"
    messageTypeFormatLen = calcsize(messageTypeFormat)

    def parse(self, message, session=None):
        """
        Parses the binary message into a higher level message

        @param message: bytearray starting with messageType
        """

        #logger.debug("Parsing raw message: %r" % (message,))
        messageStr = bytes(message)
        messagePos = 0
        messageType, = unpack(
            self.messageTypeFormat, messageStr[
                messagePos:self.messageTypeFormatLen])
        
        messagePos += self.messageTypeFormatLen
        
        try:
            # dont include message type...
            parser = messageLookup[messageType](messageStr[1:], session)
            return parser
        except KeyError:
            logger.error(
                "Need to implement parser for message type: %d" % messageType)
        
        return None
