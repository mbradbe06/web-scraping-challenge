from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd
import requests
import time

def init_browser():
    executable_path = {'executable_path': 'c:/chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()

    #--------------NASA Mars News-----------------
    #splinter navigate to mars site
    url_news = "https://mars.nasa.gov/news/"
    browser.visit(url_news)

    #give time for dynamic page to load before python script captures page's html
    time.sleep(2)

    #Retrieve page html, create BeautifulSoup object and parse w/ html.parser
    html_news = browser.html
    soup_news = bs(html_news, 'html.parser')

    #grab parent slide containing latest news title and paragraph description
    title_text = soup_news.find('li', class_='slide')

    #Extract news title from parent beautiful soup object
    news_title = title_text.h3.text

    #Extract paragraph from parent beautiful soup object
    news_p = title_text.a.text

    #---------JPL Mars Space Images - Featured Image---------
    #visit URL for JPL Featured Space Image
    url_feat = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_feat)

    #navigate to featured image page with large res
    browser.click_link_by_partial_text('FULL IMAGE')
    browser.click_link_by_partial_text('more info')

    #get html on featured image page
    html_feat = browser.html
    soup_img = bs(html_feat, 'html.parser')

    #scrape out url for featured image
    image_url = soup_img.find('figure',class_="lede").a['href']

    #concatenate image_url extension to JPL base url
    base_url = 'https://www.jpl.nasa.gov'
    featured_image_url = base_url + image_url

    #--------------Mars Weather-----------------
    #visit twitter page for scraping latest Mars weather
    url_tweet = "https://twitter.com/MarsWxReport?lang=en"
    browser.visit(url_tweet)

    time.sleep(2)

    #get html on twitter page
    html_tweet = browser.html
    soup_mars = bs(html_tweet, 'html.parser')

    #find parent of twitter posts
    tweet_parent = soup_mars.find_all('article', attrs={'role':'article'})

    #unpack soup object and retrieve first post text
    for tweet in tweet_parent[:1]:
        weather_tweet = tweet.find('div', attrs={'data-testid':'tweet'}).\
                              find('div',class_="css-901oao r-jwli3a r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0").\
                              find('span', class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0").text

    #--------------Mars Facts-----------------
    url_facts = 'https://space-facts.com/mars/'

    #read in tabular data from mars space facts website 
    mars_tables = pd.read_html(url_facts)

    #extract first table with indexing to derive the specific mars facts table we want
    mars_profile_df = mars_tables[0]

    #rename column headers
    mars_profile_df.columns = ['Description','Value']

    #convert table to html
    html_mars_table = mars_profile_df.to_html(index=False,justify='center')

    #--------------Mars Hemispheres-----------------
    
    #create list of partial hemisphere names to use as partial text for link clicking in 'for' loop 
    #to extract info, add to dict, and append to dictionary list
    hemispheres = ['Cerberus','Schiaparelli','Syrtis Major','Valles Marineris']

    #list for dictionary of hemisphere titles/img urls
    hemisphere_image_urls = []

    #for loop to extract each hemisphere img link and title 
    for hemisphere in hemispheres:
    
        #dict for hemisphere title and image url 
        hemi_dict={}
    
        #browser visit site
        url_hemispheres = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url_hemispheres)    
    
        #click link to go to each hemispheres page with larger image url and full hemisphere title
        browser.click_link_by_partial_text(hemisphere)
    
        #sleep to allow full page load and all html to be captured
        time.sleep(2)
    
        #create beautiful soup object to then parse
        html = browser.html
        soup_hemi = bs(html, 'html.parser')
    
        #retrieve hemisphere url and title from their respective tags
        hemi_image_url = soup_hemi.find('li').a['href']
        hemi_title = soup_hemi.find('h2', class_="title").text
    
        #add info to dictionary
        hemi_dict['title'] = hemi_title
        hemi_dict['img_url'] = hemi_image_url
    
        #append dictionary to list of titles/urls dicts
        hemisphere_image_urls.append(hemi_dict)
    
    mars_scrape = {
        "Mars_News_Title": news_title,
        "Mars_News_Paragraph": news_p,
        "Mars_Featured_Image": featured_image_url,
        "Mars_Weather_Tweet": weather_tweet,
        "Mars_Facts_Table": html_mars_table,
        "Mars_Hemispheres": hemisphere_image_urls 
    }

    #Close browser after scraping
    browser.quit()

    #Return results
    return mars_scrape

