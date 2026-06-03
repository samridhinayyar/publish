import os
import sqlite3
import datetime
import threading
import pandas as pd
import numpy as np
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import joblib

# Scikit-Learn Imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, f1_score

# Reporting
from reportlab.pdfgen import canvas
import openpyxl

# ==================================================
# DATABASE MANAGER
# ==================================================
class DatabaseManager:
    def __init__(self, db_name="trading_terminal.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS models 
                              (id INTEGER PRIMARY KEY, name TEXT, accuracy REAL, date TEXT, path TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS predictions 
                              (id INTEGER PRIMARY KEY, date TEXT, prediction TEXT, confidence REAL, model_used TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS datasets 
                              (id INTEGER PRIMARY KEY, name TEXT, rows INTEGER, cols INTEGER, date TEXT)''')
            conn.commit()

    def log_dataset(self, name, rows, cols):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO datasets (name, rows, cols, date) VALUES (?, ?, ?, ?)",
                         (name, rows, cols, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

    def log_model(self, name, accuracy, path):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO models (name, accuracy, date, path) VALUES (?, ?, ?, ?)",
                         (name, accuracy, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), path))
            conn.commit()

    def log_prediction(self, prediction, confidence, model_used):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO predictions (date, prediction, confidence, model_used) VALUES (?, ?, ?, ?)",
                         (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prediction, confidence, model_used))
            conn.commit()

# ==================================================
# MACHINE LEARNING ENGINE
# ==================================================
class MLEngine:
    def __init__(self):
        self.data = None
        self.X_train = self.X_test = self.y_train = self.y_test = None
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = ""
        self.models = {
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "Decision Tree": DecisionTreeClassifier(),
            "Random Forest": RandomForestClassifier(n_estimators=100),
            "KNN": KNeighborsClassifier(n_neighbors=5),
            "Gradient Boosting": GradientBoostingClassifier(),
            "AdaBoost": AdaBoostClassifier(),
            "Extra Trees": ExtraTreesClassifier(),
            "SVM": SVC(probability=True)
        }
        self.results = {}

    def load_and_engineer(self, filepath):
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            # Auto Feature Engineering
            df['Open-Close'] = df['Open'] - df['Close']
            df['High-Low'] = df['High'] - df['Low']
            df['Daily Return'] = df['Close'].pct_change()
            df['MA_5'] = df['Close'].rolling(window=5).mean()
            df['MA_10'] = df['Close'].rolling(window=10).mean()
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
            df['Volatility'] = df['Daily Return'].rolling(window=10).std()
            df['Momentum'] = df['Close'] - df['Close'].shift(5)
            
            # Simple RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Target: 1 if next day closes higher, else 0
            df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
            
            df.dropna(inplace=True)
            self.data = df
            
            features = ['Open-Close', 'High-Low', 'Daily Return', 'MA_5', 'MA_10', 'MA_20', 'EMA_10', 'Volatility', 'Momentum', 'RSI']
            X = self.data[features]
            y = self.data['Target']

            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            self.X_train = self.scaler.fit_transform(self.X_train)
            self.X_test = self.scaler.transform(self.X_test)
            
            return True, f"Engineered {len(features)} features. Dataset ready."
        except Exception as e:
            return False, str(e)

    def train_all(self, progress_callback):
        self.results = {}
        best_acc = 0
        total_models = len(self.models)
        
        for i, (name, model) in enumerate(self.models.items()):
            try:
                model.fit(self.X_train, self.y_train)
                preds = model.predict(self.X_test)
                acc = accuracy_score(self.y_test, preds)
                
                self.results[name] = {
                    "Accuracy": acc,
                    "Precision": precision_score(self.y_test, preds, zero_division=0),
                    "F1 Score": f1_score(self.y_test, preds, zero_division=0)
                }
                
                if acc > best_acc:
                    best_acc = acc
                    self.best_model = model
                    self.best_model_name = name

                progress_callback((i + 1) / total_models, name)
            except Exception as e:
                print(f"Error training {name}: {e}")

        # Save best model
        os.makedirs("saved_models", exist_ok=True)
        model_path = f"saved_models/{self.best_model_name.replace(' ', '_')}.pkl"
        joblib.dump(self.best_model, model_path)
        
        return self.best_model_name, best_acc, model_path

    def predict_latest(self):
        if self.best_model is None or self.data is None:
            return None, 0
        latest_data = self.data.iloc[-1:][['Open-Close', 'High-Low', 'Daily Return', 'MA_5', 'MA_10', 'MA_20', 'EMA_10', 'Volatility', 'Momentum', 'RSI']]
        scaled_data = self.scaler.transform(latest_data)
        prediction = self.best_model.predict(scaled_data)[0]
        
        if hasattr(self.best_model, "predict_proba"):
            confidence = np.max(self.best_model.predict_proba(scaled_data)[0]) * 100
        else:
            confidence = 85.0 # Default fallback
            
        return "BUY" if prediction == 1 else "SELL", confidence

# ==================================================
# MAIN UI APPLICATION
# ==================================================
class AITradingTerminal(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Trading Terminal Pro")
        self.geometry("1600x900")
        self.minsize(1280, 720)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.db = DatabaseManager()
        self.ml = MLEngine()
        
        # UI Layout setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        
        # Content Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.frames = {}
        self.setup_pages()
        self.show_frame("Dashboard")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        ctk.CTkLabel(self.sidebar_frame, text="AI Trading Pro", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=20, pady=(30, 30))
        
        pages = ["Dashboard", "Dataset Manager", "Model Training", "Prediction Center", "Reports", "Settings"]
        for i, page in enumerate(pages):
            btn = ctk.CTkButton(self.sidebar_frame, text=page, font=ctk.CTkFont(size=14), 
                                command=lambda p=page: self.show_frame(p), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
            btn.grid(row=i+1, column=0, padx=20, pady=10, sticky="ew")

    def setup_pages(self):
        for F in (DashboardPage, DatasetPage, TrainingPage, PredictionPage, ReportsPage, SettingsPage):
            page_name = F.__name__.replace("Page", "")
            if page_name == "Dataset": page_name = "Dataset Manager"
            if page_name == "Training": page_name = "Model Training"
            if page_name == "Prediction": page_name = "Prediction Center"
            
            frame = F(parent=self.main_frame, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()

# ==================================================
# PAGE CLASSES
# ==================================================
class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)

class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=10)
        
        self.create_card(self.cards_frame, "Best Model", "None", "cyan").pack(side="left", fill="both", expand=True, padx=10)
        self.create_card(self.cards_frame, "Highest Accuracy", "0.0%", "lime").pack(side="left", fill="both", expand=True, padx=10)
        self.create_card(self.cards_frame, "Total Predictions", "0", "orange").pack(side="left", fill="both", expand=True, padx=10)

    def create_card(self, parent, title, value, color):
        frame = ctk.CTkFrame(parent, height=150)
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=16)).pack(pady=(20, 5))
        lbl = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=36, weight="bold"), text_color=color)
        lbl.pack()
        setattr(self, f"lbl_{title.replace(' ', '_').lower()}", lbl)
        return frame

    def on_show(self):
        with self.controller.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM predictions")
            preds = cursor.fetchone()[0]
            cursor.execute("SELECT name, accuracy FROM models ORDER BY accuracy DESC LIMIT 1")
            best = cursor.fetchone()
            
            self.lbl_total_predictions.configure(text=str(preds))
            if best:
                self.lbl_best_model.configure(text=best[0])
                self.lbl_highest_accuracy.configure(text=f"{best[1]:.2%}")

class DatasetPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ctk.CTkLabel(self, text="Dataset Manager", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Upload CSV / Excel", command=self.load_data, height=40).pack(side="left", padx=10)
        
        self.status_lbl = ctk.CTkLabel(self, text="No dataset loaded.", text_color="gray")
        self.status_lbl.pack(anchor="w", padx=10, pady=10)
        
        # Plot Area
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self):
        filepath = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv *.xlsx")])
        if not filepath: return
        
        self.status_lbl.configure(text="Processing data... please wait.")
        self.update()
        
        success, msg = self.controller.ml.load_and_engineer(filepath)
        if success:
            df = self.controller.ml.data
            self.controller.db.log_dataset(os.path.basename(filepath), len(df), len(df.columns))
            self.status_lbl.configure(text=f"Success: {msg} | Shape: {df.shape}", text_color="lime")
            self.plot_data(df)
        else:
            self.status_lbl.configure(text=f"Error: {msg}", text_color="red")

    def plot_data(self, df):
        for widget in self.plot_frame.winfo_children(): widget.destroy()
        fig = Figure(figsize=(10, 4), dpi=100, facecolor='#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        ax.plot(df['Close'].values, color='cyan', label="Close Price")
        ax.plot(df['MA_20'].values, color='orange', label="20-Day MA")
        ax.tick_params(colors='white')
        ax.legend(loc="upper left")
        
        canvas_widget = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill="both", expand=True)

class TrainingPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ctk.CTkLabel(self, text="Model Training", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        self.train_btn = ctk.CTkButton(self, text="Start Auto-Training Pipeline", font=ctk.CTkFont(size=18), height=50, command=self.start_training)
        self.train_btn.pack(pady=20)
        
        self.progress = ctk.CTkProgressBar(self, width=600)
        self.progress.set(0)
        self.progress.pack(pady=10)
        
        self.log_box = ctk.CTkTextbox(self, height=300, font=("Consolas", 14))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=20)

    def log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def start_training(self):
        if self.controller.ml.data is None:
            messagebox.showwarning("Warning", "Please load a dataset first!")
            return
        
        self.train_btn.configure(state="disabled")
        self.log_box.delete("1.0", "end")
        self.log("Initializing Training Pipeline...")
        
        # Run in thread to keep UI responsive
        threading.Thread(target=self._run_training).start()

    def _run_training(self):
        def update_progress(val, name):
            self.progress.set(val)
            self.log(f"Training {name} completed.")
            
        best_name, best_acc, path = self.controller.ml.train_all(update_progress)
        self.controller.db.log_model(best_name, best_acc, path)
        
        self.log(f"\n=======================")
        self.log(f"TRAINING COMPLETE")
        self.log(f"Best Model: {best_name}")
        self.log(f"Accuracy: {best_acc:.2%}")
        self.log(f"Model saved to Database & Disk.")
        self.train_btn.configure(state="normal")

class PredictionPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ctk.CTkLabel(self, text="Prediction Center", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkButton(self, text="Generate Latest Market Prediction", height=50, command=self.predict).pack(pady=20)
        
        self.result_frame = ctk.CTkFrame(self, height=300, fg_color="#2b2b2b")
        self.result_frame.pack(fill="x", padx=50, pady=20)
        self.result_frame.pack_propagate(False)
        
        self.signal_lbl = ctk.CTkLabel(self.result_frame, text="--", font=ctk.CTkFont(size=80, weight="bold"))
        self.signal_lbl.pack(pady=(50, 10))
        
        self.conf_lbl = ctk.CTkLabel(self.result_frame, text="Confidence: --%", font=ctk.CTkFont(size=20))
        self.conf_lbl.pack()

    def predict(self):
        signal, conf = self.controller.ml.predict_latest()
        if signal is None:
            messagebox.showerror("Error", "Train a model first!")
            return
            
        color = "lime" if signal == "BUY" else "red"
        self.signal_lbl.configure(text=signal, text_color=color)
        self.conf_lbl.configure(text=f"Confidence: {conf:.2f}%")
        
        self.controller.db.log_prediction(signal, conf, self.controller.ml.best_model_name)

class ReportsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ctk.CTkLabel(self, text="Reports & Analytics", font=ctk.CTkFont(family="Inter", size=28, weight="bold"), text_color="#FFFFFF").pack(anchor="w", pady=(0, 10))
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(btn_frame, text="Generate & Open PDF", command=self.export_pdf, height=40, font=ctk.CTkFont(weight="bold"), corner_radius=6, fg_color="#FFFFFF", text_color="#000000", hover_color="#E5E5E5").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Export CSV", command=self.export_excel, height=40, font=ctk.CTkFont(weight="bold"), corner_radius=6, fg_color="#262626", text_color="#FFFFFF", hover_color="#3E3E3E").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Refresh Live Preview", command=self.load_preview, height=40, font=ctk.CTkFont(weight="bold"), corner_radius=6, fg_color="#262626", text_color="#FFFFFF", hover_color="#3E3E3E").pack(side="left", padx=10)

        # In-App Excel / Database Preview Area
        ctk.CTkLabel(self, text="Live Data Preview", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#A3A3A3").pack(anchor="w", pady=(20, 5))
        
        self.table_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#1A1A1A", border_width=1, border_color="#262626")
        self.table_frame.pack(fill="both", expand=True, pady=10)
        
        # Using standard ttk Treeview for the data grid, styled for dark mode
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#1A1A1A", foreground="#FFFFFF", fieldbackground="#1A1A1A", borderwidth=0)
        style.configure("Treeview.Heading", background="#262626", foreground="#FFFFFF", borderwidth=0, font=("Inter", 10, "bold"))
        style.map("Treeview", background=[("selected", "#3E3E3E")])

        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Date", "Prediction", "Confidence", "Model"), show="headings")
        
        headings = ["ID", "Date", "Prediction", "Confidence", "Model"]
        for col in headings:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_preview()

    def load_preview(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Fetch and display
        with self.controller.db.get_connection() as conn:
            df = pd.read_sql("SELECT * FROM predictions ORDER BY id DESC LIMIT 50", conn)
            
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(row['id'], row['date'], row['prediction'], f"{row['confidence']:.2f}%", row['model_used']))

    def export_pdf(self):
        with self.controller.db.get_connection() as conn:
            df = pd.read_sql("SELECT * FROM predictions", conn)
            
        if df.empty:
            messagebox.showinfo("Notice", "No data to export.")
            return
            
        filename = f"Summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, "Terminal Activity Summary")
        
        c.setFont("Helvetica", 12)
        y = 750
        for idx, row in df.head(30).iterrows():
            c.drawString(50, y, f"[{row['date']}] {row['prediction']} | {row['confidence']:.2f}% | Model: {row['model_used']}")
            y -= 20
            if y < 50: break
            
        c.save()
        
        # Native OS Call to open the PDF instantly
        try:
            if os.name == 'nt': # Windows
                os.startfile(filename)
            elif os.name == 'posix': # macOS / Linux
                import subprocess
                subprocess.call(('open', filename))
        except Exception as e:
            messagebox.showinfo("Success", f"File saved as: {filename}. Could not open automatically.")

    def export_excel(self):
        with self.controller.db.get_connection() as conn:
            df = pd.read_sql("SELECT * FROM predictions", conn)
        if df.empty: 
            messagebox.showinfo("Notice", "No data to export.")
            return
            
        filename = f"Data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"File written: {filename}")
        
class SettingsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        self.theme_switch = ctk.CTkSwitch(self, text="Light Theme", command=self.toggle_theme)
        self.theme_switch.pack(anchor="w", padx=20, pady=20)
        
        ctk.CTkButton(self, text="Reset Database", fg_color="red", hover_color="darkred", command=self.reset_db).pack(anchor="w", padx=20, pady=20)

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def reset_db(self):
        if messagebox.askyesno("Confirm", "Delete all saved data and models?"):
            os.remove("trading_terminal.db")
            self.controller.db.init_db()
            messagebox.showinfo("Success", "Database reset complete.")

if __name__ == "__main__":
    app = AITradingTerminal()
    app.mainloop()
