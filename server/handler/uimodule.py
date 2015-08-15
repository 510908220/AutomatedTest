__author__ = 'hzz'

import tornado.web


class CaseItemModule(tornado.web.UIModule):
	def render(self, case_item):
		return self.render_string("modules/case_item.html", case_item=case_item)


class MachineItemModule(tornado.web.UIModule):
	def render(self, machine_item):
		return self.render_string("modules/machine_item.html", machine_item=machine_item)

class ResultItemModule(tornado.web.UIModule):
	def render(self, result_item):
		return self.render_string("modules/result_item.html", result_item=result_item)