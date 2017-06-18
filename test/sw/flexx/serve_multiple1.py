from flexx import config
import os

config.hostname="""0.0.0.0"""
config.port=80

from flexx import app
from flexx.ui.examples.monitor import Monitor
from flexx.ui.examples.chatroom import ChatRoom
from flexx.ui.examples.demo import Demo
from flexx.ui.examples.colab_painting import ColabPainting


if __name__ == '__main__':

    print(config)
    print os.getenv("APPDATA")    
    print os.getenv("appdata")    

    # This example is setup as a server app
    app.serve(Monitor)
    app.serve(ChatRoom)
    app.serve(ColabPainting)
    app.serve(Demo)
    app.start()

