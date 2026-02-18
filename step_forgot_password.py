
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mail_handler

def execute_step_forgot_password(driver, email_login, mail_password=None):
    """
    Step:
    1. Click 'Forgot password?' on login page.
    2. Enter email.
    3. Click 'Send Login Link' (via Enter or button).
    4. Wait for code via IMAP
    5. Enter code.
    """
    wait = WebDriverWait(driver, 15)

    # 1. Access reset page
    url = "https://www.instagram.com/accounts/password/reset/"
    driver.get(url)
    time.sleep(3)

    # 2. Handle potential "Find by email or username instead" button
    # Mobile view often shows a screen asking for phone number first or has this button.
    try:
        # Look for "Find by email or username instead" button
        # This text might vary by language, so we might need a more robust selector if possible.
        # But user specifically mentioned this button.
        find_by_email_btn = driver.find_elements(By.XPATH, "//*[contains(text(), 'Find by email or username instead')]")
        if find_by_email_btn:
             find_by_email_btn[0].click()
             time.sleep(2)
    except Exception:
        pass

    # 3. Enter email
    print(f"Entering email: {email_login}")

    # User provided HTML:
    # <input ... aria-label="Email or username" ...>
    # Try multiple selectors for robustness
    email_input = None
    selectors = [
        (By.CSS_SELECTOR, 'input[aria-label="Email or username"]'),
        (By.CSS_SELECTOR, 'input[name="cppEmailOrUsername"]'),
        (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//input[@type='text']")
    ]
    
    for by, val in selectors:
        try:
            email_input = wait.until(EC.presence_of_element_located((by, val)))
            if email_input:
                break
        except:
            continue
            
    if not email_input:
         raise Exception("Could not find email input field")

    email_input.clear()
    email_input.send_keys(email_login)
    time.sleep(1)
    email_input.send_keys(Keys.ENTER)
    time.sleep(3)
    
    # 4. Click Continue if needed
    # The button user provided HTML for: <div ... aria-label="Continue" ...>
    print("Checking for Continue button...")
    try:
        # Try to find and click the Continue button. Wait a bit for it.
        continue_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Continue"][role="button"]'))
        )
        continue_btn.click()
        print("Clicked Continue button.")
        time.sleep(3)
    except Exception:
        print("Continue button not found or not clickable, proceeding...")

    # 5. Wait for Code from Mail
    if not mail_password:
        print("No mail password provided, skipping code verification step.")
        return True

    print("Waiting for recovery code from mail...")
    # Poll for code
    recovery_code = None
    max_wait_time = 60 # wait up to 60s for mail
    start_wait = time.time()
    
    while time.time() - start_wait < max_wait_time:
        result = mail_handler.verify_account_live(email_login, mail_password)
        
        # Check if result contains CODE=...
        if isinstance(result, str) and "CODE=" in result:
            parts = result.split("|")
            for p in parts:
                if p.startswith("CODE="):
                    code_val = p.split("=", 1)[1]
                    if code_val and code_val.strip():
                        recovery_code = code_val.strip()
                        break
        
        if recovery_code:
            break
            
        time.sleep(5)

    if not recovery_code:
        raise Exception("Failed to retrieve recovery code from email within timeout.")

    print(f"Got recovery code: {recovery_code}")

    # 6. Enter Code
    # User input: <input ... aria-label="Enter code" inputmode="numeric" ...>
    print(f"Submitting code: {recovery_code}...")
    try:
        # Check if we need to click "Continue" again or if we are stuck
        # Try multiple selectors for the code input
        selectors = [
             (By.CSS_SELECTOR, 'input[aria-label="Enter code"]'),
             (By.CSS_SELECTOR, 'input[name="security_code"]'),
             (By.XPATH, "//input[@inputmode='numeric']"),
             (By.XPATH, "//*[contains(text(), 'Enter code')]/following::input[1]")
        ]
        
        code_input = None
        for by, val in selectors:
             try:
                 print(f"Looking for code input via {by}: {val}")
                 code_input = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((by, val)))
                 if code_input:
                     break
             except:
                 continue
                 
        if not code_input:
             # Last ditch effort: dump page source to debug
             # print("Page source during error:", driver.page_source[:5000]) # truncated 
             raise Exception("Could not find code input field after trying multiple selectors.")

        code_input.click()
        code_input.clear()
        code_input.send_keys(recovery_code)
        time.sleep(1)
        code_input.send_keys(Keys.ENTER)
        time.sleep(5) 
        
        # Verify success? We assume success if no error or if URL changes
        # check url or for generic "Next" / "New Password" screens
        print("Code submitted successfully.")
        
    except Exception as e:
        raise Exception(f"Error entering recovery code: {e}")

    return True
