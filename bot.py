import aiohttp
import asyncio
import json
import os
import logging
import urllib.parse
from colorama import *
from datetime import datetime
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SnapsterTradingApp:
    def __init__(self, user_id, authorization):
        self.user_id = str(user_id)
        self.authorization = authorization

    def get_headers(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'prod.snapster.bot',
            'Origin': 'https://prod.snapster.bot',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'priority': 'u=1, i',
            'Referer': 'https://prod.snapster.bot/daily',
            'Sec-Ch-Ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128", "Microsoft Edge WebView2";v="128"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Telegram-Data': self.authorization.strip(),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        }
        return headers

    async def fetch(self, http, url, method='GET', payload=None):
        headers = self.get_headers()
        try:
            if method == 'GET':
                response = await http.get(url, headers=headers)
            elif method == 'POST':
                response = await http.post(url, headers=headers, json=payload)
            else:
                raise ValueError("Unsupported HTTP method")

            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except aiohttp.ClientResponseError as e:
            logger.error(f"Client response error: {e}")
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Client connection error: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        await asyncio.sleep(3)
        return None

    async def get_user_info(self, http):
        url = f'https://prod.snapster.bot/api/user/getUserByTelegramId?telegramId={self.user_id}'
        return await self.fetch(http, url)

    async def claim_mining(self, http):
        payload = {'telegramId': self.user_id}
        url = 'https://prod.snapster.bot/api/user/claimMiningBonus'
        return await self.fetch(http, url, method='POST', payload=payload)

    async def start_daily(self, http):
        payload = {'telegramId': self.user_id}
        url = 'https://prod.snapster.bot/api/dailyQuest/startDailyBonusQuest'
        return await self.fetch(http, url, method='POST', payload=payload)

    async def claim_referrals(self, http):
        payload = {'telegramId': self.user_id}
        url = 'https://prod.snapster.bot/api/referral/claimReferralPoints'
        return await self.fetch(http, url, method='POST', payload=payload)
    
    async def get_quests(self, http):
        url = f'https://prod.snapster.bot/api/quest/getQuests?telegramId={self.user_id}'
        return await self.fetch(http, url)

    async def start_quest(self, http, quest_id):
        payload = {'telegramId': self.user_id, 'questId': quest_id}
        url = 'https://prod.snapster.bot/api/quest/startQuest'
        return await self.fetch(http, url, method='POST', payload=payload)

    async def claim_quest(self, http, quest_id):
        payload = {'telegramId': self.user_id, 'questId': quest_id}
        url = 'https://prod.snapster.bot/api/quest/claimQuestBonus'
        return await self.fetch(http, url, method='POST', payload=payload)

async def load_auth(file_path):
    try:
        with open(file_path, 'r') as file:
            authorizations = file.readlines()
            log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: "
                f"{Fore.WHITE + Style.BRIGHT}{len(authorizations)}"
            )
            log(f"{Fore.BLUE + Style.BRIGHT}--------------------------------------------------------")
        return [auth.strip() for auth in authorizations]
    except Exception as e:
        logger.error(f"Failed to load authorizations: {e}")
        return []

def extract_telegram_id(auth_data):
    ids = []
    for data in auth_data:
        parsed_data = urllib.parse.parse_qs(data)
        if 'user' in parsed_data:
            try:
                user_data = json.loads(parsed_data['user'][0])
                ids.append(user_data['id'])
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse user data: {e}")
    return ids

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def log(msg):
    print(
        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        f"{msg}"
    )

def welcome():
    print(
        f"""
    {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Snapster Trading App - BOT
        """
        f"""
    {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
        """
    )

async def process_auth(auth):
    ids = extract_telegram_id([auth])
    if not ids:
        logger.warning(f"Failed to extract user ID from authorization: {auth}")
        return

    async with aiohttp.ClientSession() as http:
        for id in ids:
            client = SnapsterTradingApp(id, auth)

            user_info = await client.get_user_info(http)
            if user_info:
                data = user_info.get("data", {})
                username = data.get("username", "Unknown")
                points = data.get("pointsCount", 0)
                streak = data.get("dailyBonusStreakCount", 0)
                league_title = data.get("currentLeague", {}).get("title", "Unknown")

                log(
                    f"{Fore.GREEN + Style.BRIGHT}[ Username ] "
                    f"{Fore.WHITE + Style.BRIGHT}{username}"
                )
                log(
                    f"{Fore.GREEN + Style.BRIGHT}[ Points ] "
                    f"{Fore.WHITE + Style.BRIGHT}{points}"
                )
                log(
                    f"{Fore.GREEN + Style.BRIGHT}[ League ] "
                    f"{Fore.WHITE + Style.BRIGHT}{league_title}"
                )
                log(
                    f"{Fore.GREEN + Style.BRIGHT}[ Streak ] "
                    f"{Fore.WHITE + Style.BRIGHT}{streak}"
                )
            else:
                log(f"{Fore.RED + Style.BRIGHT}Failed to fetch user info")

            daily_start = await client.start_daily(http)
            if daily_start:
                result = daily_start.get("result", False)
                if result:
                    data = daily_start.get("data", {})
                    points = data.get("pointsClaimed", 0)
                    log(
                        f"{Fore.GREEN + Style.BRIGHT}[ Check-in ] "
                        f"{Fore.WHITE + Style.BRIGHT}{points} "
                        f"{Fore.GREEN + Style.BRIGHT}points claimed"
                    )
                else:
                    log(f"{Fore.YELLOW + Style.BRIGHT}[ Check-in ] Already Check-in today")
            else:
                log(f"{Fore.RED + Style.BRIGHT}[ Check-in ] Failed to get a response or already checked-in")

            mining_claim = await client.claim_mining(http)
            if mining_claim:
                result = mining_claim.get("result", False)
                if result:
                    data = mining_claim.get("data", {})
                    points = data.get("pointsClaimed", 0)
                    log(
                        f"{Fore.GREEN + Style.BRIGHT}[ Farming ] "
                        f"{Fore.WHITE + Style.BRIGHT}{points} "
                        f"{Fore.GREEN + Style.BRIGHT}points claimed"
                    )
                else:
                    log(f"{Fore.YELLOW + Style.BRIGHT}[ Farming ] No available points farming to claim")
            else:
                log(f"{Fore.RED + Style.BRIGHT}[ Farming ] Failed to get a response or no points to claim")

            referral_claim = await client.claim_referrals(http)
            if referral_claim:
                result = referral_claim.get("result", False)
                if result:
                    data = referral_claim.get("data", {})
                    points = data.get("pointsClaimed", 0)
                    log(
                        f"{Fore.GREEN + Style.BRIGHT}[ Frens ] "
                        f"{Fore.WHITE + Style.BRIGHT}{points} "
                        f"{Fore.GREEN + Style.BRIGHT}points claimed"
                    )
                else:
                    log(f"{Fore.YELLOW + Style.BRIGHT}[ Frens ] No available points frens to claim")
            else:
                log(f"{Fore.RED + Style.BRIGHT}[ Frens ] Failed to get a response or no points to claim")

            get_quests = await client.get_quests(http)
            if get_quests and get_quests.get("result"):
                quests = get_quests.get("data", [])
                pending_tasks = []

                if quests:
                    for quest in quests:
                        quest_id = quest.get("id")
                        title = quest.get("title", "No title")
                        status = quest.get("status", "No status")

                        if status in ["EARN", "UNCLAIMED"]: 
                            pending_tasks.append((quest_id, title, status))

                    if not pending_tasks:
                        log(f"{Fore.GREEN + Style.BRIGHT}[ Task ] All tasks completed.")
                    else:
                        for quest_id, title, status in pending_tasks:
                            if status == "EARN":
                                status_task = f"{Fore.BLUE + Style.BRIGHT}{status}{Style.RESET_ALL}"
                            elif status == "UNCLAIMED":
                                status_task = f"{Fore.YELLOW + Style.BRIGHT}{status}{Style.RESET_ALL}"
                            else:
                                status_task = f"{Fore.GREEN + Style.BRIGHT}{status}{Style.RESET_ALL}"

                            log(
                                f"{Fore.GREEN + Style.BRIGHT}[ Task ] "
                                f"{Fore.WHITE + Style.BRIGHT}{title} "
                                f"{Fore.BLUE + Style.BRIGHT}| "
                                f"{Fore.GREEN + Style.BRIGHT}[ Status ] "
                                f"{status_task}"
                            )

                            if status == "EARN":
                                start_quests = await client.start_quest(http, quest_id)
                                if start_quests and start_quests.get("result"):
                                    log(
                                        f"{Fore.GREEN + Style.BRIGHT}[ Task ] "
                                        f"{Fore.WHITE + Style.BRIGHT}{title} "
                                        f"{Fore.GREEN + Style.BRIGHT}finished"
                                    )
                                    time.sleep(10)
                                    
                                    claim_quests = await client.claim_quest(http, quest_id)
                                    if claim_quests and claim_quests.get("result"):
                                        points = claim_quests["data"].get("pointsClaimed", 0)
                                        log(
                                            f"{Fore.GREEN + Style.BRIGHT}[ Task ] "
                                            f"{Fore.WHITE + Style.BRIGHT}{title} "
                                            f"{Fore.GREEN + Style.BRIGHT}claimed "
                                            f"{Fore.BLUE + Style.BRIGHT}| "
                                            f"{Fore.GREEN + Style.BRIGHT}[ Reward ] "
                                            f"{Fore.WHITE + Style.BRIGHT}{points} "
                                            f"{Fore.GREEN + Style.BRIGHT}points"
                                        )
                                    else:
                                        log(f"{Fore.RED + Style.BRIGHT}[ Task ] Failed to claim task "
                                            f"{Fore.WHITE + Style.BRIGHT}{title}"
                                        )
                                else:
                                    log(f"{Fore.RED + Style.BRIGHT}[ Task ] Failed to start task "
                                        f"{Fore.WHITE + Style.BRIGHT}{title}"
                                    )
                                time.sleep(10)

                            elif status == "UNCLAIMED":
                                claim_quests = await client.claim_quest(http, quest_id)
                                if claim_quests and claim_quests.get("result"):
                                    points = claim_quests["data"].get("pointsClaimed", 0)
                                    log(
                                            f"{Fore.GREEN + Style.BRIGHT}[ Task ] "
                                            f"{Fore.WHITE + Style.BRIGHT}{title} "
                                            f"{Fore.GREEN + Style.BRIGHT}claimed "
                                            f"{Fore.BLUE + Style.BRIGHT}| "
                                            f"{Fore.GREEN + Style.BRIGHT}[ Reward ] "
                                            f"{Fore.WHITE + Style.BRIGHT}{points} "
                                            f"{Fore.GREEN + Style.BRIGHT}points"
                                        )
                                else:
                                    log(f"{Fore.RED + Style.BRIGHT}[ Task ] Failed to claim task "
                                            f"{Fore.WHITE + Style.BRIGHT}{title}"
                                        )
                            
                    log(f"{Fore.BLUE + Style.BRIGHT}--------------------------------------------------------")
                else:
                    log(f"{Fore.RED + Style.BRIGHT}[ Task ] No tasks available")
            else:
                log(f"{Fore.RED + Style.BRIGHT}[ Task ] Failed to get tasks or no result found")

            await asyncio.sleep(1)

async def main():
    while True:
        clear_terminal()
        welcome()
        authorizations = await load_auth('query.txt')

        for auth in authorizations:
            await process_auth(auth)

        seconds = 21600
        while seconds > 0:
            print(f"{Fore.WHITE + Style.BRIGHT}\rWaiting for "
                  f"{Fore.YELLOW + Style.BRIGHT}{seconds} "
                  f"{Fore.WHITE + Style.BRIGHT}seconds before next iteration...",
                  end=""
            )
            await asyncio.sleep(1)
            seconds -= 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"RuntimeError: {e}")
    except Exception as e:
        logger.error(f"Exception in main: {e}")
    except KeyboardInterrupt:
        log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Snapster Trading App - BOT")
