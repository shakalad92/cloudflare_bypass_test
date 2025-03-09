from seleniumbase import SB

with SB(uc=True, test=True, locale="en") as sb:
    url = "https://vipdrive.net/"
    sb.activate_cdp_mode(url)
    sb.uc_gui_click_captcha()
    sb.sleep(5)

    sb.save_screenshot()
