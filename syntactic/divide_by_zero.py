import tree_sitter
import tree_sitter_java

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())

div_by_zero_q = JAVA_LANGUAGE.query(
    f"""
    (binary_expression
        operator: "/"
        right: (decimal_integer_literal) @integer-value
        (#eq? @integer-value "0")
    ) @expr
    """
)

div_q = JAVA_LANGUAGE.query(
    f"""
    (binary_expression
        operator: "/"
    ) @expr
    """
)


def predict_divide_by_zero(method_body):
    if div_by_zero_q.captures(method_body):
        # We cannot simply say that it is guaranteed to occur, since code may not be reachable.
        prediction = 80
    elif div_q.captures(method_body):
        prediction = 55
    else:
        # This may be the most important result of this test - here we can confidently say that division by zero will never occur.
        # Note that this may not (obviously) be true if the method is calling a subprogram.
        prediction = 0

    print(f"divide by zero;{prediction}%")