# Project Setup

Follow these steps to set up and run the project:

## 1. Clone the Repository

```sh
git clone <repository-url>
cd <repository-name>
```

## 2. Create a Virtual Environment

Create a virtual environment using Python:

```sh
python -m venv venv
```

## 3. Activate the Virtual Environment

### On Windows:
```sh
venv\Scripts\activate
```

### On macOS/Linux:
```sh
source venv/bin/activate
```

> **Note:** Always activate the virtual environment before installing dependencies or running the application.

## 4. Install Dependencies

```sh
pip install -r requirements.txt
```


## 5. Find Your IPv4 Address on CMD

Before running the app, you need to find your device's IPv4 address (Wireless LAN adapter WiFi)

On Windows:

ipconfig

Look for the "IPv4 Address" under your active network connection.

On macOS/Linux:

```sh
ifconfig | grep 'inet '
```

or

```sh
hostname -I
```

## 6. Make an env file

```sh
DEVICE_IPV4=(yourip) no spaces dapat
```
ang other envs kay naa ras ato gc

## 7. Run the Application

```sh
python manage.py runserver "ip:port"
```

