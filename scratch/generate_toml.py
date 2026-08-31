import json

with open('gzg-asistencia-system-91d54f4af312.json', 'r') as f:
    d = json.load(f)

lines = ["[gcp_service_account]"]
for k, v in d.items():
    if isinstance(v, str):
        v_escaped = v.replace('\n', '\\n').replace('"', '\\"')
        lines.append(f'{k} = "{v_escaped}"')
    else:
        lines.append(f'{k} = {v}')

toml_content = "\n".join(lines)
with open('scratch/secrets_to_copy.toml', 'w') as f_out:
    f_out.write(toml_content)

print("TOML generado exitosamente en scratch/secrets_to_copy.toml")
