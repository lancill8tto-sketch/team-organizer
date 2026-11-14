import os
import sys
import re
import json
import uuid
import hashlib
import shutil
import sqlite3
import threading
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
import textwrap
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import time

# =========================================================================
# CONFIGURAZIONE AGGIORNAMENTI GITHUB & ABBONAMENTO MENSILE AUTOMATICO
# =========================================================================
VERSIONE_APP = "1.1.0"
GITHUB_USER = "lancill8tto-sketch"
GITHUB_REPO = "team-organizer"
GITHUB_FILE = "app.py"

LIMITE_TICKET_TRIAL = 5
GIORNI_VALIDITA_MESE = 32  # Controlla il rinnovo mensile (30 giorni + 2 di tolleranza)

# --- CONFIGURAZIONE PAGAMENTO AUTOMATICO (GUMROAD MEMBERSHIP) ---
LINK_PAGAMENTO_ABBONAMENTO = "https://gianlucabilardi.gumroad.com/l/dvxrzv"
GUMROAD_PRODUCT_ID = "7LT_XRBL__InPtzItvjhKg=="

# Chiave segreta (identica a quella del tuo KeyGeneratorPRO)
CHIAVE_SEGRETA_AUTORE = "LANCIL8TTO_TEAM_ORGANIZER_PRO_2026_SECRET"

# Configurazione iniziale dello stile grafico
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- PALETTE TEMA SCURO (CARBON-GLASS & NEON FLUO) ---
DARK_THEME = {
    "mode": "Dark",
    "CARBON_BG": "#080a0f",
    "CARBON_LINE": "#10141f",
    "CARBON_SIDEBAR": "#050608",
    "GLASS_PANEL": "#121621",
    "GLASS_CARD": "#0b0e16",
    "TEXT_MAIN": "#f8fafc",
    "TEXT_SUB": "#e9d5ff",
    "TEXT_COLLAB": "#a7f3d0",
    "TEXT_CLIENT": "#fef08a",
    "TEXT_MUTED": "#94a3b8",
    "BORDER_SUB": "#1e293b",
    # Macro-area 1: Ticket (Viola Fluo)
    "ACCENT_1": "#b026ff",
    "ACCENT_1_DARK": "#5a189a",
    "ACCENT_1_HOVER": "#9d4edd",
    "ACCENT_1_BORDER": "#9333ea",
    "BOX_TEXT_1": "#f3e8ff",
    # Macro-area 2: Collaboratori (Verde Fluo)
    "ACCENT_2": "#00ff66",
    "ACCENT_2_DARK": "#047857",
    "ACCENT_2_HOVER": "#00cc52",
    "ACCENT_2_BORDER": "#10b981",
    "BOX_TEXT_2": "#ecfdf5",
    # Macro-area 3: Clienti & Calendario (Giallo Fluo)
    "ACCENT_3": "#ffea00",
    "ACCENT_3_DARK": "#b45309",
    "ACCENT_3_HOVER": "#eab308",
    "ACCENT_3_BORDER": "#eab308",
    "BOX_TEXT_3": "#fefce8",
    # Menu Laterale
    "MENU_1_BG": "#2e1065",
    "MENU_2_BG": "#3b0764",
    "MENU_3_BG": "#4c1d95",
    "MENU_4_BG": "#581c87",
    "MENU_5_BG": "#064e3b",
    "MENU_6_BG": "#065f46",
    "MENU_7_BG": "#047857",
    "MENU_8_BG": "#422006",
    "MENU_9_BG": "#713f12",
    "MENU_10_BG": "#78350f",
    "MENU_11_BG": "#854d0e",
    "MENU_TEXT_3": "#fef08a"
}

# --- PALETTE TEMA CHIARO SOBRIO (GRIGIO CARBONIO CHIARO & SCALA CELESTE/BLU) ---
LIGHT_THEME = {
    "mode": "Light",
    "CARBON_BG": "#e2e8f0",         # Grigio molto chiaro base carbonio
    "CARBON_LINE": "#cbd5e1",       # Trama diagonale fibra di carbonio chiara
    "CARBON_SIDEBAR": "#f1f5f9",    # Grigio perla sobrio per barra laterale
    "GLASS_PANEL": "#f8fafc",       # Bianco ghiaccio per i pannelli principali
    "GLASS_CARD": "#ffffff",        # Bianco puro per schede, righe e caselle
    "TEXT_MAIN": "#0f172a",         # Blu notte scuro per massima leggibilità
    "TEXT_SUB": "#1e3a8a",          # Blu profondo per etichette
    "TEXT_COLLAB": "#0369a1",       # Blu oceano per etichette collaboratori
    "TEXT_CLIENT": "#1d4ed8",       # Blu royal per etichette clienti
    "TEXT_MUTED": "#475569",        # Grigio ardesia per testi secondari
    "BORDER_SUB": "#cbd5e1",
    # Macro-area 1: Ticket (Blu Royal / Azzurro Intenso)
    "ACCENT_1": "#0284c7",
    "ACCENT_1_DARK": "#0369a1",
    "ACCENT_1_HOVER": "#0ea5e9",
    "ACCENT_1_BORDER": "#38bdf8",
    "BOX_TEXT_1": "#0f172a",
    # Macro-area 2: Collaboratori (Celeste / Ciano Sobrio)
    "ACCENT_2": "#0ea5e9",
    "ACCENT_2_DARK": "#0284c7",
    "ACCENT_2_HOVER": "#38bdf8",
    "ACCENT_2_BORDER": "#7dd3fc",
    "BOX_TEXT_2": "#0f172a",
    # Macro-area 3: Clienti & Calendario (Blu Navy / Indaco Sobrio)
    "ACCENT_3": "#1d4ed8",
    "ACCENT_3_DARK": "#1e40af",
    "ACCENT_3_HOVER": "#2563eb",
    "ACCENT_3_BORDER": "#60a5fa",
    "BOX_TEXT_3": "#0f172a",
    # Menu Laterale in scala armonica dal Celeste al Blu
    "MENU_1_BG": "#0284c7",
    "MENU_2_BG": "#0369a1",
    "MENU_3_BG": "#075985",
    "MENU_4_BG": "#0c4a6e",
    "MENU_5_BG": "#0ea5e9",
    "MENU_6_BG": "#0284c7",
    "MENU_7_BG": "#0369a1",
    "MENU_8_BG": "#2563eb",
    "MENU_9_BG": "#1d4ed8",
    "MENU_10_BG": "#1e40af",
    "MENU_11_BG": "#1e3a8a",
    "MENU_TEXT_3": "#ffffff"
}

MESI_IT = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]


# --- FUNZIONE PERCORSO SICURO DATABASE (APPDATA / MULTI-OS) ---
def get_percorso_database(nome_app="TeamOrganizerPRO", nome_db="database_gestionale.db"):
    if sys.platform == "win32":
        cartella_base = os.getenv("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        cartella_base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        cartella_base = os.getenv("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")

    cartella_dati = os.path.join(cartella_base, nome_app)
    os.makedirs(cartella_dati, exist_ok=True)
    percorso_finale = os.path.join(cartella_dati, nome_db)

    vecchio_db_locale = os.path.join(os.path.abspath("."), "team_organizer.db")
    if os.path.exists(vecchio_db_locale) and not os.path.exists(percorso_finale):
        try:
            shutil.copy2(vecchio_db_locale, percorso_finale)
        except Exception:
            pass

    return percorso_finale


def get_machine_id():
    try:
        nodo = str(uuid.getnode())
        h = hashlib.sha256(nodo.encode("utf-8")).hexdigest().upper()
        return f"{h[0:4]}-{h[4:8]}"
    except Exception:
        return "A1B2-C3D4"


def calcola_licenza_master(machine_id):
    pulito = machine_id.strip().upper()
    raw = f"{pulito}-{CHIAVE_SEGRETA_AUTORE}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()
    return f"PRO-{h[0:4]}-{h[4:8]}-{h[8:12]}"


def normalizza_codice_hash(testo):
    """Calcola l'impronta SHA-256 ignorando differenze di a-capo tra Windows e GitHub."""
    if not testo:
        return ""
    pulito = "\n".join(line.rstrip() for line in testo.replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()
    return hashlib.sha256(pulito.encode("utf-8")).hexdigest()


# --- CLASSE PER I TOOLTIP ---
class ToolTip:
    def __init__(self, widget, text, border_color="#0284c7"):
        self.widget = widget
        self.text = text
        self.border_color = border_color
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(350, self.show_tip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        frame = ctk.CTkFrame(tw, fg_color="#0f172a", border_color=self.border_color, border_width=1, corner_radius=6)
        frame.pack()
        label = ctk.CTkLabel(frame, text=self.text, text_color="#f8fafc", padx=10, pady=4, font=ctk.CTkFont(size=11, weight="bold"))
        label.pack()

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# --- GENERATORE PDF NATIVO MULTI-PAGINA SENZA DIPENDENZE ESTERNE ---
def genera_pdf_semplice(percorso_file, righe_testo):
    def escape_pdf(s):
        sostituzioni = {
            "à": "a'", "è": "e'", "é": "e'", "ì": "i'", "ò": "o'", "ù": "u'",
            "À": "A'", "È": "E'", "É": "E'", "Ì": "I'", "Ò": "O'", "Ù": "U'",
            "€": "EUR", "°": " gradi"
        }
        for k, v in sostituzioni.items():
            s = s.replace(k, v)
        s = s.encode("latin-1", "ignore").decode("latin-1")
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    # Suddivide automaticamente le righe lunghe per evitare che escano dal foglio A4
    righe_espanse = []
    for idx, r in enumerate(righe_testo):
        for sub_r in str(r).split("\n"):
            if len(sub_r) > 88:
                wrapped = textwrap.wrap(sub_r, width=88)
                for w in wrapped:
                    righe_espanse.append((w, idx == 0))
            else:
                righe_espanse.append((sub_r, idx == 0))

    righe_per_pagina = 44
    pagine = [righe_espanse[i:i + righe_per_pagina] for i in range(0, len(righe_espanse), righe_per_pagina)]
    if not pagine:
        pagine = [[("", False)]]

    oggetti = []
    # 1: Catalog, 2: Pages, 3: Font Normale, 4: Font Grassetto
    oggetti.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    oggetti.append(b"")  # Placeholder per 2 0 obj (Pages)
    oggetti.append(b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    oggetti.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")

    kids_refs = []
    next_id = 5

    for pag in pagine:
        page_id = next_id
        content_id = next_id + 1
        next_id += 2
        kids_refs.append(f"{page_id} 0 R")

        comandi_testo = ["BT", "/F1 10 Tf", "45 790 Td", "16 TL"]
        for testo_riga, is_title in pag:
            if is_title:
                comandi_testo.append("/F2 14 Tf")
                comandi_testo.append(f"({escape_pdf(testo_riga)}) Tj")
                comandi_testo.append("T*")
                comandi_testo.append("/F1 10 Tf")
            else:
                comandi_testo.append(f"({escape_pdf(testo_riga)}) Tj")
                comandi_testo.append("T*")
        comandi_testo.append("ET")
        stream_data = "\n".join(comandi_testo).encode("latin-1")

        page_obj = (
            f"{page_id} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Contents {content_id} 0 R /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> >>\n"
            f"endobj\n"
        ).encode("latin-1")

        content_obj = (
            f"{content_id} 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("latin-1")
            + stream_data
            + b"\nendstream\nendobj\n"
        )

        oggetti.append(page_obj)
        oggetti.append(content_obj)

    kids_str = " ".join(kids_refs)
    oggetti[1] = f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {len(pagine)} >>\nendobj\n".encode("latin-1")

    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in oggetti:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)

    xref_pos = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(oggetti) + 1}\n".encode("latin-1"))
    pdf_bytes.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

    pdf_bytes.extend(f"trailer\n<< /Size {len(oggetti) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode("latin-1"))

    with open(percorso_file, "wb") as f:
        f.write(pdf_bytes)


# --- DIZIONARIO MULTILINGUA ---
BASE_TRADUZIONI = {
    "titolo_app": f"Team Organizer - Carbon PRO v{VERSIONE_APP}",
    "btn_nuovo_int": "➕  Apri nuovo ticket",
    "btn_int_aperti": "📂  Ticket Aperti",
    "btn_int_espletati": "📁  Ticket Espletati",
    "btn_int_permanenti": "🔒  Ticket Permanenti",
    "btn_calendario": "🗓️  Calendario",
    "btn_report": "📊  Report Clienti",
    "btn_nuovo_collab": "👷  Nuovo Collaboratore",
    "btn_schede_collab": "👥  Schede Collaboratori",
    "btn_nuovo_cliente": "👤  Nuovo Cliente",
    "btn_gestione_clienti": "📋  Gestione Clienti",
    "btn_mansioni": "➕  Aggiungi Mansione",
    "btn_pro": "⚡  Abbonamento PRO",
    "btn_aggiorna": "🔄  Controlla Aggiornamenti",
    "barra_titolo": f"◈  TEAM  ORGANIZER  v{VERSIONE_APP}  ◈",
    "placeholder_filtro": "Restringi il campo...",
    "lbl_cliente": "Seleziona Cliente:",
    "lbl_tel_cliente": "Tel Cliente:",
    "lbl_data": "Data Appuntamento:",
    "lbl_orario": "Orario:",
    "lbl_collaboratore": "Assegna a Collaboratore:",
    "lbl_tel_collab": "Tel Collaboratore:",
    "lbl_indirizzo": "Indirizzo Intervento:",
    "lbl_guasto": "Descrizione Guasto / Richiesta:",
    "btn_salva_whatsapp": "➕ Salva Ticket e Invia WhatsApp",
    "msg_successo_ticket": "Ticket aperto con successo e notifiche WhatsApp avviate!",
    "err_cliente": "Seleziona un cliente con numero di telefono valido!",
    "err_campi": "Compila i campi obbligatori!"
}

TRADUZIONI = {
    "it": BASE_TRADUZIONI.copy(),
    "en": {
        **BASE_TRADUZIONI,
        "btn_nuovo_int": "➕  Open new ticket",
        "btn_int_aperti": "📂  Open Tickets",
        "btn_int_espletati": "📁  Completed Tickets",
        "btn_int_permanenti": "🔒  Permanent Tickets",
        "btn_calendario": "🗓️  Calendar",
        "btn_report": "📊  Client Reports",
        "btn_nuovo_collab": "👷  New Collaborator",
        "btn_schede_collab": "👥  Collaborator Profiles",
        "btn_nuovo_cliente": "👤  New Client",
        "btn_gestione_clienti": "📋  Client Management",
        "btn_mansioni": "➕  Add Job Role",
        "btn_pro": "⚡  PRO Subscription",
        "btn_aggiorna": "🔄  Check for Updates",
        "placeholder_filtro": "Filter list...",
        "lbl_cliente": "Select Client:",
        "lbl_tel_cliente": "Client Phone:",
        "lbl_data": "Appointment Date:",
        "lbl_orario": "Time:",
        "lbl_collaboratore": "Assign to Collaborator:",
        "lbl_tel_collab": "Collaborator Phone:",
        "lbl_indirizzo": "Service Address:",
        "lbl_guasto": "Issue / Request Description:",
        "btn_salva_whatsapp": "➕ Save Ticket & Send WhatsApp",
        "msg_successo_ticket": "Ticket opened and WhatsApp notifications started!",
        "err_cliente": "Select a client with a valid phone number!",
        "err_campi": "Fill in required fields!"
    },
    "es": {
        **BASE_TRADUZIONI,
        "btn_nuovo_int": "➕  Abrir nuevo ticket",
        "btn_int_aperti": "📂  Tickets Abiertos",
        "btn_int_espletati": "📁  Tickets Completados",
        "btn_int_permanenti": "🔒  Tickets Permanentes",
        "btn_calendario": "🗓️  Calendario",
        "btn_report": "📊  Informes Clientes",
        "btn_nuovo_collab": "👷  Nuevo Colaborador",
        "btn_schede_collab": "👥  Perfiles Colaboradores",
        "btn_nuovo_cliente": "👤  Nuevo Cliente",
        "btn_gestione_clienti": "📋  Gestión de Clientes",
        "btn_mansioni": "➕  Añadir Puesto",
        "btn_pro": "⚡  Suscripción PRO",
        "btn_aggiorna": "🔄  Buscar Actualizaciones",
        "placeholder_filtro": "Filtrar...",
        "lbl_cliente": "Seleccionar Cliente:",
        "lbl_tel_cliente": "Tel. Cliente:",
        "lbl_data": "Fecha de Cita:",
        "lbl_orario": "Hora:",
        "lbl_collaboratore": "Asignar a Colaborador:",
        "lbl_tel_collab": "Tel. Colaborador:",
        "lbl_indirizzo": "Dirección:",
        "lbl_guasto": "Descripción del problema:",
        "btn_salva_whatsapp": "➕ Guardar y Enviar WhatsApp",
        "msg_successo_ticket": "¡Ticket abierto e notificaciones WhatsApp iniciadas!",
        "err_cliente": "¡Seleccione un cliente con teléfono válido!",
        "err_campi": "¡Complete los campos obligatorios!"
    },
    "fr": {
        **BASE_TRADUZIONI,
        "btn_nuovo_int": "➕  Ouvrir nouveau ticket",
        "btn_int_aperti": "📂  Tickets Ouverts",
        "btn_int_espletati": "📁  Tickets Terminés",
        "btn_int_permanenti": "🔒  Tickets Permanents",
        "btn_calendario": "🗓️  Calendrier",
        "btn_report": "📊  Rapports Clients",
        "btn_nuovo_collab": "👷  Nouveau Collaborateur",
        "btn_schede_collab": "👥  Profils Collaborateurs",
        "btn_nuovo_cliente": "👤  Nouveau Client",
        "btn_gestione_clienti": "📋  Gestion des Clients",
        "btn_mansioni": "➕  Ajouter Rôle",
        "btn_pro": "⚡  Abonnement PRO",
        "btn_aggiorna": "🔄  Vérifier Mises à jour",
        "placeholder_filtro": "Filtrer...",
        "lbl_cliente": "Sélectionner Client:",
        "lbl_tel_cliente": "Tél. Client:",
        "lbl_data": "Date du Rendez-vous:",
        "lbl_orario": "Heure:",
        "lbl_collaboratore": "Assigner au Collaborateur:",
        "lbl_tel_collab": "Tél. Collaborateur:",
        "lbl_indirizzo": "Adresse:",
        "lbl_guasto": "Description du problème:",
        "btn_salva_whatsapp": "➕ Enregistrer et Envoyer WhatsApp",
        "msg_successo_ticket": "Ticket ouvert et notifications WhatsApp lancées !",
        "err_cliente": "Sélectionnez un client avec un téléphone valide !",
        "err_campi": "Remplissez les champs obligatoires !"
    },
    "de": {
        **BASE_TRADUZIONI,
        "btn_nuovo_int": "➕  Neues Ticket öffnen",
        "btn_int_aperti": "📂  Offene Tickets",
        "btn_int_espletati": "📁  Erledigte Tickets",
        "btn_int_permanenti": "🔒  Permanente Tickets",
        "btn_calendario": "🗓️  Kalender",
        "btn_report": "📊  Kundenberichte",
        "btn_nuovo_collab": "👷  Neuer Mitarbeiter",
        "btn_schede_collab": "👥  Mitarbeiterprofile",
        "btn_nuovo_cliente": "👤  Neuer Kunde",
        "btn_gestione_clienti": "📋  Kundenverwaltung",
        "btn_mansioni": "➕  Rolle Hinzufügen",
        "btn_pro": "⚡  PRO-Abonnement",
        "btn_aggiorna": "🔄  Updates suchen",
        "placeholder_filtro": "Filtern...",
        "lbl_cliente": "Kunde auswählen:",
        "lbl_tel_cliente": "Kunden-Tel.:",
        "lbl_data": "Termindatum:",
        "lbl_orario": "Uhrzeit:",
        "lbl_collaboratore": "Mitarbeiter zuweisen:",
        "lbl_tel_collab": "Mitarbeiter-Tel.:",
        "lbl_indirizzo": "Adresse:",
        "lbl_guasto": "Problembeschreibung:",
        "btn_salva_whatsapp": "➕ Speichern & WhatsApp senden",
        "msg_successo_ticket": "Ticket geöffnet und WhatsApp-Benachrichtigungen gestartet!",
        "err_cliente": "Wählen Sie einen Kunden mit gültiger Telefonnummer!",
        "err_campi": "Pflichtfelder ausfüllen!"
    }
}

LINGUE_NOMI = {
    "it": "Italiano", "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch"
}


class TeamOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lingua_corrente = "it"
        self.notifica_timer = None
        self.machine_id = get_machine_id()
        self.is_pro = False
        self.scadenza_abbonamento_str = ""
        self.menu_attivo_corrente = "nuovo"

        # Inizializza il database usando il percorso sicuro AppData
        self.init_db()
        self.verifica_stato_licenza_locale()

        # Carica preferenza tema
        tema_salvato = self._get_config("skin_tema", "Chiaro (Celeste/Blu)")
        self.tema_nome = tema_salvato if tema_salvato in ["Chiaro (Celeste/Blu)", "Scuro (Carbon Fluo)"] else "Chiaro (Celeste/Blu)"
        self.T = LIGHT_THEME if self.tema_nome.startswith("Chiaro") else DARK_THEME
        ctk.set_appearance_mode(self.T["mode"])

        self.title(TRADUZIONI[self.lingua_corrente]["titolo_app"])
        self.geometry("1340x880")
        self.minsize(1050, 680)
        self.configure(fg_color=self.T["CARBON_BG"])

        # Salva hash del codice locale all'avvio se non presente
        self._inizializza_hash_versione_locale()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- MENU LATERALE ---
        self.sidebar_frame = ctk.CTkFrame(
            self, width=250, corner_radius=0, fg_color=self.T["CARBON_SIDEBAR"],
            border_width=1, border_color=self.T["BORDER_SUB"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(19, weight=1)

        # Pulsanti Menu Laterale
        self.btn_nuovo_int = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_nuovo_int"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_nuovo_intervento
        )
        self.btn_nuovo_int.grid(row=1, column=0, padx=18, pady=(12, 3), sticky="ew")

        self.btn_int_aperti = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_int_aperti"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_interventi_aperti
        )
        self.btn_int_aperti.grid(row=2, column=0, padx=18, pady=3, sticky="ew")

        self.btn_int_espletati = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_int_espletati"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_interventi_espletati
        )
        self.btn_int_espletati.grid(row=3, column=0, padx=18, pady=3, sticky="ew")

        self.btn_int_permanenti = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_int_permanenti"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_interventi_permanenti
        )
        self.btn_int_permanenti.grid(row=4, column=0, padx=18, pady=3, sticky="ew")

        self.btn_collaboratori = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_nuovo_collab"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_collaboratori
        )
        self.btn_collaboratori.grid(row=5, column=0, padx=18, pady=(8, 3), sticky="ew")

        self.btn_gestione_collab = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_schede_collab"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_gestione_collaboratori
        )
        self.btn_gestione_collab.grid(row=6, column=0, padx=18, pady=3, sticky="ew")

        self.btn_mansioni = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_mansioni"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_mansioni
        )
        self.btn_mansioni.grid(row=7, column=0, padx=18, pady=3, sticky="ew")

        self.btn_clienti = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_nuovo_cliente"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_clienti
        )
        self.btn_clienti.grid(row=8, column=0, padx=18, pady=(8, 3), sticky="ew")

        self.btn_gestione_clienti = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_gestione_clienti"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_gestione_clienti
        )
        self.btn_gestione_clienti.grid(row=9, column=0, padx=18, pady=3, sticky="ew")

        self.btn_calendario = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_calendario"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_calendario
        )
        self.btn_calendario.grid(row=10, column=0, padx=18, pady=3, sticky="ew")

        self.btn_report = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_report"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.mostra_sezione_report
        )
        self.btn_report.grid(row=11, column=0, padx=18, pady=3, sticky="ew")

        # Selettore Skin Chiara / Scura
        self.lbl_tema_title = ctk.CTkLabel(self.sidebar_frame, text="🎨 Tema / Skin:", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_tema_title.grid(row=12, column=0, padx=20, pady=(6, 1), sticky="w")

        self.combo_tema = ctk.CTkComboBox(
            self.sidebar_frame, values=["Chiaro (Celeste/Blu)", "Scuro (Carbon Fluo)"], height=30,
            command=self.cambia_tema_interfaccia
        )
        self.combo_tema.grid(row=13, column=0, padx=18, pady=(0, 4), sticky="ew")
        self.combo_tema.set(self.tema_nome)

        # Selettore Lingua
        self.lbl_lingua_title = ctk.CTkLabel(self.sidebar_frame, text="🌐 Lingua / Language:", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_lingua_title.grid(row=14, column=0, padx=20, pady=(4, 1), sticky="w")

        self.combo_lingua = ctk.CTkComboBox(
            self.sidebar_frame, values=list(LINGUE_NOMI.values()), height=30,
            command=self.cambia_lingua_da_combo
        )
        self.combo_lingua.grid(row=15, column=0, padx=18, pady=(0, 6), sticky="ew")
        self.combo_lingua.set("Italiano")

        self.btn_aggiorna_app = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_aggiorna"],
            font=ctk.CTkFont(size=12, weight="bold"), height=33, corner_radius=10,
            command=lambda: self.avvia_controllo_aggiornamenti(manuale=True)
        )
        self.btn_aggiorna_app.grid(row=16, column=0, padx=18, pady=3, sticky="ew")

        self.btn_licenza = ctk.CTkButton(
            self.sidebar_frame, text=TRADUZIONI[self.lingua_corrente]["btn_pro"],
            font=ctk.CTkFont(size=13, weight="bold"), height=35, corner_radius=10,
            command=self.apri_finestra_licenza
        )
        self.btn_licenza.grid(row=17, column=0, padx=18, pady=(3, 10), sticky="ew")

        # --- AREA PRINCIPALE CON TRAMA FIBRA DI CARBONIO SU CANVAS ---
        self.main_content = ctk.CTkFrame(self, fg_color=self.T["CARBON_BG"], corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(2, weight=1)

        # Canvas di sfondo per disegnare la trama diagonale fibra di carbonio
        self.bg_canvas = tk.Canvas(self.main_content, highlightthickness=0, bd=0, bg=self.T["CARBON_BG"])
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.main_content.bind("<Configure>", self._disegna_trama_carbonio)

        # Barra superiore
        self.top_bar = ctk.CTkFrame(self.main_content, height=56, corner_radius=14, border_width=1)
        self.top_bar.grid(row=0, column=0, padx=30, pady=(20, 10), sticky="ew")
        self.top_bar.grid_columnconfigure(0, weight=1)

        self.lbl_barra_titolo = ctk.CTkLabel(
            self.top_bar, text=TRADUZIONI[self.lingua_corrente]["barra_titolo"],
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_barra_titolo.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        self.lbl_notifica = ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_notifica.grid(row=0, column=1, padx=15, pady=12, sticky="e")

        self.lbl_badge_licenza = ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_badge_licenza.grid(row=0, column=2, padx=20, pady=12, sticky="e")

        # =========================================================================
        # 1. AREA TICKET
        # =========================================================================
        self.frame_nuovo_intervento = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_nuovo_intervento.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_nuovo_intervento.grid_columnconfigure(0, weight=1)
        self.frame_nuovo_intervento.grid_rowconfigure(1, weight=1)

        self.form_ticket = ctk.CTkFrame(self.frame_nuovo_intervento, corner_radius=16, border_width=2)
        self.form_ticket.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.form_ticket.grid_columnconfigure((1, 3), weight=1)

        # Riga 0: Filtro & Cliente
        self.lbl_cliente = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_cliente"], font=ctk.CTkFont(weight="bold"))
        self.lbl_cliente.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        cli_box_frame = ctk.CTkFrame(self.form_ticket, fg_color="transparent")
        cli_box_frame.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        cli_box_frame.grid_columnconfigure(1, weight=1)
        self.entry_filtro_nuovo_cli = ctk.CTkEntry(cli_box_frame, placeholder_text=TRADUZIONI["it"]["placeholder_filtro"], width=120, height=35)
        self.entry_filtro_nuovo_cli.grid(row=0, column=0, padx=(0, 6))
        self.entry_filtro_nuovo_cli.bind("<KeyRelease>", self.filtra_clienti_nuovo_ticket)
        self.combo_clienti = ctk.CTkComboBox(cli_box_frame, values=self.carica_lista_clienti(), height=35, command=self.on_cliente_selezionato)
        self.combo_clienti.grid(row=0, column=1, sticky="ew")
        self.lbl_tel_cliente = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_tel_cliente"], font=ctk.CTkFont(weight="bold"))
        self.lbl_tel_cliente.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.entry_tel_cliente = ctk.CTkEntry(self.form_ticket, height=35)
        self.entry_tel_cliente.grid(row=0, column=3, padx=15, pady=10, sticky="ew")

        # Riga 1: Data & Orario
        self.lbl_data = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_data"], font=ctk.CTkFont(weight="bold"))
        self.lbl_data.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        data_frame = ctk.CTkFrame(self.form_ticket, fg_color="transparent")
        data_frame.grid(row=1, column=1, padx=15, pady=10, sticky="ew")
        oggi = datetime.now()
        self.combo_giorno = ctk.CTkComboBox(data_frame, values=[f"{g:02d}" for g in range(1, 32)], width=65, height=35)
        self.combo_giorno.pack(side="left", padx=(0, 5))
        self.combo_giorno.set(f"{oggi.day:02d}")
        self.combo_mese = ctk.CTkComboBox(data_frame, values=MESI_IT, width=75, height=35)
        self.combo_mese.pack(side="left", padx=5)
        self.combo_mese.set(MESI_IT[oggi.month - 1])
        self.combo_anno = ctk.CTkComboBox(data_frame, values=[str(a) for a in range(2025, 2032)], width=85, height=35)
        self.combo_anno.pack(side="left", padx=5)
        self.combo_anno.set(str(oggi.year))

        self.lbl_orario = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_orario"], font=ctk.CTkFont(weight="bold"))
        self.lbl_orario.grid(row=1, column=2, padx=15, pady=10, sticky="w")
        ora_frame = ctk.CTkFrame(self.form_ticket, fg_color="transparent")
        ora_frame.grid(row=1, column=3, padx=15, pady=10, sticky="w")
        self.combo_ora = ctk.CTkComboBox(ora_frame, values=[f"{h:02d}" for h in range(24)], width=70, height=35)
        self.combo_ora.pack(side="left", padx=(0, 5))
        self.combo_ora.set("09")
        self.combo_minuti = ctk.CTkComboBox(ora_frame, values=["00", "15", "30", "45"], width=70, height=35)
        self.combo_minuti.pack(side="left", padx=5)
        self.combo_minuti.set("00")

        # Riga 2: Collaboratore
        self.lbl_collaboratore = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_collaboratore"], font=ctk.CTkFont(weight="bold"))
        self.lbl_collaboratore.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.combo_collaboratori = ctk.CTkComboBox(self.form_ticket, values=self.carica_lista_collaboratori(), height=35, command=self.on_collaboratore_selezionato)
        self.combo_collaboratori.grid(row=2, column=1, padx=15, pady=10, sticky="ew")
        self.lbl_tel_collab = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_tel_collab"], font=ctk.CTkFont(weight="bold"))
        self.lbl_tel_collab.grid(row=2, column=2, padx=15, pady=10, sticky="w")
        self.entry_tel_collaboratore = ctk.CTkEntry(self.form_ticket, height=35)
        self.entry_tel_collaboratore.grid(row=2, column=3, padx=15, pady=10, sticky="ew")

        # Riga 3: Indirizzo
        self.lbl_indirizzo = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_indirizzo"], font=ctk.CTkFont(weight="bold"))
        self.lbl_indirizzo.grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.entry_indirizzo = ctk.CTkEntry(self.form_ticket, height=35)
        self.entry_indirizzo.grid(row=3, column=1, columnspan=3, padx=15, pady=10, sticky="ew")

        # Riga 4: Guasto & Salva
        self.lbl_guasto = ctk.CTkLabel(self.form_ticket, text=TRADUZIONI["it"]["lbl_guasto"], font=ctk.CTkFont(weight="bold"))
        self.lbl_guasto.grid(row=4, column=0, padx=15, pady=10, sticky="nw")
        self.text_nuovo_guasto = ctk.CTkTextbox(self.form_ticket, height=65, border_width=1)
        self.text_nuovo_guasto.grid(row=4, column=1, columnspan=2, padx=15, pady=10, sticky="ew")
        self.btn_salva_ticket = ctk.CTkButton(
            self.form_ticket, text=TRADUZIONI["it"]["btn_salva_whatsapp"],
            font=ctk.CTkFont(size=13, weight="bold"), border_width=2, height=55, corner_radius=12, command=self.crea_nuovo_ticket
        )
        self.btn_salva_ticket.grid(row=4, column=3, padx=15, pady=10, sticky="ew")

        self.lista_box = ctk.CTkTextbox(self.frame_nuovo_intervento, corner_radius=16, border_width=2)
        self.lista_box.grid(row=1, column=0, sticky="nsew")

        # --- VISTA TICKET APERTI ---
        self.frame_interventi_aperti = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_interventi_aperti.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_interventi_aperti.grid_remove()
        self.frame_interventi_aperti.grid_columnconfigure(0, weight=1)
        self.frame_interventi_aperti.grid_rowconfigure(1, weight=1)

        self.form_aggiorna_int = ctk.CTkFrame(self.frame_interventi_aperti, corner_radius=16, border_width=2)
        self.form_aggiorna_int.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.form_aggiorna_int.grid_columnconfigure(1, weight=1)

        self.lbl_sel_ticket_ap = ctk.CTkLabel(self.form_aggiorna_int, text="Seleziona Ticket:", font=ctk.CTkFont(weight="bold"))
        self.lbl_sel_ticket_ap.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.combo_interventi_aperti = ctk.CTkComboBox(self.form_aggiorna_int, values=self.carica_lista_interventi_aperti(), height=35, command=self.carica_dettagli_intervento_aperto)
        self.combo_interventi_aperti.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        self.lbl_note_ticket_ap = ctk.CTkLabel(self.form_aggiorna_int, text="Note Intervento:", font=ctk.CTkFont(weight="bold"))
        self.lbl_note_ticket_ap.grid(row=1, column=0, padx=15, pady=10, sticky="nw")
        self.text_aggiorna_tipo = ctk.CTkTextbox(self.form_aggiorna_int, height=60, border_width=1)
        self.text_aggiorna_tipo.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        self.btn_action_frame = ctk.CTkFrame(self.form_aggiorna_int, fg_color="transparent")
        self.btn_action_frame.grid(row=1, column=2, padx=15, pady=10)
        self.btn_aggiorna_tipo_int = ctk.CTkButton(
            self.btn_action_frame, text="💾 Aggiorna Ticket", font=ctk.CTkFont(weight="bold"),
            border_width=1, height=38, command=self.aggiorna_tipo_intervento
        )
        self.btn_aggiorna_tipo_int.pack(side="left", padx=5)
        self.btn_chiudi_int = ctk.CTkButton(
            self.btn_action_frame, text="🔒 Chiudi Ticket", font=ctk.CTkFont(weight="bold"),
            fg_color="#dc2626", hover_color="#b91c1c", border_width=1, border_color="#f87171", text_color="#ffffff", height=38, command=self.chiudi_ticket
        )
        self.btn_chiudi_int.pack(side="left", padx=5)

        self.scroll_aperti = ctk.CTkScrollableFrame(self.frame_interventi_aperti, corner_radius=16, border_width=2)
        self.scroll_aperti.grid(row=1, column=0, sticky="nsew")

        # --- VISTA TICKET ESPLETATI ---
        self.frame_interventi_espletati = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_interventi_espletati.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_interventi_espletati.grid_remove()
        self.frame_interventi_espletati.grid_columnconfigure(0, weight=1)
        self.frame_interventi_espletati.grid_rowconfigure(1, weight=1)

        self.form_espletati = ctk.CTkFrame(self.frame_interventi_espletati, corner_radius=16, border_width=2)
        self.form_espletati.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.form_espletati.grid_columnconfigure((1, 3, 5), weight=1)

        self.lbl_mem_esp = ctk.CTkLabel(self.form_espletati, text="Memoria:", font=ctk.CTkFont(weight="bold"))
        self.lbl_mem_esp.grid(row=0, column=0, padx=10, pady=12, sticky="w")
        self.combo_ritenzione = ctk.CTkComboBox(
            self.form_espletati, values=["3 Mesi", "6 Mesi", "9 Mesi", "1 Anno"], height=34, width=110,
            command=lambda e: self.aggiorna_vista_interventi_espletati()
        )
        self.combo_ritenzione.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self.combo_ritenzione.set("1 Anno")

        self.lbl_cerca_cli_esp = ctk.CTkLabel(self.form_espletati, text="🔍 Nome/Cognome:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cerca_cli_esp.grid(row=0, column=2, padx=8, pady=12, sticky="w")
        self.entry_filtro_cli = ctk.CTkEntry(self.form_espletati, placeholder_text="Anche poche lettere (es. ros mar)...", height=34)
        self.entry_filtro_cli.grid(row=0, column=3, padx=8, pady=12, sticky="ew")
        self.entry_filtro_cli.bind("<KeyRelease>", lambda e: self.aggiorna_vista_interventi_espletati())

        self.lbl_cerca_data_esp = ctk.CTkLabel(self.form_espletati, text="📅 Data:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cerca_data_esp.grid(row=0, column=4, padx=8, pady=12, sticky="w")
        self.entry_filtro_data = ctk.CTkEntry(self.form_espletati, placeholder_text="Es. 13 Nov o 2026...", height=34)
        self.entry_filtro_data.grid(row=0, column=5, padx=8, pady=12, sticky="ew")
        self.entry_filtro_data.bind("<KeyRelease>", lambda e: self.aggiorna_vista_interventi_espletati())

        self.btn_reset_esp = ctk.CTkButton(
            self.form_espletati, text="🔄 Reset", width=80, height=34, font=ctk.CTkFont(weight="bold"),
            command=self.reset_filtri_espletati
        )
        self.btn_reset_esp.grid(row=0, column=6, padx=10, pady=12)

        self.scroll_espletati = ctk.CTkScrollableFrame(self.frame_interventi_espletati, corner_radius=16, border_width=2)
        self.scroll_espletati.grid(row=1, column=0, sticky="nsew")

        # --- VISTA TICKET PERMANENTI ---
        self.frame_interventi_permanenti = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_interventi_permanenti.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_interventi_permanenti.grid_remove()
        self.frame_interventi_permanenti.grid_columnconfigure(0, weight=1)
        self.frame_interventi_permanenti.grid_rowconfigure(1, weight=1)

        self.form_permanenti = ctk.CTkFrame(self.frame_interventi_permanenti, corner_radius=16, border_width=2)
        self.form_permanenti.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.form_permanenti.grid_columnconfigure((1, 3), weight=1)

        self.lbl_cerca_cli_perm = ctk.CTkLabel(self.form_permanenti, text="🔍 Cerca Nome/Cognome:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cerca_cli_perm.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.entry_filtro_perm_cli = ctk.CTkEntry(self.form_permanenti, placeholder_text="Scrivi nome o cognome anche parziale...", height=34)
        self.entry_filtro_perm_cli.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        self.entry_filtro_perm_cli.bind("<KeyRelease>", lambda e: self.aggiorna_vista_interventi_permanenti())

        self.lbl_cerca_data_perm = ctk.CTkLabel(self.form_permanenti, text="📅 Cerca per Data:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cerca_data_perm.grid(row=0, column=2, padx=15, pady=12, sticky="w")
        self.entry_filtro_perm_data = ctk.CTkEntry(self.form_permanenti, placeholder_text="Es. 13 Nov o 2026...", height=34)
        self.entry_filtro_perm_data.grid(row=0, column=3, padx=10, pady=12, sticky="ew")
        self.entry_filtro_perm_data.bind("<KeyRelease>", lambda e: self.aggiorna_vista_interventi_permanenti())

        self.btn_reset_perm = ctk.CTkButton(
            self.form_permanenti, text="🔄 Reset", width=85, height=34, font=ctk.CTkFont(weight="bold"),
            command=self.reset_filtri_permanenti
        )
        self.btn_reset_perm.grid(row=0, column=4, padx=15, pady=12)

        self.scroll_permanenti = ctk.CTkScrollableFrame(self.frame_interventi_permanenti, corner_radius=16, border_width=2)
        self.scroll_permanenti.grid(row=1, column=0, sticky="nsew")

        # =========================================================================
        # 2. AREA COLLABORATORI & MANSIONI
        # =========================================================================
        self.frame_nuovo_collab = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_nuovo_collab.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_nuovo_collab.grid_columnconfigure(0, weight=1)
        self.frame_nuovo_collab.grid_rowconfigure(1, weight=1)
        self.frame_nuovo_collab.grid_remove()

        self.form_registra_collab = ctk.CTkFrame(self.frame_nuovo_collab, corner_radius=16, border_width=2)
        self.form_registra_collab.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.form_registra_collab.grid_columnconfigure(1, weight=1)

        self.lbl_col_n = ctk.CTkLabel(self.form_registra_collab, text="Nome:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_col_n.grid(row=0, column=0, padx=20, pady=12, sticky="w")
        self.entry_collab_nome = ctk.CTkEntry(self.form_registra_collab, placeholder_text="Luca", height=36)
        self.entry_collab_nome.grid(row=0, column=1, padx=20, pady=12, sticky="ew")

        self.lbl_col_c = ctk.CTkLabel(self.form_registra_collab, text="Cognome:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_col_c.grid(row=1, column=0, padx=20, pady=12, sticky="w")
        self.entry_collab_cognome = ctk.CTkEntry(self.form_registra_collab, placeholder_text="Bianchi", height=36)
        self.entry_collab_cognome.grid(row=1, column=1, padx=20, pady=12, sticky="ew")

        self.lbl_col_t = ctk.CTkLabel(self.form_registra_collab, text="Tel Collaboratore:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_col_t.grid(row=2, column=0, padx=20, pady=12, sticky="w")
        self.entry_collab_tel = ctk.CTkEntry(self.form_registra_collab, placeholder_text="333-0000000", height=36)
        self.entry_collab_tel.grid(row=2, column=1, padx=20, pady=12, sticky="ew")

        self.lbl_col_m = ctk.CTkLabel(self.form_registra_collab, text="Mansione / Professione:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_col_m.grid(row=3, column=0, padx=20, pady=12, sticky="w")
        self.combo_mansione_collab = ctk.CTkComboBox(self.form_registra_collab, values=self.carica_lista_professioni(), height=36)
        self.combo_mansione_collab.grid(row=3, column=1, padx=20, pady=12, sticky="ew")

        self.btn_salva_collab = ctk.CTkButton(
            self.form_registra_collab, text="➕ Registra Collaboratore", font=ctk.CTkFont(size=14, weight="bold"),
            border_width=2, height=42, corner_radius=10, command=self.aggiungi_collaboratore
        )
        self.btn_salva_collab.grid(row=4, column=1, padx=20, pady=20, sticky="e")

        self.info_collab_box = ctk.CTkTextbox(self.frame_nuovo_collab, corner_radius=16, border_width=2)
        self.info_collab_box.grid(row=1, column=0, sticky="nsew")

        # --- VISTA GESTIONE COLLABORATORI ---
        self.frame_gestione_collaboratori = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_gestione_collaboratori.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_gestione_collaboratori.grid_columnconfigure((0, 1), weight=1)
        self.frame_gestione_collaboratori.grid_rowconfigure(1, weight=1)
        self.frame_gestione_collaboratori.grid_remove()

        self.form_mod_collab = ctk.CTkFrame(self.frame_gestione_collaboratori, corner_radius=16, border_width=2)
        self.form_mod_collab.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.form_mod_collab.grid_columnconfigure((1, 3), weight=1)

        self.lbl_gcol_sel = ctk.CTkLabel(self.form_mod_collab, text="Seleziona Collaboratore:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcol_sel.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.combo_mod_collab = ctk.CTkComboBox(self.form_mod_collab, values=self.carica_lista_collaboratori(), height=35, command=self.carica_dati_collaboratore_per_modifica)
        self.combo_mod_collab.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        self.lbl_gcol_man = ctk.CTkLabel(self.form_mod_collab, text="Mansione:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcol_man.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.combo_mod_collab_mansione = ctk.CTkComboBox(self.form_mod_collab, values=self.carica_lista_professioni(), height=35)
        self.combo_mod_collab_mansione.grid(row=0, column=3, padx=15, pady=10, sticky="ew")

        self.lbl_gcol_n = ctk.CTkLabel(self.form_mod_collab, text="Nuovo Nome:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcol_n.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_mod_collab_nome = ctk.CTkEntry(self.form_mod_collab, height=35)
        self.entry_mod_collab_nome.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        self.lbl_gcol_c = ctk.CTkLabel(self.form_mod_collab, text="Nuovo Cognome:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcol_c.grid(row=1, column=2, padx=15, pady=10, sticky="w")
        self.entry_mod_collab_cognome = ctk.CTkEntry(self.form_mod_collab, height=35)
        self.entry_mod_collab_cognome.grid(row=1, column=3, padx=15, pady=10, sticky="ew")

        self.lbl_gcol_t = ctk.CTkLabel(self.form_mod_collab, text="Nuovo Tel:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcol_t.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.entry_mod_collab_tel = ctk.CTkEntry(self.form_mod_collab, height=35)
        self.entry_mod_collab_tel.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        self.btn_salva_mod_collab = ctk.CTkButton(self.form_mod_collab, text="💾 Salva Modifiche", font=ctk.CTkFont(weight="bold"), border_width=1, height=35, command=self.salva_modifiche_collaboratore)
        self.btn_salva_mod_collab.grid(row=2, column=2, padx=15, pady=10, sticky="ew")
        self.btn_elimina_collab = ctk.CTkButton(self.form_mod_collab, text="🗑️ Elimina Profilo", font=ctk.CTkFont(weight="bold"), fg_color="#dc2626", hover_color="#b91c1c", border_width=1, border_color="#f87171", text_color="#ffffff", height=35, command=self.elimina_collaboratore)
        self.btn_elimina_collab.grid(row=2, column=3, padx=15, pady=10, sticky="ew")

        self.lista_collaboratori_box = ctk.CTkTextbox(self.frame_gestione_collaboratori, width=350, corner_radius=16, border_width=2)
        self.lista_collaboratori_box.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.scheda_collaboratore_box = ctk.CTkTextbox(self.frame_gestione_collaboratori, width=450, corner_radius=16, border_width=2)
        self.scheda_collaboratore_box.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        # --- VISTA MANSIONI ---
        self.frame_mansioni = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_mansioni.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_mansioni.grid_columnconfigure(0, weight=1)
        self.frame_mansioni.grid_rowconfigure(1, weight=1)
        self.frame_mansioni.grid_remove()

        self.form_mansioni = ctk.CTkFrame(self.frame_mansioni, corner_radius=16, border_width=2)
        self.form_mansioni.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.form_mansioni.grid_columnconfigure(1, weight=1)

        self.lbl_nuova_mans = ctk.CTkLabel(self.form_mansioni, text="Nuova Mansione:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_nuova_mans.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.entry_nuova_prof = ctk.CTkEntry(self.form_mansioni, placeholder_text="Es. Elettricista, Idraulico...", height=38)
        self.entry_nuova_prof.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        self.btn_aggiungi_prof = ctk.CTkButton(self.form_mansioni, text="➕ Aggiungi", font=ctk.CTkFont(weight="bold"), border_width=1, height=38, command=self.aggiungi_professione)
        self.btn_aggiungi_prof.grid(row=0, column=2, padx=20, pady=15)

        self.lista_mansioni_box = ctk.CTkTextbox(self.frame_mansioni, corner_radius=16, border_width=2)
        self.lista_mansioni_box.grid(row=1, column=0, sticky="nsew")

        # =========================================================================
        # 3. AREA CLIENTI, CALENDARIO & REPORT
        # =========================================================================
        self.frame_clienti = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_clienti.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_clienti.grid_columnconfigure((0, 1), weight=1)
        self.frame_clienti.grid_rowconfigure(1, weight=1)
        self.frame_clienti.grid_remove()

        self.form_registra_cliente = ctk.CTkFrame(self.frame_clienti, corner_radius=16, border_width=2)
        self.form_registra_cliente.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.form_registra_cliente.grid_columnconfigure((1, 3), weight=1)

        self.lbl_cli_n = ctk.CTkLabel(self.form_registra_cliente, text="Nome e Cognome Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cli_n.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.entry_cli_nome = ctk.CTkEntry(self.form_registra_cliente, placeholder_text="Mario Rossi", height=38)
        self.entry_cli_nome.grid(row=0, column=1, padx=15, pady=12, sticky="ew")

        self.lbl_cli_t = ctk.CTkLabel(self.form_registra_cliente, text="Tel Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cli_t.grid(row=0, column=2, padx=15, pady=12, sticky="w")
        self.entry_cli_tel = ctk.CTkEntry(self.form_registra_cliente, placeholder_text="+39 333...", height=38)
        self.entry_cli_tel.grid(row=0, column=3, padx=15, pady=12, sticky="ew")

        self.lbl_cli_i = ctk.CTkLabel(self.form_registra_cliente, text="Indirizzo Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_cli_i.grid(row=1, column=0, padx=15, pady=12, sticky="w")
        self.entry_cli_indirizzo = ctk.CTkEntry(self.form_registra_cliente, placeholder_text="Via Roma 10, Città", height=38)
        self.entry_cli_indirizzo.grid(row=1, column=1, columnspan=2, padx=15, pady=12, sticky="ew")

        self.btn_salva_cli = ctk.CTkButton(self.form_registra_cliente, text="➕ Registra Cliente", font=ctk.CTkFont(weight="bold"), border_width=2, height=38, command=self.aggiungi_cliente)
        self.btn_salva_cli.grid(row=1, column=3, padx=15, pady=12, sticky="e")

        self.lista_clienti_box = ctk.CTkTextbox(self.frame_clienti, width=350, corner_radius=16, border_width=2)
        self.lista_clienti_box.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.scheda_cliente_box = ctk.CTkTextbox(self.frame_clienti, width=450, corner_radius=16, border_width=2)
        self.scheda_cliente_box.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        # --- VISTA GESTIONE CLIENTI ---
        self.frame_gestione_clienti = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_gestione_clienti.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_gestione_clienti.grid_columnconfigure((0, 1), weight=1)
        self.frame_gestione_clienti.grid_rowconfigure(1, weight=1)
        self.frame_gestione_clienti.grid_remove()

        self.form_modifica_cliente = ctk.CTkFrame(self.frame_gestione_clienti, corner_radius=16, border_width=2)
        self.form_modifica_cliente.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.form_modifica_cliente.grid_columnconfigure((1, 3), weight=1)

        self.lbl_gcli_cerca = ctk.CTkLabel(self.form_modifica_cliente, text="Cerca Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcli_cerca.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.entry_cerca_gestione_cliente = ctk.CTkEntry(self.form_modifica_cliente, placeholder_text="Nome o cognome...", height=35)
        self.entry_cerca_gestione_cliente.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        self.entry_cerca_gestione_cliente.bind("<KeyRelease>", self.filtra_clienti_gestione)

        self.lbl_gcli_sel = ctk.CTkLabel(self.form_modifica_cliente, text="Seleziona:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcli_sel.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        self.combo_mod_cliente = ctk.CTkComboBox(self.form_modifica_cliente, values=self.carica_lista_clienti(), height=35, command=self.carica_dati_cliente_per_modifica)
        self.combo_mod_cliente.grid(row=0, column=3, padx=15, pady=10, sticky="ew")

        self.lbl_gcli_n = ctk.CTkLabel(self.form_modifica_cliente, text="Nuovo Nome:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcli_n.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.entry_mod_nome = ctk.CTkEntry(self.form_modifica_cliente, height=35)
        self.entry_mod_nome.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        self.lbl_gcli_t = ctk.CTkLabel(self.form_modifica_cliente, text="Nuovo Tel:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcli_t.grid(row=1, column=2, padx=15, pady=10, sticky="w")
        self.entry_mod_tel = ctk.CTkEntry(self.form_modifica_cliente, height=35)
        self.entry_mod_tel.grid(row=1, column=3, padx=15, pady=10, sticky="ew")

        self.lbl_gcli_i = ctk.CTkLabel(self.form_modifica_cliente, text="Nuovo Indirizzo:", font=ctk.CTkFont(weight="bold"))
        self.lbl_gcli_i.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.entry_mod_indirizzo = ctk.CTkEntry(self.form_modifica_cliente, height=35)
        self.entry_mod_indirizzo.grid(row=2, column=1, columnspan=2, padx=15, pady=10, sticky="ew")

        self.btn_salva_mod_cliente = ctk.CTkButton(self.form_modifica_cliente, text="💾 Salva Modifiche", font=ctk.CTkFont(weight="bold"), border_width=1, height=35, command=self.salva_modifiche_cliente)
        self.btn_salva_mod_cliente.grid(row=2, column=3, padx=15, pady=6, sticky="ew")

        self.btn_elimina_cliente = ctk.CTkButton(self.form_modifica_cliente, text="🗑️ Elimina Profilo", font=ctk.CTkFont(weight="bold"), fg_color="#dc2626", hover_color="#b91c1c", border_width=1, border_color="#f87171", text_color="#ffffff", height=35, command=self.elimina_cliente)
        self.btn_elimina_cliente.grid(row=3, column=3, padx=15, pady=(4, 12), sticky="ew")

        self.lista_gestione_clienti_box = ctk.CTkTextbox(self.frame_gestione_clienti, width=350, corner_radius=16, border_width=2)
        self.lista_gestione_clienti_box.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.scheda_gestione_clienti_box = ctk.CTkTextbox(self.frame_gestione_clienti, width=450, corner_radius=16, border_width=2)
        self.scheda_gestione_clienti_box.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        # --- VISTA CALENDARIO ---
        self.frame_calendario = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_calendario.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_calendario.grid_remove()
        self.frame_calendario.grid_columnconfigure(0, weight=1)
        self.frame_calendario.grid_rowconfigure(1, weight=1)

        self.form_cal = ctk.CTkFrame(self.frame_calendario, corner_radius=16, border_width=2, height=55)
        self.form_cal.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.lbl_cal_header = ctk.CTkLabel(self.form_cal, text="📅 Agenda e Calendario Attività (Ordine Cronologico)", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_cal_header.pack(padx=20, pady=12, side="left")

        self.scroll_calendario = ctk.CTkScrollableFrame(self.frame_calendario, corner_radius=16, border_width=2)
        self.scroll_calendario.grid(row=1, column=0, sticky="nsew")

        # --- VISTA REPORT CLIENTE (STORICO COMPLETO + ESPORTAZIONE TXT E PDF) ---
        self.frame_report = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.frame_report.grid(row=2, column=0, sticky="nsew", rowspan=2, padx=30, pady=(0, 25))
        self.frame_report.grid_remove()
        self.frame_report.grid_columnconfigure(0, weight=1)
        self.frame_report.grid_rowconfigure(1, weight=1)

        self.form_report = ctk.CTkFrame(self.frame_report, corner_radius=16, border_width=2)
        self.form_report.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.form_report.grid_columnconfigure((1, 3), weight=1)

        self.lbl_rep_cerca = ctk.CTkLabel(self.form_report, text="🔍 Filtra Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_rep_cerca.grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.entry_filtro_report_cli = ctk.CTkEntry(self.form_report, placeholder_text="Scrivi nome o cognome...", height=35)
        self.entry_filtro_report_cli.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        self.entry_filtro_report_cli.bind("<KeyRelease>", self.filtra_clienti_report)

        self.lbl_rep_sel = ctk.CTkLabel(self.form_report, text="👤 Seleziona Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_rep_sel.grid(row=0, column=2, padx=15, pady=12, sticky="w")
        self.combo_report_cliente = ctk.CTkComboBox(
            self.form_report, values=self.carica_lista_clienti_con_storico(), height=35,
            command=lambda c: self.aggiorna_anteprima_report()
        )
        self.combo_report_cliente.grid(row=0, column=3, padx=10, pady=12, sticky="ew")

        self.lbl_rep_stato = ctk.CTkLabel(self.form_report, text="📂 Stato Ticket:", font=ctk.CTkFont(weight="bold"))
        self.lbl_rep_stato.grid(row=1, column=0, padx=15, pady=12, sticky="w")
        self.combo_report_stato = ctk.CTkComboBox(
            self.form_report, values=["Tutti gli stati", "Aperto", "Espletato", "Permanente"], height=35,
            command=lambda s: self.aggiorna_anteprima_report()
        )
        self.combo_report_stato.grid(row=1, column=1, padx=10, pady=12, sticky="ew")
        self.combo_report_stato.set("Tutti gli stati")

        self.btn_rep_box = ctk.CTkFrame(self.form_report, fg_color="transparent")
        self.btn_rep_box.grid(row=1, column=2, columnspan=2, padx=15, pady=12, sticky="e")

        self.btn_esporta_rep_txt = ctk.CTkButton(
            self.btn_rep_box, text="📄 Esporta Report TXT", font=ctk.CTkFont(size=13, weight="bold"),
            border_width=2, height=38, width=190, corner_radius=10, command=self.esporta_report_cliente_txt
        )
        self.btn_esporta_rep_txt.pack(side="left", padx=8)

        self.btn_esporta_rep_pdf = ctk.CTkButton(
            self.btn_rep_box, text="📑 Esporta Report PDF", font=ctk.CTkFont(size=13, weight="bold"),
            border_width=2, height=38, width=190, corner_radius=10, command=self.esporta_report_cliente_pdf
        )
        self.btn_esporta_rep_pdf.pack(side="left", padx=8)

        self.report_box = ctk.CTkTextbox(self.frame_report, corner_radius=16, border_width=2, font=ctk.CTkFont(size=13))
        self.report_box.grid(row=1, column=0, sticky="nsew")

        # Applica il tema scelto a tutti i componenti e carica i dati
        self.applica_tema_corrente()
        self.aggiorna_cliente_iniziale()
        self.aggiorna_telefono_iniziale()
        self.aggiorna_collaboratore_gestione_iniziale()

        # All'avvio: verifica silenziosa stato abbonamento mensile online + aggiornamenti automatici
        self.after(1500, self.verifica_abbonamento_mensile_online)
        self.after(3000, lambda: self.avvia_controllo_aggiornamenti(manuale=False))

    # =========================================================================
    # MOTORE TEXTURE FIBRA DI CARBONIO & GESTIONE SKIN CHIARA / SCURA
    # =========================================================================
    def _disegna_trama_carbonio(self, event=None):
        """Disegna una elegante trama diagonale in fibra di carbonio sullo sfondo."""
        self.bg_canvas.delete("carbon_line")
        w = self.main_content.winfo_width()
        h = self.main_content.winfo_height()
        if w < 10 or h < 10:
            return
        self.bg_canvas.configure(bg=self.T["CARBON_BG"])
        col_linea = self.T["CARBON_LINE"]
        passo = 12
        for i in range(-h, w + h, passo):
            self.bg_canvas.create_line(i, 0, i + h, h, fill=col_linea, width=2, tags="carbon_line")

    def cambia_tema_interfaccia(self, scelta):
        self.tema_nome = scelta
        self._set_config("skin_tema", scelta)
        self.T = LIGHT_THEME if scelta.startswith("Chiaro") else DARK_THEME
        ctk.set_appearance_mode(self.T["mode"])
        self.applica_tema_corrente()

    def applica_tema_corrente(self):
        T = self.T
        self.configure(fg_color=T["CARBON_BG"])
        self.main_content.configure(fg_color=T["CARBON_BG"])
        self._disegna_trama_carbonio()

        self.sidebar_frame.configure(fg_color=T["CARBON_SIDEBAR"], border_color=T["BORDER_SUB"])
        self.top_bar.configure(fg_color=T["GLASS_PANEL"], border_color=T["BORDER_SUB"])
        self.lbl_barra_titolo.configure(text_color=T["TEXT_MAIN"])
        self.lbl_tema_title.configure(text_color=T["TEXT_MUTED"])
        self.lbl_lingua_title.configure(text_color=T["TEXT_MUTED"])

        self.combo_tema.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_1"], button_color=T["ACCENT_1_DARK"], dropdown_fg_color=T["GLASS_PANEL"], dropdown_text_color=T["TEXT_MAIN"])
        self.combo_lingua.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_1"], button_color=T["ACCENT_1_DARK"], dropdown_fg_color=T["GLASS_PANEL"], dropdown_text_color=T["TEXT_MAIN"])
        self.btn_aggiorna_app.configure(fg_color=T["GLASS_CARD"], hover_color=T["BORDER_SUB"], border_color=T["ACCENT_1"], text_color=T["ACCENT_1"])

        self.config_menu = {
            "nuovo":       (self.btn_nuovo_int,        T["MENU_1_BG"],  T["ACCENT_1"],        "#ffffff"),
            "aperti":      (self.btn_int_aperti,       T["MENU_2_BG"],  T["ACCENT_1_BORDER"], "#ffffff"),
            "espletati":   (self.btn_int_espletati,    T["MENU_3_BG"],  T["ACCENT_1_BORDER"], "#ffffff"),
            "permanenti":  (self.btn_int_permanenti,   T["MENU_4_BG"],  T["ACCENT_1"],        "#ffffff"),
            "collab":      (self.btn_collaboratori,    T["MENU_5_BG"],  T["ACCENT_2"],        "#ffffff"),
            "gest_collab": (self.btn_gestione_collab,  T["MENU_6_BG"],  T["ACCENT_2_BORDER"], "#ffffff"),
            "mansioni":    (self.btn_mansioni,         T["MENU_7_BG"],  T["ACCENT_2_BORDER"], "#ffffff"),
            "clienti":     (self.btn_clienti,          T["MENU_8_BG"],  T["ACCENT_3"],        T["MENU_TEXT_3"]),
            "gest_cli":    (self.btn_gestione_clienti, T["MENU_9_BG"],  T["ACCENT_3_BORDER"], T["MENU_TEXT_3"]),
            "calendario":  (self.btn_calendario,       T["MENU_10_BG"], T["ACCENT_3_BORDER"], T["MENU_TEXT_3"]),
            "report":      (self.btn_report,           T["MENU_11_BG"], T["ACCENT_3"],        T["MENU_TEXT_3"])
        }
        for chiave, (btn, bg_col, border_col, txt_col) in self.config_menu.items():
            hover_c = T["ACCENT_1_HOVER"] if chiave in ["nuovo", "aperti", "espletati", "permanenti"] else T["ACCENT_2_HOVER"] if chiave in ["collab", "gest_collab", "mansioni"] else T["ACCENT_3_HOVER"]
            btn.configure(fg_color=bg_col, hover_color=hover_c, border_color=border_col, text_color=txt_col)
        self.evidenzia_menu_attivo(self.menu_attivo_corrente)

        # Pannelli Principali
        self.form_ticket.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1"])
        self.lbl_cliente.configure(text_color=T["ACCENT_1"])
        for lbl in [self.lbl_tel_cliente, self.lbl_data, self.lbl_orario, self.lbl_indirizzo, self.lbl_guasto, self.lbl_note_ticket_ap, self.lbl_mem_esp]:
            lbl.configure(text_color=T["TEXT_SUB"])
        self.lbl_collaboratore.configure(text_color=T["ACCENT_2"])
        self.lbl_tel_collab.configure(text_color=T["TEXT_COLLAB"])

        for entry in [self.entry_filtro_nuovo_cli, self.entry_tel_cliente, self.entry_indirizzo]:
            entry.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_1_BORDER"])
        self.entry_tel_collaboratore.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2_BORDER"])

        for cb in [self.combo_clienti, self.combo_giorno, self.combo_mese, self.combo_anno, self.combo_ora, self.combo_minuti, self.combo_interventi_aperti, self.combo_ritenzione]:
            cb.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_1"], button_color=T["ACCENT_1_DARK"], dropdown_fg_color=T["GLASS_PANEL"], dropdown_text_color=T["TEXT_MAIN"])
        self.combo_collaboratori.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2"], button_color=T["ACCENT_2_DARK"], dropdown_fg_color=T["GLASS_PANEL"], dropdown_text_color=T["TEXT_MAIN"])

        self.text_nuovo_guasto.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_1_BORDER"])
        self.btn_salva_ticket.configure(fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], border_color=T["ACCENT_1"], text_color="#ffffff")
        self.lista_box.configure(fg_color=T["GLASS_PANEL"], text_color=T["BOX_TEXT_1"], border_color=T["ACCENT_1_BORDER"])

        # Aperti, Espletati, Permanenti
        self.form_aggiorna_int.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1"])
        self.lbl_sel_ticket_ap.configure(text_color=T["ACCENT_1"])
        self.text_aggiorna_tipo.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_1_BORDER"])
        self.btn_aggiorna_tipo_int.configure(fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_color=T["ACCENT_2"], text_color="#ffffff")
        self.scroll_aperti.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1_BORDER"])

        self.form_espletati.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1"])
        self.lbl_cerca_cli_esp.configure(text_color=T["ACCENT_3"])
        self.lbl_cerca_data_esp.configure(text_color=T["ACCENT_2"])
        self.entry_filtro_cli.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_3_BORDER"])
        self.entry_filtro_data.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2_BORDER"])
        self.btn_reset_esp.configure(fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], text_color="#ffffff")
        self.scroll_espletati.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1_BORDER"])

        self.form_permanenti.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1"])
        self.lbl_cerca_cli_perm.configure(text_color=T["ACCENT_3"])
        self.lbl_cerca_data_perm.configure(text_color=T["ACCENT_2"])
        self.entry_filtro_perm_cli.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_3_BORDER"])
        self.entry_filtro_perm_data.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2_BORDER"])
        self.btn_reset_perm.configure(fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], text_color="#ffffff")
        self.scroll_permanenti.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_1"])

        # Collaboratori & Mansioni
        self.form_registra_collab.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_2"])
        for lbl in [self.lbl_col_n, self.lbl_col_c, self.lbl_gcol_sel, self.lbl_nuova_mans]:
            lbl.configure(text_color=T["ACCENT_2"])
        for lbl in [self.lbl_col_t, self.lbl_col_m, self.lbl_gcol_man, self.lbl_gcol_n, self.lbl_gcol_c, self.lbl_gcol_t]:
            lbl.configure(text_color=T["TEXT_COLLAB"])
        for ent in [self.entry_collab_nome, self.entry_collab_cognome, self.entry_collab_tel, self.entry_mod_collab_nome, self.entry_mod_collab_cognome, self.entry_mod_collab_tel, self.entry_nuova_prof]:
            ent.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2_BORDER"])
        for cb in [self.combo_mansione_collab, self.combo_mod_collab, self.combo_mod_collab_mansione]:
            cb.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2"], button_color=T["ACCENT_2_DARK"], dropdown_fg_color=T["GLASS_PANEL"], dropdown_text_color=T["TEXT_MAIN"])
        for btn in [self.btn_salva_collab, self.btn_salva_mod_collab, self.btn_aggiungi_prof]:
            btn.configure(fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_color=T["ACCENT_2"], text_color="#ffffff")
        for box in [self.info_collab_box, self.lista_collaboratori_box, self.scheda_collaboratore_box, self.lista_mansioni_box]:
            box.configure(fg_color=T["GLASS_PANEL"], text_color=T["BOX_TEXT_2"], border_color=T["ACCENT_2_BORDER"])
        self.form_mod_collab.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_2"])
        self.form_mansioni.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_2"])

        # Clienti, Calendario & Report
        self.form_registra_cliente.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_3"])
        self.form_modifica_cliente.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_3"])
        self.form_report.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_3"])
        for lbl in [self.lbl_cli_n, self.lbl_cli_t, self.lbl_gcli_cerca, self.lbl_cal_header, self.lbl_rep_cerca, self.lbl_rep_sel]:
            lbl.configure(text_color=T["ACCENT_3"])
        for lbl in [self.lbl_cli_i, self.lbl_gcli_sel, self.lbl_gcli_n, self.lbl_gcli_t, self.lbl_gcli_i, self.lbl_rep_stato]:
            lbl.configure(text_color=T["TEXT_CLIENT"])
        for ent in [self.entry_cli_nome, self.entry_cli_tel, self.entry_cli_indirizzo, self.entry_cerca_gestione_cliente, self.entry_mod_nome, self.entry_mod_tel, self.entry_mod_indirizzo, self.entry_filtro_report_cli]:
            ent.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_3_BORDER"])
        for cb in [self.combo_mod_cliente, self.combo_report_cliente, self.combo_report_stato]:
            cb.configure(fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_3"], button_color=T["ACCENT_3_DARK"], dropdown_fg_color=T["GLASS_PANEL"], dropdown_text_color=T["TEXT_MAIN"])
        for btn in [self.btn_salva_cli, self.btn_salva_mod_cliente]:
            btn.configure(fg_color=T["ACCENT_3_DARK"], hover_color=T["ACCENT_3_HOVER"], border_color=T["ACCENT_3"], text_color="#ffffff")
        self.btn_esporta_rep_txt.configure(fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_color=T["ACCENT_2"], text_color="#ffffff")
        self.btn_esporta_rep_pdf.configure(fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], border_color=T["ACCENT_1"], text_color="#ffffff")
        for box in [self.lista_clienti_box, self.scheda_cliente_box, self.lista_gestione_clienti_box, self.scheda_gestione_clienti_box, self.report_box]:
            box.configure(fg_color=T["GLASS_PANEL"], text_color=T["BOX_TEXT_3"], border_color=T["ACCENT_3_BORDER"])
        self.form_cal.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_3"])
        self.scroll_calendario.configure(fg_color=T["GLASS_PANEL"], border_color=T["ACCENT_3_BORDER"])

        # Ricarica tutte le viste dinamiche con i nuovi colori
        self.aggiorna_badge_licenza()
        self.aggiorna_lista_tickets()
        self.aggiorna_vista_collaboratori()
        self.aggiorna_vista_gestione_collaboratori()
        self.aggiorna_vista_clienti()
        self.aggiorna_vista_gestione_clienti()
        self.aggiorna_vista_mansioni()
        self.aggiorna_vista_interventi_aperti()
        self.aggiorna_vista_interventi_espletati()
        self.aggiorna_vista_interventi_permanenti()
        self.aggiorna_vista_calendario()
        self.aggiorna_anteprima_report()

    # =========================================================================
    # VERIFICA ABBONAMENTO MENSILE AUTOMATICO (GUMROAD API + MASTER KEY)
    # =========================================================================
    def _get_config(self, chiave, default=""):
        self.cursor.execute("SELECT valore FROM config_app WHERE chiave = ?", (chiave,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def _set_config(self, chiave, valore):
        self.cursor.execute("INSERT OR REPLACE INTO config_app (chiave, valore) VALUES (?, ?)", (chiave, str(valore)))
        self.conn.commit()

    def verifica_stato_licenza_locale(self):
        key_salvata = self._get_config("licenza_key")
        tipo_lic = self._get_config("licenza_tipo")
        ultimo_check = float(self._get_config("ultimo_check_pagamento", "0") or 0)
        self.scadenza_abbonamento_str = self._get_config("scadenza_abbonamento", "")

        if not key_salvata:
            self.is_pro = False
            return

        if tipo_lic == "MASTER" and key_salvata == calcola_licenza_master(self.machine_id):
            if self.scadenza_abbonamento_str:
                try:
                    dt_scad = datetime.strptime(self.scadenza_abbonamento_str, "%Y-%m-%d")
                    if datetime.now() > dt_scad:
                        self.is_pro = False
                        return
                except Exception:
                    pass
            self.is_pro = True
            return

        secondi_passati = time.time() - ultimo_check
        self.is_pro = secondi_passati <= (GIORNI_VALIDITA_MESE * 86400)

    def verifica_abbonamento_mensile_online(self):
        key_salvata = self._get_config("licenza_key")
        if not key_salvata:
            return
        threading.Thread(
            target=self._thread_controllo_pagamento,
            args=(key_salvata, False, None),
            daemon=True
        ).start()

    def _thread_controllo_pagamento(self, license_key, mostra_popup=False, finestra_da_chiudere=None):
        codice = license_key.strip()

        # 1. VERIFICA TRAMITE API UFFICIALI GUMROAD CON PRODUCT ID
        if GUMROAD_PRODUCT_ID and not codice.upper().startswith("PRO-"):
            try:
                dati_post = urllib.parse.urlencode({
                    "product_id": GUMROAD_PRODUCT_ID,
                    "license_key": codice,
                    "increment_uses_count": "false"
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.gumroad.com/v2/licenses/verify",
                    data=dati_post,
                    headers={"User-Agent": "TeamOrganizerPRO-LicenseChecker"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    risposta = json.loads(resp.read().decode("utf-8"))

                if risposta.get("success"):
                    acquisto = risposta.get("purchase", {})
                    abbonamento = risposta.get("subscription", {})

                    is_scaduto = (
                        acquisto.get("refunded") or
                        acquisto.get("disputed") or
                        acquisto.get("chargebacked") or
                        acquisto.get("subscription_ended_at") or
                        acquisto.get("subscription_failed_at") or
                        abbonamento.get("ended") or
                        abbonamento.get("failed")
                    )

                    if is_scaduto:
                        self.after(0, lambda: self._revoca_abbonamento_scaduto(
                            "Il tuo abbonamento Gumroad risulta scaduto o non rinnovato.\nRinnova il pagamento per riattivare la Versione PRO!"
                        ))
                        return
                    else:
                        self.after(0, lambda: self._conferma_rinnovo_mensile(
                            codice, "SUBSCRIPTION", "Abbonamento Gumroad Attivo", mostra_popup, finestra_da_chiudere
                        ))
                        return
                else:
                    if mostra_popup:
                        self.after(0, lambda: messagebox.showerror(
                            "Licenza Non Trovata",
                            "La chiave di licenza Gumroad inserita non risulta valida o esistente."
                        ))
                    return
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    if mostra_popup:
                        self.after(0, lambda: messagebox.showerror(
                            "Licenza Non Valida",
                            "Chiave di licenza non trovata su Gumroad.\nVerifica di aver copiato correttamente il codice ricevuto via email."
                        ))
                    return
                if mostra_popup:
                    self.after(0, lambda err=e: messagebox.showerror("Errore Server Gumroad", f"Errore HTTP durante la verifica:\n{err}"))
                return
            except Exception as e:
                if mostra_popup:
                    self.after(0, lambda err=e: messagebox.showerror("Errore di Rete", f"Impossibile contattare il server Gumroad:\n{err}"))
                return

        # 2. VERIFICA FILE LICENZE GITHUB E CODICE MASTER (KeyGeneratorPRO)
        scadenza_remota = self._controlla_file_licenze_github()
        if scadenza_remota is not None:
            if scadenza_remota == "REVOCATA":
                self.after(0, lambda: self._revoca_abbonamento_scaduto(
                    "Il tuo abbonamento non risulta rinnovato per il periodo corrente."
                ))
                return
            try:
                dt_scad = datetime.strptime(scadenza_remota, "%Y-%m-%d")
                if datetime.now() > dt_scad:
                    self.after(0, lambda: self._revoca_abbonamento_scaduto(
                        f"Il tuo abbonamento è scaduto il {scadenza_remota}.\nEffettua il rinnovo per sbloccare nuovamente la Versione PRO!"
                    ))
                    return
                else:
                    if codice.upper() == calcola_licenza_master(self.machine_id):
                        self.after(0, lambda: self._conferma_rinnovo_mensile(
                            codice.upper(), "MASTER", scadenza_remota, mostra_popup, finestra_da_chiudere
                        ))
                        return
            except Exception:
                pass

        if codice.upper() == calcola_licenza_master(self.machine_id):
            self.after(0, lambda: self._conferma_rinnovo_mensile(
                codice.upper(), "MASTER", self.scadenza_abbonamento_str or "Attivo", mostra_popup, finestra_da_chiudere
            ))
        else:
            if mostra_popup:
                self.after(0, lambda: messagebox.showerror(
                    "Codice Non Valido",
                    "Il codice inserito non è valido per questo PC oppure l'abbonamento non risulta attivo."
                ))

    def _controlla_file_licenze_github(self):
        for repo in [GITHUB_REPO, "team-organizer"]:
            repo_safe = urllib.parse.quote(repo)
            for ramo in ["main", "principale", "master"]:
                url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{repo_safe}/{ramo}/licenze.json?t={int(time.time())}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "TeamOrganizerPRO-LicenseChecker"})
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        dati = json.loads(resp.read().decode("utf-8"))
                    if self.machine_id in dati:
                        return dati[self.machine_id]
                except Exception:
                    pass
        return None

    def _conferma_rinnovo_mensile(self, codice, tipo, info_scadenza, mostra_popup, finestra_da_chiudere=None):
        self._set_config("licenza_key", codice)
        self._set_config("licenza_tipo", tipo)
        self._set_config("ultimo_check_pagamento", str(time.time()))
        self._set_config("scadenza_abbonamento", info_scadenza)
        self.scadenza_abbonamento_str = info_scadenza
        self.is_pro = True
        self.aggiorna_badge_licenza()
        if finestra_da_chiudere is not None:
            try:
                finestra_da_chiudere.destroy()
            except Exception:
                pass
        if mostra_popup:
            self.mostra_notifica("Abbonamento PRO verificato e attivo!")
            messagebox.showinfo(
                "Abbonamento Attivo!",
                "🎉 Pagamento verificato con successo!\nLa tua Versione PRO è attiva e sbloccata."
            )

    def _revoca_abbonamento_scaduto(self, messaggio):
        self.is_pro = False
        self._set_config("ultimo_check_pagamento", "0")
        self.aggiorna_badge_licenza()
        self.mostra_notifica("Abbonamento scaduto!", "#dc2626")
        messagebox.showwarning("Abbonamento Scaduto", messaggio)

    def get_totale_ticket_creati_storico(self):
        val = self._get_config("totale_ticket_creati", "0")
        contatore_storico = int(val) if val.isdigit() else 0
        self.cursor.execute("SELECT COUNT(*) FROM interventi")
        attuali = self.cursor.fetchone()[0]
        totale_reale = max(contatore_storico, attuali)
        if totale_reale != contatore_storico:
            self._set_config("totale_ticket_creati", str(totale_reale))
        return totale_reale

    def incrementa_contatore_ticket_storico(self):
        tot = self.get_totale_ticket_creati_storico() + 1
        self._set_config("totale_ticket_creati", str(tot))
        self.aggiorna_badge_licenza()

    def aggiorna_badge_licenza(self):
        T = self.T
        if self.is_pro:
            extra = f" ({self.scadenza_abbonamento_str})" if self.scadenza_abbonamento_str else ""
            col_pro = "#0284c7" if T["mode"] == "Light" else "#00ff66"
            self.lbl_badge_licenza.configure(text=f"💎 ABBONAMENTO PRO ATTIVO{extra}", text_color=col_pro)
            self.btn_licenza.configure(text="💎  Abbonamento Attivo", fg_color=T["GLASS_CARD"], hover_color=T["BORDER_SUB"], border_color=col_pro, text_color=col_pro)
        else:
            usati = self.get_totale_ticket_creati_storico()
            rimasti = max(0, LIMITE_TICKET_TRIAL - usati)
            colore = T["ACCENT_3"] if rimasti > 1 else "#dc2626"
            self.lbl_badge_licenza.configure(text=f"🔓 TRIAL: {rimasti}/{LIMITE_TICKET_TRIAL} Ticket rimasti", text_color=colore)
            self.btn_licenza.configure(text="⚡  Attiva Abbonamento PRO", fg_color=T["GLASS_CARD"], hover_color=T["BORDER_SUB"], border_color=colore, text_color=colore)

    # =========================================================================
    # SISTEMA DI AGGIORNAMENTO AUTOMATICO "ZERO-VERSIONING" (RILEVAMENTO HASH)
    # =========================================================================
    def _inizializza_hash_versione_locale(self):
        try:
            if not getattr(sys, "frozen", False) and os.path.exists(os.path.abspath(__file__)):
                with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
                    h_locale = normalizza_codice_hash(f.read())
                if h_locale:
                    self._set_config("hash_codice_installato", h_locale)
        except Exception:
            pass

    def _versione_tupla(self, v_str):
        try:
            return tuple(int(x) for x in v_str.strip().split("."))
        except Exception:
            return (0, 0, 0)

    def avvia_controllo_aggiornamenti(self, manuale=False):
        if manuale:
            self.mostra_notifica("Controllo aggiornamenti su GitHub in corso...")
        threading.Thread(target=self._scarica_e_verifica_aggiornamento, args=(manuale,), daemon=True).start()

    def _scarica_e_verifica_aggiornamento(self, manuale):
        repo_candidati = [GITHUB_REPO, "team-organizer"]
        rami_candidati = ["main", "principale", "master"]

        codice_remoto = None
        ultimo_errore = None

        for repo in repo_candidati:
            repo_safe = urllib.parse.quote(repo)
            for ramo in rami_candidati:
                url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{repo_safe}/{ramo}/{GITHUB_FILE}?t={int(time.time())}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "TeamOrganizerPRO-Updater"})
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        codice_remoto = resp.read().decode("utf-8")
                    if codice_remoto:
                        break
                except Exception as e:
                    ultimo_errore = e
            if codice_remoto:
                break

        if not codice_remoto:
            if manuale:
                self.after(0, lambda: messagebox.showerror(
                    "Errore di Connessione",
                    f"Impossibile raggiungere il repository GitHub di {GITHUB_USER}.\n"
                    f"Verifica che il repository sia Pubblico e che il file si chiami '{GITHUB_FILE}'.\n\n"
                    f"Dettaglio: {ultimo_errore}"
                ))
            return

        hash_remoto = normalizza_codice_hash(codice_remoto)
        hash_salvato = self._get_config("hash_codice_installato", "")

        if not hash_salvato:
            self.after(0, lambda: self._set_config("hash_codice_installato", hash_remoto))
            hash_salvato = hash_remoto

        match = re.search(r'VERSIONE_APP\s*=\s*["\']([^"\']+)["\']', codice_remoto)
        versione_remota = match.group(1) if match else VERSIONE_APP

        codice_modificato = (hash_remoto != hash_salvato)
        versione_superiore = (self._versione_tupla(versione_remota) > self._versione_tupla(VERSIONE_APP))

        if codice_modificato or versione_superiore:
            self.after(0, lambda: self._proponi_installazione_aggiornamento(versione_remota, codice_remoto, hash_remoto))
        else:
            if manuale:
                self.after(0, lambda: self.mostra_notifica(
                    "Hai già l'ultima versione disponibile (all'ultimo aggiornamento GitHub)!"
                ))

    def _proponi_installazione_aggiornamento(self, nuova_versione, codice_remoto, hash_remoto):
        risposta = messagebox.askyesno(
            "Nuovo Aggiornamento Disponibile!",
            "È stato rilevato un nuovo aggiornamento del programma su GitHub!\n\n"
            "Tutti i tuoi clienti, ticket e abbonamento sono al sicuro in AppData.\n"
            "Vuoi installare l'aggiornamento adesso?"
        )
        if not risposta:
            return

        self._set_config("hash_codice_installato", hash_remoto)

        if getattr(sys, "frozen", False):
            messagebox.showinfo(
                "Scarica Aggiornamento",
                "Si aprirà ora la pagina ufficiale di GitHub per scaricare la versione aggiornata."
            )
            webbrowser.open(f"https://github.com/{GITHUB_USER}/{urllib.parse.quote(GITHUB_REPO)}")
            return

        try:
            percorso_script = os.path.abspath(__file__)
            percorso_backup = percorso_script + ".bak"
            shutil.copy2(percorso_script, percorso_backup)

            with open(percorso_script, "w", encoding="utf-8") as f:
                f.write(codice_remoto)

            messagebox.showinfo(
                "Aggiornamento Completato!",
                "Il programma è stato aggiornato con successo all'ultima versione disponibile su GitHub!\n\n"
                "Ora verrà riavviato automaticamente."
            )
            if hasattr(self, "conn") and self.conn:
                self.conn.commit()
                self.conn.close()

            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            messagebox.showerror("Errore Aggiornamento", f"Non è stato possibile sovrascrivere il file:\n{e}")

    # =========================================================================
    # INIZIALIZZAZIONE DATABASE
    # =========================================================================
    def init_db(self):
        self.db_path = get_percorso_database()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_app (
                chiave TEXT PRIMARY KEY,
                valore TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE,
                telefono TEXT,
                indirizzo TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS collaboratori (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                cognome TEXT,
                telefono TEXT,
                specializzazione TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS professioni (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS interventi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                telefono TEXT,
                data_ora TEXT,
                data_iso TEXT,
                collaboratore TEXT,
                indirizzo TEXT,
                guasto TEXT,
                intervento TEXT,
                stato TEXT,
                chiusura_timestamp REAL
            )
        """)

        self.cursor.execute("PRAGMA table_info(interventi)")
        colonne = [col[1] for col in self.cursor.fetchall()]
        if "data_iso" not in colonne:
            self.cursor.execute("ALTER TABLE interventi ADD COLUMN data_iso TEXT")

        self.cursor.execute("SELECT COUNT(*) FROM professioni")
        if self.cursor.fetchone()[0] == 0:
            for prof in ["Tecnico Generico", "Elettricista", "Idraulico", "Informatico", "Manutentore"]:
                self.cursor.execute("INSERT OR IGNORE INTO professioni (nome) VALUES (?)", (prof,))

        self.conn.commit()

    def on_closing(self):
        try:
            if hasattr(self, "conn") and self.conn:
                self.conn.commit()
                self.conn.close()
        except Exception:
            pass
        self.destroy()

    # =========================================================================
    # FUNZIONI DI SUPPORTO, RICERCA INTELLIGENTE NOME/COGNOME E FILTRI
    # =========================================================================
    @staticmethod
    def _match_nome_cognome(testo_cliente, testo_ricerca):
        if not testo_ricerca or not testo_ricerca.strip():
            return True
        if not testo_cliente:
            return False
        bersaglio = testo_cliente.lower()
        termini = [t for t in testo_ricerca.lower().strip().split() if t]
        return all(termine in bersaglio for termine in termini)

    def reset_filtri_espletati(self):
        self.entry_filtro_cli.delete(0, "end")
        self.entry_filtro_data.delete(0, "end")
        self.aggiorna_vista_interventi_espletati()

    def reset_filtri_permanenti(self):
        self.entry_filtro_perm_cli.delete(0, "end")
        self.entry_filtro_perm_data.delete(0, "end")
        self.aggiorna_vista_interventi_permanenti()

    def mostra_notifica(self, messaggio, colore=None):
        if colore is None:
            colore = "#0284c7" if self.T["mode"] == "Light" else "#00ff66"
        self.lbl_notifica.configure(text=f"⚡ {messaggio}", text_color=colore)
        if self.notifica_timer:
            self.after_cancel(self.notifica_timer)
        self.notifica_timer = self.after(4500, lambda: self.lbl_notifica.configure(text=""))

    def evidenzia_menu_attivo(self, chiave_attiva):
        self.menu_attivo_corrente = chiave_attiva
        bordo_attivo = "#0f172a" if self.T["mode"] == "Light" else "#ffffff"
        for chiave, (btn, bg_norm, border_norm, txt_norm) in self.config_menu.items():
            if chiave == chiave_attiva:
                btn.configure(border_width=2, border_color=bordo_attivo)
            else:
                btn.configure(border_width=1, border_color=border_norm)

    def cambia_lingua_da_combo(self, nome_lingua):
        codice = "it"
        for k, v in LINGUE_NOMI.items():
            if v == nome_lingua:
                codice = k
                break
        self.lingua_corrente = codice
        t = TRADUZIONI[codice]

        self.title(t["titolo_app"])
        self.btn_nuovo_int.configure(text=t["btn_nuovo_int"])
        self.btn_int_aperti.configure(text=t["btn_int_aperti"])
        self.btn_int_espletati.configure(text=t["btn_int_espletati"])
        self.btn_int_permanenti.configure(text=t["btn_int_permanenti"])
        self.btn_collaboratori.configure(text=t["btn_nuovo_collab"])
        self.btn_gestione_collab.configure(text=t["btn_schede_collab"])
        self.btn_mansioni.configure(text=t["btn_mansioni"])
        self.btn_clienti.configure(text=t["btn_nuovo_cliente"])
        self.btn_gestione_clienti.configure(text=t["btn_gestione_clienti"])
        self.btn_calendario.configure(text=t["btn_calendario"])
        self.btn_report.configure(text=t["btn_report"])
        self.btn_aggiorna_app.configure(text=t["btn_aggiorna"])
        self.lbl_barra_titolo.configure(text=t["barra_titolo"])

        self.lbl_cliente.configure(text=t["lbl_cliente"])
        self.lbl_tel_cliente.configure(text=t["lbl_tel_cliente"])
        self.lbl_data.configure(text=t["lbl_data"])
        self.lbl_orario.configure(text=t["lbl_orario"])
        self.lbl_collaboratore.configure(text=t["lbl_collaboratore"])
        self.lbl_tel_collab.configure(text=t["lbl_tel_collab"])
        self.lbl_indirizzo.configure(text=t["lbl_indirizzo"])
        self.lbl_guasto.configure(text=t["lbl_guasto"])
        self.btn_salva_ticket.configure(text=t["btn_salva_whatsapp"])
        self.entry_filtro_nuovo_cli.configure(placeholder_text=t["placeholder_filtro"])

    def carica_lista_clienti(self):
        self.cursor.execute("SELECT nome FROM clienti ORDER BY nome ASC")
        return [r[0] for r in self.cursor.fetchall()]

    def carica_lista_clienti_con_storico(self):
        """Restituisce l'elenco unificato di tutti i clienti in anagrafica e nei ticket storici."""
        self.cursor.execute("SELECT nome FROM clienti WHERE nome IS NOT NULL AND TRIM(nome) != ''")
        da_clienti = {r[0].strip() for r in self.cursor.fetchall()}
        self.cursor.execute("SELECT DISTINCT cliente FROM interventi WHERE cliente IS NOT NULL AND TRIM(cliente) != ''")
        da_interventi = {r[0].strip() for r in self.cursor.fetchall()}
        unificati = sorted(list(da_clienti.union(da_interventi)), key=lambda x: x.lower())
        return unificati

    def carica_lista_collaboratori(self):
        self.cursor.execute("SELECT nome, cognome FROM collaboratori ORDER BY nome ASC")
        return [f"{r[0]} {r[1]}".strip() for r in self.cursor.fetchall()]

    def carica_lista_professioni(self):
        self.cursor.execute("SELECT nome FROM professioni ORDER BY nome ASC")
        return [r[0] for r in self.cursor.fetchall()]

    def carica_lista_interventi_aperti(self):
        self.cursor.execute("SELECT id, cliente, data_ora FROM interventi WHERE stato = 'Aperto' ORDER BY id DESC")
        return [f"#{r[0]} - {r[1]} ({r[2]})" for r in self.cursor.fetchall()]

    # =========================================================================
    # EVENTI DI SELEZIONE E FILTRO
    # =========================================================================
    def filtra_clienti_nuovo_ticket(self, event=None):
        testo = self.entry_filtro_nuovo_cli.get().strip()
        tutti = self.carica_lista_clienti()
        filtrati = [c for c in tutti if self._match_nome_cognome(c, testo)]
        self.combo_clienti.configure(values=filtrati)
        if filtrati:
            self.combo_clienti.set(filtrati[0])
            self.on_cliente_selezionato(filtrati[0])

    def filtra_clienti_gestione(self, event=None):
        testo = self.entry_cerca_gestione_cliente.get().strip()
        tutti = self.carica_lista_clienti()
        filtrati = [c for c in tutti if self._match_nome_cognome(c, testo)]
        self.combo_mod_cliente.configure(values=filtrati)
        if filtrati:
            self.combo_mod_cliente.set(filtrati[0])
            self.carica_dati_cliente_per_modifica(filtrati[0])

    def filtra_clienti_report(self, event=None):
        testo = self.entry_filtro_report_cli.get().strip()
        tutti = self.carica_lista_clienti_con_storico()
        filtrati = [c for c in tutti if self._match_nome_cognome(c, testo)]
        self.combo_report_cliente.configure(values=filtrati if filtrati else [""])
        if filtrati:
            self.combo_report_cliente.set(filtrati[0])
        else:
            self.combo_report_cliente.set("")
        self.aggiorna_anteprima_report()

    def on_cliente_selezionato(self, nome_cliente):
        self.cursor.execute("SELECT telefono, indirizzo FROM clienti WHERE nome = ?", (nome_cliente,))
        res = self.cursor.fetchone()
        self.entry_tel_cliente.delete(0, "end")
        self.entry_indirizzo.delete(0, "end")
        if res:
            self.entry_tel_cliente.insert(0, res[0] or "")
            self.entry_indirizzo.insert(0, res[1] or "")

    def on_collaboratore_selezionato(self, nome_completo):
        parts = nome_completo.split(" ", 1)
        nome = parts[0]
        cognome = parts[1] if len(parts) > 1 else ""
        self.cursor.execute("SELECT telefono FROM collaboratori WHERE nome = ? AND cognome = ?", (nome, cognome))
        res = self.cursor.fetchone()
        self.entry_tel_collaboratore.delete(0, "end")
        if res:
            self.entry_tel_collaboratore.insert(0, res[0] or "")

    def carica_dati_cliente_per_modifica(self, nome_cliente):
        self.cursor.execute("SELECT nome, telefono, indirizzo FROM clienti WHERE nome = ?", (nome_cliente,))
        res = self.cursor.fetchone()
        if res:
            self.entry_mod_nome.delete(0, "end")
            self.entry_mod_nome.insert(0, res[0] or "")
            self.entry_mod_tel.delete(0, "end")
            self.entry_mod_tel.insert(0, res[1] or "")
            self.entry_mod_indirizzo.delete(0, "end")
            self.entry_mod_indirizzo.insert(0, res[2] or "")

    def carica_dati_collaboratore_per_modifica(self, nome_completo):
        parts = nome_completo.split(" ", 1)
        nome = parts[0]
        cognome = parts[1] if len(parts) > 1 else ""
        self.cursor.execute("SELECT nome, cognome, telefono, specializzazione FROM collaboratori WHERE nome = ? AND cognome = ?", (nome, cognome))
        res = self.cursor.fetchone()
        if res:
            self.entry_mod_collab_nome.delete(0, "end")
            self.entry_mod_collab_nome.insert(0, res[0] or "")
            self.entry_mod_collab_cognome.delete(0, "end")
            self.entry_mod_collab_cognome.insert(0, res[1] or "")
            self.entry_mod_collab_tel.delete(0, "end")
            self.entry_mod_collab_tel.insert(0, res[2] or "")
            if res[3]:
                self.combo_mod_collab_mansione.set(res[3])

    def carica_dettagli_intervento_aperto(self, selezione):
        if not selezione or not selezione.startswith("#"):
            return
        tid = int(selezione.split(" - ")[0].replace("#", ""))
        self.cursor.execute("SELECT intervento FROM interventi WHERE id = ?", (tid,))
        res = self.cursor.fetchone()
        self.text_aggiorna_tipo.delete("0.0", "end")
        if res and res[0]:
            self.text_aggiorna_tipo.insert("0.0", res[0])

    # =========================================================================
    # OPERAZIONI CRUD CLIENTI, COLLABORATORI E MANSIONI
    # =========================================================================
    def salva_modifiche_cliente(self):
        vecchio_nome = self.combo_mod_cliente.get()
        nuovo_nome = self.entry_mod_nome.get().strip()
        nuovo_tel = self.entry_mod_tel.get().strip()
        nuovo_ind = self.entry_mod_indirizzo.get().strip()

        if not vecchio_nome or not nuovo_nome:
            messagebox.showerror("Errore", "Il nome cliente non può essere vuoto!")
            return
        try:
            self.cursor.execute("UPDATE clienti SET nome = ?, telefono = ?, indirizzo = ? WHERE nome = ?", (nuovo_nome, nuovo_tel, nuovo_ind, vecchio_nome))
            self.cursor.execute("UPDATE interventi SET cliente = ?, telefono = ?, indirizzo = ? WHERE cliente = ? AND stato = 'Aperto'", (nuovo_nome, nuovo_tel, nuovo_ind, vecchio_nome))
            self.conn.commit()
            self.mostra_notifica("Profilo cliente aggiornato!")
            self.aggiorna_vista_clienti()
            self.aggiorna_vista_gestione_clienti()
            self.aggiorna_lista_tickets()
            self.aggiorna_vista_interventi_aperti()
            nuova_lista = self.carica_lista_clienti()
            self.combo_mod_cliente.configure(values=nuova_lista)
            self.combo_clienti.configure(values=nuova_lista)
            self.combo_report_cliente.configure(values=self.carica_lista_clienti_con_storico())
            self.combo_mod_cliente.set(nuovo_nome)
        except sqlite3.IntegrityError:
            messagebox.showerror("Errore", "Esiste già un cliente con questo nome!")

    def salva_modifiche_collaboratore(self):
        vecchio_testo = self.combo_mod_collab.get()
        if not vecchio_testo:
            return
        parts = vecchio_testo.split(" ", 1)
        v_nome = parts[0]
        v_cognome = parts[1] if len(parts) > 1 else ""
        nuovo_nome = self.entry_mod_collab_nome.get().strip()
        nuovo_cognome = self.entry_mod_collab_cognome.get().strip()
        nuovo_tel = self.entry_mod_collab_tel.get().strip()
        nuova_mansione = self.combo_mod_collab_mansione.get().strip()
        if not nuovo_nome:
            messagebox.showerror("Errore", "Il nome del collaboratore non può essere vuoto!")
            return
        vecchio_completo = f"{v_nome} {v_cognome}".strip()
        nuovo_completo = f"{nuovo_nome} {nuovo_cognome}".strip()
        self.cursor.execute("UPDATE collaboratori SET nome = ?, cognome = ?, telefono = ?, specializzazione = ? WHERE nome = ? AND cognome = ?", (nuovo_nome, nuovo_cognome, nuovo_tel, nuova_mansione, v_nome, v_cognome))
        self.cursor.execute("UPDATE interventi SET collaboratore = ? WHERE collaboratore = ? AND stato = 'Aperto'", (nuovo_completo, vecchio_completo))
        self.conn.commit()
        self.mostra_notifica("Profilo collaboratore aggiornato!")
        self.aggiorna_vista_collaboratori()
        self.aggiorna_vista_gestione_collaboratori()
        self.aggiorna_lista_tickets()
        self.aggiorna_vista_interventi_aperti()
        nuova_lista = self.carica_lista_collaboratori()
        self.combo_mod_collab.configure(values=nuova_lista)
        self.combo_collaboratori.configure(values=nuova_lista)
        self.combo_mod_collab.set(nuovo_completo)

    def elimina_cliente(self):
        cliente_da_eliminare = self.combo_mod_cliente.get()
        if not cliente_da_eliminare:
            return
        if messagebox.askyesno("Conferma", f"Eliminare l'anagrafica di '{cliente_da_eliminare}'?\n(Lo storico dei ticket passati verrà conservato)"):
            self.cursor.execute("DELETE FROM clienti WHERE nome = ?", (cliente_da_eliminare,))
            self.conn.commit()
            self.mostra_notifica("Anagrafica cliente eliminata (storico ticket salvato).")
            self.aggiorna_vista_clienti()
            self.aggiorna_vista_gestione_clienti()
            nuova_lista = self.carica_lista_clienti()
            self.combo_mod_cliente.configure(values=nuova_lista)
            self.combo_clienti.configure(values=nuova_lista)
            self.combo_report_cliente.configure(values=self.carica_lista_clienti_con_storico())
            if nuova_lista:
                self.combo_mod_cliente.set(nuova_lista[0])
                self.carica_dati_cliente_per_modifica(nuova_lista[0])
            else:
                self.combo_mod_cliente.set("")

    def elimina_collaboratore(self):
        collab_da_eliminare = self.combo_mod_collab.get()
        if not collab_da_eliminare:
            return
        parts = collab_da_eliminare.split(" ", 1)
        c_nome = parts[0]
        c_cognome = parts[1] if len(parts) > 1 else ""
        if messagebox.askyesno("Conferma", f"Eliminare il collaboratore '{collab_da_eliminare}'?\n(Lo storico dei ticket assegnati verrà conservato)"):
            self.cursor.execute("DELETE FROM collaboratori WHERE nome = ? AND cognome = ?", (c_nome, c_cognome))
            self.conn.commit()
            self.mostra_notifica("Collaboratore eliminato (storico ticket salvato).")
            self.aggiorna_vista_collaboratori()
            self.aggiorna_vista_gestione_collaboratori()
            nuova_lista = self.carica_lista_collaboratori()
            self.combo_mod_collab.configure(values=nuova_lista)
            self.combo_collaboratori.configure(values=nuova_lista)
            if nuova_lista:
                self.combo_mod_collab.set(nuova_lista[0])
                self.carica_dati_collaboratore_per_modifica(nuova_lista[0])
            else:
                self.combo_mod_collab.set("")

    def aggiorna_telefono_iniziale(self):
        valori = self.carica_lista_collaboratori()
        if valori:
            self.combo_collaboratori.set(valori[0])
            self.on_collaboratore_selezionato(valori[0])

    def aggiorna_collaboratore_gestione_iniziale(self):
        valori = self.carica_lista_collaboratori()
        if valori:
            self.combo_mod_collab.set(valori[0])
            self.carica_dati_collaboratore_per_modifica(valori[0])

    def aggiorna_cliente_iniziale(self):
        valori = self.carica_lista_clienti()
        if valori:
            self.combo_clienti.set(valori[0])
            self.on_cliente_selezionato(valori[0])
            self.combo_mod_cliente.set(valori[0])
            self.carica_dati_cliente_per_modifica(valori[0])
        valori_rep = self.carica_lista_clienti_con_storico()
        if valori_rep:
            self.combo_report_cliente.configure(values=valori_rep)
            self.combo_report_cliente.set(valori_rep[0])
            self.aggiorna_anteprima_report()

    def aggiungi_professione(self):
        nuova_prof = self.entry_nuova_prof.get().strip()
        if not nuova_prof:
            return
        try:
            self.cursor.execute("INSERT INTO professioni (nome) VALUES (?)", (nuova_prof,))
            self.conn.commit()
            self.mostra_notifica(f"Mansione '{nuova_prof}' aggiunta!")
            self.entry_nuova_prof.delete(0, "end")
            lista_prof = self.carica_lista_professioni()
            self.combo_mansione_collab.configure(values=lista_prof)
            self.combo_mod_collab_mansione.configure(values=lista_prof)
            self.aggiorna_vista_mansioni()
        except sqlite3.IntegrityError:
            messagebox.showerror("Errore", "La mansione esiste già!")

    def aggiorna_vista_mansioni(self):
        self.lista_mansioni_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome FROM professioni ORDER BY nome ASC")
        testo = "  ⚡ ELENCO MANSIONI REGISTRATE\n\n" + "".join([f"  🔹  {p[1]}\n" for p in self.cursor.fetchall()])
        self.lista_mansioni_box.insert("0.0", testo)

    def aggiungi_collaboratore(self):
        nome = self.entry_collab_nome.get().strip()
        cognome = self.entry_collab_cognome.get().strip()
        tel = self.entry_collab_tel.get().strip()
        mansione = self.combo_mansione_collab.get().strip()
        if not nome:
            messagebox.showerror("Errore", "Il campo Nome è obbligatorio.")
            return
        self.cursor.execute("INSERT INTO collaboratori (nome, cognome, telefono, specializzazione) VALUES (?, ?, ?, ?)", (nome, cognome, tel, mansione))
        self.conn.commit()
        self.mostra_notifica(f"Collaboratore '{nome} {cognome}' registrato!")
        self.entry_collab_nome.delete(0, "end")
        self.entry_collab_cognome.delete(0, "end")
        self.entry_collab_tel.delete(0, "end")
        self.aggiorna_vista_collaboratori()
        self.aggiorna_vista_gestione_collaboratori()
        nuova_lista = self.carica_lista_collaboratori()
        self.combo_collaboratori.configure(values=nuova_lista)
        self.combo_mod_collab.configure(values=nuova_lista)

    def aggiungi_cliente(self):
        nome = self.entry_cli_nome.get().strip()
        tel = self.entry_cli_tel.get().strip()
        indirizzo = self.entry_cli_indirizzo.get().strip()
        if not nome:
            messagebox.showerror("Errore", "Inserisci il nome del cliente.")
            return
        self.cursor.execute("SELECT COUNT(*) FROM clienti WHERE nome = ?", (nome,))
        if self.cursor.fetchone()[0] > 0:
            messagebox.showerror("Errore", "Cliente già esistente!")
            return
        self.cursor.execute("INSERT INTO clienti (nome, telefono, indirizzo) VALUES (?, ?, ?)", (nome, tel, indirizzo))
        self.conn.commit()
        self.mostra_notifica(f"Cliente '{nome}' registrato!")
        self.entry_cli_nome.delete(0, "end")
        self.entry_cli_tel.delete(0, "end")
        self.entry_cli_indirizzo.delete(0, "end")
        self.aggiorna_vista_clienti()
        self.aggiorna_vista_gestione_clienti()
        nuova_lista = self.carica_lista_clienti()
        self.combo_clienti.configure(values=nuova_lista)
        self.combo_mod_cliente.configure(values=nuova_lista)
        self.combo_report_cliente.configure(values=self.carica_lista_clienti_con_storico())

    # =========================================================================
    # GESTIONE TICKET E WHATSAPP
    # =========================================================================
    def formatta_numero_wa(self, telefono):
        if not telefono or telefono == "N/D":
            return None
        cifre = "".join(filter(str.isdigit, telefono))
        if len(cifre) < 8:
            return None
        if not cifre.startswith("39") and len(cifre) == 10:
            cifre = "39" + cifre
        return cifre

    def crea_nuovo_ticket(self):
        if not self.is_pro and self.get_totale_ticket_creati_storico() >= LIMITE_TICKET_TRIAL:
            messagebox.showwarning(
                "Limite Versione di Prova Raggiunto",
                f"Hai utilizzato tutti i {LIMITE_TICKET_TRIAL} ticket gratuiti di prova (o il tuo abbonamento è scaduto).\n\n"
                f"Attiva o rinnova ora il tuo Abbonamento PRO per continuare!"
            )
            self.apri_finestra_licenza()
            return

        t = TRADUZIONI[self.lingua_corrente]
        cliente = self.combo_clienti.get().strip()
        telefono = self.entry_tel_cliente.get().strip()
        giorno = self.combo_giorno.get()
        mese_str = self.combo_mese.get()
        anno = self.combo_anno.get()
        ora = self.combo_ora.get()
        minuti = self.combo_minuti.get()
        mese_num = MESI_IT.index(mese_str) + 1 if mese_str in MESI_IT else 1
        data_ora = f"{giorno} {mese_str} {anno} - Ore {ora}:{minuti}"
        data_iso = f"{anno}-{mese_num:02d}-{giorno} {ora}:{minuti}"
        collaboratore = self.combo_collaboratori.get().strip()
        indirizzo = self.entry_indirizzo.get().strip()
        tel_collab = self.entry_tel_collaboratore.get().strip()
        guasto = self.text_nuovo_guasto.get("0.0", "end").strip()

        num_cli = self.formatta_numero_wa(telefono)
        if not cliente or not num_cli:
            messagebox.showerror("Errore", t["err_cliente"])
            return

        self.cursor.execute(
            "INSERT INTO interventi (cliente, telefono, data_ora, data_iso, collaboratore, indirizzo, guasto, intervento, stato, chiusura_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (cliente, telefono, data_ora, data_iso, collaboratore, indirizzo, guasto, "", "Aperto", None)
        )
        self.conn.commit()
        self.incrementa_contatore_ticket_storico()
        self.mostra_notifica(t["msg_successo_ticket"])

        msg_cli = f"Gentile {cliente}, le confermiamo l'intervento/appuntamento per il {data_ora}.\nIndirizzo: {indirizzo}\nTecnico incaricato: {collaboratore}."
        webbrowser.open(f"https://wa.me/{num_cli}?text={urllib.parse.quote(msg_cli)}")

        num_collab = self.formatta_numero_wa(tel_collab)
        if num_collab:
            msg_collab = f"Nuovo ticket assegnato:\n👤 Cliente: {cliente}\n📱 Tel: {telefono}\n📍 Indirizzo: {indirizzo}\n⏰ {data_ora}\n⚠️ Guasto: {guasto or 'Non specificato'}"
            url_collab = f"https://wa.me/{num_collab}?text={urllib.parse.quote(msg_collab)}"
            self.after(1800, lambda u=url_collab: webbrowser.open(u))

        self.text_nuovo_guasto.delete("0.0", "end")
        self.aggiorna_lista_tickets()
        self.aggiorna_vista_interventi_aperti()
        self.aggiorna_vista_calendario()
        self.aggiorna_anteprima_report()

    def aggiorna_tipo_intervento(self):
        selezione = self.combo_interventi_aperti.get()
        if not selezione or not selezione.startswith("#"):
            return
        tid = int(selezione.split(" - ")[0].replace("#", ""))
        note = self.text_aggiorna_tipo.get("0.0", "end").strip()
        self.cursor.execute("UPDATE interventi SET intervento = ? WHERE id = ?", (note, tid))
        self.conn.commit()
        self.mostra_notifica(f"Note del Ticket #{tid} salvate!")
        self.aggiorna_vista_interventi_aperti()
        self.aggiorna_anteprima_report()

    def chiudi_ticket(self):
        selezione = self.combo_interventi_aperti.get()
        if not selezione or not selezione.startswith("#"):
            return
        tid = int(selezione.split(" - ")[0].replace("#", ""))
        note = self.text_aggiorna_tipo.get("0.0", "end").strip()
        if messagebox.askyesno("Chiudi Ticket", f"Confermi la chiusura del Ticket #{tid} e lo spostamento negli Espletati?"):
            self.cursor.execute(
                "UPDATE interventi SET stato = 'Espletato', intervento = ?, chiusura_timestamp = ? WHERE id = ?",
                (note, time.time(), tid)
            )
            self.conn.commit()
            self.mostra_notifica(f"Ticket #{tid} chiuso e spostato in Espletati!")
            self.aggiorna_lista_tickets()
            self.aggiorna_vista_interventi_aperti()
            self.aggiorna_vista_interventi_espletati()
            self.aggiorna_vista_calendario()
            self.aggiorna_anteprima_report()

    def rendi_permanente(self, tid):
        if not self.is_pro:
            messagebox.showwarning(
                "Funzione Riservata PRO",
                "L'archiviazione nei Ticket Permanenti è disponibile solo con Abbonamento PRO attivo."
            )
            self.apri_finestra_licenza()
            return

        self.cursor.execute("UPDATE interventi SET stato = 'Permanente' WHERE id = ?", (tid,))
        self.conn.commit()
        self.mostra_notifica(f"Ticket #{tid} archiviato nei Permanenti.")
        self.aggiorna_vista_interventi_espletati()
        self.aggiorna_vista_interventi_permanenti()
        self.aggiorna_vista_calendario()
        self.aggiorna_anteprima_report()

    def riporta_a_espletati(self, tid):
        self.cursor.execute("UPDATE interventi SET stato = 'Espletato' WHERE id = ?", (tid,))
        self.conn.commit()
        self.mostra_notifica(f"Ticket #{tid} riportato negli Espletati.")
        self.aggiorna_vista_interventi_permanenti()
        self.aggiorna_vista_interventi_espletati()
        self.aggiorna_vista_calendario()
        self.aggiorna_anteprima_report()

    def elimina_ticket_permanente(self, tid):
        if messagebox.askyesno("Elimina Ticket", f"Eliminare definitivamente il Ticket permanente #{tid}?"):
            self.cursor.execute("DELETE FROM interventi WHERE id = ?", (tid,))
            self.conn.commit()
            self.mostra_notifica(f"Ticket #{tid} eliminato definitivamente.", "#dc2626")
            self.aggiorna_vista_interventi_permanenti()
            self.aggiorna_vista_calendario()
            self.aggiorna_anteprima_report()

    # =========================================================================
    # ESPORTAZIONE SINGOLO TICKET E REPORT STORICO CLIENTE (TXT E PDF)
    # =========================================================================
    def recupera_dati_ticket_per_export(self, tid):
        self.cursor.execute("SELECT id, cliente, telefono, data_ora, collaboratore, indirizzo, guasto, intervento, stato FROM interventi WHERE id = ?", (tid,))
        return self.cursor.fetchone()

    def esporta_singolo_ticket_txt(self, tid):
        r = self.recupera_dati_ticket_per_export(tid)
        if not r:
            return
        percorso = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt")],
            initialfile=f"Ticket_{r[0]}_{r[1].replace(' ', '')}.txt"
        )
        if not percorso:
            return
        contenuto = (
            f"==================================================\n"
            f"  TEAM ORGANIZER PRO - SCHEDA INTERVENTO #{r[0]}\n"
            f"==================================================\n"
            f"Stato:         {r[8]}\n"
            f"Data e Ora:    {r[3]}\n"
            f"Cliente:       {r[1]} (Tel: {r[2] or 'N/D'})\n"
            f"Indirizzo:     {r[5] or 'N/D'}\n"
            f"Collaboratore: {r[4] or 'N/D'}\n"
            f"--------------------------------------------------\n"
            f"GUASTO / RICHIESTA:\n{r[6] or 'Non specificato'}\n\n"
            f"INTERVENTO ESEGUITO:\n{r[7] or 'In attesa / Non compilato'}\n"
            f"==================================================\n"
        )
        with open(percorso, "w", encoding="utf-8") as f:
            f.write(contenuto)
        self.mostra_notifica(f"Ticket #{tid} esportato in TXT!")

    def esporta_singolo_ticket_pdf(self, tid):
        if not self.is_pro:
            messagebox.showwarning(
                "Esportazione PDF Riservata PRO",
                "L'esportazione professionale in formato PDF è riservata agli utenti con Abbonamento PRO attivo.\n\n(Nella versione di prova puoi comunque esportare in formato TXT)."
            )
            self.apri_finestra_licenza()
            return

        r = self.recupera_dati_ticket_per_export(tid)
        if not r:
            return
        percorso = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            initialfile=f"Ticket_{r[0]}_{r[1].replace(' ', '')}.pdf"
        )
        if not percorso:
            return
        righe_pdf = [
            f"TEAM ORGANIZER PRO - SCHEDA INTERVENTO #{r[0]}",
            "----------------------------------------------------------------------",
            f"Stato Ticket: {r[8]}",
            f"Data e Ora: {r[3]}",
            f"Cliente: {r[1]}",
            f"Telefono Cliente: {r[2] or 'N/D'}",
            f"Indirizzo: {r[5] or 'N/D'}",
            f"Tecnico Assegnato: {r[4] or 'N/D'}",
            "----------------------------------------------------------------------",
            "DESCRIZIONE GUASTO / RICHIESTA:",
            f"{r[6] or 'Non specificato'}",
            "",
            "NOTE INTERVENTO ESEGUITO:",
            f"{r[7] or 'In attesa / Non compilato'}",
            "----------------------------------------------------------------------",
            f"Documento generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}"
        ]
        genera_pdf_semplice(percorso, righe_pdf)
        self.mostra_notifica(f"Ticket #{tid} esportato in PDF!")

    # --- FUNZIONI REPORT STORICO CLIENTE ---
    def recupera_ticket_report_cliente(self, nome_cliente, filtro_stato="Tutti gli stati"):
        if not nome_cliente:
            return []
        if filtro_stato and filtro_stato != "Tutti gli stati":
            self.cursor.execute(
                "SELECT id, cliente, telefono, data_ora, collaboratore, indirizzo, guasto, intervento, stato FROM interventi WHERE LOWER(TRIM(cliente)) = LOWER(TRIM(?)) AND stato = ? ORDER BY id DESC",
                (nome_cliente, filtro_stato)
            )
        else:
            self.cursor.execute(
                "SELECT id, cliente, telefono, data_ora, collaboratore, indirizzo, guasto, intervento, stato FROM interventi WHERE LOWER(TRIM(cliente)) = LOWER(TRIM(?)) ORDER BY id DESC",
                (nome_cliente,)
            )
        return self.cursor.fetchall()

    def aggiorna_anteprima_report(self):
        if not hasattr(self, "report_box"):
            return
        self.report_box.delete("0.0", "end")
        cliente = self.combo_report_cliente.get().strip()
        stato_scelto = self.combo_report_stato.get().strip()

        if not cliente:
            self.report_box.insert("0.0", "\n  📊 Seleziona un cliente dal menu in alto per visualizzare il Report completo dei suoi ticket.")
            return

        # Dati anagrafici cliente
        self.cursor.execute("SELECT telefono, indirizzo FROM clienti WHERE LOWER(TRIM(nome)) = LOWER(TRIM(?))", (cliente,))
        anag = self.cursor.fetchone()
        tel_cli = anag[0] if anag and anag[0] else "N/D"
        ind_cli = anag[1] if anag and anag[1] else "N/D"

        tickets = self.recupera_ticket_report_cliente(cliente, stato_scelto)

        if tickets and tel_cli == "N/D":
            tel_cli = tickets[0][2] or "N/D"
        if tickets and ind_cli == "N/D":
            ind_cli = tickets[0][5] or "N/D"

        n_aperti = sum(1 for t in tickets if t[8] == "Aperto")
        n_espletati = sum(1 for t in tickets if t[8] == "Espletato")
        n_permanenti = sum(1 for t in tickets if t[8] == "Permanente")

        intestazione = (
            f"  ================================================================================\n"
            f"  📊 REPORT STORICO CLIENTE: {cliente.upper()}\n"
            f"  ================================================================================\n"
            f"  📱 Telefono: {tel_cli}   |   📍 Indirizzo: {ind_cli}\n"
            f"  📂 Filtro Stato: {stato_scelto}   |   🔢 Totale Ticket Trovati: {len(tickets)} "
            f"(Aperti: {n_aperti} | Espletati: {n_espletati} | Permanenti: {n_permanenti})\n"
            f"  ================================================================================\n\n"
        )
        self.report_box.insert("end", intestazione)

        if not tickets:
            self.report_box.insert("end", "  Nessun ticket trovato per questo cliente con il filtro selezionato.\n")
            return

        for t in tickets:
            blocco = (
                f"  🔹 TICKET #{t[0]}   |   📅 Data/Ora: {t[3]}   |   ⚡ Stato: [{t[8]}]\n"
                f"  👷 Tecnico Assegnato: {t[4] or 'N/D'}   |   📍 Luogo: {t[5] or ind_cli}\n"
                f"  ⚠️ Guasto / Richiesta: {t[6] or 'Non specificato'}\n"
                f"  🛠️ Intervento Eseguito: {t[7] or 'In attesa / Non compilato'}\n"
                f"  --------------------------------------------------------------------------------\n\n"
            )
            self.report_box.insert("end", blocco)

    def esporta_report_cliente_txt(self):
        cliente = self.combo_report_cliente.get().strip()
        stato_scelto = self.combo_report_stato.get().strip()
        if not cliente:
            messagebox.showwarning("Attenzione", "Seleziona prima un cliente per esportare il report!")
            return

        tickets = self.recupera_ticket_report_cliente(cliente, stato_scelto)
        if not tickets:
            messagebox.showwarning("Nessun Ticket", f"Non ci sono ticket da esportare per il cliente '{cliente}'.")
            return

        self.cursor.execute("SELECT telefono, indirizzo FROM clienti WHERE LOWER(TRIM(nome)) = LOWER(TRIM(?))", (cliente,))
        anag = self.cursor.fetchone()
        tel_cli = (anag[0] if anag and anag[0] else tickets[0][2]) or "N/D"
        ind_cli = (anag[1] if anag and anag[1] else tickets[0][5]) or "N/D"

        nome_file_pulito = "".join(c for c in cliente if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
        percorso = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt")],
            initialfile=f"Report_Cliente_{nome_file_pulito}.txt"
        )
        if not percorso:
            return

        n_aperti = sum(1 for t in tickets if t[8] == "Aperto")
        n_espletati = sum(1 for t in tickets if t[8] == "Espletato")
        n_permanenti = sum(1 for t in tickets if t[8] == "Permanente")

        righe = [
            "======================================================================",
            f"  TEAM ORGANIZER PRO - REPORT STORICO CLIENTE: {cliente.upper()}",
            "======================================================================",
            f"Data generazione Report: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}",
            f"Cliente:                 {cliente}",
            f"Telefono:                {tel_cli}",
            f"Indirizzo Principale:    {ind_cli}",
            f"Filtro Stato Applicato:  {stato_scelto}",
            f"Totale Ticket in Report: {len(tickets)} (Aperti: {n_aperti}, Espletati: {n_espletati}, Permanenti: {n_permanenti})",
            "======================================================================\n"
        ]

        for idx, t in enumerate(tickets, start=1):
            righe.append(f"[{idx}] TICKET #{t[0]}  |  DATA: {t[3]}  |  STATO: {t[8].upper()}")
            righe.append(f"Tecnico Incaricato: {t[4] or 'N/D'}")
            righe.append(f"Indirizzo Ticket:   {t[5] or ind_cli}")
            righe.append(f"Guasto / Richiesta: {t[6] or 'Non specificato'}")
            righe.append(f"Note Intervento:    {t[7] or 'In attesa / Non compilato'}")
            righe.append("----------------------------------------------------------------------\n")

        with open(percorso, "w", encoding="utf-8") as f:
            f.write("\n".join(righe))

        self.mostra_notifica(f"Report TXT di {cliente} esportato con successo!")
        messagebox.showinfo("Report TXT Esportato", f"Il Report storico di '{cliente}' è stato salvato in:\n{percorso}")

    def esporta_report_cliente_pdf(self):
        if not self.is_pro:
            messagebox.showwarning(
                "Esportazione Report PDF Riservata PRO",
                "L'esportazione professionale del Report Cliente in formato PDF è riservata agli utenti con Abbonamento PRO attivo.\n\n(Nella versione di prova puoi comunque esportare il Report in formato TXT)."
            )
            self.apri_finestra_licenza()
            return

        cliente = self.combo_report_cliente.get().strip()
        stato_scelto = self.combo_report_stato.get().strip()
        if not cliente:
            messagebox.showwarning("Attenzione", "Seleziona prima un cliente per esportare il report!")
            return

        tickets = self.recupera_ticket_report_cliente(cliente, stato_scelto)
        if not tickets:
            messagebox.showwarning("Nessun Ticket", f"Non ci sono ticket da esportare per il cliente '{cliente}'.")
            return

        self.cursor.execute("SELECT telefono, indirizzo FROM clienti WHERE LOWER(TRIM(nome)) = LOWER(TRIM(?))", (cliente,))
        anag = self.cursor.fetchone()
        tel_cli = (anag[0] if anag and anag[0] else tickets[0][2]) or "N/D"
        ind_cli = (anag[1] if anag and anag[1] else tickets[0][5]) or "N/D"

        nome_file_pulito = "".join(c for c in cliente if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
        percorso = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            initialfile=f"Report_Cliente_{nome_file_pulito}.pdf"
        )
        if not percorso:
            return

        n_aperti = sum(1 for t in tickets if t[8] == "Aperto")
        n_espletati = sum(1 for t in tickets if t[8] == "Espletato")
        n_permanenti = sum(1 for t in tickets if t[8] == "Permanente")

        righe_pdf = [
            f"TEAM ORGANIZER PRO - REPORT CLIENTE: {cliente.upper()}",
            "================================================================================",
            f"Generato il: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}   |   Filtro: {stato_scelto}",
            f"Cliente: {cliente}   |   Tel: {tel_cli}",
            f"Indirizzo: {ind_cli}",
            f"Totale Ticket: {len(tickets)}  (Aperti: {n_aperti} | Espletati: {n_espletati} | Permanenti: {n_permanenti})",
            "================================================================================",
            ""
        ]

        for idx, t in enumerate(tickets, start=1):
            righe_pdf.append(f"[{idx}] TICKET #{t[0]} - Data: {t[3]} - Stato: {t[8].upper()}")
            righe_pdf.append(f"Tecnico: {t[4] or 'N/D'}   |   Indirizzo: {t[5] or ind_cli}")
            righe_pdf.append(f"Guasto / Richiesta: {t[6] or 'Non specificato'}")
            righe_pdf.append(f"Intervento Eseguito: {t[7] or 'In attesa / Non compilato'}")
            righe_pdf.append("--------------------------------------------------------------------------------")
            righe_pdf.append("")

        genera_pdf_semplice(percorso, righe_pdf)
        self.mostra_notifica(f"Report PDF di {cliente} esportato con successo!")
        messagebox.showinfo("Report PDF Esportato", f"Il Report PDF di '{cliente}' è stato salvato in:\n{percorso}")

    # =========================================================================
    # AGGIORNAMENTO VISTE GRAFICHE
    # =========================================================================
    def aggiorna_lista_tickets(self):
        self.lista_box.delete("0.0", "end")
        self.cursor.execute("SELECT cliente, telefono, data_ora, collaboratore, indirizzo, guasto FROM interventi WHERE stato = 'Aperto' ORDER BY id DESC")
        righe = self.cursor.fetchall()
        testo = "  🔹 ELENCO TICKET ATTIVI\n\n" + ("".join([f"  👷 {r[3]} | 👤 {r[0]} | 📱 {r[1]} | 📍 {r[4]} | ⏰ {r[2]} | ⚠️ {r[5] or 'N/D'}\n" + "━" * 95 + "\n" for r in righe]) if righe else "  Nessun ticket registrato.")
        self.lista_box.insert("0.0", testo)

    def aggiorna_vista_interventi_aperti(self):
        T = self.T
        for widget in self.scroll_aperti.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, cliente, collaboratore, guasto, intervento, data_ora FROM interventi WHERE stato = 'Aperto' ORDER BY id DESC")
        righe = self.cursor.fetchall()
        if righe:
            for r in righe:
                row_frame = ctk.CTkFrame(self.scroll_aperti, fg_color=T["GLASS_CARD"], corner_radius=12, border_width=1, border_color=T["ACCENT_1"])
                row_frame.pack(fill="x", padx=10, pady=6)
                row_frame.grid_columnconfigure(0, weight=1)
                info_text = f"🔹 ID: {r[0]}  |  📅 {r[5]}  |  👤 Cliente: {r[1]}  |  👷 Tecnico: {r[2]}\n⚠️ Guasto: {r[3] if r[3] else 'Non specificato'}  |  🛠️ Intervento: {r[4] if r[4] else 'In attesa...'}"
                lbl = ctk.CTkLabel(row_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12, weight="bold"), text_color=T["TEXT_MAIN"])
                lbl.grid(row=0, column=0, padx=15, pady=10, sticky="w")
                btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                btn_frame.grid(row=0, column=1, padx=15, pady=10, sticky="e")

                btn_txt = ctk.CTkButton(btn_frame, text="📄", width=38, height=34, fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_width=1, border_color=T["ACCENT_2"], text_color="#ffffff", font=ctk.CTkFont(size=14), command=lambda tid=r[0]: self.esporta_singolo_ticket_txt(tid))
                btn_txt.pack(side="left", padx=4)
                ToolTip(btn_txt, "Esporta in TXT", T["ACCENT_2"])

                btn_pdf = ctk.CTkButton(btn_frame, text="📑", width=38, height=34, fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], border_width=1, border_color=T["ACCENT_1"], text_color="#ffffff", font=ctk.CTkFont(size=14), command=lambda tid=r[0]: self.esporta_singolo_ticket_pdf(tid))
                btn_pdf.pack(side="left", padx=4)
                ToolTip(btn_pdf, "Esporta in PDF (PRO)", T["ACCENT_1"])
        else:
            lbl = ctk.CTkLabel(self.scroll_aperti, text="Nessun ticket aperto.", font=ctk.CTkFont(size=13), text_color=T["TEXT_MUTED"])
            lbl.pack(padx=20, pady=20)

        lista_aggiornata = self.carica_lista_interventi_aperti()
        self.combo_interventi_aperti.configure(values=lista_aggiornata)
        if lista_aggiornata:
            self.combo_interventi_aperti.set(lista_aggiornata[0])
            self.carica_dettagli_intervento_aperto(lista_aggiornata[0])
        else:
            self.combo_interventi_aperti.set("")
            self.text_aggiorna_tipo.delete("0.0", "end")

    def aggiorna_vista_interventi_espletati(self):
        T = self.T
        for widget in self.scroll_espletati.winfo_children():
            widget.destroy()

        ritenzione_scelta = self.combo_ritenzione.get()
        adesso = time.time()
        secondi_limite = None
        if ritenzione_scelta == "3 Mesi":
            secondi_limite = adesso - (3 * 30 * 86400)
        elif ritenzione_scelta == "6 Mesi":
            secondi_limite = adesso - (6 * 30 * 86400)
        elif ritenzione_scelta == "9 Mesi":
            secondi_limite = adesso - (9 * 30 * 86400)
        elif ritenzione_scelta == "1 Anno":
            secondi_limite = adesso - (365 * 86400)

        filtro_cli = self.entry_filtro_cli.get().strip()
        filtro_data = self.entry_filtro_data.get().strip().lower()

        query = "SELECT id, cliente, collaboratore, guasto, intervento, data_ora, chiusura_timestamp, data_iso FROM interventi WHERE stato = 'Espletato'"
        params = []
        if secondi_limite is not None:
            query += " AND (chiusura_timestamp >= ? OR chiusura_timestamp IS NULL)"
            params.append(secondi_limite)
        query += " ORDER BY id DESC"

        self.cursor.execute(query, params)
        tutte_righe = self.cursor.fetchall()

        righe = []
        for r in tutte_righe:
            ok_nome = self._match_nome_cognome(r[1], filtro_cli)
            testo_data_completo = f"{r[5] or ''} {r[7] or ''}".lower()
            ok_data = (not filtro_data) or all(tok in testo_data_completo for tok in filtro_data.split())
            if ok_nome and ok_data:
                righe.append(r)

        if righe:
            for r in righe:
                row_frame = ctk.CTkFrame(self.scroll_espletati, fg_color=T["GLASS_CARD"], corner_radius=12, border_width=1, border_color=T["ACCENT_1_BORDER"])
                row_frame.pack(fill="x", padx=10, pady=6)
                row_frame.grid_columnconfigure(0, weight=1)
                info_text = f"🔹 ID: {r[0]}  |  📅 {r[5]}  |  👤 Cliente: {r[1]}  |  👷 Tecnico: {r[2]}\n⚠️ Guasto: {r[3] if r[3] else 'Non specificato'}  |  🛠️ Intervento: {r[4] if r[4] else 'Non specificato'}"
                lbl = ctk.CTkLabel(row_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12, weight="bold"), text_color=T["TEXT_MAIN"])
                lbl.grid(row=0, column=0, padx=15, pady=10, sticky="w")
                btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                btn_frame.grid(row=0, column=1, padx=15, pady=10, sticky="e")

                btn_txt = ctk.CTkButton(btn_frame, text="📄", width=38, height=35, fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_width=1, border_color=T["ACCENT_2"], text_color="#ffffff", font=ctk.CTkFont(size=14), command=lambda tid=r[0]: self.esporta_singolo_ticket_txt(tid))
                btn_txt.pack(side="left", padx=4)
                ToolTip(btn_txt, "Esporta in TXT", T["ACCENT_2"])

                btn_pdf = ctk.CTkButton(btn_frame, text="📑", width=38, height=35, fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], border_width=1, border_color=T["ACCENT_1"], text_color="#ffffff", font=ctk.CTkFont(size=14), command=lambda tid=r[0]: self.esporta_singolo_ticket_pdf(tid))
                btn_pdf.pack(side="left", padx=4)
                ToolTip(btn_pdf, "Esporta in PDF (PRO)", T["ACCENT_1"])

                btn_lock = ctk.CTkButton(btn_frame, text="🔒", width=40, height=35, fg_color=T["ACCENT_3_DARK"], hover_color=T["ACCENT_3_HOVER"], border_width=1, border_color=T["ACCENT_3"], text_color="#ffffff", font=ctk.CTkFont(size=16), command=lambda tid=r[0]: self.rendi_permanente(tid))
                btn_lock.pack(side="left", padx=5)
                ToolTip(btn_lock, "Sposta in permanenti (PRO)", T["ACCENT_3"])
        else:
            lbl = ctk.CTkLabel(self.scroll_espletati, text="Nessun ticket espletato trovato con i filtri inseriti.", font=ctk.CTkFont(size=13), text_color=T["TEXT_MUTED"])
            lbl.pack(padx=20, pady=20)

    def aggiorna_vista_interventi_permanenti(self):
        T = self.T
        for widget in self.scroll_permanenti.winfo_children():
            widget.destroy()

        filtro_cli = self.entry_filtro_perm_cli.get().strip() if hasattr(self, "entry_filtro_perm_cli") else ""
        filtro_data = self.entry_filtro_perm_data.get().strip().lower() if hasattr(self, "entry_filtro_perm_data") else ""

        self.cursor.execute("SELECT id, cliente, collaboratore, guasto, intervento, data_ora, data_iso FROM interventi WHERE stato = 'Permanente' ORDER BY id DESC")
        tutte_righe = self.cursor.fetchall()

        righe = []
        for r in tutte_righe:
            ok_nome = self._match_nome_cognome(r[1], filtro_cli)
            testo_data_completo = f"{r[5] or ''} {r[6] or ''}".lower()
            ok_data = (not filtro_data) or all(tok in testo_data_completo for tok in filtro_data.split())
            if ok_nome and ok_data:
                righe.append(r)

        if righe:
            for r in righe:
                row_frame = ctk.CTkFrame(self.scroll_permanenti, fg_color=T["GLASS_CARD"], corner_radius=12, border_width=1, border_color=T["ACCENT_1"])
                row_frame.pack(fill="x", padx=10, pady=6)
                row_frame.grid_columnconfigure(0, weight=1)
                info_text = f"🔒 ID: {r[0]}  |  📅 {r[5]}  |  👤 Cliente: {r[1]}  |  👷 Tecnico: {r[2]}\n⚠️ Guasto: {r[3] if r[3] else 'Non specificato'}  |  🛠️ Intervento: {r[4] if r[4] else 'Non specificato'}"
                lbl = ctk.CTkLabel(row_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12, weight="bold"), text_color=T["TEXT_MAIN"])
                lbl.grid(row=0, column=0, padx=15, pady=10, sticky="w")
                btn_actions = ctk.CTkFrame(row_frame, fg_color="transparent")
                btn_actions.grid(row=0, column=1, padx=15, pady=10, sticky="e")

                btn_txt = ctk.CTkButton(btn_actions, text="📄", width=38, height=35, fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_width=1, border_color=T["ACCENT_2"], text_color="#ffffff", font=ctk.CTkFont(size=14), command=lambda tid=r[0]: self.esporta_singolo_ticket_txt(tid))
                btn_txt.pack(side="left", padx=4)
                ToolTip(btn_txt, "Esporta in TXT", T["ACCENT_2"])

                btn_pdf = ctk.CTkButton(btn_actions, text="📑", width=38, height=35, fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], border_width=1, border_color=T["ACCENT_1"], text_color="#ffffff", font=ctk.CTkFont(size=14), command=lambda tid=r[0]: self.esporta_singolo_ticket_pdf(tid))
                btn_pdf.pack(side="left", padx=4)
                ToolTip(btn_pdf, "Esporta in PDF (PRO)", T["ACCENT_1"])

                btn_unlock = ctk.CTkButton(btn_actions, text="🔓", width=40, height=35, fg_color=T["ACCENT_3_DARK"], hover_color=T["ACCENT_3_HOVER"], border_width=1, border_color=T["ACCENT_3"], text_color="#ffffff", font=ctk.CTkFont(size=16), command=lambda tid=r[0]: self.riporta_a_espletati(tid))
                btn_unlock.pack(side="left", padx=5)
                ToolTip(btn_unlock, "Sposta in espletati", T["ACCENT_3"])

                btn_del = ctk.CTkButton(btn_actions, text="🗑️", width=40, height=35, fg_color="#dc2626", hover_color="#b91c1c", border_width=1, border_color="#f87171", text_color="#ffffff", font=ctk.CTkFont(size=16), command=lambda tid=r[0]: self.elimina_ticket_permanente(tid))
                btn_del.pack(side="left", padx=5)
                ToolTip(btn_del, "Elimina ticket permanente", "#f87171")
        else:
            lbl = ctk.CTkLabel(self.scroll_permanenti, text="Nessun ticket permanente trovato con i filtri inseriti.", font=ctk.CTkFont(size=13), text_color=T["TEXT_MUTED"])
            lbl.pack(padx=20, pady=20)

    def aggiorna_vista_calendario(self):
        T = self.T
        for widget in self.scroll_calendario.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, cliente, data_ora, collaboratore, indirizzo, guasto, stato FROM interventi ORDER BY COALESCE(data_iso, '9999-99-99') ASC, id DESC")
        righe = self.cursor.fetchall()
        if righe:
            for r in righe:
                colore_bordo = T["ACCENT_1"] if r[6] == "Aperto" else T["ACCENT_2"] if r[6] == "Espletato" else T["ACCENT_3"]
                row_frame = ctk.CTkFrame(self.scroll_calendario, fg_color=T["GLASS_CARD"], corner_radius=12, border_width=1, border_color=colore_bordo)
                row_frame.pack(fill="x", padx=10, pady=6)
                info_text = f"📅 Data: {r[2]}   |   ⚡ Stato: [{r[6]}]\n👤 Cliente: {r[1]}   |   👷 Tecnico: {r[3]}\n📍 Indirizzo: {r[4] or 'N/D'}   |   ⚠️ Guasto: {r[5] or 'N/D'}"
                lbl = ctk.CTkLabel(row_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12, weight="bold"), text_color=T["TEXT_MAIN"])
                lbl.pack(padx=15, pady=12, anchor="w")
        else:
            lbl = ctk.CTkLabel(self.scroll_calendario, text="Nessun evento in calendario.", font=ctk.CTkFont(size=13), text_color=T["TEXT_MUTED"])
            lbl.pack(padx=20, pady=20)

    def aggiorna_vista_collaboratori(self):
        self.info_collab_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, cognome, telefono, specializzazione FROM collaboratori")
        self.info_collab_box.insert("0.0", "  🔹 ARCHIVIO COLLABORATORI\n\n" + "".join([f"  • {c[1]} {c[2]}  |  📱 Tel: {c[3] or 'N/D'}  |  🛠️ Mansione: {c[4]}\n" for c in self.cursor.fetchall()]))

    def aggiorna_vista_gestione_collaboratori(self):
        self.lista_collaboratori_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, cognome, telefono, specializzazione FROM collaboratori")
        self.lista_collaboratori_box.insert("0.0", "  🔹 LISTA COLLABORATORI\n\n" + "".join([f"  • {c[1]} {c[2]}\n" for c in self.cursor.fetchall()]))
        self.scheda_collaboratore_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, cognome, telefono, specializzazione FROM collaboratori")
        dettagli = "  ⚡ DETTAGLI E CONTATTI\n\n" + "".join([f"  👤 {c[1]} {c[2]}\n  📱 Tel: {c[3] or 'N/D'}\n  🛠️ Mansione: {c[4]}\n" + "━" * 40 + "\n" for c in self.cursor.fetchall()])
        self.scheda_collaboratore_box.insert("0.0", dettagli)

    def aggiorna_vista_clienti(self):
        self.lista_clienti_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, telefono, indirizzo FROM clienti")
        self.lista_clienti_box.insert("0.0", "  🔹 ELENCO CLIENTI\n\n" + "".join([f"  • {c[1]} - {c[2]}\n" for c in self.cursor.fetchall()]))
        self.scheda_cliente_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, telefono, indirizzo FROM clienti")
        dettagli = "  ⚡ RUBRICA INDIRIZZI CLIENTI\n\n" + "".join([f"  👤 {c[1]}\n  📱 Tel: {c[2] or 'N/D'}\n  📍 Indirizzo: {c[3] or 'N/D'}\n" + "━" * 40 + "\n" for c in self.cursor.fetchall()])
        self.scheda_cliente_box.insert("0.0", dettagli)

    def aggiorna_vista_gestione_clienti(self):
        self.lista_gestione_clienti_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, telefono, indirizzo FROM clienti")
        self.lista_gestione_clienti_box.insert("0.0", "  🔹 GESTIONE CLIENTI\n\n" + "".join([f"  • {c[1]}\n" for c in self.cursor.fetchall()]))
        self.scheda_gestione_clienti_box.delete("0.0", "end")
        self.cursor.execute("SELECT id, nome, telefono, indirizzo FROM clienti")
        dettagli = "  ⚡ SCHEDE COMPLETE CLIENTI\n\n" + "".join([f"  👤 {c[1]}\n  📱 Tel: {c[2] or 'N/D'}\n  📍 Indirizzo: {c[3] or 'N/D'}\n" + "━" * 40 + "\n" for c in self.cursor.fetchall()])
        self.scheda_gestione_clienti_box.insert("0.0", dettagli)

    # =========================================================================
    # NAVIGAZIONE TRA LE SCHERMATE E FINESTRA ABBONAMENTO MENSILE PRO
    # =========================================================================
    def nascondi_tutti_i_quadri(self):
        for f in [
            self.frame_nuovo_intervento, self.frame_nuovo_collab, self.frame_gestione_collaboratori,
            self.frame_clienti, self.frame_gestione_clienti, self.frame_interventi_aperti,
            self.frame_interventi_espletati, self.frame_interventi_permanenti,
            self.frame_calendario, self.frame_mansioni, self.frame_report
        ]:
            f.grid_remove()

    def mostra_sezione_nuovo_intervento(self):
        self.nascondi_tutti_i_quadri()
        self.frame_nuovo_intervento.grid()
        self.evidenzia_menu_attivo("nuovo")

    def mostra_sezione_interventi_aperti(self):
        self.nascondi_tutti_i_quadri()
        self.frame_interventi_aperti.grid()
        self.aggiorna_vista_interventi_aperti()
        self.evidenzia_menu_attivo("aperti")

    def mostra_sezione_interventi_espletati(self):
        self.nascondi_tutti_i_quadri()
        self.frame_interventi_espletati.grid()
        self.aggiorna_vista_interventi_espletati()
        self.evidenzia_menu_attivo("espletati")

    def mostra_sezione_interventi_permanenti(self):
        if not self.is_pro:
            messagebox.showwarning(
                "Archivio Permanente Riservato PRO",
                "La sezione Ticket Permanenti è disponibile solo con Abbonamento PRO attivo."
            )
            self.apri_finestra_licenza()
            return
        self.nascondi_tutti_i_quadri()
        self.frame_interventi_permanenti.grid()
        self.aggiorna_vista_interventi_permanenti()
        self.evidenzia_menu_attivo("permanenti")

    def mostra_sezione_collaboratori(self):
        self.nascondi_tutti_i_quadri()
        self.frame_nuovo_collab.grid()
        self.evidenzia_menu_attivo("collab")

    def mostra_sezione_gestione_collaboratori(self):
        self.nascondi_tutti_i_quadri()
        self.frame_gestione_collaboratori.grid()
        self.evidenzia_menu_attivo("gest_collab")

    def mostra_sezione_mansioni(self):
        self.nascondi_tutti_i_quadri()
        self.frame_mansioni.grid()
        self.evidenzia_menu_attivo("mansioni")

    def mostra_sezione_clienti(self):
        self.nascondi_tutti_i_quadri()
        self.frame_clienti.grid()
        self.evidenzia_menu_attivo("clienti")

    def mostra_sezione_gestione_clienti(self):
        self.nascondi_tutti_i_quadri()
        self.frame_gestione_clienti.grid()
        self.evidenzia_menu_attivo("gest_cli")

    def mostra_sezione_calendario(self):
        self.nascondi_tutti_i_quadri()
        self.frame_calendario.grid()
        self.aggiorna_vista_calendario()
        self.evidenzia_menu_attivo("calendario")

    def mostra_sezione_report(self):
        self.nascondi_tutti_i_quadri()
        self.frame_report.grid()
        clienti_storico = self.carica_lista_clienti_con_storico()
        attuale = self.combo_report_cliente.get()
        self.combo_report_cliente.configure(values=clienti_storico if clienti_storico else [""])
        if attuale in clienti_storico:
            self.combo_report_cliente.set(attuale)
        elif clienti_storico:
            self.combo_report_cliente.set(clienti_storico[0])
        else:
            self.combo_report_cliente.set("")
        self.aggiorna_anteprima_report()
        self.evidenzia_menu_attivo("report")

    def apri_cartella_database(self):
        cartella = os.path.dirname(self.db_path)
        if sys.platform == "win32":
            os.startfile(cartella)
        elif sys.platform == "darwin":
            webbrowser.open(f"file://{cartella}")
        else:
            webbrowser.open(cartella)

    def apri_finestra_licenza(self):
        T = self.T
        win = ctk.CTkToplevel(self)
        win.title("Team Organizer - Gestione Abbonamento PRO")
        win.geometry("580x520")
        win.configure(fg_color=T["CARBON_BG"])
        win.grab_set()

        colore_tema = T["ACCENT_2"] if self.is_pro else T["ACCENT_3"]
        card = ctk.CTkFrame(win, fg_color=T["GLASS_PANEL"], corner_radius=16, border_width=2, border_color=colore_tema)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        titolo_stato = "💎 ABBONAMENTO PRO ATTIVO" if self.is_pro else "🔓 VERSIONE DI PROVA / ABBONAMENTO NON ATTIVO"
        ctk.CTkLabel(card, text=titolo_stato, font=ctk.CTkFont(size=16, weight="bold"), text_color=colore_tema).pack(pady=(16, 6))

        usati = self.get_totale_ticket_creati_storico()
        testo_info = (
            f"Il tuo abbonamento è attivo e verificato ({self.scadenza_abbonamento_str or 'Licenza PRO Attiva'}).\n"
            "• Ticket e Clienti illimitati\n"
            "• Esportazione schede e Report in PDF e TXT\n"
            "• Archivio Permanente sbloccato"
            if self.is_pro else
            f"Hai utilizzato {usati}/{LIMITE_TICKET_TRIAL} ticket gratuiti.\n"
            "Abbonati online su Gumroad per ricevere subito il tuo Codice Licenza automatico\n"
            "(oppure comunica il tuo ID Macchina al fornitore per attivazione diretta):"
        )
        ctk.CTkLabel(card, text=testo_info, justify="center", font=ctk.CTkFont(size=12), text_color=T["TEXT_MAIN"]).pack(pady=6, padx=20)

        if not self.is_pro:
            ctk.CTkButton(
                card, text="💳 Abbonati Ora Online su Gumroad (Sblocco Automatico)", height=38,
                fg_color=T["ACCENT_3_DARK"], hover_color=T["ACCENT_3_HOVER"],
                border_width=1, border_color=T["ACCENT_3"], text_color="#ffffff",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: webbrowser.open(LINK_PAGAMENTO_ABBONAMENTO)
            ).pack(fill="x", padx=30, pady=(6, 4))

        id_frame = ctk.CTkFrame(card, fg_color=T["GLASS_CARD"], corner_radius=10, border_width=1, border_color=T["ACCENT_1"])
        id_frame.pack(fill="x", padx=30, pady=8)
        ctk.CTkLabel(id_frame, text=f"🖥️  ID Macchina:   {self.machine_id}", font=ctk.CTkFont(size=14, weight="bold"), text_color=T["ACCENT_1"]).pack(side="left", padx=15, pady=10)

        def copia_id():
            self.clipboard_clear()
            self.clipboard_append(self.machine_id)
            self.mostra_notifica("ID Macchina copiato negli appunti!")

        ctk.CTkButton(
            id_frame, text="📋 Copia ID", width=95, height=30,
            fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], text_color="#ffffff",
            command=copia_id
        ).pack(side="right", padx=12, pady=8)

        act_frame = ctk.CTkFrame(card, fg_color="transparent")
        act_frame.pack(fill="x", padx=30, pady=6)

        input_row = ctk.CTkFrame(act_frame, fg_color="transparent")
        input_row.pack(fill="x", pady=(0, 8))
        input_row.grid_columnconfigure(0, weight=1)

        entry_key = ctk.CTkEntry(
            input_row, placeholder_text="Incolla Codice Licenza Gumroad o Master PRO",
            height=38, fg_color=T["GLASS_CARD"], text_color=T["TEXT_MAIN"], border_color=T["ACCENT_2"], font=ctk.CTkFont(size=13, weight="bold")
        )
        entry_key.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        chiave_attuale = self._get_config("licenza_key")
        if chiave_attuale:
            entry_key.insert(0, chiave_attuale)

        def incolla_codice():
            try:
                testo_appunti = self.clipboard_get().strip()
                entry_key.delete(0, "end")
                entry_key.insert(0, testo_appunti)
            except Exception:
                pass

        ctk.CTkButton(
            input_row, text="📋 Incolla", width=95, height=38,
            fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], border_width=1, border_color=T["ACCENT_1"], text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"), command=incolla_codice
        ).grid(row=0, column=1)

        def avvia_verifica():
            codice_inserito = entry_key.get().strip()
            if not codice_inserito:
                messagebox.showwarning("Attenzione", "Clicca su '📋 Incolla' o inserisci un Codice Licenza valido!")
                return

            codice_atteso = calcola_licenza_master(self.machine_id).strip().upper()

            if codice_inserito.upper() == codice_atteso:
                self._conferma_rinnovo_mensile(codice_inserito.upper(), "MASTER", "Attivo", True, win)
                return

            threading.Thread(
                target=self._thread_controllo_pagamento,
                args=(codice_inserito, True, win),
                daemon=True
            ).start()

        ctk.CTkButton(
            act_frame, text="🔑 Verifica Pagamento e Attiva PRO", height=38,
            fg_color=T["ACCENT_2_DARK"], hover_color=T["ACCENT_2_HOVER"], border_width=1, border_color=T["ACCENT_2"], text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"), command=avvia_verifica
        ).pack(fill="x")

        ctk.CTkLabel(
            card, text=f"📁 Database sicuro in:\n{self.db_path}",
            justify="center", font=ctk.CTkFont(size=10), text_color=T["TEXT_MUTED"]
        ).pack(pady=(6, 4), padx=15)

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(pady=6)

        ctk.CTkButton(
            btn_box, text="📂 Apri Cartella Dati",
            fg_color=T["ACCENT_1_DARK"], hover_color=T["ACCENT_1_HOVER"], text_color="#ffffff",
            command=self.apri_cartella_database
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_box, text="Chiudi",
            fg_color="#475569", hover_color="#334155", text_color="#ffffff",
            command=win.destroy
        ).pack(side="left", padx=8)


if __name__ == '__main__':
    app = TeamOrganizerApp()
    app.mainloop()
