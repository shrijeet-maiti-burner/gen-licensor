# GenLicensor

**GenLicensor** utilizes generative AI to validate the legitimacy of software installations on corporate devices, ensuring they comply with organizational policies and licensing standards.

## Overview

**GenLicensor** consists of three key components that systematically scan installed software, verify it against approved standards using AI, and manage compliance through automated reminders and uninstallations.

## Components Description

### 1. Fetch Script (`fetch.py`)

#### Functionality:
- Scans various registry paths on Windows systems to gather detailed information about all installed software, including hidden installations.

#### Key Details:
- **Scanned Registry Paths**:
  - `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`
  - `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`
  - `HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Installer\Products`

- **Data Processing**:
  - Cleans software names by removing numeric versions and metadata, ensuring consistent entries for database storage.

### 2. Query Script (`query.py`)

#### Functionality:
- Queries IBM Watson AI for details on non-approved software, including license type, name, safety status, and category.

#### AI Integration:
- Utilizes `ibm/granite-13b-instruct-v2` for its precision in natural language processing, enabling it to generate direct, concise responses essential for regulatory compliance.

### 3. Uninstall Script (`uninstall.py`)

#### Functionality:
- Monitors and manages the uninstallation process for software flagged as unsafe. Sends email reminders and automatically uninstalls software after non-compliance.

#### Operations:
- Retrieves uninstall commands directly from the registry and executes them silently to avoid user intervention, designed for seamless operation in an enterprise environment.

## Proof of Concept (PoC) Implementation

### Usage of CSVs:
- **Rationale**: Due to IBM Watson AI token limitations and to facilitate rapid development and testing, CSV files are used instead of a full database in the PoC phase.
- **Functionality**:
  - `query.py` simulates querying AI for software details and logs responses into a CSV.
  - `uninstall.py` uses a CSV to track software marked as unsafe, managing reminders and uninstallations.

### Transition to Production:
- In the fully deployed state, comprehensive MySQL databases will replace CSVs, enhancing data handling capabilities and supporting extensive enterprise-level operations.

## Setup Instructions

### Prerequisites:
- Install Python 3.8+ and MySQL Server 5.7+.
- Configure database connections in scripts and SMTP details for email functionalities in `uninstall.py`.

### Execution:
Run the scripts sequentially to ensure system functionality:
```bash
python fetch.py  # Fetches and stores software details.
python query.py  # Queries AI and updates records.
python uninstall.py  # Manages compliance actions.
```
## Configuration Details

- **Database**: Set up `mysql.connector` in each script for MySQL interactions.
- **SMTP Settings**: Configured in `uninstall.py` for sending email notifications.
- **API Keys**: Insert IBM Watson AI API keys in `query.py`.

## Dependencies

- Required Python packages include `pandas`, `mysql-connector-python`, and `requests`.
- Dependencies also include MySQL server, an SMTP server for emails, and IBM Watson AI service access.

## Licensing

This project is under the MIT License.