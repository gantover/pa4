from shared import *

while_q = JAVA_LANGUAGE.query(
    f"""
    (while_statement condition: (parenthesized_expression)) @while
    """
)

"""
watches for while loops and guesses that it might be an infinite loop
"""
def runs_forever(method_node):
    for w in while_q.captures(method_node)["while"]:
        print(w)
    
