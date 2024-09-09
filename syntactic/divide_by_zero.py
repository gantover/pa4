import tree_sitter
import tree_sitter_java

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())

def predict_divide_by_zero(method_body):
    div_by_zero_q = JAVA_LANGUAGE.query(
        f"""
        (binary_expression
            operator: "/"
            right: (decimal_integer_literal) @integer-value
            (#eq? @integer-value "0")
        ) @expr
        """
    )
    prediction = 0
    if div_by_zero_q.captures(method_body):
        prediction = 100

    print(f"divide by zero;{prediction}%")