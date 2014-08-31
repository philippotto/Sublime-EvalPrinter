import sublime, sublime_plugin
import subprocess
import os
try:
	from EvalPrinter.KillableCmd import KillableCmd
except:
	from KillableCmd import KillableCmd

class EvalPrintCommand(sublime_plugin.TextCommand):

	def run(self, edit, codeStr=None):

		view = self.view

		codeStr = codeStr or Helper.getSelectedText(view)
		syntax = view.settings().get('syntax')

		if "Plain text" in syntax:
			syntax = Helper.getSetting("default_language")

		output = EvalEvaluator.evalPrint(codeStr, syntax)
		Helper.showResult(output)


class EvalPrintEnterLiveSessionCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		view = self.view
		toggledValue = not view.settings().get("isEvalPrinterLiveSession", False)
		view.settings().set("isEvalPrinterLiveSession", toggledValue)
		sublime.status_message("EvalPrinter's Live Session is " + ("on" if toggledValue else "off"))

		if toggledValue:
			flags = 0
			if len(Helper.getSelectedText(view)) == view.size():
				# everything was selected, which is why we don't want to highlight the LiveSessionRegions
				flags = sublime.HIDDEN
				view.settings().set("EvalPrinterLiveSessionFullBuffer", True)

			view.add_regions("EvalPrinterLiveSessionRegions", view.sel(), "string", flags=flags)
			view.run_command("eval_print")
		else:
			view.erase_regions("EvalPrinterLiveSessionRegions")
			view.settings().set("EvalPrinterLiveSessionFullBuffer", False)


class ModifyListener(sublime_plugin.EventListener):

	def on_modified_async(self, view):

		if not view.settings().get("isEvalPrinterLiveSession", False):
			view.erase_regions("EvalPrinterLiveSessionRegions")
			return

		fullBuffer = view.settings().get("EvalPrinterLiveSessionFullBuffer", False)
		if fullBuffer:
			liveSessionRegions = [sublime.Region(0, view.size())]
		else:
			liveSessionRegions = view.get_regions("EvalPrinterLiveSessionRegions")


		areRegionsNotEmpty = any(map(lambda r: r.size() > 0, liveSessionRegions))
		if areRegionsNotEmpty:
			codeStr = Helper.getSelectedText(view, liveSessionRegions)
			view.run_command("eval_print", dict(codeStr = codeStr))
		elif not fullBuffer:
			# liveSessionRegions is an empty region; deactive LiveSessionMode
			view.run_command("eval_print_enter_live_session")



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
	def getSelectedText(view, regions=None):

		regions = regions or view.sel()
		codeParts = []

		for region in regions:

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

		timeoutLimit = Helper.getSetting("execution_timeout")
		return KillableCmd(cmd, timeoutLimit, shell).Run()


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

	@staticmethod
	def getSetting(attr):

		settings = sublime.load_settings("EvalPrinter.sublime-settings")
		return settings.get(attr)
