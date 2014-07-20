import sublime
from unittest import TestCase

version = sublime.version()

class TestMultiEditUtils(TestCase):

	def setUp(self):

		self.view = sublime.active_window().new_file()


	def tearDown(self):

		if self.view:
			self.view.set_scratch(True)
			self.view.window().run_command("close_file")


	def testCompile(self):

		codeStr = "do (-> return 2 + 3)"
		compiledString = "(function() {\n  return 2 + 3;\n})();\n"
		self.view.run_command("test_eval_printer", dict(action = "compile", codeStr = codeStr))

		contentRegion = sublime.Region(0, self.view.size())
		bufferContent = self.view.substr(contentRegion)

		self.assertEqual(bufferContent, compiledString)


	def testRun(self):

		codeStr = "do (-> return 2 + 3)"
		resultString = "5\n"
		self.view.run_command("test_eval_printer", dict(action = "run", codeStr = codeStr))

		contentRegion = sublime.Region(0, self.view.size())
		bufferContent = self.view.substr(contentRegion)

		self.assertEqual(bufferContent, resultString)
