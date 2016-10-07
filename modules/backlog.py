#!/usr/bin/env python
"""
backlog.py - jenni backlog utilities

For Summa:
`pip install numpy scipy networkx summa`
For Sumy:
`pip install sumy nltk numpy`
`python -c "import nltk; nltk.download('punkt')"`
"""

import os, re
import threading
from modules import unicode as uc

# Summa
import summa

# Sumy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.summarizers.kl import KLSummarizer
# Import all summarizers until a good working one is chosen
AVAILABLE_METHODS = {
    "luhn": LuhnSummarizer,
    "edmundson": EdmundsonSummarizer,
    "lsa": LsaSummarizer,
    "text-rank": TextRankSummarizer,
    "lex-rank": LexRankSummarizer,
    "sum-basic": SumBasicSummarizer,
    "kl": KLSummarizer,
}

# Config
LANGUAGE = "german"

def setup(self):
    fn = self.nick + "-" + self.config.host + ".backlog.db"
    self.backlog_filename = os.path.join(os.path.expanduser("~/.jenni"), fn)
    if not os.path.exists(self.backlog_filename):
        try: f = open(self.backlog_filename, "w")
        except OSError: pass
        else:
            f.write("")
            f.close()
    self.backlog_lock = threading.Lock()


# Backlog utils
def read_backlog(jenni, filter_channel=None, max_lines=100):
    """Read backlog file and return all entries from a specific channel"""
    channel_log = list()

    jenni.backlog_lock.acquire()
    try:
        backlog_file = open(jenni.backlog_filename, "r")
        backlog_lines = backlog_file.readlines()

        for line in backlog_lines:
            elements = line.split(",", 2)
            if len(elements) < 3: continue
            (channel, nick, log) = elements

            if filter_channel and channel != filter_channel:
                continue
            channel_log.append(log)

        backlog_file.close()
    finally:
        jenni.backlog_lock.release()
    return channel_log[-max_lines:]

def update_backlog(jenni, input):
    """Write every received line to a backlog file"""
    channel = uc.encode(uc.decode(input.sender))
    nick = (input.nick).encode("utf-8")
    line = input.group()
    if type(line) != type(str()):
        line = uc.encode(line)

    # Rules for lines that should be excluded
    if not channel.startswith("#"):
        return
    elif line.startswith("."):
        return
    elif line.startswith("s/"):
        return

    jenni.backlog_lock.acquire()
    try:
        backlog_file = open(jenni.backlog_filename, "a")
        backlog_file.write("{},{},{}\n".format(channel, nick, line))
        backlog_file.close()
        #TODO: Check backlog size and clear oldest entries if needed
    finally:
        jenni.backlog_lock.release()
update_backlog.rule = r".*"
update_backlog.priority = "medium"


# Summa
def backlog_summa(jenni, input):
    """Parses the backlog of the current channel and creates a summary with summa"""
    backlog_length = 1000
    summary_length = 8

    channel = input.sender
    nick = input.nick
    command = input.group(1)
    cmds = input.group().split()
    if len(cmds) > 1 and cmds[1].isdigit():
        backlog_length = int(cmds[1])
    if len(cmds) > 2 and cmds[2].isdigit():
        summary_length = int(cmds[2])

    # Backlog is only logged for channels
    if not channel.startswith("#"):
        return

    backlog = read_backlog(jenni, channel, backlog_length)
    backlog_str = "\n".join(backlog)

    # Get summary
    if command != "keywords":
        summary = summa.summarizer.summarize(backlog_str, language=LANGUAGE, words=summary_length*10)
        jenni.say("Summary:")
        for line in summary.split("\n"):
            jenni.say(line)

    # Get keywords
    if command != "summary":
        keywords = summa.keywords.keywords(backlog_str, language=LANGUAGE, words=summary_length)
        keyword_str = ", ".join(keywords.split("\n"))
        jenni.say("Keywords: " + str(keyword_str))

backlog_summa.commands = ["summa", "tldr", "summary", "keywords"]
backlog_summa.example = ".summa [backlog_length] [summary_length]"
backlog_summa.priority = "high"


# Sumy
def backlog_sumy(jenni, input):
    """Parses the backlog of the current channel and creates a summary with sumy"""
    backlog_length = 100
    summary_length = 5
    summarize_type = "sum-basic"

    channel = input.sender
    nick = input.nick
    cmds = input.group().split()
    if len(cmds) > 1 and cmds[1].isdigit():
        backlog_length = int(cmds[1])
    if len(cmds) > 2 and cmds[2].isdigit():
        summary_length = int(cmds[2])
    if len(cmds) > 3:
        summarize_type = cmds[3]
        jenni.say(summarize_type)

    # Backlog is only logged for channels
    if not channel.startswith("#"):
        return

    backlog = read_backlog(jenni, channel, backlog_length)
    backlog_str = "\n".join(backlog)

    # Get summary
    parser = PlaintextParser.from_string(backlog_str, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    # Allow selection of summarizer
    summarizer_class = next(cls for name, cls in AVAILABLE_METHODS.items() if summarize_type)
    summarizer = summarizer_class(stemmer)
    if summarizer_class is EdmundsonSummarizer:
        summarizer.null_words = get_stop_words(LANGUAGE)
    else:
        summarizer.stop_words = get_stop_words(LANGUAGE)

    jenni.say("Summary:")
    for sentence in summarizer(parser.document, summary_length):
        jenni.say(str(sentence))

backlog_sumy.commands = ["sumy"]
backlog_sumy.example = ".sumy [backlog_length] [summary_length] [luhn,edmundson,lsa,text-rank,lex-rank,sum-basic,kl]"
backlog_sumy.priority = "high"


if __name__ == "__main__":
    print __doc__.strip()
