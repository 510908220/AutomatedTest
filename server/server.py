#!/usr/bin/env python

import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from pymongo import MongoClient

from handler import handle
from handler import uimodule
from handler import config

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/cases/(.*?)", handle.CasesHandler),
			(r"/tasks/(.*?)", handle.TasksHandler),
			(r"/results/(.*?)", handle.ResultsHandler),
			(r"/machines/(.*?)", handle.MachinesHandler),
			(r"/", handle.HomeHandler),
		]
		settings = dict(
			blog_title=u"Automate Test",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			ui_modules={"CaseItem": uimodule.CaseItemModule, "MachineItem": uimodule.MachineItemModule, "ResultItem":uimodule.ResultItemModule},
			debug=True
		)
		super(Application, self).__init__(handlers, **settings)
		client = MongoClient('mongodb://localhost:27017/')
		self.db = client[config.DB_NAME]


def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
	main()
