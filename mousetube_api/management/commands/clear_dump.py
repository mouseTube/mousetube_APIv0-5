import json

# Charge le fichier dump avec un encodage plus permissif
with open('references_softwares_contacts.json', 'r', encoding='ISO-8859-1') as f:
    data = json.load(f)

# Champs à supprimer
fields_to_remove = ['created_by', 'id_user', 'created_at', 'modified_at']

# Nettoyage
for obj in data:
    if obj['model'] in ['mousetube_api.contact', 'mousetube_api.software', 'mousetube_api.reference']:
        for field in fields_to_remove:
            if field in obj['fields']:
                del obj['fields'][field]

# Sauvegarde du fichier nettoyé
with open('dump_clean.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Dump nettoyé -> dump_clean.json")