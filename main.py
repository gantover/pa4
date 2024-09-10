#!/usr/bin/env python3
from shared import *
from bytecode.assertion_error import assertion_error
from syntactic.analysis import run_analysis as run_syntactic_analysis

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

classfile = (Path("../jpamb/decompiled") / i["class_name"].replace(".", "/")).with_suffix(
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

srcfile = (Path("../jpamb/src/main/java") / i["class_name"].replace(".", "/")).with_suffix(
    ".java"
)

run_syntactic_analysis(i["class_name"], i["method_name"], i["params"], srcfile)

sys.exit(0)
