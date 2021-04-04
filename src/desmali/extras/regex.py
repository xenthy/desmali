import re
from typing import Match

# .class public Lcom/google/android/material/button/MaterialButton;
CLASS: Match = re.compile(r"\.class.+?(?P<name>\S+?;)")

# Lcom/google/android/material/button/MaterialButton;
CLASSES: Match = re.compile(r"L[^():\s]+?;", re.UNICODE)

# .source "MainActivity.kt"
SOURCES: Match = re.compile(r"\.source.+?(?P<name>\w+)")

# regex pattern to identify lines that contains a method
# read more about Named Capturing Groups: https://www.regular-expressions.info/refext.html
METHOD: Match = re.compile(r"\.method.+?(?P<method>\S+?)" +
                           r"\((?P<args>\S*?)\)" +
                           r"(?P<return>\S+)",
                           re.UNICODE)

# :goto_0
LABEL: Match = re.compile(r"^[ ]{4}(?P<name>:.+)")

# goto :goto_0
GOTO: Match = re.compile(r"^[\t ]+(?P<name>goto :.+)")

# return-void, return v0
RETURN: Match = re.compile(r"^[ ]{4}return.*")

# .catchall {:a .. :b} :c
TRY_CATCH: Match = re.compile(r"^[ ]{4}.catch.+?"
                              r"{(?P<try_start>:\S*)"
                              r".+?(?P<try_end>:\S*)}"
                              r"[ ](?P<handler>:\S*)")

# obfuscated files
OBFUSCATED: Match = re.compile(r".+[\/]([a-z]|github|v\d)[\/].+",
                               re.UNICODE)

# string constants
STATIC_STRING: Match = re.compile(
    r"\.field.+?static.+?(?P<string_name>\S+?):"
    r'Ljava/lang/String;\s=\s"(?P<string_value>.+)"',
    re.UNICODE,
)

CONST_STRING: Match = re.compile(
    r"\s+const-string(/jumbo)?\s(?P<register>[vp0-9]+),\s"
    r'"(?P<string>.+)"',
    re.UNICODE,
)

CLASS_NAME: Match = re.compile(r"\.class.+?(?P<class_name>\S+?;)", re.UNICODE)

LOCALS: Match = re.compile(r"\s+\.locals\s(?P<local_count>\d+)")

SKIP_FILE: Match = re.compile(r"/androidx?/")

COM_PATH: Match = re.compile(r"/(com/.+)")

# invoke-static {v4, v4}, Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I
INVOKE: Match = re.compile(r"^[ ]{4}(?P<invocation>invoke-\S+)\s"
                           r"{(?P<variables>[0-9pv.,\s]*)},\s"
                           r"(?P<class>\S+?)"
                           r"->(?P<method>\S+?)"
                           r"\((?P<args>\S*?)\)"
                           r"(?P<return_type>\S+)")
# .locals <number>
LOCALS_PATTERN: Match = re.compile(r"\s+\.locals\s(?P<local_count>\d+)")
