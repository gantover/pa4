import sys, logging
import json, re
import tree_sitter
import tree_sitter_java
from pathlib import Path
l = logging
l.basicConfig(level=logging.DEBUG)

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
parser = tree_sitter.Parser(JAVA_LANGUAGE)

def unwrap(node, expected_error):
    if node != None and node.text != None:
        return node.text.decode()
    else:
        l.error("failed to unwrap: %r", expected_error)
        sys.exit(-1)

