# migrate_contacts_to_users.py

import django
import os

# Configure Django
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "mousetube_api.settings"
)  # <-- Remplace par ton projet
django.setup()

from mousetube_api.models import (
    Contact,
    User,
    Software,
)  # <-- Remplace "mousetube_api" par ton nom d'application


def migrate_contacts_to_users(dry_run=True):
    created_users = []
    linked_softwares = []

    for contact in Contact.objects.all():
        if not contact.email:
            continue  # On ignore les Contacts sans email

        # Vérifier si un User correspondant existe déjà
        user = User.objects.filter(
            name_user=contact.lastname, email_user=contact.email
        ).first()

        if not user:
            if not dry_run:
                user = User.objects.create(
                    name_user=contact.lastname,
                    first_name_user=contact.firstname or "",
                    email_user=contact.email or "",
                )
            else:
                user = User(  # fake instance pour afficher ce qui serait créé
                    name_user=contact.lastname,
                    first_name_user=contact.firstname or "",
                    email_user=contact.email or "",
                )
            created_users.append(user)

        # Mettre à jour les logiciels liés à ce contact
        softwares = contact.software_to_contact.all()
        for software in softwares:
            if not dry_run:
                # Lier le Software au User (assure-toi que Software a une relation ManyToMany avec User)
                software.users.add(user)
            linked_softwares.append((software, user, contact))

    # Afficher un rapport
    print("===== Rapport de migration =====")
    print(f"Utilisateurs créés ({len(created_users)}) :")
    for u in created_users:
        print(f"- {u.first_name_user} {u.name_user} ({u.email_user})")

    print(f"\nLiens Software-User effectués ({len(linked_softwares)}) :")
    for sw, usr, ct in linked_softwares:
        print(
            f"- Software '{sw.software_name}' lié à User '{usr.name_user}' (depuis Contact '{ct.lastname}')"
        )

    if dry_run:
        print("\n**Ceci était un DRY RUN : aucune donnée n'a été modifiée.**")
    else:
        print("\n**Migration effective terminée.**")


if __name__ == "__main__":
    # Mettre dry_run=False pour appliquer réellement
    migrate_contacts_to_users(dry_run=False)
