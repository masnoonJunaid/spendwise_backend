# SpendWise - Personal Budget Tracker

SpendWise is a personal budget tracking application that helps users manage their income, expenses, and overall financial health. It allows users to categorize transactions, set budgets, and compare their expenses against their budget.

## Features
- User authentication (register, login, token refresh)
- Add and manage **categories** (income & expense categories)
- Record **transactions** (income & expenses)
- View **transaction summaries** and filters by date, category, and amount
- Set and manage **monthly budgets**
- Compare **budget vs actual expenses**
- Secure API endpoints using Django REST Framework

## Project Structure
```
├── django_backend/  # Main Django project directory
│   ├── finance/  # Django app
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   ├── spend_wise/  # Django project configuration directory
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── .gitIgnore
│   ├── manage.py  # Django project management script
│   ├── README.md
│   ├── requirements.txt  # List of project dependencies
├── venv/  # Virtual environment
```

## Setup Instructions

### 1️⃣ Prerequisites
Ensure you have the following installed:
- Python 3.x
- Django 4.x
- Django REST Framework
- PostgreSQL (or SQLite for local development)
- Virtual environment (optional but recommended)

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/spendwise.git
cd spendwise/django_backend
```

### 2️⃣ Create .env file and create these variables with credential shared
```bash
DATABASE_URL=''
JWT_SECRET=''
DJANGO_SECRET=''
```

### 3️⃣ Create a Virtual Environment & Activate It
```bash
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate  # For Windows
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Set Up the Database
Modify `settings.py` to configure your database (PostgreSQL recommended).
Then, run:
```bash
python manage.py migrate
```

### 6️⃣ Create a Superuser
```bash
python manage.py createsuperuser
```

### 7️⃣ Run the Development Server
```bash
python manage.py runserver
```
Access the API at `http://127.0.0.1:8000/`

## API Endpoints

### 🔹 Authentication
| Method | Endpoint         | Description |
|--------|----------------|-------------|
| POST   | `/api/register/` | Register a new user |
| POST   | `/api/login/` | User login |
| POST   | `/api/refresh/` | Refresh access token |

### 🔹 Categories
| Method | Endpoint              | Description |
|--------|----------------------|-------------|
| GET    | `/api/categories/`    | List all categories |
| POST   | `/api/categories/`    | Create a new category |
| PUT    | `/api/categories/{id}/` | Update a category |
| DELETE | `/api/categories/{id}/` | Delete a category |

### 🔹 Transactions
| Method | Endpoint                  | Description |
|--------|--------------------------|-------------|
| GET    | `/api/transactions/`      | List all transactions |
| POST   | `/api/transactions/`      | Add a new transaction |
| PUT    | `/api/transactions/{id}/` | Update a transaction |
| DELETE | `/api/transactions/{id}/` | Delete a transaction |

### 🔹 Budget
| Method | Endpoint               | Description |
|--------|-----------------------|-------------|
| GET    | `/api/budget/`        | View current budget |
| POST   | `/api/budget/`        | Set a new budget |
| GET    | `/api/budget-summary/{YYYY-MM}/` | View budget vs. actual expenses for a given month |

## Next Steps
- Frontend development with **React + D3.js** for budget visualization
- Adding filters and pagination for transactions
- Enhancing security with token-based authentication

## Contributing
Assesment project, Contribution not encouraged! 🚀

