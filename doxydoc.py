import sublime, sublime_plugin
import re

def get_settings():
    return sublime.load_settings("DoxyDoc.sublime-settings")


def get_setting(key, default=None):
    return get_settings().get(key, default)

setting = get_setting

def get_template_args(templates):
    # Strip decltype statements
    templates = re.sub(r"decltype\(.+\)", "", templates)
    # Strip default parameters
    templates = re.sub(r"\s*=\s*.+,", ",", templates)
    # Strip type from template
    return re.split(r",\s*", re.sub(r"[A-Za-z_][\w.<>]*\s+([A-Za-z_][\w.<>]*)", r"\1", templates))

def read_line(view, point):
    if (point >= view.size()):
        return

    next_line = view.line(point)
    return view.substr(next_line)

def get_function_args(fn_str):
    print('Before: {0}'.format(fn_str))
    # Remove references and pointers
    fn_str = fn_str.replace("&", "")
    fn_str = fn_str.replace("*", "")

    # Remove va_list and variadic templates
    fn_str = fn_str.replace("...", "")

    # Remove cv-qualifiers
    fn_str = re.sub(r"(?:const|volatile)\s*", "", fn_str)

    # Remove namespaces
    fn_str = re.sub(r"\w+::", "", fn_str)

    # Remove template arguments in types
    fn_str = re.sub(r"([a-zA-Z_]\w*)\s*<.+>", r"\1", fn_str)

    # Remove parentheses
    fn_str = re.sub(r"\((.*)\)", r"\1", fn_str)

    # Remove arrays
    fn_str = re.sub(r"\[.*\]", "", fn_str)
    print('After: {0}'.format(fn_str))

    arg_regex = r"(?P<type>[a-zA-Z_]\w*)\s*(?P<name>[a-zA-Z_]\w*)"

    if ',' not in fn_str:
        if ' ' not in fn_str:
            return [("void", "")]
        else:
            m = re.search(arg_regex, fn_str)
            if m and m.group("type"):
                return [(m.group("type"), m.group("name"))]

    result = []
    for arg in fn_str.split(','):
        m = re.search(arg_regex, arg)
        if m and m.group('type'):
            result.append( (m.group('type'), m.group('name')) )

    return result

class DoxydocCommand(sublime_plugin.TextCommand):
    def set_up(self):
        identifier =  r"([a-zA-Z_]\w*)"
        function_identifiers = r"\s*(?:(?:inline|static|constexpr|friend|virtual|explicit|\[\[.+\]\])\s+)*"
        self.command_type = '@' if setting("javadoc", True) else '\\'
        self.regexp = {
            "templates": r"\s*template\s*<(.+)>\s*",
            "class": r"\s*(?:class|struct)\s*" + identifier + r"\s*{?",
            "function": function_identifiers + r"(?P<return>(?:typename\s*)?[\w:<>]+)?\s*"
                                               r"(?P<subname>[A-Za-z_]\w*::)?"
                                               r"(?P<name>operator\s*.{1,2}|[A-Za-z_:]\w*)\s*"
                                               r"\((?P<args>[:<>\[\]\(\),.*&\w\s]*)\).+",

            "constructor": function_identifiers + r"(?P<return>)" # dummy so it doesn't error out
                                                  r"~?(?P<name>[a-zA-Z_]\w*)(?:\:\:[a-zA-Z_]\w*)?"
                                                  r"\((?P<args>[:<>\[\]\(\),.*&\w\s]*)\).+"
        }

    def write(self, view, string):
        view.run_command("insert_snippet", {"contents": string })

    def run(self, edit, mode = None):
        if setting("enabled", True):
            self.set_up()
            snippet = self.retrieve_snippet(self.view)
            if snippet:
                self.write(self.view, snippet)
            else:
                sublime.status_message("DoxyDoc: Unable to retrieve snippet")

    def retrieve_snippet(self, view):
        print('okay?')
        point = view.sel()[0].begin()
        max_lines = 5 # maximum amount of lines to parse functions with
        current_line = read_line(view, point)
        if not current_line or current_line.find("/**") == -1:
            # Strange bug..
            return "\n * ${0}\n */"

        point += len(current_line) + 1

        next_line = read_line(view, point)

        if not next_line:
            return "\n * ${0}\n */"

        # if the next line is already a comment, no need to reparse
        if re.search(r"^\s*\*", next_line):
            return "\n * "

        retempl = re.search(self.regexp["templates"], next_line)

        if retempl:
            # The following line is either a template function or
            # templated class/struct
            template_args = get_template_args(retempl.group(1))
            point += len(next_line) + 1
            second_line = read_line(view, point)
            function_line = read_line(view, point)
            function_point = point + len(function_line) + 1

            for x in range(0, max_lines + 1):
                line = read_line(view, function_point)

                if not line:
                    break
                function_line += line
                function_point += len(line) + 1

            # Check if it's a templated constructor or destructor
            reconstr = re.match(self.regexp["constructor"], function_line)

            if reconstr:
                return self.template_function_snippet(reconstr, template_args)

            # Check if it's a templated function
            refun = re.search(self.regexp["function"], function_line)

            if refun:
                return self.template_function_snippet(refun, template_args)

            # Check if it's a templated class
            reclass = re.search(self.regexp["class"], second_line)

            if reclass:
                return self.template_snippet(template_args)

        function_lines = ''.join(next_line) # make a copy
        function_point = point + len(next_line) + 1

        for x in range(0, max_lines + 1):
            line = read_line(view, function_point)

            if not line:
                break

            function_lines += line
            function_point += len(line) + 1

        # Check if it's a regular constructor or destructor
        regex_constructor = re.match(self.regexp["constructor"], function_lines)
        if regex_constructor:
            return self.function_snippet(regex_constructor)

        # Check if it's a regular function
        regex_function = re.search(self.regexp["function"], function_lines)
        if regex_function:
            return self.function_snippet(regex_function)

        # Check if it's a regular class
        regex_class = re.search(self.regexp["class"], next_line)
        if regex_class:
            # Regular class
            return self.regular_snippet()

        # if all else fails, just send a closing snippet
        return "\n * ${0}\n */"


    def regular_snippet(self):
        snippet = ("\n * {0}brief ${{1:[brief description]}}"
                   "\n * {0}details ${{2:[long description]}}\n * \n */".format(self.command_type))
        return snippet

    def template_snippet(self, template_args):
        snippet = ("\n * {0}brief ${{1:[brief description]}}"
                   "\n * {0}details ${{2:[long description]}}\n * ".format(self.command_type))

        index = 3
        for x in template_args:
            snippet += "\n * {0}tparam {1} ${{{2}:[description]}}".format(self.command_type, x, index)
            index += 1

        snippet += "\n */"
        return snippet

    def template_function_snippet(self, regex_obj, template_args):
        snippet = ""
        index = 1
        if "friend " in regex_obj.group(0):
            snippet = "\n * {0}relates ${{1:[class name]}}".format(self.command_type)
            index += 1

        snippet += ("\n * {0}brief ${{{1}:[brief description]}}"
                    "\n * {0}details ${{{2}:[long description]}}\n * ".format(self.command_type, index, index + 1))
        index += 2

        # Function arguments
        args = regex_obj.group("args")

        if args and args != "void":
            args = get_function_args(args)
            for type, name in args:
                if type in template_args:
                    template_args.remove(type)
                snippet += "\n * {0}param {1} ${{{2}:[description]}}".format(self.command_type, name, index)
                index += 1

        for arg in template_args:
            snippet += "\n * {0}tparam {1} ${{{2}:[description]}}".format(self.command_type, arg, index)
            index += 1

        return_type = regex_obj.group("return")

        if return_type and return_type != "void":
            snippet += "\n * {0}return ${{{1}:[description]}}".format(self.command_type, index)

        snippet += "\n */"
        return snippet

    def function_snippet(self, regex_obj):
        fn = regex_obj.group(0)
        index = 1
        snippet = ""
        if "friend " in fn:
            snippet += "\n * {0}relates ${{1:[class name]}}".format(self.command_type)
            index += 1

        snippet += ("\n * {0}brief ${{{1}:[brief description]}}"
                    "\n * {0}details ${{{2}:[long description]}}".format(self.command_type, index, index + 1))
        index += 2

        args = regex_obj.group("args")

        if args and args != "void":
            snippet += "\n * "
            args = get_function_args(args)
            for _, name in args:
                snippet += "\n * {0}param {1} ${{{2}:[description]}}".format(self.command_type, name, index)
                index += 1

        return_type = regex_obj.group("return")

        if return_type and return_type != "void":
            if index == 5:
                snippet += "\n * "
            snippet += "\n * {0}return ${{{1}:[description]}}".format(self.command_type, index)

        snippet += "\n */"
        return snippet

