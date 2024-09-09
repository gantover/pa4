from shared import *

while_q = JAVA_LANGUAGE.query(
    f"""
    (while_statement condition: (parenthesized_expression)) @while
    """
)

"""
watches for while loops and guesses that it might be an infinite loop
"""
def runs_forever(method_node: tree_sitter.Node):
    while_statements = while_q.captures(method_node).get("while")
    if (while_statements != None):
        for w in while_statements:
            condition = w.child_by_field_name("condition")
            condition = unwrap(condition, "failed to extract condition")
            l.debug(f"found while statement with condition {condition}")
            print("*;60%")
    else:
        print("*;-inf")
        l.debug("no while loop")
