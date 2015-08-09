__author__ = 'hzz'
import os
import tornado.web
import tornado.gen
from datetime import datetime
from . import config


class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db


class HomeHandler(BaseHandler):
	def get(self, page):
		if not page:
			self.render("home.html")
		elif page == "cases.html":
			self.render(page, case_items=CasesHandler.get_case_items())
		elif page == "tasks.html":
			case_items = CasesHandler.get_case_items()
			case_names = [case_item["name"] for case_item in case_items]
			self.render(page, case_names=case_names)


class CasesHandler(BaseHandler):
	@staticmethod
	def get_case_items():
		case_items = []
		for case_path in config.CASES_DIR.iterdir():
			item = {}
			item["size"] = case_path.stat().st_size / 1024
			item["name"] = case_path.stem
			item["time"] = datetime.fromtimestamp(case_path.stat().st_mtime).strftime("%d/%m/%y %H:%M")
			case_items.append(item)
		return case_items

	@staticmethod
	def del_case(case_name):
		case_path = config.CASES_DIR.joinpath(case_name + ".zip")
		if case_path.exists():
			os.remove(str(case_path))

	def post(self, param):
		if param == "upload":
			file_metas = self.request.files['file']

			for meta in file_metas:
				file_name = meta['filename']
				file_path = config.CASES_DIR.joinpath(file_name)
				with open(str(file_path), 'wb') as up:
					up.write(meta['body'])
		elif param == "del":
			case_name = self.get_argument("case_name")
			CasesHandler.del_case(case_name)
		self.redirect("/cases.html")


class TasksHandler(BaseHandler):
	def add_task(self, version, cases, email):
		tb_task = self.db[config.TB_TASK]
		task_info = {
			"version": version,
			"cases": cases,
			"email": email
		}
		task_id = tb_task.insert_one({"pending": task_info}).inserted_id
		return task_id

	def post(self, param):
		if param == "produce":
			version = self.get_argument("version")
			cases = self.get_arguments("cases")
			email = True if self.get_argument("email", None) else False
			self.add_task(version, cases, email)
		self.redirect("/tasks.html")
