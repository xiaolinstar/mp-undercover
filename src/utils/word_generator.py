#!/usr/bin/env python3
"""
词语生成器
负责生成随机词语对
"""

import random


class WordGenerator:
    """词语生成器"""
    
    def __init__(self, word_pairs: list[tuple[str, str]]):
        self.word_pairs = word_pairs
    
    def get_random_word_pair(self) -> tuple[str, str]:
        """获取随机词语对"""
        return random.choice(self.word_pairs)
    
    def get_word_pair_by_category(self, category: str) -> tuple[str, str]:
        """根据类别获取词语对（预留功能）"""
        # 这里可以根据类别筛选词语对
        # 当前版本直接返回随机词语对
        return self.get_random_word_pair()
    
    def add_word_pair(self, civilian_word: str, undercover_word: str) -> None:
        """添加词语对"""
        self.word_pairs.append((civilian_word, undercover_word))
    
    def remove_word_pair(self, civilian_word: str, undercover_word: str) -> bool:
        """移除词语对"""
        try:
            self.word_pairs.remove((civilian_word, undercover_word))
            return True
        except ValueError:
            return False