SELECT c.column_name FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage AS ccu USING (
     constraint_schema, constraint_name)
JOIN information_schema.columns AS c ON
c.table_schema = tc.constraint_schema AND
               tc.table_name = c.table_name
               AND ccu.column_name = c.column_name
where constraint_type = 'PRIMARY KEY' and tc.table_name = %s;
