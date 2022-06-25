from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# URLs
url_login = 'https://sso.ui.ac.id/cas/login?service=http%3A%2F%2Fbeasiswa.ui.ac.id%2Fapps%2Flogin%2Findex'
url_home = 'http://beasiswa.ui.ac.id/apps/site/index'
url_ipk = 'http://beasiswa.ui.ac.id/apps/pendaftaranrolependaftar/inputDataPelamar?idPaket=181'
url_logout = 'http://beasiswa.ui.ac.id/apps/login/logout'

# Initialize selenium
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Mobile Safari/537.36 Edg/102.0.1245.44'
}
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 2)

# User Model
class User(BaseModel):
    username: str
    password: str

# Selenium functions
def login(username, password):
    if username == '' or password == '':
        return 'username dan password tidak boleh kosong'
    driver.get(url_login)
    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="fm1"]/div[3]/button').click()
    try:
        wait.until(EC.url_to_be(url_home))
    except TimeoutException:
        return driver.find_element(By.ID, 'status').text

def check_ipk():
    driver.get(url_ipk)
    return {
        'nama': driver.find_element(By.ID, 'Pelamar_nama').get_attribute("value"),
        'npm': driver.find_element(By.ID, 'Pelamar_npm').get_attribute("value"),
        'ipk': driver.find_element(By.ID, 'Pelamar_ipk').get_attribute("value")
    }

def logout():
    driver.get(url_logout)


# Fast API
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/cek-ipk")
async def ipk_gui(request: Request):
    return templates.TemplateResponse("blablabla.html", {"request": request})

@app.post("/cek-ipk")
async def ipk_api(user: User):
    response = login(user.username, user.password)
    if response:
        return {"message": response}
    response = check_ipk()
    logout()
    return {"message": response}
