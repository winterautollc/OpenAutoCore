# OpenAuto

**OpenAuto** is a free and open-source automotive shop management system built using **Python**, **PyQt6**, and **MySQL**. It is designed to help independent auto repair shops manage customers, vehicles, invoices, appointments, and more — all from one modular interface.

---

## 🚀 Features

- Customer and vehicle management
- Estimate and invoice tracking
- Scheduling and appointment calendar
- Custom pricing matrix
- MySQL database backend
- Modular PyQt6 UI with dark theme support
- Soft-delete/archive system to preserve data
- Multithreaded real-time UI updates

---

## Project Structure

```bash
OpenAuto/
├── main.py                  # App entry point
├── openauto/
│   ├── ui/                  # PyUIC or custom PyQt6 interface files
│   ├── managers/            # Handles business logic
│   ├── repositories/        # Database access layer (MySQL)
│   ├── themes/              # QSS styling files (light/dark mode)
│   └── old_files/           # Archived or deprecated code
├── tests/                   # Optional unit tests
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation (this file)
```

---

## 🧪 Installation

```bash
# Clone the repository
git clone https://github.com/winterautollc/OpenAutoCore.git
cd OpenAuto

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_windows.txt # use this for Windows
```

---

## 🛠 MySQL Setup

You’ll need to create a MySQL database and update `.env` variables:

```env
MYSQL_HOST=localhost
MYSQL_USER=openautoadmin
MYSQL_PASSWORD=OpenAuto1!
MYSQL_NAME=openauto
```

Optionally use `mysql_clone.py` to copy table structures for testing.

---

## 🖥 Usage

```bash
python main.py
```

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
You are free to use, modify, and distribute it — but proprietary forks are **not** allowed.

---

## ❤️ Contributing

Contributions are welcome! If you're interested in helping:
- Fork the repo
- Open a pull request
- Suggest features or report issues

---

## 📬 Contact

If you're an automotive shop interested in trying OpenAuto, or a developer looking to contribute, reach out at:

**📧 your.email@example.com**
