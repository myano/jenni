"""
Create table banned_words_warnings for
modules/banned_words.py
"""

from yoyo import step

__depends__ = {}

step(
    "CREATE TABLE banned_words_warning(nick VARCHAR(255), channel VARCHAR(255), num_warnings INT)",
    "DROP TABLE banned_words_warning"
)
