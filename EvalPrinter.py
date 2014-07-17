import sublime, sublime_plugin
import subprocess

class CompileCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		coffeeStr = getSelection(self.view)

		compiledJS = compile(coffeeStr)
		showResult(compiledJS)


class CompileAndRunCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		view = self.view
		coffeeStr = getSelection(view)
		compiledCode = compile(coffeeStr)
		output = run()
		showResult(output)


class EnterLiveSession(sublime_plugin.TextCommand):

	def run(self, edit):

		toggledValue = not self.view.settings().get("isLiveRunnerSession", False)
		self.view.settings().set("isLiveRunnerSession", toggledValue)



class ModifyListener(sublime_plugin.EventListener):

	def on_modified_async(self, view):

		if view.settings().get("isLiveRunnerSession", False):
			coffeeStr = view.substr(sublime.Region(0, view.size()))
			compiledJS = compile(coffeeStr)

			if compiledJS:
				showResult(compiledJS)
			else:
				markFaultyCode()

			print("compiledJS", compiledJS)



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
		shell=True)
	sp.wait()
	# ,
	# 	stderr=subprocess.PIPE,
	# 	stdout=subprocess.PIPE)

	# out, err = sp.communicate()
	# print(out)


def compile(coffeeStr):

	with open("code.coffee", "wt") as out_file:
		out_file.write(coffeeStr)


	cmd = "coffee -p -b code.coffee > code.js"
	executeCommand(cmd)

	with open('code.js', 'r') as f:
		compiledJS = f.read()

	return compiledJS


def run():

	executeCommand("(node -p < code.js) > output.txt")

	with open('output.txt', 'r') as f:
		output = f.read()

	return output



