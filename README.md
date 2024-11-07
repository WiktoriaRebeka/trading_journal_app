
# Trading Journal with Leverage Calculator

This Trading Journal application helps traders document, analyze, and optimize trades, with features for risk management through leverage calculations and performance tracking. It includes interactive data visualizations, custom strategies, and user management to support a comprehensive trading experience.

## Features

- **Trade Logging**: Log trades with fields for entry, exit, strategy, currency pair, and outcome to track and analyze trading performance.
- **Leverage Calculator**: Calculate appropriate leverage, position size, and risk-reward ratios to optimize trade setup.
- **Performance Reports**: Access performance reports with visual representations of PnL, win rate, and strategy effectiveness.
- **Strategy Management**: Define and test strategies, complete with indicators, timeframes, and entry/exit rules.
- **User Management**: Secure registration, login, activation, and password reset functionalities.
- **Responsive Interface**: Interactive, user-friendly interface with dynamic updates, chart visualizations, and filtering options.

## Project Structure

The project is organized into Backend and Frontend components, with separate directories for each functionality.

### Backend

The backend is built with Django and consists of files and directories that manage data, user authentication, and application logic.

#### Core Files

- `manage.py`: Main Django file for executing commands, like running the server and managing migrations.
- `settings.py`: Configuration for Django settings, including database connections, installed apps, and middleware.
- `wsgi.py`: Serves the application for deployment in production.

#### Models and Data Management

- `models.py`: Defines data models for trade entries, strategies, and leverage calculations.
- `reports.py`: Generates reports on user trading performance, like win/loss ratios and PnL analysis.
- `strategies.py`: Contains the logic for creating and managing custom trading strategies.
- `migrations/`: Manages database schema changes and migrations.

#### User Management (`users/` Directory)

- `admin.py`: Configures user-related data within the Django admin interface.
- `forms.py`: Manages user registration, login, and profile forms.
- `models.py`: Defines user profiles and authentication models, supporting custom fields.
- `urls.py`: Routes for user-related pages, such as registration, login, and account activation.
- `views.py`: Contains view logic for user authentication and profile management.

#### Templates and Frontend Pages

- `templates/app_main/`: Main templates for dashboard, journal, reports, and strategies views.
- `templates/users/`: User-related HTML templates, including activation, login, and registration pages.

### Frontend

The frontend leverages JavaScript for dynamic functionality, HTML for page structure, and CSS for styling. Below are the core files and descriptions of their roles.

#### JavaScript Files

**Core Functionality**

- `addNewEntry.js`: Opens a modal for adding a new trade entry, collects form data, and sends it to the server to log the trade.
- `calculations.js`: Contains core calculation functions for risk, leverage, position sizing, and target prices, providing essential trade parameters for decision-making.
- `calendar.js`: Handles calendar navigation, allowing users to view monthly performance without page reloads.
- `dashboard.js`: Initializes and manages the dashboard's interactive elements, including navigation to other sections like the journal and strategies pages.

**Event Handling and UI Updates**

- `events.js`: Binds various events, such as resetting the form, switching target modes, and calculating trade metrics based on user input.
- `filterReports.js`: Manages filtering options on the reports page, allowing users to narrow down data based on date range, currency pairs, and strategies. It updates charts and tables with AJAX requests for real-time results.
- `journal_data.js`: Supports data interaction in the journal, including adding trades, updating entries, and applying filters to display relevant trades based on user criteria.
- `journal_style.js`: Controls the styling and layout of the journal table, managing scroll buttons and column widths to ensure readability and usability.
- `strategies.js`: Manages strategies within the application, allowing users to add, edit, or delete strategies and interactively update the strategies table.
- `ui.js`: Handles general UI updates, such as resetting the form, updating currency labels, and toggling visibility of elements based on user selections.

#### CSS Files

- `calendar.css`: Styles the calendar view, creating a grid layout and using colors to indicate positive or negative PnL for each day. Provides styling for days with and without trades, allowing users to quickly assess daily performance.
- `dashboard.css`: Styles the main dashboard, including the navigation bar, buttons, and leverage calculator sections. It ensures a clean layout with clearly defined sections and a professional look that aligns with the trading platform.
- `journal.css`: Manages the layout and styling of the journal table, including responsive columns and scrollable tables. Adds styles for scroll buttons and ensures that trade data remains easily accessible.

## Installation and Setup

### Prerequisites

- Python 3.8+
- Django 3.x or higher
- MySQL Workbench (for database management)

### Setup Instructions

1. Clone the repository.
2. Navigate to the project directory.
3. Set up a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Configure the database settings in `settings.py` to connect to your MySQL Workbench.
6. Run migrations:
    ```bash
    python manage.py migrate
    ```
7. Start the development server:
    ```bash
    python manage.py runserver
    ```
