import sys, logging
import tree_sitter
import tree_sitter_java

from syntactic.divide_by_zero import predict_divide_by_zero
from syntactic.runs_forever import runs_forever
from syntactic.null_pointer import predict_null_pointer

l = logging
l.basicConfig(level=logging.DEBUG)

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
parser = tree_sitter.Parser(JAVA_LANGUAGE)

TYPE_LOOKUP = {
    "Z": "boolean",
    "I": "int",
}

def run_analysis(class_name, method_name, method_params, srcfile):
    with open(srcfile, "rb") as f:
        source_code_bytes = f.read()
        method_node = _get_method_node(class_name, method_name, method_params, source_code_bytes)

        predict_divide_by_zero(method_node)
        runs_forever(method_node)
        predict_null_pointer(method_node, source_code_bytes)

def _get_method_node(class_name, method_name, method_params, source_code):
    tree = parser.parse(source_code)

    simple_classname = class_name.split(".")[-1]

    # To figure out how to write these you can consult the
    # https://tree-sitter.github.io/tree-sitter/playground
    class_q = JAVA_LANGUAGE.query(
        f"""
        (class_declaration 
            name: ((identifier) @class-name 
                (#eq? @class-name "{simple_classname}"))) @class
    """
    )

    for node in class_q.captures(tree.root_node)["class"]:
        break
    else:
        l.error(f"could not find a class of name {simple_classname} in source")
        sys.exit(-1)

    method_name = method_name

    method_q = JAVA_LANGUAGE.query(
        f"""
        (method_declaration name: 
        ((identifier) @method-name (#eq? @method-name "{method_name}"))
        ) @method
    """
    )

    for node in method_q.captures(node)["method"]:
        if not (p := node.child_by_field_name("parameters")):
            l.debug(f"Could not find parameteres of {method_name}")
            continue

        params = [c for c in p.children if c.type == "formal_parameter"]

        if len(params) == len(method_params) and all(
            (tp := t.child_by_field_name("type")) is not None
            and tp.text is not None
            and TYPE_LOOKUP[tn] == tp.text.decode()
            for tn, t in zip(method_params, params)
        ):
            break
    else:
        l.warning(f"could not find a method of name {method_name} in {simple_classname}")
        sys.exit(-1)

    return node
