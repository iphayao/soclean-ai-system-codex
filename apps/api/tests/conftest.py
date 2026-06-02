import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ.pop("OPENAI_API_KEY", None)
