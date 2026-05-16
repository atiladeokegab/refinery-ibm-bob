"""COBOL parser: tree-sitter wrapper with regex fallback."""
from pathlib import Path

_HAS_TS = False
_ts_parser = None

# Try bundled compiled grammar first (vendor/cobol.dll)
_GRAMMAR_DLL = Path(__file__).parent.parent / "vendor" / "cobol.dll"

try:
    import ctypes
    import warnings
    from tree_sitter import Language, Parser as _TSParser
    if _GRAMMAR_DLL.exists():
        _lib = ctypes.CDLL(str(_GRAMMAR_DLL))
        _fn = _lib.tree_sitter_COBOL
        _fn.restype = ctypes.c_void_p
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            _COBOL_LANG = Language(_fn())
        _ts_parser = _TSParser(_COBOL_LANG)
        _HAS_TS = True
except Exception:
    pass

from .ast_features import extract_from_regex, extract_from_tree


class COBOLParser:
    """Parse COBOL source and extract a numeric feature dict.

    Uses tree-sitter when available; falls back to regex for all features.
    Never modifies the source — read-only analysis only.
    """

    def parse(self, source: str):
        """Return a tree-sitter Tree, or None if the grammar is unavailable."""
        if _HAS_TS:
            try:
                return _ts_parser.parse(source.encode("utf-8"))
            except Exception:
                pass
        return None

    def extract_features(self, source: str) -> dict:
        """Return dict with keys matching COBOLState AST fields.

        Keys: loc, perform_depth, working_storage_bytes, file_section_count,
              compute_verb_count, search_verb_count, sort_verb_count.
        """
        tree = self.parse(source)
        if tree is not None:
            return extract_from_tree(tree, source)
        return extract_from_regex(source)
