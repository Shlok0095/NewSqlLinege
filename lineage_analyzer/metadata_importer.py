# lineage_analyzer/metadata_importer.py

import tkinter as tk
from tkinter import filedialog, ttk
import os
from .metadata import MetadataStore

class MetadataImporterUI:
    """UI component for importing metadata from various sources."""
    
    def __init__(self, master, metadata_store=None):
        """Initialize the UI component."""
        self.master = master
        self.metadata_store = metadata_store or MetadataStore()
        
        self.frame = ttk.Frame(master, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.file_tab = ttk.Frame(self.notebook)
        self.paste_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.file_tab, text="Import File")
        self.notebook.add(self.paste_tab, text="Paste Metadata")
        
        # Setup file import tab
        self._setup_file_import_tab()
        
        # Setup paste tab
        self._setup_paste_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Set initial status
        self.status_var.set("Ready to import metadata")
    
    def _setup_file_import_tab(self):
        """Setup the file import tab."""
        # File path frame
        file_path_frame = ttk.Frame(self.file_tab)
        file_path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_path_frame, text="File:").pack(side=tk.LEFT, padx=5)
        
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(file_path_frame, textvariable=self.file_path_var, width=50)
        file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_button = ttk.Button(file_path_frame, text="Browse...", command=self._browse_file)
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # File type frame
        file_type_frame = ttk.Frame(self.file_tab)
        file_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_type_frame, text="Supported file types:").pack(side=tk.LEFT, padx=5)
        ttk.Label(file_type_frame, text="JSON, CSV, SQL, PDF").pack(side=tk.LEFT, padx=5)
        
        # Import button
        import_button = ttk.Button(self.file_tab, text="Import", command=self._import_file)
        import_button.pack(anchor=tk.CENTER, pady=10)
    
    def _setup_paste_tab(self):
        """Setup the paste tab."""
        # Instructions
        ttk.Label(self.paste_tab, text="Paste metadata content below:").pack(anchor=tk.W, padx=5, pady=5)
        
        # Text area for pasting
        self.paste_text = tk.Text(self.paste_tab, width=80, height=20)
        self.paste_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Format frame
        format_frame = ttk.Frame(self.paste_tab)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT, padx=5)
        
        self.format_var = tk.StringVar(value="auto")
        format_options = ["auto", "json", "csv", "sql"]
        format_dropdown = ttk.Combobox(format_frame, textvariable=self.format_var, values=format_options, state="readonly")
        format_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Import button
        import_button = ttk.Button(self.paste_tab, text="Process Pasted Content", command=self._process_pasted_content)
        import_button.pack(anchor=tk.CENTER, pady=10)
    
    def _browse_file(self):
        """Open file browser dialog."""
        filetypes = [
            ("All supported files", "*.json;*.csv;*.sql;*.pdf"),
            ("JSON files", "*.json"),
            ("CSV files", "*.csv"),
            ("SQL files", "*.sql"),
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select metadata file",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def _import_file(self):
        """Import metadata from the selected file."""
        file_path = self.file_path_var.get().strip()
        
        if not file_path:
            self.status_var.set("Error: Please select a file to import")
            return
        
        if not os.path.exists(file_path):
            self.status_var.set(f"Error: File not found: {file_path}")
            return
        
        try:
            self.status_var.set(f"Importing metadata from {file_path}...")
            self.master.update_idletasks()  # Update UI
            
            self.metadata_store.import_metadata_from_file(file_path)
            
            self.status_var.set(f"Successfully imported metadata from {file_path}")
        except Exception as e:
            self.status_var.set(f"Error importing file: {str(e)}")
    
    def _process_pasted_content(self):
        """Process pasted metadata content."""
        text = self.paste_text.get("1.0", tk.END).strip()
        
        if not text:
            self.status_var.set("Error: Please paste metadata content to process")
            return
        
        format_type = self.format_var.get()
        
        try:
            self.status_var.set("Processing pasted metadata...")
            self.master.update_idletasks()  # Update UI
            
            self.metadata_store.process_pasted_metadata(text, format_type)
            
            self.status_var.set("Successfully processed pasted metadata")
        except Exception as e:
            self.status_var.set(f"Error processing pasted content: {str(e)}")

def launch_metadata_importer(metadata_store=None):
    """Launch the metadata importer UI."""
    root = tk.Tk()
    root.title("SQL Lineage Analyzer - Metadata Importer")
    root.geometry("800x600")
    
    # Set application icon if available
    try:
        root.iconbitmap("assets/icon.ico")
    except:
        pass
    
    app = MetadataImporterUI(root, metadata_store)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
    
    return app.metadata_store

if __name__ == "__main__":
    # For testing
    metadata_store = launch_metadata_importer()
    print(f"Imported metadata for {len(metadata_store.metadata)} databases") 