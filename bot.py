import requests
from colorama import init, Fore, Style
import json
import time
import random
import logging


init()


logging.basicConfig(filename='request_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def read_tokens(file_path):
    try:
        with open(file_path, 'r') as file:
            tokens = []
            for line in file:
                line = line.strip()
                if line and ':' in line:
                    bearer_token, refresh_token = line.split(':', 1)
                    tokens.append((bearer_token, refresh_token))
        logging.info(f"Read {len(tokens)} token pairs from {file_path}")
        return tokens
    except FileNotFoundError:
        print(f"{Fore.RED}Error: {file_path} file not found!{Style.RESET_ALL}")
        logging.error(f"{file_path} file not found")
        return []
    except Exception as e:
        print(f"{Fore.RED}Error reading {file_path}: {str(e)}{Style.RESET_ALL}")
        logging.error(f"Error reading {file_path}: {str(e)}")
        return []

def read_proxies(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        logging.info(f"Read {len(proxies)} proxies from {file_path}")
        return proxies
    except FileNotFoundError:
        print(f"{Fore.RED}Error: {file_path} file not found!{Style.RESET_ALL}")
        logging.error(f"{file_path} file not found")
        return []
    except Exception as e:
        print(f"{Fore.RED}Error reading {file_path}: {str(e)}{Style.RESET_ALL}")
        logging.error(f"Error reading {file_path}: {str(e)}")
        return []

def get_proxy_config(proxy):
    try:
        user_pass, ip_port = proxy.split('@')
        username, password = user_pass.split(':')
        ip, port = ip_port.split(':')
        return {
            'http': f'http://{username}:{password}@{ip}:{port}',
            'https': f'http://{username}:{password}@{ip}:{port}'
        }
    except ValueError:
        print(f"{Fore.RED}Invalid proxy format: {proxy}{Style.RESET_ALL}")
        logging.error(f"Invalid proxy format: {proxy}")
        return None

def make_session_request(bearer_token, refresh_token, proxy_config, retries=3):
    url = 'https://auth.privy.io/api/v1/sessions'
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {bearer_token}',
        'content-type': 'application/json',
        'origin': 'https://app.megaphone.xyz',
        'priority': 'u=1, i',
        'privy-app-id': 'cmad061qo006sk30nmcppln0s',
        'privy-ca-id': '14bcb3bf-53d8-4fcf-b1a0-bcf275a05528',
        'privy-client': 'react-auth:2.23.0',
        'referer': 'https://app.megaphone.xyz/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
    }
    payload = {'refresh_token': refresh_token}

    
    session_cookies = {
        'cf_clearance': 'x_YZJcX1q2R4RWHQ8wfFh7FIypTwlEK2C3fj99ighEQ-1758797701-1.2.1.1-EeehQ8JZvqR55QaU2SeZc8.pwSEl9u9yR3Sp5nh1gOIGJdgJp.muuRCm.YqYPcIimwTk2q3BaNdCbAe5WFaCqHu5GlGGEvhl8GjkpDwdQCu8vRRQPSlygizB7ENftA3569LSjwAVUa5pF6N_8QeQFlcgazcFnGu4vdV.8375FUjC2Ay9sQE3a.ztOlf.aDIn2YRDw4sUvvu.X2KCiP3Z4CnJVRD8lARewlMyd_aV4PM',
        '__cf_bm': 'QP_9OROsm0dpX7_WIE_OjQ1q8RTVMjkmbeklnrAV8Ao-1758797740-1.0.1.1-cwSFMscC3Zy9wW.7tkXdziGCMO50xcZu2lKp6SnNcMd6PgTdBH1_i2OsNyIlo_0URx6czDmwDmM2rALXH0r4lQ7y7gd.Ol1_4zW4fXLRxEQ',
        '_cfuvid': 'EaBOkjpt9Za4u2URtX0KcX4DT5EZxz1sbK5MTVdzQFE-1758797740851-0.0.1.1-604800000'
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, cookies=session_cookies, json=payload, proxies=proxy_config, timeout=10)
            if response.status_code == 200:
                try:
                    session_data = response.json()
                except ValueError:
                    print(f"{Fore.RED}Session response is not valid JSON: {response.text}{Style.RESET_ALL}")
                    logging.error(f"Session response is not valid JSON: {response.text}")
                    return None
                if isinstance(session_data, dict) and 'privy_access_token' in session_data and 'identity_token' in session_data:
                    print(f"{Fore.GREEN}Session request successful for token!{Style.RESET_ALL}")
                    logging.info(f"Session request successful for refresh_token {refresh_token[:10]}...")
                    logging.info(f"Tokens received: privy_access_token={session_data['privy_access_token'][:10]}..., identity_token={session_data['identity_token'][:10]}...")
                    return session_data
                else:
                    print(f"{Fore.RED}Session response missing required tokens or invalid: {session_data}{Style.RESET_ALL}")
                    logging.error(f"Session response missing required tokens or invalid: {session_data}")
                    return None
            else:
                print(f"{Fore.RED}Session request failed with status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")
                logging.error(f"Session request failed with status {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error making session request (attempt {attempt + 1}/{retries}): {str(e)}{Style.RESET_ALL}")
            logging.error(f"Session request error (attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)
            continue
    return None

def make_activity_request(tokens, proxy_config, retries=3):
    url = 'https://app.megaphone.xyz/_serverFn/src_data_pages_ts--verifyActivity_createServerFn_handler?createServerFn'
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://app.megaphone.xyz',
        'priority': 'u=1, i',
        'referer': 'https://app.megaphone.xyz/pages/solstice?r=uU527uiFWtH3',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-tsr-redirect': 'manual'
    }
    activity_cookies = {
        '_clck': 'iscmkx^2^fzm^0^2050',
        'privy-session': 't',
        'privy-token': tokens.get('privy_access_token', ''),
        '_clsk': '169besn^1758797747831^2^0^a.clarity.ms/collect',
        'privy-id-token': tokens.get('identity_token', ''),
        'cf_clearance': 'x_YZJcX1q2R4RWHQ8wfFh7FIypTwlEK2C3fj99ighEQ-1758797701-1.2.1.1-EeehQ8JZvqR55QaU2SeZc8.pwSEl9u9yR3Sp5nh1gOIGJdgJp.muuRCm.YqYPcIimwTk2q3BaNdCbAe5WFaCqHu5GlGGEvhl8GjkpDwdQCu8vRRQPSlygizB7ENftA3569LSjwAVUa5pF6N_8QeQFlcgazcFnGu4vdV.8375FUjC2Ay9sQE3a.ztOlf.aDIn2YRDw4sUvvu.X2KCiP3Z4CnJVRD8lARewlMyd_aV4PM',
        '__cf_bm': 'QP_9OROsm0dpX7_WIE_OjQ1q8RTVMjkmbeklnrAV8Ao-1758797740-1.0.1.1-cwSFMscC3Zy9wW.7tkXdziGCMO50xcZu2lKp6SnNcMd6PgTdBH1_i2OsNyIlo_0URx6czDmwDmM2rALXH0r4lQ7y7gd.Ol1_4zW4fXLRxEQ',
        '_cfuvid': 'EaBOkjpt9Za4u2URtX0KcX4DT5EZxz1sbK5MTVdzQFE-1758797740851-0.0.1.1-604800000'
    }

    payload = {
        'data': {
            'activityId': 'cabd7970-050e-4c24-a596-c12370184d95'
        },
        'context': {}
    }

    logging.info(f"Activity request cookies: privy-token={activity_cookies['privy-token'][:10]}..., privy-id-token={activity_cookies['privy-id-token'][:10]}...")
    logging.info(f"Activity request payload: {json.dumps(payload)}")

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, cookies=activity_cookies, json=payload, proxies=proxy_config, timeout=10)
            if response.status_code == 200:
                print(f"{Fore.GREEN}Activity request successful!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Response:{Style.RESET_ALL}")
                print(json.dumps(response.json(), indent=2))
                logging.info(f"Activity request successful: {json.dumps(response.json())}")
            else:
                print(f"{Fore.RED}Activity request failed with status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")
                logging.error(f"Activity request failed with status {response.status_code}: {response.text}")
            return
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error making activity request (attempt {attempt + 1}/{retries}): {str(e)}{Style.RESET_ALL}")
            logging.error(f"Activity request error (attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)
            continue

def countdown_timer(hours):
    seconds = hours * 3600
    print(f"{Fore.YELLOW}No tokens left. Starting 20-hour countdown...{Style.RESET_ALL}")
    logging.info("Starting 20-hour countdown")
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        print(f"{Fore.YELLOW}Time remaining: {hours:02d}:{mins:02d}:{secs:02d}{Style.RESET_ALL}", end='\r')
        time.sleep(1)
        seconds -= 1
    print(f"{Fore.GREEN}Countdown finished! Restarting...{Style.RESET_ALL}")
    logging.info("Countdown finished, restarting")

def main():
    while True:
        
        tokens = read_tokens('token.txt')
        proxies = read_proxies('proxy.txt')

        if not tokens:
            print(f"{Fore.RED}No tokens found in token.txt!{Style.RESET_ALL}")
            countdown_timer(20)
            continue

        
        valid_proxies = []
        if proxies:
            for proxy in proxies:
                proxy_config = get_proxy_config(proxy)
                if proxy_config:
                    valid_proxies.append(proxy)
            if valid_proxies:
                print(f"{Fore.CYAN}Found {len(valid_proxies)} proxies with valid format{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}No valid proxies found! Using no proxy.{Style.RESET_ALL}")
                logging.warning("No valid proxies found, proceeding without proxy")
        else:
            print(f"{Fore.RED}No proxies found in proxy.txt! Using no proxy.{Style.RESET_ALL}")
            logging.warning("No proxies found, proceeding without proxy")
            valid_proxies = []

        
        for bearer_token, refresh_token in tokens:
            print(f"{Fore.CYAN}Processing refresh_token: {refresh_token[:10]}...{Style.RESET_ALL}")
            logging.info(f"Processing refresh_token: {refresh_token[:10]}...")

            
            proxy_config = None
            if valid_proxies:
                proxy = random.choice(valid_proxies)
                print(f"{Fore.CYAN}Using proxy: {proxy}{Style.RESET_ALL}")
                logging.info(f"Using proxy: {proxy}")
                proxy_config = get_proxy_config(proxy)
                if not proxy_config:
                    print(f"{Fore.YELLOW}Skipping token due to invalid proxy format.{Style.RESET_ALL}")
                    logging.warning("Skipping token due to invalid proxy format")
                    continue
            else:
                print(f"{Fore.CYAN}No valid proxies, proceeding without proxy{Style.RESET_ALL}")
                logging.info("No valid proxies, proceeding without proxy")

            
            session_response = make_session_request(bearer_token, refresh_token, proxy_config)
            
            if session_response:
                
                tokens_dict = {
                    'privy_access_token': session_response.get('privy_access_token'),
                    'identity_token': session_response.get('identity_token')
                }
            else:
                print(f"{Fore.YELLOW}Session request failed, skipping activity request.{Style.RESET_ALL}")
                logging.warning("Session request failed, skipping activity request")
                continue

            
            if tokens_dict['privy_access_token'] and tokens_dict['identity_token']:
                make_activity_request(tokens_dict, proxy_config)
            else:
                print(f"{Fore.RED}Skipping activity request due to missing or invalid tokens.{Style.RESET_ALL}")
                logging.error("Skipping activity request due to missing or invalid tokens")
            
            
            time.sleep(2)

        
        countdown_timer(20)

if __name__ == "__main__":
    main()
