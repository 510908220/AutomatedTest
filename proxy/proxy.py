# -*- coding: utf-8 -*-
from xmlrpc.server import SimpleXMLRPCServer
import os
import shutil
from zipfile import ZipFile
import subprocess
import time
import cfg


class ProxyState(object):
	IDLE = 0
	RUNNING = 1
	_StateToFile = {
		RUNNING: "running.txt",
	}

	RUNNING_FLAG = cfg.CASE_DIR.joinpath(_StateToFile[RUNNING])

	@staticmethod
	def set_state(state):
		if state == ProxyState.RUNNING:
			with open(str(ProxyState.RUNNING_FLAG), "w") as f:
				pass

	@staticmethod
	def get_state():
		if ProxyState.RUNNING_FLAG.exists():
			return ProxyState.RUNNING
		return ProxyState.IDLE

	@staticmethod
	def clear_state():
		if ProxyState.RUNNING_FLAG.exists():
			os.remove(str(ProxyState.RUNNING_FLAG))


class CaseState(object):
	IDLE = 0
	RUNNING = 1
	FINISHED = 2
	_StateToFile = {
		RUNNING: "running.txt",
		FINISHED: "output.txt"
	}

	@staticmethod
	def set_state(case_name, state):
		if state == CaseState.RUNNING:
			with open(str(cfg.CASE_DIR.joinpath(case_name).joinpath(CaseState._StateToFile[CaseState.RUNNING])),
			          "w") as f:
				pass

	@staticmethod
	def get_state(case_name):
		if cfg.CASE_DIR.joinpath(case_name).joinpath(CaseState._StateToFile[CaseState.FINISHED]).exists():
			return CaseState.FINISHED
		elif cfg.CASE_DIR.joinpath(case_name).joinpath(CaseState._StateToFile[CaseState.RUNNING]).exists():
			return CaseState.RUNNING
		else:
			return CaseState.IDLE

	@staticmethod
	def clear_state(case_name):
		file_names = CaseState._StateToFile.values()
		for file_name in file_names:
			flag_file = cfg.CASE_DIR.joinpath(case_name).joinpath(file_name)
			if flag_file.exists():
				os.remove(str(flag_file))


class ProxyService(object):
	def __init__(self):
		self.running_process = None

	def case_exists(self, case_name):
		"""
		检测用例是否存在
		"""
		return cfg.CASE_DIR.joinpath(case_name).exists()

	def push_case(self, case_name, bin):
		"""
		推送用例到测试机
		"""
		case_dir = cfg.CASE_DIR.joinpath(case_name)
		if case_dir.exists():
			shutil.rmtree(str(case_dir))

		tmp_zip = case_dir.with_suffix(".zip")
		with open(str(tmp_zip), 'wb') as f:
			f.write(bin.data)
		with ZipFile(str(tmp_zip)) as zip:
			zip.extractall(str(tmp_zip.parent))
		os.remove(str(tmp_zip))

	def run_case(self, case_name):
		"""
		运行用例，设置代理和用例状态
		"""
		ProxyState.set_state(ProxyState.RUNNING)
		CaseState.set_state(case_name, CaseState.RUNNING)
		cmd = cfg.CASE_DIR.joinpath(case_name).joinpath("run.py")
		cmd = "C:/Python34/python.exe" + " " + str(cmd)
		self.running_process = subprocess.Popen(cmd)

	def get_result(self, case_name):
		"""
		获取用例结果，并且重置代理和用例的状态
		"""
		data = ""
		with open(str(cfg.CASE_DIR.joinpath(case_name).joinpath(CaseState._StateToFile[CaseState.FINISHED]))) as f:
			data = f.read()
		self.reset_proxy(case_name)
		return data

	def reset_proxy(self, case_name):
		ProxyState.clear_state()
		CaseState.clear_state(case_name)

		while self.running_process.returncode == None:
			time.sleep(0.1)
			self.running_process.kill()

	def proxy_running(self):
		return ProxyState.get_state() == ProxyState.RUNNING

	def case_finished(self, case_name):
		return CaseState.get_state(case_name) == CaseState.FINISHED


server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
server.register_introspection_functions()
server.register_instance(ProxyService(), allow_dotted_names=True)
server.serve_forever()
