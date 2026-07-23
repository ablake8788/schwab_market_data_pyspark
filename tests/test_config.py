import pytest

from core.config import AppConfig


@pytest.fixture(autouse=True)
def _reset_singleton():
    AppConfig.reset()
    yield
    AppConfig.reset()


def _write_ini(tmp_path, contents: str):
    ini_path = tmp_path / "test_config.ini"
    ini_path.write_text(contents, encoding="utf-8")
    return ini_path


def test_load_reads_sql_and_spark_sections(tmp_path):
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass

[spark]
app_name = my_app
master = local[2]
""")

    cfg = AppConfig.load(str(ini_path))

    assert cfg.sql.server == "testserver"
    assert cfg.sql.database == "testdb"
    assert cfg.sql.username == "testuser"
    assert cfg.sql.password == "testpass"
    assert cfg.sql.trust_cert == "yes"  # default
    assert cfg.sql.table_history == "dbo.SchwabQuotesHistory"  # default
    assert cfg.spark.app_name == "my_app"
    assert cfg.spark.master == "local[2]"
    assert cfg.spark.shuffle_partitions == 4  # default


def test_load_applies_optional_overrides(tmp_path):
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass
trust_cert = no
table_history = dbo.CustomHistory
table_bollinger = dbo.CustomBollinger
table_zscore = dbo.CustomZScore

[spark]
shuffle_partitions = 8
fetch_size = 5000
""")

    cfg = AppConfig.load(str(ini_path))

    assert cfg.sql.trust_cert == "no"
    assert cfg.sql.table_history == "dbo.CustomHistory"
    assert cfg.sql.table_bollinger == "dbo.CustomBollinger"
    assert cfg.sql.table_zscore == "dbo.CustomZScore"
    assert cfg.spark.shuffle_partitions == 8
    assert cfg.spark.fetch_size == 5000


def test_load_works_without_spark_section(tmp_path):
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass
""")

    cfg = AppConfig.load(str(ini_path))

    assert cfg.spark.app_name == "schwab_market_data_pyspark"
    assert cfg.spark.master == "local[*]"


def test_load_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        AppConfig.load("does_not_exist.ini")


def test_load_without_email_section_leaves_it_none(tmp_path):
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass
""")

    cfg = AppConfig.load(str(ini_path))

    assert cfg.email is None


def test_load_reads_email_section_case_insensitively(tmp_path):
    # configparser section names are case-sensitive by default; some tools
    # (and this project's own .ini) write "[Email]" not "[email]".
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass

[Email]
enabled = true
smtp_server = smtp.example.com
smtp_user = sender@example.com
smtp_password = secret
to_email = a@example.com
""")

    cfg = AppConfig.load(str(ini_path))

    assert cfg.email is not None
    assert cfg.email.smtp_server == "smtp.example.com"


def test_load_reads_email_section(tmp_path):
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass

[email]
enabled = true
smtp_server = smtp.example.com
smtp_port = 587
smtp_user = sender@example.com
smtp_password = secret
to_email = a@example.com, b@example.com
subject = Test Subject
""")

    cfg = AppConfig.load(str(ini_path))

    assert cfg.email is not None
    assert cfg.email.enabled is True
    assert cfg.email.smtp_server == "smtp.example.com"
    assert cfg.email.smtp_port == 587
    assert cfg.email.from_email == "sender@example.com"  # defaults to smtp_user
    assert cfg.email.to_email == ("a@example.com", "b@example.com")
    assert cfg.email.subject == "Test Subject"


def test_load_caches_singleton(tmp_path):
    ini_path = _write_ini(tmp_path, """
[sqlserver]
driver = ODBC Driver 17 for SQL Server
server = testserver
database = testdb
username = testuser
password = testpass
""")

    first = AppConfig.load(str(ini_path))
    second = AppConfig.load(str(ini_path))

    assert first is second
