#!/usr/bin/env python3

import sys, logging
from parsing import MethodId
from Datatypes import SignedUnknown

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
    l.error("import error", e)

l.debug("--- STATIC ---")
try:
    parsed = BytecodeAnalyser.parseMethod(m, SignedUnknown)
except Exception as e:
    l.error("parsing error:", e)
    
try:
    results = parsed.run(400)
    parsed.interpretResults(results)
except Exception as e:
    l.error("running error:", e)