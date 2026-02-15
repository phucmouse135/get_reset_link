
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def execute_step_forgot_password(driver, email_login):
    """
    Step:
    1. Click 'Forgot password?' on login page.
    2. Enter email.
    3. Click 'Send Login Link' (via Enter or button).
    """
    wait = WebDriverWait(driver, 10)

    # 1. Click "Forgot password?"
    # truy cập https://www.instagram.com/accounts/password/reset/
    url = "https://www.instagram.com/accounts/password/reset/"
    driver.get(url)
    time.sleep(3)

    # 2. Enter email
    print(f"Entering email: {email_login}")
    try:
        # The user provided input HTML: <input ... placeholder="Email, Phone, or Username" ...>
        # Often these inputs have name="email_or_username" or similar, or we can use the class provided.
        # User only gave class and id="_r_12_" (ids might be dynamic).
        # Let's look for an input suitable for email.
        
        # Commonly on IG forgot pass page: <input name="cppEmailOrUsername">
        try:
             email_input = wait.until(EC.presence_of_element_located((By.NAME, "cppEmailOrUsername")))
        except:
             # Fallback to a generic input on the page if name changes, or use the placeholder if available
             email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))

        email_input.clear()
        email_input.send_keys(email_login)
        time.sleep(1)
        
        # 3. Click Enter or "Send Login Link"
        email_input.send_keys(Keys.ENTER)
        
        # Wait for confirmation of sent link "Email Sent" or similar UI change
        # Not explicitly asked, but good practice. Assuming success if no error immediately.
        time.sleep(5)
        
    except Exception as e:
        print(f"Error entering email or submitting: {e}")
        raise e

    return True
