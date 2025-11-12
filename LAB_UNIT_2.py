#!/usr/bin/env python3
"""
contact_book_debug.py
Robust, debug-friendly version of the contact book.
Prints tracebacks for unexpected errors and handles common corrupt/missing data cases.
"""

import csv
import json
import os
import shutil
import uuid
import traceback
from typing import List, Dict, Optional

CSV_HEADERS = ["id", "name", "phone", "email", "notes"]


def make_backup(path: str) -> None:
    try:
        if os.path.exists(path):
            backup_path = f"{path}.bak"
            shutil.copy2(path, backup_path)
            print(f"[backup] Saved corrupt/old file to: {backup_path}")
    except Exception as e:
        print(f"[backup] Could not create backup: {e}")


def format_contact(c: Dict) -> str:
    # Use .get to avoid KeyError if file is malformed
    cid = c.get("id", "") or ""
    name = c.get("name", "") or ""
    phone = c.get("phone", "") or ""
    email = c.get("email", "") or ""
    notes = c.get("notes", "") or ""
    return f"{cid[:8]:8} | {name:<20} | {phone:<15} | {email:<25} | {notes}"


def print_header():
    print("-" * 90)
    print(f"{'ID':8} | {'Name':20} | {'Phone':15} | {'Email':25} | Notes")
    print("-" * 90)


# --- File I/O with robust exception handling ----
def load_json(path: str) -> List[Dict]:
    if not os.path.exists(path):
        print(f"[load_json] File not found: {path} — starting with empty list.")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON root is not a list (expected list of contacts).")
            # ensure each element is a dict
            clean = []
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    clean.append(item)
                else:
                    print(f"[load_json] Skipping non-dict entry at index {i}: {item!r}")
            return clean
    except json.JSONDecodeError as e:
        print(f"[load_json] JSON decode error: {e}")
        make_backup(path)
        print("[load_json] Backed up corrupted JSON. Starting with empty contact list.")
        return []
    except Exception as e:
        print(f"[load_json] Unexpected error: {e}")
        traceback.print_exc()
        return []


def save_json(path: str, contacts: List[Dict]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[save_json] Failed to save JSON: {e}")
        traceback.print_exc()


def load_csv(path: str) -> List[Dict]:
    if not os.path.exists(path):
        print(f"[load_csv] File not found: {path} — starting with empty list.")
        return []
    contacts = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if not any(row.values()):
                    # skip entirely empty rows
                    continue
                # fill missing headers
                contact = {k: (row.get(k) or "") for k in CSV_HEADERS}
                # generate id if missing or blank
                if not contact["id"]:
                    contact["id"] = str(uuid.uuid4())
                    print(f"[load_csv] Row {i} missing id — generated new id {contact['id'][:8]}")
                contacts.append(contact)
        return contacts
    except Exception as e:
        print(f"[load_csv] Error reading CSV: {e}")
        traceback.print_exc()
        make_backup(path)
        print("[load_csv] Backed up corrupted CSV. Starting with empty contact list.")
        return []


def save_csv(path: str, contacts: List[Dict]) -> None:
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for c in contacts:
                row = {k: c.get(k, "") for k in CSV_HEADERS}
                writer.writerow(row)
    except Exception as e:
        print(f"[save_csv] Failed to save CSV: {e}")
        traceback.print_exc()


# --- Contact operations ---
def add_contact(contacts: List[Dict], name: str, phone: str, email: str, notes: str = "") -> Dict:
    new_contact = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "notes": notes.strip(),
    }
    contacts.append(new_contact)
    return new_contact


def list_contacts(contacts: List[Dict]) -> None:
    if not contacts:
        print("No contacts found.")
        return
    print_header()
    for c in contacts:
        print(format_contact(c))
    print("-" * 90)
    print(f"Total contacts: {len(contacts)}")


def search_contacts(contacts: List[Dict], query: str) -> List[Dict]:
    q = query.strip().lower()
    results = []
    for c in contacts:
        try:
            if (q in (c.get("name","") or "").lower() or
                q in (c.get("phone","") or "").lower() or
                q in (c.get("email","") or "").lower() or
                q in (c.get("notes","") or "").lower() or
                q in (c.get("id","") or "").lower()):
                results.append(c)
        except Exception:
            # defensive: if some entry is malformed, skip it but print debug
            print(f"[search_contacts] Skipping malformed contact: {c!r}")
    return results


def find_contact_by_id(contacts: List[Dict], cid: str) -> Optional[Dict]:
    if not cid:
        return None
    for c in contacts:
        if not isinstance(c, dict):
            continue
        # exact match or prefix match
        if c.get("id") == cid or (isinstance(c.get("id"), str) and c.get("id","").startswith(cid)):
            return c
    return None


def update_contact(contact: Dict, name: Optional[str], phone: Optional[str], email: Optional[str], notes: Optional[str]) -> None:
    if not isinstance(contact, dict):
        raise TypeError("update_contact expects a dict for contact")
    if name is not None and name.strip() != "":
        contact["name"] = name.strip()
    if phone is not None and phone.strip() != "":
        contact["phone"] = phone.strip()
    if email is not None and email.strip() != "":
        contact["email"] = email.strip()
    if notes is not None:
        contact["notes"] = notes.strip()


def delete_contact(contacts: List[Dict], contact: Dict) -> bool:
    try:
        contacts.remove(contact)
        return True
    except ValueError:
        return False


# --- CLI with safer input handling ---
def main():
    try:
        print("File-based Contact Book (debug mode)")
        storage = ""
        while storage not in ("json", "csv"):
            storage = input("Choose storage format (json/csv) [json]: ").strip().lower() or "json"

        default_path = "contacts.json" if storage == "json" else "contacts.csv"
        path = input(f"Enter file path [{default_path}]: ").strip() or default_path

        contacts = load_json(path) if storage == "json" else load_csv(path)
        print(f"[info] Loaded {len(contacts)} contacts from {path}.")

        def save():
            if storage == "json":
                save_json(path, contacts)
            else:
                save_csv(path, contacts)

        while True:
            print("\nMenu: [A]dd  [L]ist  [S]earch  [U]pdate  [D]elete  [Q]uit")
            choice = input("Choose option: ").strip().lower()
            if not choice:
                continue

            if choice in ("a", "add"):
                name = input("Name: ").strip()
                phone = input("Phone: ").strip()
                email = input("Email: ").strip()
                notes = input("Notes (optional): ").strip()
                new = add_contact(contacts, name, phone, email, notes)
                save()
                print(f"Added: {format_contact(new)}")

            elif choice in ("l", "list"):
                list_contacts(contacts)

            elif choice in ("s", "search"):
                q = input("Search query (name/phone/email/id): ").strip()
                results = search_contacts(contacts, q)
                print(f"Found {len(results)} result(s) for '{q}':")
                if results:
                    print_header()
                    for r in results:
                        print(format_contact(r))
                    print("-" * 90)

            elif choice in ("u", "update"):
                q = input("Enter contact id (or search term to find): ").strip()
                target = find_contact_by_id(contacts, q) if q else None
                if not target:
                    matches = search_contacts(contacts, q)
                    if not matches:
                        print("No matches found.")
                        continue
                    print("Matches:")
                    print_header()
                    for m in matches:
                        print(format_contact(m))
                    print("-" * 90)
                    sel = input("Enter exact id to update (or blank to cancel): ").strip()
                    if not sel:
                        print("Update cancelled.")
                        continue
                    target = find_contact_by_id(contacts, sel)
                    if not target:
                        print("ID not found. Cancelled.")
                        continue

                print("Leave blank to keep current value.")
                new_name = input(f"Name [{target.get('name','')}]: ")
                new_phone = input(f"Phone [{target.get('phone','')}]: ")
                new_email = input(f"Email [{target.get('email','')}]: ")
                new_notes = input(f"Notes [{target.get('notes','')}]: ")
                update_contact(target,
                               name=new_name or None,
                               phone=new_phone or None,
                               email=new_email or None,
                               notes=new_notes or None)
                save()
                print("Updated contact:")
                print_header()
                print(format_contact(target))

            elif choice in ("d", "delete"):
                q = input("Enter contact id (or search term to find): ").strip()
                target = find_contact_by_id(contacts, q) if q else None
                if not target:
                    matches = search_contacts(contacts, q)
                    if not matches:
                        print("No matches found.")
                        continue
                    print("Matches:")
                    print_header()
                    for m in matches:
                        print(format_contact(m))
                    print("-" * 90)
                    sel = input("Enter exact id to delete (or blank to cancel): ").strip()
                    if not sel:
                        print("Delete cancelled.")
                        continue
                    target = find_contact_by_id(contacts, sel)
                    if not target:
                        print("ID not found. Cancelled.")
                        continue

                confirm = input(f"Are you sure you want to delete '{target.get('name','')}'? (y/N): ").strip().lower()
                if confirm == "y":
                    ok = delete_contact(contacts, target)
                    if ok:
                        save()
                        print("Contact deleted.")
                    else:
                        print("Failed to delete (not found).")
                else:
                    print("Delete cancelled.")

            elif choice in ("q", "quit", "exit"):
                save()
                print("Goodbye — contacts saved.")
                break
            else:
                print("Unknown option. Try again.")
    except Exception as e:
        print("[CRITICAL] Unhandled exception occurred:")
        traceback.print_exc()
        print("Please copy & paste the above traceback into the chat so I can help debug further.")


if __name__ == "__main__":
    main()
