#!/usr/bin/env python3
from shared import *
from assertion_error import assertion_error

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

l.debug("check assertion")

l.debug("read the method name")

# Read the method_name
RE = r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
if not (i := re.match(RE, name)):
    l.error("invalid method name: %r", name)
    sys.exit(-1)

TYPE_LOOKUP = {
    "Z": "boolean",
    "I": "int",
}

"""
Bytecode analysis
"""


classfile = (Path("decompiled") / i["class_name"].replace(".", "/")).with_suffix(
    ".json"
)

with open(classfile) as f:
    l.debug("read decompiled classfile %s", classfile)
    classfile = json.load(f)

l.debug("looking up method")
# Lookup method
# looking through all methods to find ours
for m in classfile["methods"]:
    if (
        m["name"] == i["method_name"]
        and len(i["params"]) == len(m["params"])
        and all(
            TYPE_LOOKUP[tn] == t["type"]["base"]
            for tn, t in zip(i["params"], m["params"])
        )
    ):
        break
else:
    print("Could not find method in bytecode")
    sys.exit(-1)


assertion_error(m["code"]["bytecode"])


"""
Tree-sitter analysis
"""

srcfile = (Path("src/main/java") / i["class_name"].replace(".", "/")).with_suffix(
    ".java"
)

with open(srcfile, "rb") as f:
    l.debug("parse sourcefile %s", srcfile)
    tree = parser.parse(f.read())

simple_classname = i["class_name"].split(".")[-1]

# To figure out how to write these you can consult the
# https://tree-sitter.github.io/tree-sitter/playground
class_q = JAVA_LANGUAGE.query(
    f"""
    (class_declaration 
        name: ((identifier) @class-name 
               (#eq? @class-name "{simple_classname}"))) @class
"""
)

for node in class_q.captures(tree.root_node)["class"]:
    break
else:
    l.error(f"could not find a class of name {simple_classname} in {srcfile}")
    sys.exit(-1)

l.debug("Found class %s", node.range)

method_name = i["method_name"]

method_q = JAVA_LANGUAGE.query(
    f"""
    (method_declaration name: 
      ((identifier) @method-name (#eq? @method-name "{method_name}"))
    ) @method
"""
)

