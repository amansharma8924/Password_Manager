# manager.py - Main entry point - yahan se poora program chalta hai

import os
import sys
import time
import threading
import getpass
from datetime import datetime
from typing import Optional

# Rich library imports - colored beautiful CLI output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Apni files import karo
from crypto import decrypt_data
from storage import load_passwords, save_passwords, file_exists
from generator import generate_password, check_strength, get_strength_color
from search import search_passwords, filter_by_category, filter_favorites, sort_entries, get_all_entries
from stats import calculate_stats
from exporter import export_to_txt, export_to_csv, export_encrypted_backup
from importer import import_from_csv

# Try clipboard import (optional - agar nahi hai toh skip)
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

console = Console()  # Rich console object - isse print karte hain

# ─────────────────────────────────────────────
# GLOBAL SESSION STATE
# ─────────────────────────────────────────────
passwords_db: dict = {}          # In-memory password store
master_pwd: str = ""             # Current session master password
last_activity: float = time.time()  # Last action timestamp
AUTO_LOGOUT_MINUTES = 5          # X min baad auto logout
INACTIVITY_SECONDS = AUTO_LOGOUT_MINUTES * 60
logout_event = threading.Event() # Background thread stop signal


# ─────────────────────────────────────────────
# AUTO-LOGOUT BACKGROUND THREAD
# ─────────────────────────────────────────────
def auto_logout_watcher():
    """
    Background thread that checks every 10 seconds.
    If more time than INACTIVITY_SECONDS has passed, then log out.
    """
    while not logout_event.is_set():
        time.sleep(10)  # 10 second wait
        idle_time = time.time() - last_activity
        if idle_time >= INACTIVITY_SECONDS:
            console.print(f"\n[bold red]⏰ {AUTO_LOGOUT_MINUTES} Auto-logout happened after minutes of inactivity![/bold red]")
            console.print("[yellow]Restart the program and enter the master password again.[/yellow]\n")
            logout_event.set()
            os._exit(0)  # Hard exit


def reset_activity():
    """Call after every action - reset the inactivity timer."""
    global last_activity
    last_activity = time.time()


# ─────────────────────────────────────────────
# CLIPBOARD HELPERS
# ─────────────────────────────────────────────
def copy_to_clipboard(text: str):
    """Copy the password to the clipboard and clear it after 30 seconds."""
    if not CLIPBOARD_AVAILABLE:
        console.print("[dim]Clipboard unavailable (install pyperclip)[/dim]")
        return

    pyperclip.copy(text)
    console.print("[green]📋 Password has been copied to the clipboard! (It will be cleared in 30 seconds)[/green]")

    # Background thread - 30 sec baad clipboard clear karo
    def clear_cb():
        time.sleep(30)
        try:
            if pyperclip.paste() == text:  # Agar abhi bhi same text hai
                pyperclip.copy('')
                console.print("\n[dim]🗑️  Clipboard got auto-cleared.[/dim]")
        except Exception:
            pass

    t = threading.Thread(target=clear_cb, daemon=True)
    t.start()


# ─────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────
def clear_screen():
    """Clear the terminal screen (for both Windows and Linux)."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print your header banner."""
    console.print(Panel.fit(
        "[bold cyan]🔐 PYTHON PASSWORD MANAGER[/bold cyan]\n"
        "[dim]Secure • Encrypted • Fast[/dim]",
        border_style="cyan"
    ))


def print_divider():
    """Section divider line."""
    console.print("[dim]─" * 50 + "[/dim]")


def display_password_table(entries: list, title: str = "Passwords"):
    """
    Show the list of passwords in Rich table format.
    entries: list of (service_name, entry_dict)
    """
    if not entries:
        console.print("[yellow]No entry was received.[/yellow]")
        return

    # Table banao
    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )

    # Columns add karo
    table.add_column("#", style="dim", width=4)
    table.add_column("Service", style="bold cyan", min_width=15)
    table.add_column("Username", style="white", min_width=15)
    table.add_column("Category", style="yellow", width=10)
    table.add_column("Tags", style="dim", min_width=10)
    table.add_column("⭐", width=3)
    table.add_column("Updated", style="dim", min_width=12)

    for i, (service, entry) in enumerate(entries, 1):
        tags = ', '.join(entry.get('tags', []))[:20]  # 20 char tak
        updated = entry.get('updated_at', '')[:10]     # Sirf date part
        fav = "⭐" if entry.get('favorite') else ""

        table.add_row(
            str(i),
            service,
            entry.get('username', ''),
            entry.get('category', 'other'),
            tags,
            fav,
            updated
        )

    console.print(table)


# ─────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────
def authenticate() -> bool:
    """
    Log in with the master password.
    First time = set new password. 
    Existing = verify (max 3 attempts).
    Returns: True if authenticated.
    """
    global passwords_db, master_pwd

    print_header()

    if not file_exists():
        # ── Pehli baar: Master password set karo ──
        console.print("\n[bold green]👋 Welcome! Setting up for the first time.[/bold green]")
        console.print("[yellow]Set a strong master password.[/yellow]\n")

        while True:
            pwd1 = getpass.getpass("🔑 New master password: ")
            if len(pwd1) < 6:
                console.print("[red]The password should be at least 6 characters long![/red]")
                continue
            pwd2 = getpass.getpass("🔑 Enter again (confirm): ")
            if pwd1 != pwd2:
                console.print("[red]Passwords did not match! Try again.[/red]")
                continue
            break

        # Score check
        score, level, _ = check_strength(pwd1)
        color = get_strength_color(level)
        console.print(f"Master password strength: [{color}]{level}[/{color}]")

        # Empty vault save karo
        master_pwd = pwd1
        save_passwords({}, master_pwd)
        passwords_db = {}
        console.print("[bold green]✅ Master password has been set! Logging in...[/bold green]\n")
        return True

    else:
        # ── Existing user: Password verify karo ──
        console.print("\n[bold cyan]🔒 Enter the master password.[/bold cyan]\n")
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            pwd = getpass.getpass(f"🔑 Master password (attempt {attempt}/{max_attempts}): ")

            with Progress(SpinnerColumn(), TextColumn("[cyan]Verifying..."), transient=True) as progress:
                progress.add_task("", total=None)
                result = load_passwords(pwd)

            if result is not None:
                # Sahi password
                master_pwd = pwd
                passwords_db = result
                console.print(f"[bold green]✅ Login successful! {len(passwords_db)} Passwords were loaded.[/bold green]\n")
                return True
            else:
                remaining = max_attempts - attempt
                if remaining > 0:
                    console.print(f"[red]❌ Wrong password! {remaining} attempts left.[/red]")
                else:
                    console.print("[bold red]🚫 3 wrong attempts! The program is shutting down.[/bold red]")
                    sys.exit(1)

    return False


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
def show_dashboard():
    """Show the stats dashboard after login."""
    reset_activity()
    stats = calculate_stats(passwords_db)

    # Main stats panel
    stats_text = (
        f"[bold white]Total Passwords:[/bold white]  [cyan]{stats['total']}[/cyan]\n"
        f"[bold white]Favorites:[/bold white]         [yellow]⭐ {stats['favorites_count']}[/yellow]\n"
        f"[bold white]Weak Passwords:[/bold white]    [red]{len(stats['weak_passwords'])}[/red]\n"
        f"[bold white]Duplicates:[/bold white]        [orange3]{len(stats['duplicate_passwords'])}[/orange3]\n"
        f"[bold white]Old (90+ days):[/bold white]    [dim]{len(stats['old_passwords'])}[/dim]"
    )
    console.print(Panel(stats_text, title="📊 Dashboard", border_style="cyan"))

    # Category breakdown
    if stats['by_category']:
        cat_text = ""
        for cat, count in sorted(stats['by_category'].items()):
            cat_text += f"  {cat:<12} : {count}\n"
        console.print(Panel(cat_text.strip(), title="📁 By Category", border_style="dim"))

    # Warnings
    if stats['weak_passwords']:
        weak_list = ", ".join([s for s, _ in stats['weak_passwords'][:5]])
        console.print(f"[red]⚠️  Weak passwords: {weak_list}[/red]")

    if stats['duplicate_passwords']:
        console.print(f"[orange3]⚠️  {len(stats['duplicate_passwords'])} There are duplicate password groups![/orange3]")


# ─────────────────────────────────────────────
# ADD PASSWORD
# ─────────────────────────────────────────────
def add_password():
    """Add a new password entry in the vault."""
    reset_activity()
    console.print("\n[bold cyan]➕ Add a new password[/bold cyan]")
    print_divider()

    # Service name
    service = Prompt.ask("Service/Website naam").strip()
    if not service:
        console.print("[red]Service name cannot be empty![/red]")
        return
    if service in passwords_db:
        console.print(f"[red]'{service}' Already exists! Edit it or use a different name.[/red]")
        return

    # Username
    username = Prompt.ask("Username/Email", default="")

    # Password - generate ya manually enter
    use_gen = Confirm.ask("Auto-generate password?", default=True)
    if use_gen:
        try:
            length = int(Prompt.ask("Password length", default="16"))
            use_sym = Confirm.ask("Symbols include karo?", default=True)
        except ValueError:
            length, use_sym = 16, True

        password = generate_password(length=length, use_symbols=use_sym)
        console.print(f"[green]Generated: {password}[/green]")
    else:
        password = getpass.getpass("Password: ")
        if not password:
            console.print("[red]Password empty nahi ho sakta![/red]")
            return

    # Strength check
    score, level, suggestions = check_strength(password)
    color = get_strength_color(level)
    console.print(f"Strength: [{color}]{level}[/{color}] (score: {score}/10)")
    if suggestions:
        for s in suggestions[:2]:
            console.print(f"  [dim]💡 {s}[/dim]")

    # Duplicate check
    for svc, entry in passwords_db.items():
        if entry.get('password') == password:
            console.print(f"[orange3]⚠️  This password is also being used in '{svc}'![/orange3]")

    # Category
    cats = "work / personal / social / banking / email / other"
    console.print(f"[dim]Categories: {cats}[/dim]")
    category = Prompt.ask("Category", default="other").strip().lower()
    valid_cats = ['work', 'personal', 'social', 'banking', 'email', 'other']
    if category not in valid_cats:
        category = 'other'

    # Tags
    tags_input = Prompt.ask("Tags (comma separated)", default="")
    tags = [t.strip() for t in tags_input.split(',') if t.strip()]

    # Notes
    notes = Prompt.ask("Notes (optional)", default="")

    # Favorite
    favorite = Confirm.ask("Favorite mark karo?", default=False)

    # Entry banao
    now = datetime.now().isoformat()
    passwords_db[service] = {
        'username': username,
        'password': password,
        'notes': notes,
        'category': category,
        'tags': tags,
        'favorite': favorite,
        'created_at': now,
        'updated_at': now,
        'last_used': '',
        'history': []  # Password history empty se start
    }

    # Save karo
    if save_passwords(passwords_db, master_pwd):
        console.print(f"\n[bold green]✅ '{service}' Successfully got saved![/bold green]")
    else:
        console.print("[red]There was an error in saving![/red]")


# ─────────────────────────────────────────────
# VIEW PASSWORD
# ─────────────────────────────────────────────
def view_password():
    """Show the complete details of any one password."""
    reset_activity()
    if not passwords_db:
        console.print("[yellow]Vault empty![/yellow]")
        return

    service = Prompt.ask("Enter service name").strip()
    if service not in passwords_db:
        console.print(f"[red]'{service}' Not found![/red]")
        return

    entry = passwords_db[service]

    # Last used update karo
    passwords_db[service]['last_used'] = datetime.now().isoformat()
    save_passwords(passwords_db, master_pwd)

    # Detail table
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Field", style="bold cyan", width=14)
    table.add_column("Value", style="white")

    score, level, _ = check_strength(entry.get('password', ''))
    color = get_strength_color(level)

    table.add_row("Service", service)
    table.add_row("Username", entry.get('username', ''))
    table.add_row("Password", f"[bold]{entry.get('password', '')}[/bold]")
    table.add_row("Strength", f"[{color}]{level}[/{color}]")
    table.add_row("Category", entry.get('category', ''))
    table.add_row("Tags", ', '.join(entry.get('tags', [])))
    table.add_row("Notes", entry.get('notes', ''))
    table.add_row("Favorite", "⭐ Yes" if entry.get('favorite') else "No")
    table.add_row("Created", entry.get('created_at', '')[:19])
    table.add_row("Updated", entry.get('updated_at', '')[:19])
    table.add_row("Last Used", entry.get('last_used', '')[:19])

    console.print(Panel(table, title=f"🔐 {service}", border_style="cyan"))

    # Clipboard copy
    copy_to_clipboard(entry.get('password', ''))


# ─────────────────────────────────────────────
# EDIT PASSWORD
# ─────────────────────────────────────────────
def edit_password():
    """Edit existing entry."""
    reset_activity()
    service = Prompt.ask("Service name for editing").strip()
    if service not in passwords_db:
        console.print(f"[red]'{service}' Not found![/red]")
        return

    entry = passwords_db[service]
    console.print(f"\n[cyan]Editing: {service}[/cyan] [dim](leave empty = will remain the same)[/dim]")

    # Har field ke liye current value dikhao
    new_username = Prompt.ask(f"Username", default=entry.get('username', ''))
    change_pwd = Confirm.ask("I want to change the password?", default=False)

    new_password = entry.get('password', '')
    if change_pwd:
        use_gen = Confirm.ask("Auto-generate new password?", default=True)
        if use_gen:
            try:
                length = int(Prompt.ask("Length", default="16"))
            except ValueError:
                length = 16
            new_password = generate_password(length=length)
            console.print(f"[green]Generated: {new_password}[/green]")
        else:
            new_password = getpass.getpass("New password: ")

        # History mein purana password save karo (max 5)
        history = entry.get('history', [])
        history.insert(0, {
            'password': entry['password'],
            'changed_at': datetime.now().isoformat()
        })
        entry['history'] = history[:5]  # Sirf last 5 rakhna

    new_notes = Prompt.ask("Notes", default=entry.get('notes', ''))
    valid_cats = ['work', 'personal', 'social', 'banking', 'email', 'other']
    new_cat = Prompt.ask("Category", default=entry.get('category', 'other')).lower()
    if new_cat not in valid_cats:
        new_cat = entry.get('category', 'other')

    tags_input = Prompt.ask("Tags", default=', '.join(entry.get('tags', [])))
    new_tags = [t.strip() for t in tags_input.split(',') if t.strip()]
    new_fav = Confirm.ask("Favorite?", default=entry.get('favorite', False))

    # Update karo
    passwords_db[service].update({
        'username': new_username,
        'password': new_password,
        'notes': new_notes,
        'category': new_cat,
        'tags': new_tags,
        'favorite': new_fav,
        'updated_at': datetime.now().isoformat()
    })

    if save_passwords(passwords_db, master_pwd):
        console.print(f"[bold green]✅ '{service}' update successful![/bold green]")
    else:
        console.print("[red]save error occurred![/red]")


# ─────────────────────────────────────────────
# DELETE PASSWORD
# ─────────────────────────────────────────────
def delete_password():
    """Delete the password entry (with confirmation)."""
    reset_activity()
    service = Prompt.ask("The name of the service to delete").strip()
    if service not in passwords_db:
        console.print(f"[red]'{service}' non found![/red]")
        return

    # Confirm maango
    if Confirm.ask(f"[red]'{service}'permanently delete?[/red]", default=False):
        del passwords_db[service]
        if save_passwords(passwords_db, master_pwd):
            console.print(f"[bold green]✅ '{service}' delete successful![/bold green]")
    else:
        console.print("[dim]Cancle delete.[/dim]")


# ─────────────────────────────────────────────
# LIST & SEARCH
# ─────────────────────────────────────────────
def list_and_search_menu():
    """Sub-menu of list, search, and filter."""
    reset_activity()
    console.print("\n[bold cyan]🔍 Search & Filter[/bold cyan]")
    print_divider()
    console.print("1. Show all password")
    console.print("2. Search")
    console.print("3. Filter by category")
    console.print("4. Show only favorites")
    console.print("0. Return/Exit")

    choice = Prompt.ask("Choice", default="0")

    if choice == '1':
        sort_by = Prompt.ask("Sort by? (name/created/last_used)", default="name")
        entries = sort_entries(get_all_entries(passwords_db), sort_by)
        display_password_table(entries, "All Passwords")

    elif choice == '2':
        query = Prompt.ask("Search query")
        results = search_passwords(passwords_db, query)
        display_password_table(results, f"Search: '{query}'")
        console.print(f"[dim]{len(results)} results mile.[/dim]")

    elif choice == '3':
        console.print("[dim]work / personal / social / banking / email / other[/dim]")
        cat = Prompt.ask("Category")
        results = filter_by_category(passwords_db, cat)
        display_password_table(results, f"Category: {cat}")

    elif choice == '4':
        results = filter_favorites(passwords_db)
        display_password_table(results, "⭐ Favorites")


# ─────────────────────────────────────────────
# PASSWORD GENERATOR (standalone)
# ─────────────────────────────────────────────
def password_generator_menu():
    """Standalone password generator + strength checker."""
    reset_activity()
    console.print("\n[bold cyan]🎲 Password Generator[/bold cyan]")
    print_divider()
    console.print("1. Random password generated")
    console.print("2. Password strength check")
    console.print("0. Return/Exit")

    choice = Prompt.ask("Choice", default="0")

    if choice == '1':
        try:
            length = int(Prompt.ask("Length (8-64)", default="16"))
        except ValueError:
            length = 16
        use_up = Confirm.ask("Uppercase?", default=True)
        use_lo = Confirm.ask("Lowercase?", default=True)
        use_di = Confirm.ask("Digits?", default=True)
        use_sy = Confirm.ask("Symbols?", default=True)

        pwd = generate_password(length, use_up, use_lo, use_di, use_sy)
        score, level, suggestions = check_strength(pwd)
        color = get_strength_color(level)

        console.print(f"\n[bold white]Generated:[/bold white] [green]{pwd}[/green]")
        console.print(f"[bold white]Strength:[/bold white]  [{color}]{level}[/{color}] ({score}/10)")
        copy_to_clipboard(pwd)

    elif choice == '2':
        pwd = getpass.getpass("Password for checking: ")
        score, level, suggestions = check_strength(pwd)
        color = get_strength_color(level)

        console.print(f"\n[bold white]Strength:[/bold white] [{color}]{level}[/{color}] ({score}/10)")
        if suggestions:
            console.print("[yellow]Suggestions:[/yellow]")
            for s in suggestions:
                console.print(f"  💡 {s}")


# ─────────────────────────────────────────────
# IMPORT / EXPORT MENU
# ─────────────────────────────────────────────
def import_export_menu():
    """Sub-menu of Import/Export."""
    reset_activity()
    console.print("\n[bold cyan]📦 Import / Export[/bold cyan]")
    print_divider()
    console.print("1. Export to TXT (unencrypted)")
    console.print("2. Export to CSV")
    console.print("3. Export encrypted backup (.enc)")
    console.print("4. Import from CSV")
    console.print("0. Return/Exit")

    choice = Prompt.ask("Choice", default="0")

    if choice == '1':
        console.print("[red]⚠️  WARNING: TXT file will not be encrypted![/red]")
        if Confirm.ask("Need to continue?", default=False):
            fname = export_to_txt(passwords_db)
            console.print(f"[green]✅ Exported: {fname}[/green]")

    elif choice == '2':
        fname = export_to_csv(passwords_db)
        console.print(f"[green]✅ CSV export: {fname}[/green]")

    elif choice == '3':
        fname = export_encrypted_backup()
        console.print(f"[green]✅ Encrypted backup: {fname}[/green]")

    elif choice == '4':
        filepath = Prompt.ask("CSV file path").strip()
        try:
            imported, skipped, errors = import_from_csv(filepath, passwords_db)
            save_passwords(passwords_db, master_pwd)
            console.print(f"[green]✅ Imported: {imported} | Skipped: {skipped}[/green]")
            if errors:
                for e in errors[:5]:
                    console.print(f"[dim]  {e}[/dim]")
        except Exception as e:
            console.print(f"[red]Import error: {e}[/red]")


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────
def main_menu():
    """Main navigation menu loop."""
    while True:
        reset_activity()
        console.print("\n[bold cyan]━━━ MAIN MENU ━━━[/bold cyan]")
        console.print("1. 📊 Dashboard")
        console.print("2. ➕ Add password")
        console.print("3. 👁️  View password")
        console.print("4. ✏️  Edit password")
        console.print("5. 🗑️  Delete password")
        console.print("6. 🔍 Search & Filter")
        console.print("7. 🎲 Password Generator")
        console.print("8. 📦 Import / Export")
        console.print("0. 🚪 Exit")
        print_divider()

        choice = Prompt.ask("[bold]Choice[/bold]", default="0")

        if choice == '1':
            show_dashboard()
        elif choice == '2':
            add_password()
        elif choice == '3':
            view_password()
        elif choice == '4':
            edit_password()
        elif choice == '5':
            delete_password()
        elif choice == '6':
            list_and_search_menu()
        elif choice == '7':
            password_generator_menu()
        elif choice == '8':
            import_export_menu()
        elif choice == '0':
            if Confirm.ask("Do you want to exit??", default=True):
                logout_event.set()
                console.print("[bold green]👋 Goodbye! Stay Secure![/bold green]")
                sys.exit(0)
        else:
            console.print("[red]Wrong choice! Choose from 0-8.[/red]")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Authentication
    if not authenticate():
        sys.exit(1)

    # Auto-logout background thread start karo
    watcher = threading.Thread(target=auto_logout_watcher, daemon=True)
    watcher.start()

    # Dashboard dikhao aur main loop shuru karo
    show_dashboard()
    main_menu()
