import json
import re
from collections import defaultdict

ANCHOR_PREFIXES = (
    "block.", "item.", "fluid.", "entity.", "enchantment.", "effect.", "biome."
)

STOPWORDS = {
    "tooltip", "desc", "description", "line", "info", "jei", "name", 
    "subtitle", "title", "lang"
}

class AnchorLangSorter:
    def __init__(self, data: dict):
        self.data = data
        self.anchor_ids = set()
        self.anchor_clusters = defaultdict(list)
        self.unanchored_keys = []

    def _tokenize(self, key: str) -> list:
        return key.split('.')

    def _is_valid_token(self, token: str) -> bool:
        if re.match(r'^-?\d+$', token): return False
        if re.match(r'^[0-9a-fA-F]{8,}$', token) and not token.isalpha(): return False
        if token.lower() in STOPWORDS: return False
        return True
    
    def _natural_sort_key(self, text: str) -> list:
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

    def _build_anchors_and_cluster(self):
        # 1. アンカーとなるIDを抽出する
        for key in self.data.keys():
            if key.startswith(ANCHOR_PREFIXES):
                tokens = self._tokenize(key)
                core_id = tokens[-1]
                if self._is_valid_token(core_id):
                    self.anchor_ids.add(core_id)
        
        # 2. 全キーを走査し、アンカーに吸着させる
        for key in self.data.keys():
            tokens = self._tokenize(key)
            matched_anchor = None
            
            for token in sorted(tokens, key=len, reverse=True):
                if token in self.anchor_ids:
                    matched_anchor = token
                    break
            
            if matched_anchor:
                self.anchor_clusters[matched_anchor].append(key)
            else:
                self.unanchored_keys.append(key)

    def sort_to_json_string(self) -> str:
        """データをソートし、空行を挿入したJSON形式の文字列を返す"""
        self._build_anchors_and_cluster()
        
        sorted_final_data = {}
        dummy_counter = 0

        def sort_cluster_keys(keys):
            return sorted(keys, key=lambda k: (len(self._tokenize(k)), self._natural_sort_key(k)))

        anchors = sorted(self.anchor_clusters.keys(), key=self._natural_sort_key)
        
        for i, anchor in enumerate(anchors):
            keys_in_cluster = sort_cluster_keys(self.anchor_clusters[anchor])
            
            for k in keys_in_cluster:
                sorted_final_data[k] = self.data[k]
            
            # 空行判定ロジック
            if i < len(anchors) - 1:
                next_anchor = anchors[i + 1]
                next_keys = self.anchor_clusters[next_anchor]
                if len(keys_in_cluster) > 1 or len(next_keys) > 1:
                    sorted_final_data[f"__BLANK_LINE_{dummy_counter}__"] = ""
                    dummy_counter += 1

        if self.unanchored_keys and anchors:
            sorted_final_data[f"__BLANK_LINE_{dummy_counter}__"] = ""
            dummy_counter += 1
            
        for k in sorted(self.unanchored_keys, key=self._natural_sort_key):
            sorted_final_data[k] = self.data[k]

        # メモリ上でJSON文字列を生成
        json_text = json.dumps(sorted_final_data, indent=2, ensure_ascii=False)

        # ダミーキーを空行に置換（ファイルI/Oを介さずメモリ上で完結）
        json_text = re.sub(r'[ \t]*"__BLANK_LINE_\d+__": "",?\r?\n', '\n', json_text)
        json_text = re.sub(r',\s*\}', '\n}', json_text)

        return json_text