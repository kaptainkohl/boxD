import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template

# WS_HANDLERS maintains a list of currently-opened ws connections
WS_HANDLERS = []

# maintain message history for new connections
MESSAGE_HISTORY = []

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(".")
        self.write(loader.load("client/index.html").generate())

class WSHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        print 'connection opened.'
        self.write_message("The server graciously welcomes you.")
        self.write_message("There are {} other people here".format(str(len(WS_HANDLERS))))

        if MESSAGE_HISTORY:
            self.write_message("Here are the past messages...")

        # send a dump of the message history to the new client
        for message in MESSAGE_HISTORY:
            self.write_message(message)

        # let everyone else know there's a new client
        for ws_handler in WS_HANDLERS:
            ws_handler.write_message("Someone joined.  There are now {} people here".format(str(len(WS_HANDLERS) + 1)))

        WS_HANDLERS.append(self)

    def on_message(self, message):

        # iterate over our list of connections and forward the message to each
        for ws_handler in WS_HANDLERS:

            # if the connection we're about to send to is the one who sent the message...
            if ws_handler is self:
                name = "You"       # ...refer to the client as "you"
            else:
                name = "A client"  # otherwise refer to the client as "A client"

            MESSAGE_HISTORY.append("Past message:  {}".format(message))     # add the message to history
            ws_handler.write_message("{} said:  {}".format(name, message))  # send the message.

        print 'message received:  {}'.format(message)

    def on_close(self):
        WS_HANDLERS.remove(self)  # remove the closed connection from our list of handlers

        # let the other clients know someone left
        for ws_handler in WS_HANDLERS:
            ws_handler.write_message('somebody left')

        print 'connection closed...'


application = tornado.web.Application([
  (r'/ws', WSHandler),  # endpoint for handling websocket connections
  (r'/', MainHandler),  # endpoint for general entry
  (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'static/css'})  # static css
])

if __name__ == "__main__":
    print 'starting'
    application.listen(9090)
    tornado.ioloop.IOLoop.instance().start()