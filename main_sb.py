from seleniumbase import Driver

driver = Driver(server="http://localhost:4444/wd/hub", browser="chrome")
url = "https://vipdrive.net"
driver.uc_open_with_reconnect(url, 4)
driver.uc_gui_click_captcha()
driver.quit()