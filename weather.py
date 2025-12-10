import requests
from bs4 import BeautifulSoup


def get_weather_data(city: str='thiruvananthapuram'):
    url = 'https://www.google.com/search?q='+'weather'+city

    res = requests.get(url).content

    soup = BeautifulSoup(res, 'html.parser')

    temperature = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
 
    # formatting data
    data = str.split('\n')
    time = data[0]
    sky = data[1]

    # getting all div tag
    listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
    strd = listdiv[5].text
    
    # getting other required data
    pos = strd.find('Wind')
    other_data = strd[pos:]
    out = f'The temperature is {temperature}. with a {sky} sky'
    print(out)
    return out

if __name__ == '__main__':

    get_weather_data('varkala')
