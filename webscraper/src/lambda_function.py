import json
import pykakasi
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import lxml.html
import os

kakasi = pykakasi.kakasi()
kakasi.setMode("H","a") # Hiragana to ascii, default: no conversion
kakasi.setMode("K","a") # Katakana to ascii, default: no conversion
kakasi.setMode("J","a") # Japanese to ascii, default: no conversion
kakasi.setMode("r","Hepburn") # default: use Hepburn Roman table
kakasi.setMode("s", True) # add space, default: no separator
conv = kakasi.getConverter()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1280x1696')
chrome_options.add_argument('--user-data-dir=/tmp/user-data')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--log-level=0')
chrome_options.add_argument('--v=99')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--data-path=/tmp/data-path')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--homedir=/tmp')
chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
 
def lambda_handler(event,context):
    if 'type' in event:
        commands = event['command']
        command_type = event['type']
        return control(commands,command_type)
    else:
        return "invalid command"

def control(commands,command_type):
    driver = webdriver.Chrome(os.getcwd() + "/bin/chromedriver",chrome_options=chrome_options)  
    
    if command_type == "commutesearch":
        driver.get("https://suumo.jp/jj/chintai/kensaku/FR301FB005/?ar=030&bs=040")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='searchbox']/a")))
        #Handle stations input
        stations = commands['stations']
        station_inputs = driver.find_elements_by_name('toEki')
        station_distances = (driver.find_elements_by_name('tj'))
        station_changes = (driver.find_elements_by_name('nk'))
        addstationbtn = driver.find_element_by_id('js-timePanel-addStationBtn')
        for i in range(len(stations)-1):
            addstationbtn.click()
        for i in range(len(stations)):
            station_inputs[i].click()
            station_inputs[i].send_keys(stations[i][0])    
            Select(station_distances[i]).select_by_value(str(stations[i][1]))
            Select(station_changes[i]).select_by_value(str(stations[i][2]))
    
    if command_type == "trainsearch":
        if commands['prefecture'] == 'tokyo':
            driver.get("https://suumo.jp/jj/chintai/kensaku/FR301FB003/?ar=030&bs=040&ra=013")
        if commands['prefecture'] == 'kanagawa':
            driver.get("https://suumo.jp/jj/chintai/kensaku/FR301FB003/?ar=030&bs=040&ra=014")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'js-gotoEkiBtn')))
        for lineid in commands['lines']:
            print(lineid)
            if not driver.find_element_by_id(lineid).is_selected():
                driver.find_element_by_id(lineid).click()
        driver.find_element_by_id('js-gotoEkiBtn2').click()
        
        
    #Handle search options
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='searchbox']/a")))
    if command_type == "trainsearch":
        more_station_handler(driver)

    options = commands['options']
    #Price options
    #Limits for month price
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='searchbox']/a")))
    Select(driver.find_element_by_name('cb')).select_by_value(options['price'][0])
    Select(driver.find_element_by_name('ct')).select_by_value(options['price'][1])
    if(options['nof']):
        #No other fees
        driver.find_element_by_id('co4').click()
    else:
        # No Deposit and insurance
        if options['ndein'] :
            driver.find_element_by_id('co3').click()            
        # Common service fee and admin fee included in price
        if options['csaf'] : 
            driver.find_element_by_id('co0').click()
        # Key money
        if options['nkeym']:
            driver.find_element_by_id('co2').click()
            
    # Walk options, only one option possible, send handle in android
    driver.find_element_by_id(options['walk']).click()
    
    #room types
    if 'rtyp' in options:
        for i in options['rtyp']:
            driver.find_element_by_id(i).click()
    
    #house types
    if 'htyp' in options:
        for i in options['htyp']:
            driver.find_element_by_id(i).click()
    
    #Limits for room area
    Select(driver.find_element_by_name('mb')).select_by_value(options['area'][0])
    Select(driver.find_element_by_name('mt')).select_by_value(options['area'][1])
    
    #buildyear
    element = driver.find_element_by_id(options['byea'])
    webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
   
    if 'other' in options:
        for i in options['other']:
            element = driver.find_element_by_id(i)
            webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
            
    if command_type == 'trainsearch':                
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='searchbox']/a")))
        for stationid in commands['stations'][0]:
            try:
                if not driver.find_element_by_id(stationid).is_selected():
                    driver.find_element_by_id(stationid).click()
            except:
                print(driver.current_url)

    driver.find_element_by_xpath("//div[@class='searchbox']/a").click()
    #WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'js-bukkenList')))
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.get(driver.current_url+"&po1=12&pc=50")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//td[@class='ui-text--midium ui-text--bold']/a")))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    page_source = driver.page_source
    current_url = driver.current_url
    return load_page(page_source,current_url,command_type)     

def more_station_handler(driver):
    for i in driver.find_elements_by_link_text("沿線の駅を全て表示する"):
        try:
            i.click()
        except:
            more_station_handler(driver)
    
    
def load_page(page_source,url,command_type):
#    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # test for results of suumo houses list
    doc = lxml.html.fromstring(page_source)
    
    # test for results of suumo houses list
    #doc = doc.xpath("//div[@class='cassetteitem']/text()")
    # houses = doc.xpath("//div[@class='cassetteitem']/text()")
    # # Get house names
    house_name = doc.xpath("//div[@class='cassetteitem_content-title']/text()")

    # # Get house types
    house_type = doc.xpath("//span[@class='ui-pct ui-pct--util1']/text()")
        
    # Get house area
    house_area = doc.xpath("//li[@class='cassetteitem_detail-col1']/text()")

    # Get house station info, 3 stations for every house
    house_stations = doc.xpath("//li[@class='cassetteitem_detail-col2']")

    # Get house floors, age, first element is age, second floors
    house_flages = doc.xpath("//li[@class='cassetteitem_detail-col3']")

    #TODO Fix imgurls houses, rooms seem to work..
    #Img src link
    house_imgurl = doc.xpath("//div[@class='cassetteitem_object-item']/img")
        
    #Get the train station distance and transfers from that house
    if(command_type == "commutesearch"):
        house_stationsinfo = doc.xpath("//ul[@class='cassetteitem_transfer-list']/li/text()")

    #Get amount of rooms per house and parse this in list
    rows = doc.xpath("//table[@class='cassetteitem_other']")
    room_amount = []
    for i in range(len(rows)):
        room_amount.append(len(rows[i].getchildren())-1)
    
    #Get the per room rent
    room_rent = doc.xpath("//span[@class='cassetteitem_other-emphasis ui-text--bold']/text()")
        
    #Get the per room admin fee
    room_adminfee = doc.xpath("//span[@class='cassetteitem_price cassetteitem_price--administration']/text()")

    #Get the per room deposit
    room_deposit = doc.xpath("//span[@class='cassetteitem_price cassetteitem_price--deposit']/text()")

    #Get the per room key money
    room_keymoney = doc.xpath("//span[@class='cassetteitem_price cassetteitem_price--gratuity']/text()")

    #Get the per room floor
    room_floor = doc.xpath("//tr[@class='js-cassette_link']/td[contains(text(), '階') or contains(text(),'-')]/text()")
    for i in range(len(room_floor)):
        room_floor[i] = room_floor[i].strip().replace('階','')
    
    #Get the per room type
    room_type = doc.xpath("//span[@class='cassetteitem_madori']/text()")
    room_type = [w.replace('ワンルーム', 'oneroom') for w in room_type]
    
    #Get the room_handle needed for contact
    room_handles  = doc.xpath("//a[@class='js-cassette_link_href cassetteitem_other-linktext']")
        
    #Get the per room area
    room_area = doc.xpath("//span[@class='cassetteitem_menseki']/text()")

    #Get the per room area
    query = doc.xpath("//tr[@class='js-cassette_link']/td[2]/div")
    room_imgurls = []
    for  i in query:
        if(i.get('data-imgs')):
            temp10 = i.get('data-imgs').split(',')
            room_imgurls.append(temp10)
            #room_imgurls.append('none')
        else:
            room_imgurls.append(['none'])
    
    houses = []
    house_station = []
    house_flage = []
    room_iter = 0
    for i in range(len(house_name)):
        
        #Make list for house stations, a list of lists for each house
        imgurl = house_imgurl[i].get('src')
        temp1 = house_stations[i].getchildren()
        if(command_type == "commutesearch"):
            stationinfo = house_stationsinfo[i]
        else:
            stationinfo = []
        temp2 = []
        for k in range(len(temp1)):
            if temp1[k].xpath("text()"):
                temp2.append(conv.do((temp1[k].xpath("text()")[0])).replace("ＪＲ","JR"))
        house_station.append(temp2)
        
        #Make list of lists for house floor and ages together
        temp1 = house_flages[i].getchildren()
        temp2 = []
        for k in range(len(temp1)):
            if temp1[k].xpath("text()"):
                temp2.append(temp1[k].xpath("text()")[0])
        house_flage.append(temp2)
        
        rooms = []
        for l in range(room_amount[i]):
            temp4 = []
            temp4 = {"adminfee": room_adminfee[room_iter].replace("円","¥"),"area":room_area[room_iter],"deposit": str(float(room_deposit[room_iter].replace("万円","").replace("-","0"))*10)+"k¥","keymoney": str(float(room_keymoney[room_iter].replace("万円","").replace("-","0"))*10)+"k¥","type":room_type[room_iter],"rent":str(float(room_rent[room_iter].replace("万円","").replace("-","0"))*10)+"k¥","floor": room_floor[room_iter],"imgs":room_imgurls[room_iter],"roomhandle":room_handles[i].get('href')}
            room_iter = room_iter + 1
            rooms.append(temp4)
        
        # make list of jsons for each house to be received in Android
        houses.append({"type":house_type[i].replace("賃貸マンション","Condo").replace("賃貸アパート","Apartment").replace("一戸建て","detached"),"name":conv.do(house_name[i]), "area":conv.do(house_area[i]),"floors": house_flage[0][1].replace("階建",""), "age": house_flage[0][0].replace("築","").replace("年",""),"stations":house_station[i], "img": imgurl, "rooms": rooms,"stationinfo":stationinfo,"areajapanese":house_area[i]})
    return {"houses":houses,"url":url}
   