__author__ = 'hzz'

import tornado.web


class CaseItemModule(tornado.web.UIModule):
	def render(self, case_item):
		return self.render_string("modules/case_item.html", case_item=case_item)
