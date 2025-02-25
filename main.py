import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

# <input class="tds-form-input-text" id="d87545bb-448f-4f45-aa17-29527dcac945" name="personal.firstName" required="" pattern="^([^\s].{1,99})$" aria-invalid="true" value="" aria-describedby="d87545bb-448f-4f45-aa17-29527dcac945-feedback">


def fill_form(page):
    # fill out common fields such as first and last name, emails, etcs.
    try:
        # Wait for the page to be fully loaded
        page.wait_for_load_state('networkidle')
        # Wait for the input to be visible
        page.wait_for_selector(
            'input.tds-form-input-text[name="personal.firstName"]', state='visible')

        # Fill the input
        page.fill(
            'input.tds-form-input-text[name="personal.firstName"]', 'Your first name')
        page.fill(
            'input.tds-form-input-text[name="personal.lastName"]', 'Your last name')
        page.fill(
            'input.tds-form-input-text[name="personal.preferredName"]', 'Your preferred name')
        page.fill(
            'input.tds-form-input-text[name="personal.phone"]', 'Your phone number')
        page.fill(
            'input.tds-form-input-text[name="personal.email"]', 'your email')
    except Exception as e:
        print(f"Error in fill_form: {e}")


def fill_legal(page):
    try:
        # Wait for the page to be fully loaded
        page.wait_for_load_state('networkidle')

        noticePeriod = page.query_selector(
            '.tds-form-input-select[name="legal.legalNoticePeriod"]')
        if noticePeriod:
            noticePeriod.select_option(value='immediately')
        else:
            print("Error, couldn't find the period")

        visa_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalImmigrationSponsorship" and @value="yes"]')
        if visa_radio:
            visa_radio.check()
        else:
            print("Error, couldn't find the option (immi)")

        otherPosistions_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalConsiderOtherPositions" and @value="yes"]')
        if otherPosistions_radio:
            otherPosistions_radio.check()
        else:
            print("Error, couldn't find the option (pos)")

        previouslyEmployed_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalFormerTeslaEmployee" and @value="no"]')
        if previouslyEmployed_radio:
            previouslyEmployed_radio.check()
        else:
            print("Error, couldn't find the option (prev Employed)")

        previouslyIntern_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalFormerTeslaInternOrContractor" and @value="no"]')
        if previouslyIntern_radio:
            previouslyIntern_radio.check()
        else:
            print("Error, couldn't find the option (prev Intern)")

        student_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalUniversityStudent" and @value="no"]')
        if student_radio:
            student_radio.check()
        else:
            print("Error, couldn't find the option (student)")

        receiveNotification_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalReceiveNotifications" and @value="yes"]')
        if receiveNotification_radio:
            receiveNotification_radio.check()
        else:
            print("Error, couldn't find the option (Notif)")

        consent_radio = page.query_selector(
            '//input[@class="tds-form-input-choice" and @name="legal.legalAcknowledgment"]')
        if consent_radio:
            consent_radio.check()
        else:
            print("Error, couldn't find the option (consent)")

        # page.wait_for_selector(
        #     'input.tds-form-input-text[name="legal.legalAcknowledgmetnName"]', state='visible')
        page.fill(
            'input.tds-form-input-text[name="legal.legalAcknowledgmentName"]', 'Kritchanon Prasobjaturaporn')

    except Exception as e:
        print(f"Error in fill_form: {e}")


def main():
    # Constant
    URL = 'https://www.tesla.com/en_AU/careers/search/job/sales-advisor-gold-coast-234240'

    RESUME_FILE = os.path.abspath(
        r'.../Resume.pdf') ## Path to your resume
    if not os.path.exists(RESUME_FILE):
        # raise FileNotFoundError
        print(f'Resume file not found: "{RESUME_FILE}"')
        return

    try:
        playwright = sync_playwright().start()
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the job posting
        page.goto(URL)

        # Close the region sidebar
        close = page.query_selector('//button[@class="tds-modal-close"]')
        if close:
            close.click()

        # Click 'Apply' button and wait for the new page
        page.click('//a[@class="tds-btn" and text()="Apply"]')

        # Wait for new page/tab to be created
        new_page = context.wait_for_event('page')

        # # Wait for the new page to load
        new_page.wait_for_load_state('networkidle')

        # # Switch focus to new page
        new_page.bring_to_front()

        # Fill the form on the new page
        fill_form(new_page)

        # Select Contact Phone Type
        select_phone_type = new_page.query_selector(
            '//select[@class="tds-form-input-select"]')
        if select_phone_type:
            select_phone_type.select_option(value='mobile')
        else:
            print('Whoops, unsupported type')

        select_country = new_page.query_selector(
            '.tds-form-input-select[name="personal.country"]')
        if select_country:
            select_country.select_option(value="AU")
        else:
            print('Whoops, unsupported type')

        # Upload resume
        upload_button = new_page.wait_for_selector('//input[@class="tds-form-input-file-upload"]',
                                                   state='visible',
                                                   timeout=10000)
        if upload_button:
            # Find the associated input element
            file_input = new_page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(RESUME_FILE)
                print("Resume uploaded successfully")

                # Wait for upload confirmation if needed
                time.sleep(2)
            else:
                print("File input element not found")
        else:
            print("Upload button not found")

        # user's confirmation for going to next page
        confirm = input("Ready to click the button? (y/n): ")
        if confirm.lower() == 'y':
            new_page.click('//button[@class="tds-btn" and text()="Next"]')
        else:
            print("Operation cancelled by user")
        # # # Last page

        # # # Wait for new page/tab to be created
        # last_page = context.wait_for_event('new_page')

        # # # Wait for the new page to load
        # last_page.wait_for_load_state('networkidle')

        # # # Switch focus to new page
        # last_page.bring_to_front()

        fill_legal(new_page)
        confirm = input("Ready to submit (y/n): ")
        if confirm.lower() == 'y':
            new_page.click('//button[@class="tds-btn" and @type="submit"]')
        else:
            print("Operation cancelled by user")

        time.sleep(5)
        print("Operation is complete")

    except TimeoutError:
        print('Timed out waiting for the application from to load.')
    except Exception as e:
        print(f'An error occurred: {str(e)}')
    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()
