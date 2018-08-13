import yaml

def generator(f_schema):
    cfg = yaml.load(open(f_schema))
    for iter in range(len(cfg)):
        cfg.keys(iter)



generator('schema.yml')
