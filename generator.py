import yaml

def generator(f_schema):
    cfg = yaml.load(open(f_schema))
    statements = []
    for i in cfg:
        string = '\n'
        string += 'create table(\n' + i + '\n'
        fields = cfg.get(i).get('fields')
        for fields_key in fields:
            string += '    ' + fields_key + ' ' + fields.get(fields_key) + '\n'
        statements.append(string + ');')
    return statements

# a = generator('schema.yml')
# print(a[0])
# print(a[1])