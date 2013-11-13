## DoxyDoc

DoxyDoc is a plug-in that allows you to auto-complete doc block comments for C++ using Doxygen. Inspired by 
[PhpDoc](https://github.com/SublimeText/PhpDoc) and [DocBlockr](https://github.com/spadgos/sublime-jsdocs) this was made by 
frustrations due to lack of proper C++ support from DocBlockr. The latter plug-in had no capabilities to parse templated
functions or classes and would just leave the comment hanging.

There are no plans to support other languages as DocBlockr does this job fairly well.

## Installation

Currently the only way to install this is through running `git clone` of this repository in your package directory.

The command to do so is the following:

    git clone https://github.com/Rapptz/doxydoc.git DoxyDoc

## Usage

Just like DocBlockr, pressing `/**` and then enter (but not tab) would automatically insert the corresponding documentation.
There are no keyboard shortcuts to memorise. A couple things from DocBlockr are lacking though, which you can find in the
TODO below.

Along with automatically generating documentation, DoxyDoc allows autocompletion of some common Doxygen snippets as listing
[all of the supported ones](http://www.stack.nl/~dimitri/doxygen/manual/commands.html) would be extremely big. You can get
a list of them by pressing `@` and a list will pop up automatically. Pressing Enter or Tab will insert the text for you, these
work just like regular Sublime Text snippets.

## Todo

- Allow configuration of options. Some examples:
    - @ vs \ for Doxygen commands
    - Ability to insert @author tags in the snippets
    - Indentation choice
- Support other types of comments such as /// and //!
- Variable documentation

Patches are welcome.

