import yaml
with open('/app/config/configuration.yaml', 'r') as f:
    lines = f.readlines()
result = []
in_mqtt = False
for line in lines:
    if line.startswith('mqtt:'):
        in_mqtt = True
        continue
    if in_mqtt and line.strip() == '':
        in_mqtt = False
        continue
    if not in_mqtt:
        result.append(line)
with open('/app/config/configuration.yaml', 'w') as f:
    f.writelines(result)
