import os
from pathlib import Path
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from DOP.RPA.Log import Log
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

# variable global
OUTPUT_DIR = Path(os.getenv("ROBOT_ARTIFACTS", "output"))
img_folder = os.path.join(OUTPUT_DIR, "image_files")
pdf_folder = os.path.join(OUTPUT_DIR, "pdf_files")
output_folder = os.path.join(OUTPUT_DIR, "output")

orders_file = os.path.join(OUTPUT_DIR, "orders.csv")
zip_file = os.path.join(OUTPUT_DIR, "pdf_archive.zip")
csv_url = "https://robotsparebinindustries.com/orders.csv"

# init contructor
log = Log()
selenium = Selenium()
http = HTTP()
tables = Tables()
pdf = PDF()
archive = Archive()


@task
def order_robots_from_robot_sparebin_industries_inc():
    global img_folder, pdf_folder, output_folder, orders_file, zip_file, csv_url

    open_the_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_the_annoying_modal()
        fill_the_form(row)
        preview_the_robot()
        submit_the_order()
        orderid, img_filename = take_a_screenshot_of_the_robot()
        pdf_filename = store_the_recept_as_a_pdf_file(orderid)
        embed_the_robot_screenshot_to_the_receipt_PDF_file(img_filename, pdf_filename)
        go_to_order_another_robot()
    create_a_zip_file_of_the_receipts()


def open_the_robot_order_website():
    selenium.open_available_browser(url="https://robotsparebinindustries.com/#/robot-order", maximized=True)

def get_orders():
    http.download(url=csv_url, target_file=orders_file)
    table = tables.read_table_from_csv(path=orders_file)
    return table

def close_the_annoying_modal():
    selenium.wait_and_click_button(locator="xpath://*[@id='root']/div/div[2]/div/div/div/div/div/button[2]")

def fill_the_form(myrow):
    selenium.wait_until_element_is_visible(locator="//*[@id='head']", timeout=5)
    selenium.select_from_list_by_value("//*[@id='head']", myrow["Head"])

    selenium.wait_until_element_is_enabled("body", timeout=5)
    selenium.select_radio_button("body", myrow["Body"])

    selenium.wait_until_element_is_enabled("xpath://html/body/div/div/div[1]/div/div[1]/form/div[3]/input", timeout=5)
    selenium.input_text("xpath://html/body/div/div/div[1]/div/div[1]/form/div[3]/input", myrow["Legs"])

    selenium.wait_until_element_is_enabled("//*[@id='address']", timeout=5)
    selenium.input_text("//*[@id='address']", myrow["Address"])

def preview_the_robot():
    status_wait = True
    status_click = True
    while(status_click):
        status_click = run_keywork_click_and_return_status("//*[@id='preview']", '//*[@id="robot-preview-image"]')

    while(status_wait):
        status_wait = run_keywork_wait_and_return_status("//*[@id='robot-preview-image']")


def submit_the_order():
    status_wait = True
    status_click = True
    while(status_click):
        status_click = run_keywork_click_and_return_status("//*[@id='order']", '//*[@id="receipt"]')

    while(status_wait):
        status_wait = run_keywork_wait_and_return_status("//*[@id='receipt']")

def take_a_screenshot_of_the_robot():
    selenium.wait_until_element_is_visible('//*[@id="robot-preview-image"]')
    selenium.wait_until_element_is_visible("//img[@alt='Head']")
    selenium.wait_until_element_is_visible("//img[@alt='Body']")
    selenium.wait_until_element_is_visible("//img[@alt='Legs']")
    selenium.wait_until_element_is_visible("xpath://html/body/div/div/div[1]/div/div[1]/div/div/p[1]")

    orderid = selenium.get_text('//*[@id="receipt"]/p[1]')

    fully_qualified_img_filename = os.path.join(img_folder, f"{orderid}.png")
    selenium.capture_element_screenshot('//*[@id="robot-preview-image"]', fully_qualified_img_filename)

    return orderid, fully_qualified_img_filename

def go_to_order_another_robot():
    selenium.click_button('//*[@id="order-another"]')

def create_a_zip_file_of_the_receipts():
    archive.archive_folder_with_zip(pdf_folder, zip_file, recursive=True, include="*.pdf")

def store_the_recept_as_a_pdf_file(order_number):
    selenium.wait_until_element_is_visible('//*[@id="receipt"]')
    order_receipt_html = selenium.get_element_attribute('//*[@id="receipt"]', "outerHTML")
    fully_qualified_pdf_filename = os.path.join(pdf_folder, f"{order_number}.pdf")
    pdf.html_to_pdf(order_receipt_html, fully_qualified_pdf_filename)
    return fully_qualified_pdf_filename

def embed_the_robot_screenshot_to_the_receipt_PDF_file(img_file, pdf_file):
    pdf.open_pdf(pdf_file)
    myfiles = []
    pdf.add_files_to_pdf(myfiles,pdf_file,True)

def run_keywork_wait_and_return_status(locator):
    try:
        selenium.page_should_contain_element(locator)
        return False
    except Exception as e:
        return True
    
def run_keywork_click_and_return_status(locator1,locator2):
    try:
        selenium.click_button(locator1)
        selenium.page_should_contain_element(locator2)
        return False
    except Exception as e:
        return True
    
def create_file_exists(path, content):
    if not os.path.exists(path):
        with open(path, 'x') as file:
            file.write(content)
        return path
    else:
        pass
        return path