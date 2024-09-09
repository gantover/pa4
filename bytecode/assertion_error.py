from shared import *

def assertion_error(bytecode):
    l.debug("trying to find an assertion error being created")
# Look if the method contains an assertion error:
    for inst in bytecode:
        if (
            inst["opr"] == "invoke"
            and inst["method"]["ref"]["name"] == "java/lang/AssertionError"
        ):
            l.debug("Found it")
            print("assertion error;80%")
            # I'm kind of sure the answer is yes.
            break
    else:
        # I'm pretty sure the answer is no
        l.debug("did not find it")
        print("assertion error;20%")
