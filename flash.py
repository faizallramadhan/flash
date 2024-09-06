import requests
import json
import urllib.parse

def parse_query_params(query):
    return dict(urllib.parse.parse_qsl(query))

def get_common_headers(authorization_token, x_custom_token):
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {authorization_token.strip()}',
        'cache-control': 'no-cache',
        'connection': 'keep-alive',
        'content-type': 'application/json',
        'host': 'api.flashflash.vip',
        'origin': 'https://tma.flashflash.vip',
        'pragma': 'no-cache',
        'referer': 'https://tma.flashflash.vip/',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128", "Microsoft Edge WebView2";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
        'x-custom-token': f'Bearer {x_custom_token.strip()}'
    }

def get_tasks(authorization_token, x_custom_token):
    try:
        response = requests.get('https://api.flashflash.vip/task', headers=get_common_headers(authorization_token, x_custom_token))
        response.raise_for_status()
        tasks = response.json()

        if not tasks:
            print('All Tasks Already Claimed 100%')
            return

        print('Tasks:')
        for task in tasks:
            print(f'{task["id"]} | {task["prize"]} | {task["title"]}')

        for task in tasks:
            post_task(task["id"], authorization_token, x_custom_token)

    except requests.RequestException as e:
        print('Error fetching tasks:', e)

def post_task(task_id, authorization_token, x_custom_token):
    try:
        response = requests.post('https://api.flashflash.vip/task',
                                 json={'id': task_id},
                                 headers=get_common_headers(authorization_token, x_custom_token))
        response.raise_for_status()
        print(f'Task {task_id} posted successfully.')
    except requests.RequestException as e:
        print(f'Error posting task {task_id}:', e)

def daily_login(authorization_token, x_custom_token):
    try:
        response = requests.post('https://tma.flashflash.vip/task/daily',
                                 headers=get_common_headers(authorization_token, x_custom_token))
        response.raise_for_status()
        print('Daily login successful.')
    except requests.RequestException as e:
        if response.json().get('message') == 'Cannot claim daily task again!':
            print('Daily Already Claimed')
        else:
            print('Error during daily login:', e)

def main():
    try:
        with open('auth.txt', 'r') as file:
            accounts = [line.strip() for line in file if line.strip()]

        for index, account in enumerate(accounts):
            try:
                params = parse_query_params(account)
                query_id = params['hash']
                decoded_user = urllib.parse.unquote(params['user'])
                parsed_user = json.loads(decoded_user)

                telegram_user_id = parsed_user['id']
                user_name = f"{parsed_user['first_name']} {parsed_user['last_name']}"
                token = account.strip()

                payload = {
                    'data': {
                        'queryId': query_id,
                        'telegramUserId': telegram_user_id,
                        'referralCode': '',
                        'userName': user_name,
                        'token': token,
                        'xCustomToken': ''
                    }
                }

                response = requests.post('https://api.flashflash.vip/auth/login',
                                         json=payload,
                                         headers=get_common_headers(token, 'Bearer'))
                response.raise_for_status()
                data = response.json()
                api_token = data['token']
                user = data['user']
                x_custom_token = api_token

                print('==================================================================')
                print(f'Response for Account {index + 1} [Line {index + 1} in auth.txt]:')
                print(f'Token: {api_token}')
                print(f'User: {user["telegramUserId"]} | {user["userName"]} | {user["point"]}')
                print(f'ETH: {user.get("ethWalletAddress", "N/A")}')
                print(f'TON: {user.get("tonWalletAddress", "N/A")}')
                print('')

                daily_login(token, x_custom_token)
                get_tasks(token, x_custom_token)
            except requests.RequestException as e:
                print(f'Error for account {index + 1} [Line {index + 1} in auth.txt]:', e)

    except FileNotFoundError:
        print('Error reading auth.txt')

if __name__ == '__main__':
    main()
