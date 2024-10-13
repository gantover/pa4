#!/usr/bin/env python3

import sys, logging
from parsing import MethodId

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

l.debug("read the method name")
method = MethodId.parse(name)
l.debug(f"found method from name : {method}")

l.debug("looking up method")
m = method.load()
l.debug(f"method content : {m}")

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
    results = parsed.run(400)
    parsed.interpretResults(results)
except Exception as e:
    print("running error:", e)