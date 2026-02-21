
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

    # 5. Check for Code from Mail (First Attempt)
    if not mail_password:
        print("No mail password provided, skipping mail check.")
        return True

    print("Checking for recovery mail (Attempt 1)...")
    
    def check_mail_for_code(timeout=30):
        start_wait = time.time()
        while time.time() - start_wait < timeout:
            result = mail_handler.verify_account_live(email_login, mail_password)
            if isinstance(result, str) and "CODE=" in result:
                # Just need to confirm mail exists with code
                return True
            time.sleep(5)
        return False

    # Try first attempt
    if check_mail_for_code(timeout=30):
        print("Mail found with code. Success!")
        return True
    
    print("Mail not found in first attempt. Retrying with Option 2...")
    
    # 6. Retry Logic: Go Back -> Select Option 2 -> Continue -> Check Mail Again
    try:
        # Click Back
        # Try finding a UI back button first, else browser back
        print("Clicking Back...")
        back_buttons = driver.find_elements(By.XPATH, "//*[contains(@aria-label, 'Back') or contains(text(), 'Back')]")
        if back_buttons:
             try:
                 back_buttons[0].click()
             except:
                 driver.back()
        else:
             driver.back()
        
        time.sleep(5)
        
        # Select Option 2
        # Assuming a list of radio buttons or list items.
        # Instagram recovery options often look like:
        # <label ... ><input type="radio" ...></label>
        print("Selecting Option 2...")
        options = driver.find_elements(By.XPATH, "//input[@type='radio']")
        
        if len(options) >= 2:
            try:
                # Click the label or the input
                driver.execute_script("arguments[0].click();", options[1])
                print("Selected Option 2.")
            except Exception as e:
                print(f"Failed to click Option 2: {e}")
        else:
            print("Less than 2 options found, trying general list items...")
            # detailed selection logic might be needed here if structure differs
            # fallback to whatever is clickable that looks like an option
            pass
            
        time.sleep(2)
        
        # Click Continue again
        print("Clicking Continue after selecting Option 2...")
        try:
            continue_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Continue"][role="button"], button[type="submit"]'))
            )
            continue_btn.click()
            time.sleep(3)
        except Exception:
            print("Continue button not found (2nd time), check if flow continued auto.")

        # Check mail again (Second Attempt)
        print("Checking for recovery mail (Attempt 2)...")
        if check_mail_for_code(timeout=60): # Wait longer this time
             print("Mail found with code (Attempt 2). Success!")
             return True
        else:
             raise Exception("Mail not received after retrying Option 2.")

    except Exception as e:
        raise Exception(f"Retry flow failed: {e}")

    return True
