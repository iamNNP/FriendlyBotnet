# FriendlyBotnet

Полезный ботнет для асинхронного управления несколькими устройствами с помощью протокола SSH

## Установка

Активируйте виртуальное окружение python

```bash
cd FriendlyBotnet && python -m venv venv

source venv/bin/activate # On Linux
venv\Scripts\activate # On Windows

pip install -r requirements.txt
```

## Использование

Установите докер и сбилдите докер-контейнеры
```bash
# skip on Windows, just start the Docker Engine app
sudo systemctl start docker.service
docker-compose up -d
```

Запустите приложение
```bash
python manage.py runserver
```
Сначала добавьте список подключений к желаемым компьютерам (в тестовом случае для докер-контейнеров, просто скопируйте содержимое из файла containers.txt)

Вы можете запускать команды на выбранных вами контейнерах (вы можете выбирать их кликая по ним)
![clickable containers image](./static/chrome_pQW7lIkkGH.png)
Вставьте свою команду сюда и нажмите кнопку Start command или Enter
![start command field](./static/ShareX_Ghif8goS6G.png)
Вы можете добавить сценарии (последовательность команд) и запускать их кликая по ним
![start command field](./static/chrome_2m3aESau5H.png)


Friendly Botnet to deal with multiple machines using SSH protocol.

## Installation

Activate the virtual environment:

```bash
cd FriendlyBotnet && python -m venv venv

source venv/bin/activate # On Linux
venv\Scripts\activate # On Windows

pip install -r requirements.txt
```

## Usage

Install Docker and build test containers
```bash
# skip on Windows, just start the Docker Engine app
sudo systemctl start docker.service
docker-compose up -d
```

Run the app
```bash
python manage.py runserver
```
First add SSH list of connections to your machines (in test case for docker containers, just copy it from containers.txt file)

You can run commands on selected containers (unselect them by clicking on the container card)
![clickable containers image](./static/chrome_pQW7lIkkGH.png)
Paste your command here and click enter, or press start command
![start command field](./static/ShareX_Ghif8goS6G.png)
You can add shortcuts (a sequence of commands) and run them by clicking on the buttons
![start command field](./static/chrome_2m3aESau5H.png)


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.