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
        # print(self.data['Category']['relations'])

    @staticmethod
    def create_table(name, data):
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
            fields=',\n    '.join(
                [f'{k} {v.upper()}' for k, v in data['fields'].items()]
            )
        )
        return table

    @staticmethod
    def trigger_for_created(name):
        trigger = (
            'CREATE OR REPLACE FUNCTION updated() RETURNS TRIGGER\n'
            'AS $$\n'
            'BEGIN\n'
            '    UPDATE {table_name} SET updated = NOW() WHERE id = OLD.id;\n\n'
            '    RETURN OLD;\n'
            'END;\n'
            '$$ LANGUAGE plpgsql;\n\n'
            'DROP TRIGGER IF EXISTS tr_updated ON {table_name};\n'
            'CREATE TRIGGER tr_updated AFTER UPDATE ON {table_name}\n'
            'FOR EACH ROW EXECUTE PROCEDURE updated();\n'

        ).format(
            table_name=name.lower()
        )
        return trigger

    @staticmethod
    def trigger_for_updated(name):
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

    def create_relations(self, table):
        rel = self.data[table]['relations']
        keys = list(rel.keys())
        result = ''

        for i in keys:
            t = table.lower()
            t2 = i.lower()

            if rel[i] == 'one' and self.data[i]['relations'][table] == 'many':
                return f'ALTER TABLE {t} ADD COLUMN {t2}_id INTEGER REFERENCES {t2}(id);\n'

            if rel[i] == 'many' and self.data[i]['relations'][table] == 'many':
                result = f'DROP TABLE IF EXISTS {t}_{t2};\n' \
                         f'CREATE TABLE {t}_{t2} (\n' \
                         f'     {t}_id INTEGER REFERENCES {t}(id),\n' \
                         f'     {t2}_id INTEGER REFERENCES {t2}(id)\n' \
                          ');\n'
                del self.data[i]['relations'][table]

        return result

    def generate_tables(self):
        for table, data in self.data.items():
            self.tables.append(self.create_table(table, data))
            self.tables.append(self.create_relations(table))

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
