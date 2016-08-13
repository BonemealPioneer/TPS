import ConfigParser, __builtin__

from config.server import ServerConfig
from net.server import TerrariaServer

def load_config():
  config = ConfigParser.RawConfigParser()
  config.read('server.cfg')
  return ServerConfig().from_config(config)

def main():
  config = load_config()
  
  __builtin__.server = TerrariaServer(config)
  server.run()

if __name__ == '__main__':
  main()
