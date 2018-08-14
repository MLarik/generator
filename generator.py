import yaml

def generator(f_schema):
    cfg = yaml.load(open(f_schema))
    statements = []
    for i in cfg:
        string = '\n'
        string += 'create table(\n' + i + '\n'
        fields = cfg.get(i).get('fields')
        for j in fields:
            string += '    ' + j + ' ' + fields.get(j) + '\n'
        statements.append(string + ');')
    return statements

# a = generator('schema.yml')
# print(a[0])
# print(a[1])
