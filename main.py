# Mode d'emploi :
# 1. Installer la dépendance de lecture PDF : pip install pypdf
# 2. Lancer l'application : python main.py
# 3. Dans la fenêtre, sélectionnez le dossier des PDF source, le dossier où écrire les CSV,
#    et éventuellement un dossier d'archive pour déplacer les PDF traités. Cliquez sur
#    "Lancer le traitement" pour générer les CSV et suivre l'avancement dans le journal.

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import build_title_description_from_filename
from csv_writer import write_quiz_csv
from pdf_parser import extract_text_from_pdf, parse_quiz_from_text


class QuizProcessorApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("BIA PDF -> CSV")
        master.geometry("650x400")

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.archive_dir = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        padding = {"padx": 10, "pady": 5}

        frm = ttk.Frame(self.master)
        frm.pack(fill=tk.BOTH, expand=True, **padding)

        self._add_path_selector(frm, "Dossier PDF source", self.input_dir, 0)
        self._add_path_selector(frm, "Dossier CSV de sortie", self.output_dir, 1)
        self._add_path_selector(frm, "Dossier d'archive (optionnel)", self.archive_dir, 2)

        self.run_button = ttk.Button(frm, text="Lancer le traitement", command=self.run_processing)
        self.run_button.grid(row=3, column=0, columnspan=3, sticky="ew", **padding)

        log_label = ttk.Label(frm, text="Journal d'état :")
        log_label.grid(row=4, column=0, sticky="w", **padding)

        self.log_text = tk.Text(frm, height=12, wrap="word", state="disabled")
        self.log_text.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))

        frm.rowconfigure(5, weight=1)
        frm.columnconfigure(1, weight=1)

    def _add_path_selector(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(parent, text="Parcourir", command=lambda: self._browse_directory(variable)).grid(
            row=row, column=2, padx=5, pady=5
        )

    def _browse_directory(self, variable: tk.StringVar) -> None:
        directory = filedialog.askdirectory()
        if directory:
            variable.set(directory)

    def log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def run_processing(self) -> None:
        input_dir = self.input_dir.get().strip()
        output_dir = self.output_dir.get().strip()
        archive_dir = self.archive_dir.get().strip()

        if not input_dir or not os.path.isdir(input_dir):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier PDF source valide.")
            return
        if not output_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie pour les CSV.")
            return

        os.makedirs(output_dir, exist_ok=True)
        if archive_dir:
            os.makedirs(archive_dir, exist_ok=True)

        self.run_button.configure(state="disabled")
        self.log("Démarrage du traitement...")
        threading.Thread(target=self._process_pdfs, args=(input_dir, output_dir, archive_dir), daemon=True).start()

    def _process_pdfs(self, input_dir: str, output_dir: str, archive_dir: str) -> None:
        try:
            pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
            if not pdf_files:
                self.log("Aucun fichier PDF trouvé dans le dossier source.")
                return

            for filename in pdf_files:
                pdf_path = os.path.join(input_dir, filename)
                self.log(f"Traitement de {filename}...")
                try:
                    text = extract_text_from_pdf(pdf_path)
                    questions = parse_quiz_from_text(text)
                    if not questions:
                        raise ValueError("Aucune question détectée dans le fichier.")

                    title, description = build_title_description_from_filename(filename)
                    csv_name = os.path.splitext(filename)[0] + ".csv"
                    output_path = os.path.join(output_dir, csv_name)
                    write_quiz_csv(title, description, questions, output_path)
                    self.log(f"CSV généré : {csv_name}")

                    if archive_dir:
                        dest_path = os.path.join(archive_dir, filename)
                        os.replace(pdf_path, dest_path)
                        self.log(f"PDF archivé : {dest_path}")
                except Exception as exc:  # noqa: BLE001
                    self.log(f"Erreur sur {filename} : {exc}")
                    continue
            self.log("Traitement terminé.")
        finally:
            self.run_button.configure(state="normal")


def main() -> None:
    root = tk.Tk()
    QuizProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
