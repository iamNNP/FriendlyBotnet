# FriendlyBotnet

Friendly Botnet to deal with multiple machines using SSH protocol.

## Installation

Activate the virtual environment:

```bash
cd FriendlyBotnet && python -m venv venv
```
```bash
source venv/bin/activate
```
On Linux and 
```bash
venv\Scripts\activate
```
On Windows
```bash
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


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)