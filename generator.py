import yaml


class Generator(object):
    def __init__(self, schema_path):
        self.schema_path = schema_path
        self.tables = []
        self.triggers = []
        self.data = None

    def read_schema(self):
        with open(self.schema_path, 'r') as f:
            self.data = yaml.load(f.read())

    def create_table(self, name, data):
        table = (
            'DROP TABLE IF EXISTS {table_name};\n'
            'CREATE TABLE {table_name} (\n'
            '    id SERIAL NOT NULL PRIMARY KEY,\n'
            '    {fields},\n'
            '    created TIMESTAMP NOT NULL,\n'
            '    updated TIMESTAMP NOT NULL\n'
            ');\n'
        ).format(
            table_name=name.lower(),
            fields=',\n  '.join(
                [f'{k} {v.upper()}' for k, v in data['fields'].items()]
            )
        )
        self.tables.append(table)

    def trigger_for_created(self, name):
        trigger = (
            'CREATE OR REPLACE FUNCTION updated() RETURNS TRIGGER\n'
            'AS $$\n'
            'BEGIN\n'
            '    UPDATE {table_name} SET updated = NOW() WHERE id = OLD.id;\n\n'
            '    RETURN OLD;\n'
            'END;\n'
            '$$ LANGUAGE plpgsql;\n\n'
            'DROP TRIGGER IF EXISTS tr_updated ON {table_name};\n'
            'CREATE TRIGGER tr_updated AFTER UPDATE ON {table_name};\n'
            'FOR EACH ROW EXECUTE PROCEDURE updated();\n'

        ).format(
            table_name=name.lower()
        )
        return trigger

    def trigger_for_updated(self, name):
        trigger = (
            'CREATE OR REPLACE FUNCTION created() RETURNS TRIGGER\n'
            'AS $$\n'
            'BEGIN\n'
            '    UPDATE {table_name} SET created = NOW() WHERE id = OLD.id;\n\n'
            '    RETURN OLD;\n'
            'END;\n'
            '$$ LANGUAGE plpgsql;\n\n'
            'DROP TRIGGER IF EXISTS tr_created ON {table_name};\n'
            'CREATE TRIGGER tr_created AFTER INSERT ON {table_name}\n'
            'FOR EACH ROW EXECUTE PROCEDURE created();\n'

        ).format(
            table_name=name.lower()
        )
        return trigger

    def generate_tables(self):
        for table, data in self.data.items():
            self.create_table(table, data)

    def generate_triggers(self):
        for i in self.data:
            self.triggers.append(self.trigger_for_created(i))
            self.triggers.append(self.trigger_for_updated(i))

    def write_to_file(self):
        with open('db.sql', 'w') as f:
            f.write('\n'.join(self.tables))
            f.write('\n')
            f.write('\n'.join(self.triggers))

    def generate(self):
        self.read_schema()
        self.generate_tables()
        self.generate_triggers()
        self.write_to_file()


g = Generator('schema.yml')
g.generate()
