import yaml
# from datetime import datetime

def generator(f_schema):
    cfg = yaml.load(open(f_schema))
    statements = []
    for i in cfg:
        string = '\n'
        string += 'create table(\n' + i + '\n'
        fields = cfg.get(i).get('fields')
        string += '    id serial primary key ' + '\n'
        for fields_key in fields:
            string += '    ' + fields_key + ' ' + fields.get(fields_key) + '\n'
        string += '    created ' + 'datetime\n'
        string += '    updated ' + 'datetime\n'
        statements.append(string + ');')

    return statements

# a = generator('schema.yml')
# print(a[0])
# print(a[1])
