
# region Applicaiton info
application_version = "1.1.0"
__author__ = "Ahmed Ali"
__copyright__ = "Copyright © 2022"
__version__ = application_version
__email__ = "ahmedali70x@gmail.com"
__status__ = "Production"
try:
    import csv
    import os
    import sys

    import requests
    from bs4 import BeautifulSoup as soup

except:
    def install(package):
        import subprocess
        subprocess.check_call(['pip3', "install", package])
    install("BeautifulSoup4")
    install("requests")
    import csv
    import os
    import sys

    import requests
    from bs4 import BeautifulSoup as soup

# endregion


# my_url = 'https://www.yelp.com/biz/claremont-club-and-spa-a-fairmont-hotel-berkeley-2?osq=Hotels'


def open_url(URL):  # opening URL and grabbing the web page
    response = requests.get(URL)
    if response:
        page_soup = soup(response.text, 'html.parser')
        return page_soup
    else:
        return False


def pages_url(main_url):  # rerieve the list of pages
    pages_url_list = []
    first_page = open_url(main_url)
    if first_page:
        pages_url_list.append(main_url)
        num_of_pages = first_page.find('div',  {
                                       'class': 'border-color--default__09f24__NPAKY text-align--center__09f24__fYBGO'}).span.text
        pages = int(num_of_pages.split(' ')[2])
        
        if pages > 1:
            for num in range(1, pages):
                num *= 10
                next_url = main_url+"?start="+str(num)
                pages_url_list.append(next_url)
    return(pages_url_list)



def soap_search(html_soap):  # Search for the review data in each page
    hotel_name = html_soap.find('h1', attrs = {'class' : 'css-1x9iesk'}).text
    hotel_name = clean_filename(hotel_name) #Sanitize the file name and make it valid
    hotel_file = f'{hotel_name}.csv'  
    reviews = html_soap.findAll(
        'div', {'class': 'review__09f24__oHr9V border-color--default__09f24__NPAKY'})
    
    for review in reviews: #Loop through page reviews
        name = review.find(
            'span', attrs={'class': 'fs-block css-1iikwpv'}).a.text
        location = review.find('span', attrs={'class': 'css-1sufhje'}).text
        rating = review.find('span', attrs={
                             'class': 'display--inline__09f24__c6N_k border-color--default__09f24__NPAKY'}).div["aria-label"]
        date = review.find('span', attrs={'class': 'css-1e4fdj9'}).text
        comment = review.find(
            'span', attrs={'class': 'raw__09f24__T4Ezm'}).text or " "
        cur_review = [name, location, rating, date, comment]

        existing_reviews = []
        if os.path.isfile(hotel_file):
            header = True 
            existing_reviews = get_existing_reviews(hotel_file)
        else:
            header = False

        try: 
            #Append to the file if it exists or create a new file      
            with open(hotel_file, '+a', encoding='utf-8', newline='') as file:
                csv_writer = csv.writer(file)
                if not header: #Insert the header if it is not exist
                    csv_writer.writerow(
                        ["Name", "location", "Rating", "Date", "Review"])

                if cur_review not in existing_reviews: #Check if current review is duplicated

                    csv_writer.writerow(cur_review)
                # print(cur_review[0])

        except:
            print(" [Status] Can not proceed while the CSV file is opened")
            print(" Please close the CSV file and run again")
            sys.exit(0)

#Retrieve total numer of reviews
def total_reviews(html_soap):
    total_reviews = html_soap.find('span', attrs = {'class' : 'css-1yy09vp'}).text
    return total_reviews

#Convert a text into valid file name
def clean_filename(name):
    if not name:
        return ''
    badchars = "\\/:*?\"<>%^|&,$£!\\'\\,"
    for c in badchars:
        name = name.replace(c, '')
    name= name.split()
    name = "_".join(name)
    return name; 

#Retreive existing reviews from CSV file 
def get_existing_reviews(csv_file):
    with open (csv_file, "r", encoding="utf-8") as read_file:
        csv_file = csv.reader(read_file)
        header = next(csv_file)
        csv_list = list(csv_file)
        return csv_list


def sanitize_url(url):
    return url.split("?")[0]


def main():
    try:
        my_url = input(" Please enter a hotel URL: ")
        my_url = sanitize_url(my_url) #Remove extra text from the url
        print(" [Status] Connecting to the URL...")

        pages_url_list = pages_url(my_url) #Retrieve list for all review pages
        # pages_url_list = pages_url_list[0:3] #Testing


        if pages_url_list: #Loop through review pages if exists
            print(" [Status] Successfully connnected.. !")

            for index, page in enumerate(pages_url_list):
                
                html_page = open_url(page)
                if index == 0 : #print total number of reviews
                    review_numbers = total_reviews(html_page)
                    print(f" [Status] Total reviews: {review_numbers}\n")
                    
                print(
                    f' [Status] Scraping page: {index+1}/{len(pages_url_list)}')
                try:
                    if html_page:
                        soap_search(html_page)
                except:
                    print(f" [Status] Error while scrapping page no.{index+1}")
                    continue
            print("\n [Status] Task completed!")
        else:
            print(" [Status] Unable to connect to the submitted URL")
            quit()

    except Exception as err:
        print(" [Status] Connection error, invalid URL")
        print(err)


if __name__ == "__main__":
    main()
