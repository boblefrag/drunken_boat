select column_name, data_type, is_nullable, column_default
from information_schema.columns where table_schema = %s and table_name=%s
