# Catalyst Communications

Catalyst Communications is a modern Communication and Operations Automation (CoA) system designed to streamline
workflows, enhance collaboration, and automate tasks. Built using **Django** and **Bootstrap**, it offers a seamless and
responsive user experience for businesses aiming to optimize their communication and operational efficiency.

## Features
- **Task Management**: Organize and track tasks with an intuitive interface.
- **Automation**: Automate repetitive operations using Celery and Redis.
- **RESTful APIs**: Extend and integrate with other platforms seamlessly.
- **Responsive Design**: Built with Bootstrap for a consistent experience across devices.
- **Scalable Architecture**: Powered by Django and PostgreSQL for robust performance.

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: Bootstrap (HTML, CSS, JavaScript)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **APIs**: Django REST Framework
- **Real-Time Communication**: WebSockets via Django Channels

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Node.js (optional for additional frontend tools)

### Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/hesham-04/catalyst-communications.git
    cd catalyst-communications
    ```
2. Set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure the `.env` file with your database and Redis settings.
5. Apply migrations:
    ```bash
    python manage.py makemigrations accounts core  assets vendor loan invoice quotation expense loan customer project transaction
    python manage.py migrate
    ```
6. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

- Access the application at `http://127.0.0.1:8000` in your browser.
- Explore task management, collaboration tools, and other features.

## Contributing

We welcome contributions! Follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature-name
    ```
3. Make your changes and commit them:
    ```bash
    git commit -m "Description of changes"
    ```
4. Push to your branch:
    ```bash
    git push origin feature-name
    ```
5. Open a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or feedback, please contact us
at [support@catalystcommunications.com](mailto:support@catalystcommunications.com).

## Imports Order
Recommended Import Order
Based on the dependencies, the correct order for importing the data is:

Customer
Lender
Project
Invoice
Expense
Loan
Loan Return
Sheet8 (Transactions)
