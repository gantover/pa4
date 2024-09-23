#!/usr/bin/env python3

import sys, logging
from parsing import MethodId

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

try:
    parsed = BytecodeAnalyser.parseMethod(m)
except Exception as e:
    print("parsing error:", e)
    
try:
    parsed.run(100)
except Exception as e:
    print("running error:", e)
