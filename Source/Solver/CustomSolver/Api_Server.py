from quart import Quart, request, jsonify
import asyncio
import time
from patchright.async_api import async_playwright
from colorama import *
from logmagix import Logger
import uuid
from Source.Solver.CustomSolver.Solver import *
from Source.Solver.CustomSolver.Results import *
from Source.Solver.CustomSolver.CloudFlare.solver import *
from Source.Solver.CustomSolver.CloudFlare.Data import *
import datetime

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")


class TurnstileAPIServer:
    
    HTML_TEMPLATE = """
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Turnstile Solver</title>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" 
                async="" defer=""></script>
    </head>
    <body>
        <!-- cf turnstile -->
    </body>
    </html>
    """



    def __init__(self, debug: bool = False):
        self.app = Quart(__name__)
        self.app.config['PROVIDE_AUTOMATIC_OPTIONS'] = True
        self.log = Logger()
        self.debug = debug
        self.page_pool = None
        self.browser = None
        self.context = None
        self.browser_args = [
            "--disable-blink-features=AutomationControlled",
        ]
        self._setup_routes()

        print(f"{timestamp()} | {Fore.LIGHTBLUE_EX}HOSTING{Fore.RESET} | Server has Loaded [{Fore.LIGHTBLUE_EX}Host{Fore.RESET}: http://localhost:8080]")

    def _setup_routes(self) -> None:
        self.app.before_serving(self._startup)
        self.app.route('/create_task', methods=['POST'])(self.process_turnstile)
        self.app.route('/get_result/<task_id>', methods=['GET'])(self.get_task_status)
        self.app.route('/balance', methods=['POST'])(self.view_balance)
        self.app.route('/solve_cloudflare', methods=['POST'])(self.get_cf_token)


    async def _startup(self) -> None:
        try:
            await self._initialize_browser()
        except Exception as e:
            print(f"Failed To Setup Browser")
            raise

    async def _initialize_browser(self) -> None:
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=self.browser_args
        )
        self.context = await self.browser.new_context()
        self.page_pool = PagePool(
            self.context,
            debug=self.debug,
            log=self.log
        )
        await self.page_pool.initialize()

    async def _solve_turnstile(self, url: str, sitekey: str, task_id: str) -> TurnstileAPIResult:
        start_time = time.time()

        page = await self.page_pool.get_page()
        try:
            url_with_slash = url + "/" if not url.endswith("/") else url
            turnstile_div = f'<div class="cf-turnstile" data-sitekey="{sitekey}"></div>'
            page_data = self.HTML_TEMPLATE.replace("<!-- cf turnstile -->", turnstile_div)

            await page.route(url_with_slash, lambda route: route.fulfill(body=page_data, status=200))
            await page.goto(url_with_slash)

            await page.eval_on_selector(
                "//div[@class='cf-turnstile']",
                "el => el.style.width = '70px'"
            )


            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                try:
                    turnstile_check = await page.input_value("[name=cf-turnstile-response]")
                    if turnstile_check == "":
                        attempts += 1
                        await page.click("//div[@class='cf-turnstile']", timeout=3000)
                        await asyncio.sleep(0.5)
                    else:
                        element = await page.query_selector("[name=cf-turnstile-response]")
                        if element:
                            value = await element.get_attribute("value")
                            elapsed_time = round(time.time() - start_time, 3)

                            print(f"{timestamp()} | {Fore.GREEN}SUCCESS{Fore.RESET} | Successfully Solved Captcha [{Fore.GREEN}TaskID{Fore.RESET}: {task_id}] [{Fore.GREEN}Time{Fore.RESET}: {elapsed_time}]")
        
                            return TurnstileAPIResult(
                                capcha_key=value,
                                elapsed_time=elapsed_time
                            )
                        break
                except:
                    pass

            return TurnstileAPIResult(
                capcha_key=None,
                status="failure",
                error="Max attempts reached without solution"
            )

        except Exception as e:
            return TurnstileAPIResult(
                capcha_key=None,
                status="error",
                error=str(e)
            )
        
        finally:
            await page.goto("about:blank")
            await self.page_pool.return_page(page)
                                    
    async def process_turnstile(self):
        json_data = await request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON"}), 400

        
        api_key = json_data.get('api_key')
        if not api_key or api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 403

        balance = API_KEYS[api_key]
        if balance < 0.001:
            return jsonify({"error": "Insufficient balance"}), 402

        
        task_id = str(uuid.uuid4())
        TASKS[task_id] = {
            "status": "pending",
            "api_key": api_key,
            "result": None
        }
        
        print(f"{timestamp()} | {Fore.YELLOW}CAPCHA{Fore.RESET}  | Captcha Detected Solving [{Fore.YELLOW}TaskID{Fore.RESET}: {task_id}] [{Fore.YELLOW}Solver{Fore.RESET}: Custom]")
    
        url = json_data.get('url')
        sitekey = json_data.get('sitekey')

        if not url or not sitekey:
            return jsonify({
                "status": "error",
                "error": "Both 'url' and 'sitekey' are required"
            }), 400

        try:
            result = await self._solve_turnstile(url=url, sitekey=sitekey, task_id=task_id)
            

            result.task_id = task_id
            
          
            TASKS[task_id]["result"] = result.__dict__
            TASKS[task_id]["status"] = "completed"


            if result.status == "success":
                API_KEYS[api_key] -= 0.002
                write_api_keys(API_KEYS)

            save_tasks_to_file()
            return jsonify({"Price": "0.002","task_id": task_id}), 200 if result.status == "success" else 500
        

        except Exception as e:
            TASKS[task_id]["status"] = "error"
            TASKS[task_id]["result"] = {"error": str(e)}
            save_tasks_to_file()
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500


    async def get_task_status(self, task_id):
     task = TASKS.get(task_id)
     if task:
         
         result = task.get('result', {})
         captcha_key = result.pop('capcha_key', None)
         taskid = result.pop('task_id', None)
         
         response = {
             "status": task.get('status'),
             "captcha_key": captcha_key,
             "task_id": taskid,
             "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
             
         }
         return jsonify(response), 200
     else:
         return jsonify({"error": "Task not found"}), 404
     
    async def view_balance(self):
        

        json_data = await request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid JSON"}), 400

        api_key = json_data.get('api_key')
        if not api_key or api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 403
        
        balance = API_KEYS[api_key]  # Get the balance for the API key
        return jsonify({"api_key": api_key, "balance": balance}), 200
    

    async def get_cf_token(self) -> None:
      
      json_data = await request.get_json()
      if not json_data:
            return jsonify({"error": "Invalid JSON"}), 400

      api_key = json_data.get('api_key')
      if not api_key or api_key not in API_KEYS:
        return jsonify({"error": "Invalid API key"}), 403
      
      url = json_data.get('url')
      if not url:
            return jsonify({"error": "No Url Provided"}), 403
    

      user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"  
      timeout = 30
      proxy = None
      debug = False
      verbose = False

      logging_level = logging.INFO if verbose else logging.ERROR
      logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        level=logging_level,
    )

      logging.info("Launching %s browser...", "headed" if debug else "headless")

      challenge_messages = {
        ChallengePlatform.JAVASCRIPT: "Solving Cloudflare challenge [JavaScript]...",
        ChallengePlatform.MANAGED: "Solving Cloudflare challenge [Managed]...",
        ChallengePlatform.INTERACTIVE: "Solving Cloudflare challenge [Interactive]...",
    }

      solver = CloudflareSolver(
        user_agent=user_agent,
        timeout=timeout,
        http2=True,
        http3=True,
        headless=not debug,
        proxy=proxy,
    )

      try:
        await solver.setup_browser()

        logging.info("Going to %s...", url)

        try:
            await solver.page.goto(url)
        except PlaywrightError as err:
            logging.error(err)
            return

        clearance_cookie = solver.extract_clearance_cookie(await solver.cookies)

        if clearance_cookie is None:
            challenge_platform = await solver.detect_challenge()

            if challenge_platform is None:
                logging.error("No Cloudflare challenge detected.")
                return

            logging.info(challenge_messages[challenge_platform])

            try:
                await solver.solve_challenge()
            except PlaywrightError as err:
                logging.error(err)

            clearance_cookie = solver.extract_clearance_cookie(await solver.cookies)

      finally:
        await solver.close_browser()

      if clearance_cookie is None:
        return jsonify({"Error": "Failed to retrieve a Cloudflare Clearance cookie"}), 500

      logging.info("Cookie: cf_clearance=%s", clearance_cookie["value"])
      logging.info("User agent: %s", user_agent)

      if not verbose:
        return jsonify({"CloudFlare_Clearance_Key": clearance_cookie["value"], "UserAgent": user_agent}), 200
      