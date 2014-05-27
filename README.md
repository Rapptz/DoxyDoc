## DoxyDoc

DoxyDoc is a plug-in that allows you to auto-complete doc block comments for C++ using Doxygen. Inspired by
[PhpDoc](https://github.com/SublimeText/PhpDoc) and [DocBlockr](https://github.com/spadgos/sublime-jsdocs) this was made due
to frustrations due to lack of proper C++ support from DocBlockr. The latter plug-in had no capabilities to parse templated
functions or classes and would just leave the comment hanging.

There are no plans to support other languages as DocBlockr does this job fairly well.

## Installation

The easy way to install this is through Package Control.

- Press Ctrl + Shift + P
- Type "install" without quotes to get to Package Control: Install Package
- Type "DoxyDoc" without quotes and you'll see this package.

Another way to install this is through running `git clone` of this repository in your package directory.

The command to do so is the following:

    git clone https://github.com/Rapptz/doxydoc.git DoxyDoc

## Usage

Just like DocBlockr, pressing `/**` and then enter or tab would automatically insert the corresponding documentation.
There are no keyboard shortcuts to memorise.

![](http://rapptz.github.io/doxydoc/images/comment-complete.gif)

As you can see, pressing enter consecutively would automatically continue the comment.

DoxyDoc also supports C++ function documenting in various forms.

A basic function is trivial to document:

![](http://rapptz.github.io/doxydoc/images/function1.gif)

If a function has a template parameter, a `@tparam` property is automatically added as well.

![](http://rapptz.github.io/doxydoc/images/function2.gif)

However if the function uses the template type parameter in the function it'll try its best to not include it.

![](http://rapptz.github.io/doxydoc/images/function3.gif)

DoxyDoc also supports adding the `@return` property if the return value is not void.

![](http://rapptz.github.io/doxydoc/images/function4.gif)

DoxyDoc also supports basic documenting of class names, templated or not.

![](http://rapptz.github.io/doxydoc/images/templateclass.gif)

Note that all the fields are just Sublime Text snippets, so tabbing over will allow you to seamlessly edit the
parameters for the tags.

Along with automatically generating documentation, DoxyDoc allows autocompletion of some common Doxygen snippets as listing
[all of the supported ones](http://www.stack.nl/~dimitri/doxygen/manual/commands.html) would be extremely big. You can get
a list of them by pressing `@` and a list will pop up automatically.

A couple things from DocBlockr are lacking though, which you can find in the TODO below.

## Issues and Limitations

C++ is notoriously hard to parse, so it'll be insane to say that this so-called parser is perfect as it is far from it.
Occasional bugs are sure to pop up every so often, which is why I made this to be as simple as possible. Since the "parser" is
essentially a bunch of regex under the hood, some abnormalities are bound to pop up because I chose to take part in two
problems rather than one.

Limitations are mostly involving template parameters and some complex functions. I also haven't tried function pointers in
function arguments, so that will most likely be faulty as well. You are free to open up an issue in the issue
tracker if you believe the bug is too severe or it ruins your flow. You're also welcome to submit a patch yourself to fix the
functionality. :)

## Todo

- Allow configuration of options. Some examples:
    - Ability to insert @author tags in the snippets
    - Indentation choice
- Support other types of comments such as /// and //!
- Variable documentation
