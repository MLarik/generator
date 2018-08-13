import yaml

def generator(f_schema):
    cfg = yaml.load(open(f_schema))
    statements = []
    for i in range(len(cfg)):
        string = 'create table(\n'
        current_key = cfg.keys(i)
        string += current_key
        fields = cfg.get(current_key).get('fields')
        for j in range(len(fields)):
            current_key2 = fields.keys(j)
            string += '    ' + current_key2 + fields.get(current_key2) + '\n'

        string += ');'

generator('schema.yml')
