import sublime
from unittest import TestCase
import time

version = sublime.version()

class TestMultiEditUtils(TestCase):

	def setUp(self):

		self.view = sublime.active_window().new_file()


	def tearDown(self):

		if self.view:
			self.view.set_scratch(True)
			self.view.window().run_command("close_file")


	def assertCode(self, codeStr, expectedValue, syntax):

		self.view.run_command("test_eval_printer", dict(codeStr = codeStr, syntax = syntax))

		contentRegion = sublime.Region(0, self.view.size())
		bufferContent = self.view.substr(contentRegion)

		self.assertEqual(bufferContent.strip(), expectedValue)


	def testSingleLinePython(self):

		codeStr = "len('testPython')"
		expectedValue = "10"
		self.assertCode(codeStr, expectedValue, "Python")


	def testMultiLinePython(self):

		codeStr = "arr = []\nfor el in [1, 2, 3, 4]:\n  arr.append(10 * el)\nprint(arr)"
		expectedValue = "[10, 20, 30, 40]"

		self.assertCode(codeStr, expectedValue, "Python")


	def testSingleLineJavaScript(self):

		codeStr = "Math.sqrt(6 + 3)"
		expectedValue = "3"

		self.assertCode(codeStr, expectedValue, "JavaScript")


	def testMultiLineJavaScript(self):

		codeStr = "(function() {\n return 'multiLineTest'\n})()"
		expectedValue = "multiLineTest"

		self.assertCode(codeStr, expectedValue, "JavaScript")


	def testSingleLineCoffeeScript(self):

		codeStr = "do (-> return 2 + 3)"
		ST2Fix = "  " if int(sublime.version()) < 3000 else ""
		expectedValue = "5\n\n--------------------------------------------------------------------------------\n\n(function() {\n  return 2 + 3;\n" + ST2Fix + "})();"

		self.assertCode(codeStr, expectedValue, "CoffeeScript")


	def testMultiLineCoffeeScript(self):

		codeStr = "do ->\n  return 2 + 3"
		ST2Fix = "  " if int(sublime.version()) < 3000 else ""
		expectedValue = "5\n\n--------------------------------------------------------------------------------\n\n(function() {\n  return 2 + 3;\n" + ST2Fix + "})();"

		self.assertCode(codeStr, expectedValue, "CoffeeScript")
