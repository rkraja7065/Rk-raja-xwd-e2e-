import streamlit as st
import streamlit.components.v1 as components
import time
import threading
import uuid
import hashlib
import os
import subprocess
import json
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests

st.set_page_config(
    page_title="YKTI RAWAT",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

* {
    font-family: 'Outfit', sans-serif !important;
}

/* 📌 LIGHT BEAUTIFUL BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #f4f9ff 0%, #e9f3ff 40%, #e1f0ff 100%);
    background-attachment: fixed;
    color: #333 !important;
}

/* 📌 MAIN CONTAINER – PREMIUM TILE BOX */
.main .block-container {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 28px;
    padding: 40px;
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    animation: smoothFade 0.5s ease;
}

@keyframes smoothFade {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}

/* 📌 HEADER MODERN TILE */
.main-header {
    background: linear-gradient(135deg, #ffffff, #f0f8ff, #e7f3ff);
    border-radius: 25px;
    padding: 50px 25px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 140, 255, 0.12);
    border: 1px solid rgba(0, 140, 255, 0.15);
}

.main-header h1 {
    color: #0077ff;
    font-size: 3rem;
    font-weight: 900;
}

.main-header p {
    color: #005fcc;
    font-size: 1.2rem;
    opacity: 0.85;
}

/* 📌 INPUT FIELDS */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {
    background: #ffffff;
    border-radius: 12px;
    padding: 14px;
    border: 1.5px solid #cfe4ff;
    color: #333;
    font-size: 1rem;
    transition: 0.2s ease;
}

.stTextInput>div>div>input:focus {
    border-color: #0078ff;
    box-shadow: 0 0 12px rgba(0,120,255,0.3);
}

label {
    color: #006be8 !important;
    font-weight: 700 !important;
}

/* 📌 BUTTON — PREMIUM GLOSSY */
.stButton>button {
    background: linear-gradient(135deg, #009dff 0%, #006bff 100%);
    color: white;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 1rem 2rem;
    border-radius: 14px;
    border: none;
    transition: 0.3s ease;
    box-shadow: 0 10px 20px rgba(0,100,255,0.25);
}
.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(0,100,255,0.35);
}

/* 📌 TABS – CLEAN WHITE */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 16px;
    padding: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #f4f9ff;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    color: #0077ff;
    border: 1px solid rgba(0,0,0,0.05);
}

.stTabs [aria-selected="true"] {
    background: #0077ff;
    color: white;
    box-shadow: 0 0 14px rgba(0,100,255,0.4);
}

/* 📌 ICON STYLING – PREMIUM LOOK */
i, svg {
    width: 26px !important;
    height: 26px !important;
    padding: 10px;
    border-radius: 12px;
    background: linear-gradient(135deg, #ffffff, #eaf3ff);
    box-shadow: 0 4px 15px rgba(0,100,255,0.2);
    border: 1px solid rgba(0, 120, 255, 0.15);
    fill: #006bff !important;
}

/* 📌 CONSOLE */
.console-output {
    background: #ffffff;
    border: 2px solid #b7d9ff;
    border-radius: 15px;
    padding: 20px;
    font-family: "Consolas";
    max-height: 400px;
    color: #005fcc;
    overflow-y: auto;
    box-shadow: 0 10px 25px rgba(0,100,255,0.15);
}

.console-line {
    background: #eef6ff;
    padding: 10px;
    border-left: 4px solid #0077ff;
    border-radius: 6px;
    margin-bottom: 8px;
    font-weight: 500;
}

/* 📌 SUCCESS / ERROR BOX */
.success-box {
    background: linear-gradient(135deg, #c7ffea, #9dffe0);
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    color: #007f5b;
    font-weight: 700;
}
.error-box {
    background: linear-gradient(135deg, #ffe1e1, #ffd4d4);
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    color: #b10000;
    font-weight: 700;
}

/* 📌 FOOTER */
.footer {
    text-align: center;
    color: #0077ff;
    font-weight: 800;
    margin-top: 2rem;
    padding: 1.5rem;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
ADMIN_UID = "100036283209197"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False

def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    
    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page Title: {page_title}', automation_state)
        log_message(f'{process_id}: Page URL: {page_url}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Could not get page info: {e}', automation_state)
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    
    log_message(f'{process_id}: Trying {len(message_input_selectors)} selectors...', automation_state)
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            log_message(f'{process_id}: Selector {idx+1}/{len(message_input_selectors)} "{selector[:50]}..." found {len(elements)} elements', automation_state)
            
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element with selector #{idx+1}', automation_state)
                        
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            pass
                        
                        element_text = driver.execute_script("return arguments[0].placeholder || arguments[0].getAttribute('aria-label') || arguments[0].getAttribute('aria-placeholder') || '';", element).lower()
                        
                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            log_message(f'{process_id}: ✅ Found message input with text: {element_text[:50]}', automation_state)
                            return element
                        elif idx < 10:
                            log_message(f'{process_id}: ✅ Using primary selector editable element (#{idx+1})', automation_state)
                            return element
                        elif selector == '[contenteditable="true"]' or selector == 'textarea' or selector == 'input[type="text"]':
                            log_message(f'{process_id}: ✅ Using fallback editable element', automation_state)
                            return element
                except Exception as e:
                    log_message(f'{process_id}: Element check failed: {str(e)[:50]}', automation_state)
                    continue
        except Exception as e:
            continue
    
    try:
        page_source = driver.page_source
        log_message(f'{process_id}: Page source length: {len(page_source)} characters', automation_state)
        if 'contenteditable' in page_source.lower():
            log_message(f'{process_id}: Page contains contenteditable elements', automation_state)
        else:
            log_message(f'{process_id}: No contenteditable elements found in page', automation_state)
    except Exception:
        pass
    
    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome'
    ]
    
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break
    
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            log_message('Chrome started with detected ChromeDriver!', automation_state)
        else:
            driver = webdriver.Chrome(options=chrome_options)
            log_message('Chrome started with default driver!', automation_state)
        
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'
    
    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]
    
    return message

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        driver = setup_browser(automation_state)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, automation_state)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state)
            automation_state.running = False
            db.set_automation_running(user_id, False)
            return 0
        
        delay = int(config['delay'])
        messages_sent = 0
        messages_list = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]
        
        if not messages_list:
            messages_list = ['Hello!']
        
        while automation_state.running:
            base_message = get_next_message(messages_list, automation_state)
            
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                
                if sent == 'button_not_found':
                    log_message(f'{process_id}: Send button not found, using Enter key...', automation_state)
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                    log_message(f'{process_id}: ✅ Sent via Enter: "{message_to_send[:30]}..."', automation_state)
                else:
                    log_message(f'{process_id}: ✅ Sent via button: "{message_to_send[:30]}..."', automation_state)
                
                messages_sent += 1
                automation_state.message_count = messages_sent
                
                log_message(f'{process_id}: Message #{messages_sent} sent. Waiting {delay}s...', automation_state)
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:100]}', automation_state)
                time.sleep(5)
        
        log_message(f'{process_id}: Automation stopped. Total messages: {messages_sent}', automation_state)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state)
        automation_state.running = False
        db.set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def send_admin_notification(user_config, username, automation_state, user_id):
    driver = None
    try:
        log_message(f"ADMIN-NOTIFY: Preparing admin notification...", automation_state)
        
        admin_e2ee_thread_id = db.get_admin_e2ee_thread_id(user_id)
        
        if admin_e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Using saved admin thread: {admin_e2ee_thread_id}", automation_state)
        
        driver = setup_browser(automation_state)
        
        log_message(f"ADMIN-NOTIFY: Navigating to Facebook...", automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if user_config['cookies'] and user_config['cookies'].strip():
            log_message(f"ADMIN-NOTIFY: Adding cookies...", automation_state)
            cookie_array = user_config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except Exception:
                            pass
        
        user_chat_id = user_config.get('chat_id', '')
        admin_found = False
        e2ee_thread_id = admin_e2ee_thread_id
        chat_type = 'REGULAR'
        
        if e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Opening saved admin conversation...", automation_state)
            
            if '/e2ee/' in str(e2ee_thread_id) or admin_e2ee_thread_id:
                conversation_url = f'https://www.facebook.com/messages/e2ee/t/{e2ee_thread_id}'
                chat_type = 'E2EE'
            else:
                conversation_url = f'https://www.facebook.com/messages/t/{e2ee_thread_id}'
                chat_type = 'REGULAR'
            
            log_message(f"ADMIN-NOTIFY: Opening {chat_type} conversation: {conversation_url}", automation_state)
            driver.get(conversation_url)
            time.sleep(8)
            admin_found = True
        
        if not admin_found or not e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: Searching for admin UID: {ADMIN_UID}...", automation_state)
            
            try:
                profile_url = f'https://www.facebook.com/{ADMIN_UID}'
                log_message(f"ADMIN-NOTIFY: Opening admin profile: {profile_url}", automation_state)
                driver.get(profile_url)
                time.sleep(8)
                
                message_button_selectors = [
                    'div[aria-label*="Message" i]',
                    'a[aria-label*="Message" i]',
                    'div[role="button"]:has-text("Message")',
                    'a[role="button"]:has-text("Message")',
                    '[data-testid*="message"]'
                ]
                
                message_button = None
                for selector in message_button_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            for elem in elements:
                                text = elem.text.lower() if elem.text else ""
                                aria_label = elem.get_attribute('aria-label') or ""
                                if 'message' in text or 'message' in aria_label.lower():
                                    message_button = elem
                                    log_message(f"ADMIN-NOTIFY: Found message button: {selector}", automation_state)
                                    break
                            if message_button:
                                break
                    except:
                        continue
                
                if message_button:
                    log_message(f"ADMIN-NOTIFY: Clicking message button...", automation_state)
                    driver.execute_script("arguments[0].click();", message_button)
                    time.sleep(8)
                    
                    current_url = driver.current_url
                    log_message(f"ADMIN-NOTIFY: Redirected to: {current_url}", automation_state)
                    
                    if '/messages/t/' in current_url or '/e2ee/t/' in current_url:
                        if '/e2ee/t/' in current_url:
                            e2ee_thread_id = current_url.split('/e2ee/t/')[-1].split('?')[0].split('/')[0]
                            chat_type = 'E2EE'
                            log_message(f"ADMIN-NOTIFY: ✅ Found E2EE conversation: {e2ee_thread_id}", automation_state)
                        else:
                            e2ee_thread_id = current_url.split('/messages/t/')[-1].split('?')[0].split('/')[0]
                            chat_type = 'REGULAR'
                            log_message(f"ADMIN-NOTIFY: ✅ Found REGULAR conversation: {e2ee_thread_id}", automation_state)
                        
                        if e2ee_thread_id and e2ee_thread_id != user_chat_id and user_id:
                            current_cookies = user_config.get('cookies', '')
                            db.set_admin_e2ee_thread_id(user_id, e2ee_thread_id, current_cookies, chat_type)
                            admin_found = True
                    else:
                        log_message(f"ADMIN-NOTIFY: Message button didn't redirect to messages page", automation_state)
                else:
                    log_message(f"ADMIN-NOTIFY: Could not find message button on profile", automation_state)
            
            except Exception as e:
                log_message(f"ADMIN-NOTIFY: Profile approach failed: {str(e)[:100]}", automation_state)
            
            if not admin_found or not e2ee_thread_id:
                log_message(f"ADMIN-NOTIFY: ⚠️ Could not find admin via search, trying DIRECT MESSAGE approach...", automation_state)
                
                try:
                    profile_url = f'https://www.facebook.com/messages/new'
                    log_message(f"ADMIN-NOTIFY: Opening new message page...", automation_state)
                    driver.get(profile_url)
                    time.sleep(8)
                    
                    search_box = None
                    search_selectors = [
                        'input[aria-label*="To:" i]',
                        'input[placeholder*="Type a name" i]',
                        'input[type="text"]'
                    ]
                    
                    for selector in search_selectors:
                        try:
                            search_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if search_elements:
                                for elem in search_elements:
                                    if elem.is_displayed():
                                        search_box = elem
                                        log_message(f"ADMIN-NOTIFY: Found 'To:' box with: {selector}", automation_state)
                                        break
                                if search_box:
                                    break
                        except:
                            continue
                    
                    if search_box:
                        log_message(f"ADMIN-NOTIFY: Typing admin UID in new message...", automation_state)
                        driver.execute_script("""
                            arguments[0].focus();
                            arguments[0].value = arguments[1];
                            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        """, search_box, ADMIN_UID)
                        time.sleep(5)
                        
                        result_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="option"], li[role="option"], a[role="option"]')
                        if result_elements:
                            log_message(f"ADMIN-NOTIFY: Found {len(result_elements)} results, clicking first...", automation_state)
                            driver.execute_script("arguments[0].click();", result_elements[0])
                            time.sleep(8)
                            
                            current_url = driver.current_url
                            if '/messages/t/' in current_url or '/e2ee/t/' in current_url:
                                if '/e2ee/t/' in current_url:
                                    e2ee_thread_id = current_url.split('/e2ee/t/')[-1].split('?')[0].split('/')[0]
                                    chat_type = 'E2EE'
                                    log_message(f"ADMIN-NOTIFY: ✅ Direct message opened E2EE: {e2ee_thread_id}", automation_state)
                                else:
                                    e2ee_thread_id = current_url.split('/messages/t/')[-1].split('?')[0].split('/')[0]
                                    chat_type = 'REGULAR'
                                    log_message(f"ADMIN-NOTIFY: ✅ Direct message opened REGULAR chat: {e2ee_thread_id}", automation_state)
                                
                                if e2ee_thread_id and e2ee_thread_id != user_chat_id and user_id:
                                    current_cookies = user_config.get('cookies', '')
                                    db.set_admin_e2ee_thread_id(user_id, e2ee_thread_id, current_cookies, chat_type)
                                    admin_found = True
                except Exception as e:
                    log_message(f"ADMIN-NOTIFY: Direct message approach failed: {str(e)[:100]}", automation_state)
        
        if not admin_found or not e2ee_thread_id:
            log_message(f"ADMIN-NOTIFY: ❌ ALL APPROACHES FAILED - Could not find/open admin conversation", automation_state)
            return
        
        conversation_type = "E2EE" if "e2ee" in driver.current_url else "REGULAR"
        log_message(f"ADMIN-NOTIFY: ✅ Successfully opened {conversation_type} conversation with admin", automation_state)
        
        message_input = find_message_input(driver, 'ADMIN-NOTIFY', automation_state)
        
        if message_input:
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conversation_type = "E2EE 🔒" if "E2EE" in driver.current_url.lower() else "Regular 💬"
            notification_msg = f"🦂YKTI RAWAT- User Started Automation\n\n👤 Username: {username}\n⏰ Time: {current_time}\n📱 Chat Type: {conversation_type}\n🆔 Thread ID: {e2ee_thread_id if e2ee_thread_id else 'N/A'}"
            
            log_message(f"ADMIN-NOTIFY: Typing notification message...", automation_state)
            driver.execute_script("""
                const element = arguments[0];
                const message = arguments[1];
                
                element.scrollIntoView({behavior: 'smooth', block: 'center'});
                element.focus();
                element.click();
                
                if (element.tagName === 'DIV') {
                    element.textContent = message;
                    element.innerHTML = message;
                } else {
                    element.value = message;
                }
                
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
            """, message_input, notification_msg)
            
            time.sleep(1)
            
            log_message(f"ADMIN-NOTIFY: Trying to send message...", automation_state)
            send_result = driver.execute_script("""
                const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                
                for (let btn of sendButtons) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return 'button_clicked';
                    }
                }
                return 'button_not_found';
            """)
            
            if send_result == 'button_not_found':
                log_message(f"ADMIN-NOTIFY: Send button not found, using Enter key...", automation_state)
                driver.execute_script("""
                    const element = arguments[0];
                    element.focus();
                    
                    const events = [
                        new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                        new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                        new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                    ];
                    
                    events.forEach(event => element.dispatchEvent(event));
                """, message_input)
                log_message(f"ADMIN-NOTIFY: ✅ Sent via Enter key", automation_state)
            else:
                log_message(f"ADMIN-NOTIFY: ✅ Send button clicked", automation_state)
            
            time.sleep(2)
        else:
            log_message(f"ADMIN-NOTIFY: ❌ Failed to find message input", automation_state)
            
    except Exception as e:
        log_message(f"ADMIN-NOTIFY: ❌ Error sending notification: {str(e)}", automation_state)
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f"ADMIN-NOTIFY: Browser closed", automation_state)
            except:
                pass

def run_automation_with_notification(user_config, username, automation_state, user_id):
    send_admin_notification(user_config, username, automation_state, user_id)
    send_messages(user_config, automation_state, user_id)

def start_automation(user_config, user_id):
    automation_state = st.session_state.automation_state
    
    if automation_state.running:
        return
    
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    
    db.set_automation_running(user_id, True)
    
    username = db.get_username(user_id)
    thread = threading.Thread(target=run_automation_with_notification, args=(user_config, username, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    st.session_state.automation_state.running = False
    db.set_automation_running(user_id, False)

def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🦂YKTI RAWAT</h1>
        <p>END TO END (E2EE) OFFLINE CONVO SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign-up"])
    
    with tab1:
        st.markdown("### WELCOME BACK!")
        username = st.text_input("USERNAME", key="login_username", placeholder="Enter your username")
        password = st.text_input("PASSWORD", key="login_password", type="password", placeholder="Enter your password")
        
        if st.button("LOGIN", key="login_btn", use_container_width=True):
            if username and password:
                user_id = db.verify_user(username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    
                    should_auto_start = db.get_automation_running(user_id)
                    if should_auto_start:
                        user_config = db.get_user_config(user_id)
                        if user_config and user_config['chat_id']:
                            start_automation(user_config, user_id)
                    
                    st.success(f"✅ WELCOME BACK, {username.upper()}!")
                    st.rerun()
                else:
                    st.error("❌ INVALID USERNAME OR PASSWORD!")
            else:
                st.warning("⚠️ PLEASE ENTER BOTH USERNAME AND PASSWORD")
    
    with tab2:
        st.markdown("### CREATE NEW ACCOUNT")
        new_username = st.text_input("CHOOSE USERNAME", key="signup_username", placeholder="Choose a unique username")
        new_password = st.text_input("CHOOSE PASSWORD", key="signup_password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("CONFIRM PASSWORD", key="confirm_password", type="password", placeholder="Re-enter your password")
        
        if st.button("CREATE ACCOUNT", key="signup_btn", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = db.create_user(new_username, new_password)
                    if success:
                        st.success(f"✅ {message} PLEASE LOGIN NOW!")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ PASSWORDS DO NOT MATCH!")
            else:
                st.warning("⚠️ PLEASE FILL ALL FIELDS")

def main_app():
    st.markdown("""
    <div class="main-header">
        <h1>🦂 YKTI RAWAT</h1>
        <p>FACEBOOK E2EE CONVO SERVER SYSTEM </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.auto_start_checked and st.session_state.user_id:
        st.session_state.auto_start_checked = True
        should_auto_start = db.get_automation_running(st.session_state.user_id)
        if should_auto_start and not st.session_state.automation_state.running:
            user_config = db.get_user_config(st.session_state.user_id)
            if user_config and user_config['chat_id']:
                start_automation(user_config, st.session_state.user_id)
    
    st.sidebar.markdown('<div class="sidebar-header">👤 USER DASHBOARD</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"**USERNAME:** {st.session_state.username}")
    st.sidebar.markdown(f"**USER ID:** {st.session_state.user_id}")
    st.sidebar.markdown('<div class="success-box">✅ PREMIUM ACCESS</div>', unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
        if st.session_state.automation_state.running:
            stop_automation(st.session_state.user_id)
        
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.automation_running = False
        st.session_state.auto_start_checked = False
        st.rerun()
    
    user_config = db.get_user_config(st.session_state.user_id)
    
    if user_config:
        tab1, tab2 = st.tabs(["E2EE SET-UP✅", "🔥 AUTOMATION"])
        
        with tab1:
            st.markdown('<div class="section-title">END TO END SETTINGS</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                chat_id = st.text_input("PASTE E2EE ID ", value=user_config['chat_id'], 
                                       placeholder="e.g., 10000634210631",
                                       help="Facebook conversation ID from the URL")
                
                name_prefix = st.text_input("HATERS NAME", value=user_config['name_prefix'],
                                           placeholder="JISKO PELNA HAI USKA NAME",
                                           help="Prefix to add before each message")
                
                delay = st.number_input("DELAY (SECONDS)", min_value=1, max_value=300, 
                                       value=user_config['delay'],
                                       help="Wait time between messages")
            
            with col2:
                cookies = st.text_area("PASTE FACEBOOK COOKIES  ", 
                                      value="",
                                      placeholder="Paste your Facebook cookies here",
                                      height=150,
                                      help="Your cookies are encrypted and never shown to anyone")
                
                messages = st.text_area("TYPE MESSAGE ONE PER LINE", 
                                       value=user_config['messages'],
                                       placeholder="Enter your messages here, one per line",
                                       height=200,
                                       help="Enter each message on a new line")
            
            if st.button("💾 SAVE E2EE ", use_container_width=True):
                final_cookies = cookies if cookies.strip() else user_config['cookies']
                db.update_user_config(
                    st.session_state.user_id,
                    chat_id,
                    name_prefix,
                    delay,
                    final_cookies,
                    messages
                )
                st.success("✅ E2EE SAVED SUCCESSFULLY!")
                st.rerun()
        
        with tab2:
            st.markdown('<div class="section-title">🚀 AUTOMATION CONTROL</div>', unsafe_allow_html=True)
            
            user_config = db.get_user_config(st.session_state.user_id)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.metric("MESSAGES SENT", st.session_state.automation_state.message_count)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                status = "🟢 RUNNING" if st.session_state.automation_state.running else "🔴 STOP"
                st.metric("STATUS", status)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                display_chat_id = user_config['chat_id'][:8] + "..." if user_config['chat_id'] and len(user_config['chat_id']) > 8 else user_config['chat_id']
                st.metric("CHAT ID", display_chat_id or "NOT SET")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("▶️ START E2EE AUTOMATION", disabled=st.session_state.automation_state.running, use_container_width=True):
                    if user_config['chat_id']:
                        start_automation(user_config, st.session_state.user_id)
                        st.success("✅ AUTOMATION STARTED!")
                        st.rerun()
                    else:
                        st.error("❌ PLEASE SET CHAT ID IN CONFIGURATION FIRST!")
            
            with col2:
                if st.button("⏹️ STOP E2EE AUTOMATION", disabled=not st.session_state.automation_state.running, use_container_width=True):
                    stop_automation(st.session_state.user_id)
                    st.warning("⚠️ AUTOMATION STOPPED!")
                    st.rerun()
            
            if st.session_state.automation_state.logs:
                st.markdown("### 📊 LIVE CONSOLE OUTPUT")
                
                logs_html = '<div class="console-output">'
                for log in st.session_state.automation_state.logs[-30:]:
                    logs_html += f'<div class="console-line">{log}</div>'
                logs_html += '</div>'
                
                st.markdown(logs_html, unsafe_allow_html=True)
                
                if st.button("🔄 REFRESH LOGS", use_container_width=True):
                    st.rerun()
    else:
        st.warning("⚠️ NO CONFIGURATION FOUND. PLEASE REFRESH THE PAGE!")

if not st.session_state.logged_in:
    login_page()
else:
    main_app()

st.markdown('<div class="footer">MADE IN INDIA 🇮🇳 WP+918115048433</div>', unsafe_allow_html=True)
