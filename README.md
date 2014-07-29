Sublime-EvalPrinter [![Build Status](https://travis-ci.org/philippotto/Sublime-EvalPrinter.svg?branch=master)](https://travis-ci.org/philippotto/Sublime-EvalPrinter)
===================

EvalPrinter is a Sublime Text 2/3 Plugin which transpiles, evaluates and prints code. This allows rapid testing of code snippets without leaving your code editor.
To see which languages are supported, see the appropriate section.


## Motivation

You are writing some code and you are unsure if it does what you want? Is JavaScript's second parameter for ```String.prototype.slice``` the index of the last character? Or is it the amount of characters to slice? Does Python's ```reverse```-method for lists return a reversed copy or does it modify the instance?
Do you need these braces in your CoffeeScript code or are they optional?

Don't look this up in the documention! Don't open a shell, in which you replicate the code you already wrote! Stay in Sublime and just evaluate/transpile your code. With EvalPrinter.


## Features

You can trigger the ```eval_print``` command to transpile/evaluate the current selection (or the current line if nothing is selected). The default keybinding is ```shift+alt+enter```.
By default, the output will yield the result of the last expression. Additional output can be achieved via the standard logging methods of the current programming language (e.g. ```console.log``` in JavaScript and ```print``` in Python).

![](http://philippotto.github.io/Sublime-EvalPrinter/screens/javascript.gif)


Another possibility is to enter a "live session", in which the code of the active view will be transpiled/evaluated after each keystroke. The command is called ```eval_print_enter_live_session``` and the default keybinding is ```ctrl/super+shift+alt+enter```.


![](http://philippotto.github.io/Sublime-EvalPrinter/screens/javascript-live-session.gif)


For languages which will be transpiled (e.g. CoffeeScript), the output will also include the result of the transpilation process:

![](http://philippotto.github.io/Sublime-EvalPrinter/screens/coffeescript.gif)


## Supported languages

Currently, the following languages are supported:

- JavaScript
- CoffeeScript
- Python

Feel free to open issues or submit pull requests to add support for other languages.


## Installation

Either use [Package Control](https://sublime.wbond.net/installation) and search for `EvalPrinter` or clone this repository into Sublime Text "Packages" directory.
