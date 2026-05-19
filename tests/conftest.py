import os

# Tests run without MySQL; persistence is covered in repository unit tests.
os.environ.setdefault("DATABASE_ENABLED", "false")
