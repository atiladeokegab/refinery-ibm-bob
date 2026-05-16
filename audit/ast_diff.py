from __future__ import annotations
import re
from audit.models import SemanticChange


def _walk(node, target_type: str) -> list:
    """Recursively collect nodes whose type contains target_type."""
    results = []
    if target_type in node.type.lower():
        results.append(node)
    for child in node.children:
        results.extend(_walk(child, target_type))
    return results


def _node_text(node, source: str) -> str:
    return source[node.start_byte:node.end_byte]


def _find_paragraph(source: str, byte_offset: int) -> str:
    before = source[:byte_offset]
    hits = list(re.finditer(
        r"^\s{4,11}([A-Z0-9][\w-]+)\.$", before, re.MULTILINE | re.IGNORECASE
    ))
    return hits[-1].group(1) if hits else "PROCEDURE"


def check_computes_ast(
    orig_tree, mod_tree, orig_src: str, mod_src: str
) -> list[SemanticChange]:
    orig_nodes = _walk(orig_tree.root_node, "compute")
    mod_nodes = _walk(mod_tree.root_node, "compute")

    orig_exprs = [re.sub(r"\s+", " ", _node_text(n, orig_src)).strip() for n in orig_nodes]
    mod_exprs  = [re.sub(r"\s+", " ", _node_text(n, mod_src)).strip()  for n in mod_nodes]

    changes: list[SemanticChange] = []
    for i, (o, m) in enumerate(zip(orig_exprs, mod_exprs)):
        if o != m:
            loc = _find_paragraph(orig_src, orig_nodes[i].start_byte)
            changes.append(SemanticChange(
                change_type="COMPUTE_EXPR",
                location=loc,
                original=o,
                modified=m,
                severity="HIGH",
            ))

    if len(orig_exprs) != len(mod_exprs):
        changes.append(SemanticChange(
            change_type="COMPUTE_EXPR",
            location="PROCEDURE",
            original=f"{len(orig_exprs)} COMPUTE verbs",
            modified=f"{len(mod_exprs)} COMPUTE verbs",
            severity="HIGH",
        ))
    return changes


def check_data_types_ast(
    orig_tree, mod_tree, orig_src: str, mod_src: str
) -> list[SemanticChange]:
    def _extract(tree, src: str) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for node in _walk(tree.root_node, "data_description"):
            text = _node_text(node, src)
            name_m = re.search(r"\b\d{2}\s+([\w-]+)", text)
            pic_m  = re.search(r"PIC(?:TURE)?(?:\s+IS)?\s+([S9XAV()\d\/]+)", text, re.IGNORECASE)
            if name_m and pic_m:
                name = name_m.group(1).upper()
                pic  = re.sub(r"\s+", "", pic_m.group(1)).upper()
                comp3 = bool(re.search(r"\bCOMP-3\b", text, re.IGNORECASE))
                result[name] = {"pic": pic, "comp3": comp3}
        return result

    orig_fields = _extract(orig_tree, orig_src)
    mod_fields  = _extract(mod_tree,  mod_src)

    changes: list[SemanticChange] = []
    for name, orig_info in orig_fields.items():
        if name not in mod_fields:
            continue
        mod_info = mod_fields[name]
        if orig_info["pic"] != mod_info["pic"]:
            changes.append(SemanticChange(
                change_type="DATA_TYPE",
                location=name,
                original=f"PIC {orig_info['pic']}",
                modified=f"PIC {mod_info['pic']}",
                severity="HIGH",
            ))
        elif orig_info["comp3"] != mod_info["comp3"]:
            orig_str = f"PIC {orig_info['pic']}" + (" COMP-3" if orig_info["comp3"] else "")
            mod_str  = f"PIC {mod_info['pic']}"  + (" COMP-3" if mod_info["comp3"] else "")
            changes.append(SemanticChange(
                change_type="DATA_TYPE",
                location=name,
                original=orig_str,
                modified=mod_str,
                severity="LOW",  # storage-format change only — precision preserved
            ))
    return changes


def check_verb_counts_ast(orig_tree, mod_tree) -> list[SemanticChange]:
    verb_fragments = {"PERFORM": "perform", "SEARCH": "search", "SORT": "sort"}
    changes: list[SemanticChange] = []
    for verb, fragment in verb_fragments.items():
        orig_count = len(_walk(orig_tree.root_node, fragment))
        mod_count  = len(_walk(mod_tree.root_node,  fragment))
        if orig_count != mod_count:
            changes.append(SemanticChange(
                change_type="VERB_COUNT",
                location="PROCEDURE",
                original=f"{verb}={orig_count}",
                modified=f"{verb}={mod_count}",
                severity="MEDIUM",
            ))
    return changes
