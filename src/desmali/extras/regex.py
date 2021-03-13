import re

# regex pattern to identify lines that contains a method
# read more about Named Capturing Groups: https://www.regular-expressions.info/refext.html
METHOD = re.compile(r"\.method.+?(?P<name>\S+?)" +
                    r"\((?P<args>\S*?)\)" +
                    r"(?P<return>\S+)",
                    re.UNICODE)

# :goto_0
LABEL = re.compile(r"^[ ]{4}(?P<name>:.+)")

# goto :goto_0
GOTO = re.compile(r"^[\t ]+(?P<name>goto :.+)")

# return-void, return v0
RETURN = re.compile(r"^[ ]{4}return.*")

# .catchall {:a .. :b} :c
TRY_CATCH = re.compile(r"^[ ]{4}.catch.+?"
                       r"{(?P<try_start>:\S*)"
                       r".+?(?P<try_end>:\S*)}"
                       r"[ ](?P<handler>:\S*)")
