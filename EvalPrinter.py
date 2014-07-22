import sublime, sublime_plugin
import subprocess
import os

class TranspileCommand(sublime_plugin.TextCommand):

	def run(self, edit, entireFile=False):

		if entireFile:
			contentRegion = sublime.Region(0, self.view.size())
			coffeeStr = self.view.substr(contentRegion)
		else:
			coffeeStr = getSelection(self.view)

		transpiledJS = transpile(coffeeStr)
		if not transpiledJS:
			showResult("An unknown error occured while transpiling.")
		else:
			showResult(transpiledJS)



class TranspileAndRunCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		view = self.view
		coffeeStr = getSelection(view)
		transpiledCode = transpile(coffeeStr)
		output = run()
		showResult(output)



class EnterLiveSession(sublime_plugin.TextCommand):

	def run(self, edit):

		toggledValue = not self.view.settings().get("isEvalPrinterLiveSession", False)
		self.view.settings().set("isEvalPrinterLiveSession", toggledValue)
		sublime.status_message("EvalPrinter's Live Session is " + ("on" if toggledValue else "off"))



class ModifyListener(sublime_plugin.EventListener):

	def on_modified_async(self, view):

		if view.settings().get("isEvalPrinterLiveSession", False):
			view.run_command("transpile", dict(entireFile = True))



class TestEvalPrinterCommand(sublime_plugin.TextCommand):

	def run(self, edit, action, codeStr):

		if action == "transpile":
			output = transpile(codeStr)
		else:
			transpile(codeStr)
			output = run()

		self.view.run_command("append", {"characters": output})



def getSelection(view):

	codeParts = []

	for region in view.sel():

		if region.a == region.b:
			region = view.line(region)

		code = view.substr(region)
		codeParts.append(code)

	return "\n".join(codeParts)



def showResult(resultStr):

	myOutput = sublime.active_window().create_output_panel("myOutput")
	sublime.active_window().run_command("show_panel", {"panel": "output.myOutput"})

	myOutput.run_command("append", {"characters": resultStr})
	myOutput.set_syntax_file("Packages/JavaScript/JavaScript.tmLanguage")


def markFaultyCode():

	pass


def executeCommand(cmd):

	startupinfo = None
	if sublime.platform() == "windows":
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

	sp = subprocess.Popen(cmd,
		startupinfo=startupinfo,
		stderr=subprocess.PIPE,
		stdout=subprocess.PIPE,
		shell=True)

	out, err = sp.communicate()
	out = out.decode("ascii")
	err = err.decode("ascii")

	if err or sp.returncode != 0:
		return out + err.replace("\r", "")

	return out


def getCodeFilePath():

	epPath = os.path.join(sublime.packages_path(), "EvalPrinter")
	fileName = "code.coffee"
	filePath = os.path.join(epPath, fileName)

	return filePath


def transpile(coffeeStr):

	filePath = getCodeFilePath()

	with open(filePath, "wt") as out_file:
		out_file.write(coffeeStr)

	cmd = 'coffee -p -b "' + filePath + '"'
	transpiledJS = executeCommand(cmd)

	return transpiledJS


def run():

	filePath = getCodeFilePath()

	return executeCommand('coffee -p -b "' + filePath + '" | node -p')
