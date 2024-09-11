import streamlit as st
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import xlsxwriter
import io

email = "" # Lınkedin email
password = "" # Lınkedin password

emailLoginXpath = '//*[@id="username"]'
passwordLoginXpath = '//*[@id="password"]'
loginButtonXpath = '//*[@id="organic-div"]/form/div[3]/button'
searchInputXpath = '//*[@id="global-nav-typeahead"]/input'
userProfileEntryXpath = '//*[@id="fie-impression-container"]/div[1]/div[1]/div/div/a[1]'
userToUserEntryXpath = '//*[@id="profile-content"]/div/div[2]/div/div/aside/section[2]/div[3]/ul/li[1]/div/div[2]/div[1]/a'
messageBarXpath = '//*[@id="msg-overlay"]/div[1]/header/div[2]/button/span/span[1]'
userNameXpath = '//*[@id="profile-content"]/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/span/a/h1[1]'
userCompanyAndIndustry = '//*[@id="profile-content"]/div/div[2]/div/div/main/section[3]/div[3]/ul/li[1]/div/div[2]/div/div/span[1]/span[1]'
contactInfoXpath = '//*[@id="top-card-text-details-contact-info"]'

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

st.markdown(
    """
    <h1 style='text-align: center'>LinkedIn Scraper</h1>
    """,
    unsafe_allow_html=True
)

if st.session_state.submitted:
    st.markdown(
        """
        <p style='text-align: center;'>İşlem tamamlandı.</p>
        """,
        unsafe_allow_html=True
    )
else:
    userInput = st.text_input("Enter the LinkedIn username to search")
    numUserDataSelect = st.number_input("How many users will you pull data from?", min_value=1, value=1)
    submitButton = st.button("Submit")

    if submitButton and userInput.strip():
        st.session_state.submitted = True
        st.markdown(
            """
            <h4 style='text-align: center;'>Uygulama başlatılıyor</h4>
            """,
            unsafe_allow_html=True
        )

        url = "https://www.linkedin.com/login"
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        emailLoginInput = wait.until(EC.visibility_of_element_located((By.XPATH, emailLoginXpath)))
        emailLoginInput.send_keys(email)

        passwordLoginInput = wait.until(EC.visibility_of_element_located((By.XPATH, passwordLoginXpath)))
        passwordLoginInput.send_keys(password)

        loginButtonClick = wait.until(EC.element_to_be_clickable((By.XPATH, loginButtonXpath)))
        loginButtonClick.click()

        time.sleep(5)

        searchButtonInput = wait.until(EC.element_to_be_clickable((By.XPATH, searchInputXpath)))
        searchButtonInput.send_keys(userInput)
        searchButtonInput.send_keys(u'\ue007')
        time.sleep(5)

        userProfileEntryClick = wait.until(EC.element_to_be_clickable((By.XPATH, userProfileEntryXpath)))
        userProfileEntryClick.click()
        time.sleep(5)

        usernames = []

        dataPulled = 0

        while dataPulled < numUserDataSelect:
            try:
                userToUserEntryClick = wait.until(EC.element_to_be_clickable((By.XPATH, userToUserEntryXpath)))
                userToUserEntryClick.click()
                time.sleep(5)

                userNameElement = wait.until(EC.element_to_be_clickable((By.XPATH, userNameXpath)))
                userNameText = userNameElement.text
                usernames.append(userNameText)
                st.markdown(f"<p style='text-align: left;'>Kullanıcı adı: {userNameText}</p>", unsafe_allow_html=True)

                dataPulled += 1

                if dataPulled == numUserDataSelect:
                    break

                print("Sonraki kullanıcıya geçiliyor")
                time.sleep(5)

            except selenium.common.exceptions.ElementClickInterceptedException:
                messageBarClick = wait.until(EC.element_to_be_clickable((By.XPATH, messageBarXpath)))
                messageBarClick.click()
                time.sleep(5)

                userToUserEntryClick = wait.until(EC.element_to_be_clickable((By.XPATH, userToUserEntryXpath)))
                userToUserEntryClick.click()
                time.sleep(10)

                userNameElement = wait.until(EC.element_to_be_clickable((By.XPATH, userNameXpath)))
                userNameText = userNameElement.text
                usernames.append(userNameText)
                st.markdown(f"<p style='text-align: left;'>Kullanıcı adı: {userNameText}</p>", unsafe_allow_html=True)

                dataPulled += 1
                print("Data Pulled: ", dataPulled)

                if dataPulled == numUserDataSelect:
                    break

                print("Sonraki kullanıcıya geçiliyor")
                time.sleep(5)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        for i, username in enumerate(usernames):
            worksheet.write(i, 0, username)

        workbook.close()
        output.seek(0)

        st.download_button(
            label="Download Excel file",
            data=output,
            file_name="usernames.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.session_state.submitted = False
        driver.quit()

    elif submitButton:
        st.markdown(
            """
            <h5 style='text-align: center;'>Lütfen başlangıç kullanıcı adını giriniz</h5>
            """,
            unsafe_allow_html=True
        )