#!/usr/bin/env python3

import sys, logging
from parsing import MethodId
from Instructions import staticVariableCollect

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

l.debug("read the method name")
method = MethodId.parse(name)

l.debug("looking up method")
m = method.load()

try:
    import BytecodeAnalyser
except Exception as e:
    print("import error", e)

l.debug("--- STATIC ---")
try:
    parsed = BytecodeAnalyser.parseMethod(m)
except Exception as e:
    print("parsing error:", e)
    
try:
    staticVariableCollect.collecting = True
    parsed.run(100)
    staticVariableCollect.collecting = False
except Exception as e:
    print("running error:", e)

# Dynamic analysis (turned off by default to not output predictions)
"""
l.debug("--- DYNAMIC ---")
try:
    l.debug(f"static variables collected : {staticVariableCollect}")
    BytecodeAnalyser.dynamicParseMethod(m)
except Exception as e:
    print("error:", e)
"""