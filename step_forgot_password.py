
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

    # 5. Check for "Confirm your profile" in body instead of mail check
    print("Checking for 'Confirm your profile' text in body...")
    time.sleep(5)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    
    if "Confirm your profile" in body_text:
        print("'Confirm your profile' found. Going back to select another option...")
        
        # 6. Go Back -> Select Option 2 -> Continue
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
            print("Selecting Option 2...")
            
            # Strategy: Find unselected options
            selected_option_found = False
            
            # 1. Look for radio inputs
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            if len(radios) >= 2:
                print(f"Found {len(radios)} radio inputs. Selecting the second one.")
                try:
                    driver.execute_script("arguments[0].click();", radios[1])
                    selected_option_found = True
                except:
                    pass
            
            if not selected_option_found:
                 # 2. Look for role="radio"
                 role_radios = driver.find_elements(By.CSS_SELECTOR, '[role="radio"]')
                 if len(role_radios) >= 2:
                     print(f"Found {len(role_radios)} role='radio' elements. Selecting the second one.")
                     try:
                         driver.execute_script("arguments[0].click();", role_radios[1])
                         selected_option_found = True
                     except:
                         pass

            if not selected_option_found:
                # 3. Look for list items that are clickable (often div with role button)
                # Sometimes options are simply divs with text.
                print("Fallback: Trying to find unselected option by checked state...")
                
                # Try finding checked one first to avoid re-clicking it
                checked_xpaths = ["//input[@type='radio' and @checked]", "//*[@aria-checked='true']"]
                checked_el = None
                for xp in checked_xpaths:
                    els = driver.find_elements(By.XPATH, xp)
                    if els:
                        checked_el = els[0]
                        break
                
                # Now find all potential options
                potential_options = driver.find_elements(By.CSS_SELECTOR, "li, [role='radio'], input[type='radio']")
                
                for opt in potential_options:
                    if opt != checked_el:
                         print("Clicking a potential unselected option...")
                         try:
                             driver.execute_script("arguments[0].click();", opt)
                             selected_option_found = True
                             break
                         except:
                             continue

            if not selected_option_found:
                print("Warning: Could not robustly identify a second option. Flow might fail.")

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

            # Wait for "Confirm your profile" again
            print("Waiting for 'Confirm your profile' screen...")
            WebDriverWait(driver, 15).until(
                lambda d: "Confirm your profile" in d.find_element(By.TAG_NAME, "body").text
            )
            print("Done: 'Confirm your profile' screen reached.")

        except Exception as e:
            raise Exception(f"Retry flow failed: {e}")

    else:
        print("'Confirm your profile' not found immediately, assuming flow is correct or different screen.")
    
    return True

