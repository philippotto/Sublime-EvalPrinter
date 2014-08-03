import sublime, sublime_plugin
import subprocess
import os
from sys import platform as _platform

class EvalPrintCommand(sublime_plugin.TextCommand):

	def run(self, edit, entireFile=False):

		view = self.view

		if entireFile:
			contentRegion = sublime.Region(0, self.view.size())
			codeStr = self.view.substr(contentRegion)
		else:
			codeStr = Helper.getSelection(self.view)

		syntax = view.settings().get('syntax')

		if "Plain text" in syntax:
			settings = sublime.load_settings("EvalPrinter.sublime-settings")
			syntax = settings.get("default_language")

		output = EvalEvaluator.evalPrint(codeStr, syntax)
		Helper.showResult(output)



class EvalPrintEnterLiveSessionCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		toggledValue = not self.view.settings().get("isEvalPrinterLiveSession", False)
		self.view.settings().set("isEvalPrinterLiveSession", toggledValue)
		sublime.status_message("EvalPrinter's Live Session is " + ("on" if toggledValue else "off"))
		if toggledValue:
			self.view.run_command("eval_print", dict(entireFile = True))


class ModifyListener(sublime_plugin.EventListener):

	def on_modified_async(self, view):

		if view.settings().get("isEvalPrinterLiveSession", False):
			view.run_command("eval_print", dict(entireFile = True))



class TestEvalPrinterCommand(sublime_plugin.TextCommand):

	def run(self, edit, codeStr, syntax):

		output = EvalEvaluator.evalPrint(codeStr, syntax)

		if int(sublime.version()) < 3000:
			self.view.run_command("insert", {"characters": output})
		else:
			self.view.run_command("append", {"characters": output})



class EvalEvaluator:

	@staticmethod
	def evalPrint(codeStr, syntax):

		output = None

		if "Python" in syntax:
			output = EvalEvaluator.runPython(codeStr)
		elif "JavaScript" in syntax:
			output = EvalEvaluator.runJavaScript(codeStr)
		elif "CoffeeScript" in syntax:
			output = EvalEvaluator.runCoffee(codeStr)
		else:
			output = "Couldn't determine a supported language. Maybe you want to set the default_language setting."

		return output


	@staticmethod
	def runJavaScript(codeStr):

		return Helper.executeCommand(["node", "-p", codeStr], False)


	@staticmethod
	def runCoffee(codeStr):

		# does not work with multi-line-strings:
		# transpileCmd = ['coffee', '-p', '-b', '-e', codeStr]

		# does not work on unix:
		# transpileCmd = ['coffee', '-p', '-b', Helper.writeToTmp(codeStr)]

		transpileCmd = 'coffee -p -b "' + Helper.writeToTmp(codeStr) + '"'
		transpiledJS = Helper.executeCommand(transpileCmd)

		evaluatedJS = Helper.executeCommand(["node", "-p", transpiledJS], False)

		return Helper.formatTwoOutputs(evaluatedJS, transpiledJS)


	@staticmethod
	def runPython(codeStr):

		codeStr = Helper.unindentCode(codeStr)

		try:
			output = str(eval(codeStr))
		except:
			output = Helper.executeCommand(["python", "-c", codeStr], False)

		return output



class Helper:

	@staticmethod
	def getSelection(view):

		codeParts = []

		for region in view.sel():

			if region.a == region.b:
				region = view.line(region)

			code = view.substr(region)
			codeParts.append(code)

		return "\n".join(codeParts)


	@staticmethod
	def showResult(resultStr):

		if int(sublime.version()) < 3000:
			sublime.active_window().run_command("show_panel", {"panel": "output.myOutput"})
			myOutput = sublime.active_window().get_output_panel("myOutput")

			edit = myOutput.begin_edit()
			myOutput.insert(edit, 0, resultStr)
			myOutput.end_edit(edit)

		else:
			myOutput = sublime.active_window().create_output_panel("myOutput")
			sublime.active_window().run_command("show_panel", {"panel": "output.myOutput"})

			myOutput.run_command("append", {"characters": resultStr})

		myOutput.set_syntax_file("Packages/JavaScript/JavaScript.tmLanguage")


	@staticmethod
	def executeCommand(cmd, shell=True):

		startupinfo = None
		if sublime.platform() == "windows":
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		try:
			sp = subprocess.Popen(cmd,
				startupinfo=startupinfo,
				stderr=subprocess.PIPE,
				stdout=subprocess.PIPE,
				shell=shell,
				env=os.environ.copy())

			out, err = map(lambda x: x.decode("ascii").replace("\r", ""), sp.communicate())

		except:
			if _platform == "darwin":
				return """Unfortunately, EvalPrinter currently has some issues with OS X.
Subscribe to the following issue to get notified about the fix: https://github.com/philippotto/Sublime-EvalPrinter/issues/1"""

		if err or sp.returncode != 0:
			return out + err

		return out


	@staticmethod
	def unindentCode(codeStr):
		# finds the smallest common indentation and removes it,
		# so that indented code can be evaluated properly

		indentations = []
		codeLines = codeStr.splitlines()

		for l in codeLines:
			if l.lstrip() == "":
				# ignore empty lines
				continue

			indentation = len(l) - len(l.lstrip())
			indentations.append(indentation)

		unindentLength = min(indentations)

		newCodeLines = [l[unindentLength:] for l in codeLines]
		return "\n".join(newCodeLines)



	@staticmethod
	def getCodeFilePath():

		# epPath = os.path.join(sublime.packages_path(), "EvalPrinter")
		epPath = sublime.packages_path()
		fileName = "ep_tmp"
		filePath = os.path.join(epPath, fileName)

		return filePath


	@staticmethod
	def writeToTmp(s):

		filePath = Helper.getCodeFilePath()

		with open(filePath, "wt") as out_file:
			out_file.write(s)

		return filePath


	@staticmethod
	def formatTwoOutputs(a, b):

		if "error" in a.lower():
			a, b = b, a

		return  a + "\n" + "-" * 80 + "\n\n" + b