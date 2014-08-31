import os
import subprocess
import threading
import sublime, sublime_plugin
from sys import platform as _platform

class KillableCmd(threading.Thread):
	def __init__(self, cmd, timeout, shell):

		threading.Thread.__init__(self)

		self.cmd = cmd
		self.shell = shell
		self.timeout = timeout


	def run(self):

		startupinfo = None

		if sublime.platform() == "windows":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		try:
			self.p = subprocess.Popen(self.cmd,
				startupinfo=startupinfo,
				stderr=subprocess.PIPE,
				stdout=subprocess.PIPE,
				shell=self.shell,
				env=os.environ.copy())


			out, err = map(lambda x: x.decode("ascii").replace("\r", ""), self.p.communicate())

		except:
			if _platform == "darwin":
				self.returnValue = """Unfortunately, EvalPrinter currently has some issues with OS X.
Subscribe to the following issue to get notified about the fix: https://github.com/philippotto/Sublime-EvalPrinter/issues/1"""
				return

		if err or self.p.returncode != 0:
			self.returnValue = out + err
			return

		self.returnValue = out


	def Run(self):

		self.start()
		self.join(self.timeout)

		if self.is_alive():
			self.p.terminate()
			self.join()
			return "The execution took longer than " + str(self.timeout) + " second(s). Aborting..."

		return self.returnValue

