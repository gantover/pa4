import tree_sitter
import tree_sitter_java

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())

null_assignment_q = JAVA_LANGUAGE.query(
    f"""
    (local_variable_declaration
        declarator: 
            (variable_declarator
                name: (identifier) @null_arr_id
                dimensions: (dimensions)
                value: (null_literal)
            )
    )
    """
)

arr_access_q = JAVA_LANGUAGE.query(
    f"""
    [
        (array_access
            array: (identifier) @arr_id
        )
        (field_access
            object: (identifier) @arr_id
        )
    ]
    """
)

def predict_null_pointer(method_body, source_code_bytes):
    prediction = 5
    node = null_assignment_q.captures(method_body)
    if node:
        node = node["null_arr_id"][0]
        # identifier name needs to be read from the source file
        var_name = source_code_bytes[node.start_byte:node.end_byte].decode('utf8')
        
        access_node = arr_access_q.captures(method_body)
        if access_node and var_name == source_code_bytes[access_node["arr_id"][0].start_byte:access_node["arr_id"][0].end_byte].decode('utf8'):
            prediction = 60

    print(f"null pointer;{prediction}%")