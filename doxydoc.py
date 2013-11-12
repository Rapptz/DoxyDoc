import sublime, sublime_plugin
import re

def get_template_args(templates):
    # Strip default parameters
    templates = re.sub(r"\s*=\s*.+,", ",", templates)
    # Strip typename or class identifiers and split based on commas
    # Effectively removing anonymous typenames in the process.
    return re.split(r",\s*", re.sub(r"(?:typename|class)\.*\s*", "", templates))

def read_line(view, point):
    if (point >= view.size()):
        return

    next_line = view.line(point)
    return view.substr(next_line)

def get_function_args(fn_str):
    # Remove references
    fn_str = fn_str.replace("&", "")

    # Remove cv-qualifiers
    fn_str = re.sub(r"(?:const|volatile)\s*", "", fn_str)

    # Remove namespaces
    fn_str = re.sub(r"\w+::", "", fn_str)

    # Remove template arguments in types
    fn_str = re.sub(r"([a-zA-Z_]\w*)\s*<.+>", "\\1", fn_str)

    result = []
    for arg in fn_str.split(','):
        m = re.search(r"(?P<type>[a-zA-Z_]\w*)\s*(?P<name>[a-zA-Z_]\w*)", arg)
        if m and m.group('type'):
            result.append( (m.group('type'), m.group('name')) )

    return result

class DoxydocCommand(sublime_plugin.TextCommand):
    def set_up(self):
        identifier =  r"([a-zA-Z_]\w*)"
        function_identifiers = r"\s*(?:(?:inline|static|constexpr|friend|virtual|explicit|\[\[.+\]\])\s+)*"
        self.regexp = {
            "templates": r"\s*template\s*<(.+)>\s*",
            "class": r"\s*(?:class|struct)\s*" + identifier + r"\s*{?",
            "function": function_identifiers + r"(?P<return>(?:typename\s*)?[\w:<>]+)?\s*(?P<subname>[A-Za-z_]\w*::)?"
                                               r"(?P<name>operator\s*.{1,2}|[A-Za-z_:]\w*)\s*\((?P<args>[:<>,.&\w\s]*)\).+"
        }

    def write(self, view, string):
        view.run_command("insert_snippet", {"contents": string })

    def run(self, edit, mode = None):
        self.set_up()
        snippet = self.retrieve_snippet(self.view)
        if snippet:
            self.write(self.view, snippet)
        else:
            print "unable to print snippet"

    def retrieve_snippet(self, view):
        point = view.sel()[0].begin()
        current_line = read_line(view, point)
        if not current_line or current_line.find("/**") == -1:
            # Strange bug.. 
            return "\n * ${0}\n */"

        point += len(current_line) + 1

        next_line = read_line(view, point)

        if not next_line:
            return "\n * ${0}\n */"

        retempl = re.search(self.regexp["templates"], next_line)

        if retempl:
            # The following line is either a template function or
            # templated class/struct
            template_args = get_template_args(retempl.group(1))
            point += len(next_line) + 1
            second_line = read_line(view, point)

            refun = re.search(self.regexp["function"], second_line)

            if refun:
                return self.template_function_snippet(refun, template_args)

            reclass = re.search(self.regexp["class"], second_line)

            if reclass:
                return self.template_snippet(template_args)

        regex_function = re.search(self.regexp["function"], next_line)

        if regex_function:
            return self.function_snippet(regex_function)

        regex_class = re.search(self.regexp["class"], next_line)

        if regex_class:
            # Regular class
            return self.regular_snippet()

        # if all else fails, just send a closing snippet
        return "\n * ${0}\n */"


    def regular_snippet(self):
        snippet = "\n * @brief ${1:[brief description]}\n * @details ${2:[long description]}\n * \n */"
        return snippet

    def template_snippet(self, template_args):
        snippet = "\n * @brief ${1:[brief description]}\n * @details ${2:[long description]}\n * "

        index = 3
        for x in template_args:
            snippet += "\n * @tparam {0} ${{{1}:[description]}}".format(x, index)
            index += 1

        snippet += "\n */"
        return snippet

    def template_function_snippet(self, regex_obj, template_args):
        snippet = ""
        index = 1
        if "friend " in regex_obj.group(0):
            snippet = "\n * @relates ${1:[class name]}"
            index += 1

        snippet += "\n * @brief ${{{0}:[brief description]}}\n * @details ${{{1}:[long description]}}\n * ".format(index, index + 1)
        index += 2
        param_snippet = ""

        # Function arguments
        args = regex_obj.group("args")

        if args and args != "void":
            args = get_function_args(args)
            for type, name in args:
                if type in template_args:
                    template_args.remove(type)
                param_snippet += "\n * @param {0} ${{{1}:[description]}}".format(name, index)
                index += 1

        for arg in template_args:
            snippet += "\n * @tparam {0} ${{{1}:[description]}}".format(arg, index)
            index += 1

        snippet += "\n * " + param_snippet

        return_type = regex_obj.group("return")

        if return_type and return_type != "void":
            snippet += "\n * @return ${{{0}:[description]}}".format(index)

        snippet += "\n */"
        return snippet

    def function_snippet(self, regex_obj):
        fn = regex_obj.group(0)
        index = 1
        snippet = ""
        if "friend " in fn:
            snippet += "\n * @relates ${1:[class name]}"
            index += 1

        snippet += "\n * @brief ${{{0}:[brief description]}}\n * @details ${{{1}:[long description]}}\n * ".format(index, index + 1)
        index += 2

        args = regex_obj.group("args")

        if args and args != "void":
            args = get_function_args(args)
            for _, name in args:
                snippet += "\n * @param {0} ${{{1}:[description]}}".format(name, index)
                index += 1

        return_type = regex_obj.group("return")

        if return_type and return_type != "void":
            snippet += "\n * @return ${{{0}:[description]}}".format(index)

        snippet += "\n */"
        return snippet    

