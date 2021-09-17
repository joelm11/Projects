from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import requests
import re
import time

"""
Requests HTML, parses, downloads necessary images, and formats  
"""
class scraper:
    def __init__(self):
        self.infoString = "{Empty}"
        self.opggImgSize = 64
        self.runeSize = 54
        self.keystoneRuneSize = 128
        self.miniRuneSize = 20
    """
    To Do:
    **Instead of saving images just put into list and then modify**
     """
    def getWinrate(self, summonerName):
        r = requests.get('https://na.op.gg/summoner/userName={userName}'.format(userName=summonerName), headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
        soup = BeautifulSoup(r.content,'html.parser')
        wins = soup.select('.wins')[0].text
        losses = soup.select('.losses')[0].text
        winrate = re.search(r'(\d\d)%', soup.select('.winratio')[0].text)[1]
        self.infoString = "With {wins} and {losses}, {summonerName} has a {winrate}% winrate.".format(wins=wins,losses=losses,
        summonerName=summonerName,winrate=winrate)

    def getCounters(self, champName):
        startUrl = 'https://na.op.gg/champion/'+champName+'/statistics'
        r = requests.get(startUrl, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
        soup = BeautifulSoup(r.content,'html.parser')
        counters = soup.select('.champion-stats-header-matchup__table__champion')
        counterList = [re.search(r'\s(\w*)\s', counter.text)[1] for counter in counters]
        counterList = counterList[:3]
        self.infoString = "The highest winrate counters to {champion}: {one}, {two}, and {three}.".format(
        champion = champName, one = counterList[0], two = counterList[1], three = counterList[2]
        )

    def getbuildsbetter(self,champName, soup = None):
        if soup is None:
            startUrl = startUrl = 'https://na.op.gg/champion/'+champName+'/statistics'
            r = requests.get(startUrl, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
            soup = BeautifulSoup(r.content,'html.parser')

        css = '.champion-overview__stats--win.champion-overview__border strong'
        bestBuild = soup.select(css)
        greatest = re.search(r'(\d*.\d*)%', bestBuild[0].text)[0]
        index = 2
        #Scrape all winrates in list, find highest winrate and position in row
        #Winrate position is used to find nth child in list.
        for i in range(2,7):
            temp = re.search(r'(\d*.\d*)%', bestBuild[i].text)[1]
            if temp > greatest:
                greatest = temp
                greatestindex = index
            index += 1
        greatestindex = greatestindex+1
        bestBuild = soup.select('.champion-overview__row:nth-child(%d) .champion-stats__list'%greatestindex)
        #getitem links from prior chunk
        itemHtml = bestBuild[0].select('img')
        itemLinks = [itemlink.get('src') for itemlink in itemHtml]
        i = 0
        imageList = []
        for item in itemLinks:
            image = requests.get('https:'+item, stream=True, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
            image.raw.decode_content = True #To decompress images
            with Image.open(image.raw) as img:
                if i % 2 ==0:
                    img.convert('RGBA')
                    imageList.append(img)
            image.close() #Necessary when using request stream
            i += 1
        #manipulate images
        imageList = iter(imageList)
        outputImage = Image.new('RGBA', (self.opggImgSize*5, self.opggImgSize))
        arrow = Image.open('rightarrow3.png')
        arrow.thumbnail((self.opggImgSize,self.opggImgSize))
        for index in range(0,5):
            if index % 2 == 0:
                temp = next(imageList)
                outputImage.paste(temp,((index*self.opggImgSize),0))
            else:
                outputImage.paste(arrow,(index*self.opggImgSize,0))
        outputImagename = "retImages/%sfinalbuild.png"%champName
        outputImage.save(outputImagename)
        self.infoString = 'C:/Users/Joel/uvic/Seng265/mirror/pybot/%s'%outputImagename

    def getskills(self,champName):
        startUrl = startUrl = 'https://na.op.gg/champion/'+champName+'/statistics'
        r = requests.get(startUrl, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
        soup = BeautifulSoup(r.content,'html.parser')
        skills = soup.select('tbody~ tbody .champion-stats__list')
        skillshtml = skills[0].select('img')
        skillstext = skills[0].get_text()
        skillLetters = re.findall(r'[QWE]', skillstext)
        skillLetters = iter(skillLetters)
        skillimgs = [skillimg.get('src') for skillimg in skillshtml]
        skillImages = []
        i = 0
        for skill in skillimgs:
            image = requests.get('https:'+skill, stream=True, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
            image.raw.decode_content = True
            with Image.open(image.raw) as img:
                if i % 2 ==0:
                    img = img.convert(mode = 'RGBA')
                    skillImages.append(img)
            image.close()
            i += 1
        skillImages = iter(skillImages)
        outputImage = Image.new('RGBA', (self.opggImgSize*5, self.opggImgSize))
        fnt = ImageFont.truetype("C:/Users/Joel/uvic/Seng265/mirror/pybot/Roboto-Black.ttf", size = 50)
        arrow = Image.open('rightarrow3.png')
        arrow.thumbnail((self.opggImgSize,self.opggImgSize))
        for index in range(0,5):
            if index % 2 == 0:
                baseImg = next(skillImages)
                baseImg = baseImg.resize((self.opggImgSize, self.opggImgSize))
                temp = Image.new("RGBA", baseImg.size, (255,255,255,0))
                overlay = ImageDraw.Draw(temp)
                message = next(skillLetters)
                overlay.text((12,5.5), message, font = fnt, fill = (255,255,255,150))
                baseOverlaid = Image.alpha_composite(baseImg, temp)
                outputImage.paste(baseOverlaid,((index*self.opggImgSize),0))
            else:
                outputImage.paste(arrow,(index*self.opggImgSize,0))
        outputImagename = "retImages/%sfinalskills.png"%champName
        outputImage.save(outputImagename)
        self.infoString = 'C:/Users/Joel/uvic/Seng265/mirror/pybot/%s'%outputImagename
        return soup

    def getbuildandskills(self,champName):
        soup = self.getskills(champName)
        self.getbuildsbetter(champName, soup)
        outputImage = Image.new('RGBA', (self.opggImgSize*5, self.opggImgSize*2))
        skills = Image.open('retImages/%sfinalskills.png'%champName)
        build = Image.open('retImages/%sfinalbuild.png'%champName)
        outputImage.paste(skills,(0,0))
        outputImage.paste(build,(0,self.opggImgSize))
        outputImagename = "retImages/%sfinalbuildandskills.png"%champName
        outputImage.save(outputImagename)
        self.infoString = 'C:/Users/Joel/uvic/Seng265/mirror/pybot/%s'%outputImagename
        return soup

    def getrunes(self,champName, soup = None):
        if soup is None:
            startUrl = startUrl = 'https://na.op.gg/champion/'+champName+'/statistics'
            r = requests.get(startUrl, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
            soup = BeautifulSoup(r.content,'html.parser')
        runeBlock = soup.select('tr:nth-child(1) .perk-page-wrap')[0]
        activeRunes = runeBlock.select('tr:nth-child(1) .perk-page__item--active img')
        activeRunesImgs = [activeRune.get('src') for activeRune in activeRunes]

            #TODO maybe also grab little runes
        miniRunes = runeBlock.select('tr:nth-child(1) .active.tip')
        miniRunesImgs = [miniRune.get('src') for miniRune in miniRunes]
        #print(miniRunesImgs)
        i = 0
        activeRuneImages = []
        for activeRuneImg in activeRunesImgs:
            image = requests.get('https:'+activeRuneImg, stream=True, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
            image.raw.decode_content = True
            with Image.open(image.raw) as img:
                img = img.convert('RGBA')
                activeRuneImages.append(img)
            image.close()
            i += 1
        activeRuneImages = iter(activeRuneImages)
        miniRuneImages = []
        for miniRuneImg in miniRunesImgs:
            image = requests.get('https:'+miniRuneImg, stream=True, headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
            image.raw.decode_content = True
            with Image.open(image.raw) as img:
                img = img.convert('RGBA')
                miniRuneImages.append(img)
            image.close()
            i += 1
        miniRuneImages = iter(miniRuneImages)
            #128 + 4 +4 = 136 width
            #4+128+4+54+4+54+4+54+4 = 310 height
            #mini runes of size 48
        outputImage = Image.new('RGBA', (136, 310))
        for index in range(0,9):
            if index == 0:
                runeImg = next(activeRuneImages)
                runeImg.thumbnail((self.keystoneRuneSize, self.keystoneRuneSize))
                outputImage.paste(runeImg, (2, 8))
            elif index == 4 or index == 5:
                runeImg = next(activeRuneImages)
                runeImg.thumbnail((self.runeSize, self.runeSize))
                outputImage.paste(runeImg, (78, 128 + 4*(index % 4 + 2) + 54*(index % 4)))
            elif index == 6:
                runeminiImg1 = next(miniRuneImages)
                runeminiImg2 = next(miniRuneImages)
                runeminiImg3 = next(miniRuneImages)
                runeminiImg1.thumbnail((self.miniRuneSize, self.miniRuneSize))
                runeminiImg2.thumbnail((self.miniRuneSize, self.miniRuneSize))
                runeminiImg3.thumbnail((self.miniRuneSize, self.miniRuneSize))
                outputImage.paste(runeminiImg1, (95, 128 + 4*(index % 4 + 4) + 54*(index % 4)))
                outputImage.paste(runeminiImg2, (82, 128 + 4*(index % 4 + 9) + 54*(index % 4)))
                outputImage.paste(runeminiImg3, (108, 128 + 4*(index % 4 + 9) + 54*(index % 4)))
                break
            else:
                runeImg = next(activeRuneImages)
                runeImg.thumbnail((self.runeSize, self.runeSize))
                outputImage.paste(runeImg, (4, 128 + 4*(index + 1) + 54*(index - 1)))
        outputImagename = "retimages/%sfinalrunes.png"%champName
        outputImage.save(outputImagename)
        self.infoString = 'C:/Users/Joel/uvic/Seng265/mirror/pybot/%s'%outputImagename


    def getall(self,champName):
        start = time.time()
        filepaths = []
        soup = self.getbuildandskills(champName)
        filepaths.append(self.infoString)
        self.getrunes(champName, soup)
        filepaths.append(self.infoString)
        end = time.time()
        print("Time to complete requests and image processing:",end-start)
        return filepaths

    def get_champion_winrate(self, summonerName, champName):
        r = requests.get('https://na.op.gg/summoner/userName={userName}'.format(userName=summonerName), headers={'User-Agent': 'Chrome/58.0.3029.110', 'Referer' : "https://www.google.com"})
        soup = BeautifulSoup(r.content,'html.parser')
        soup.select("td[data-value = 'Quinn']")
        print(soup.prettify())
        return


    def getTeamcomp(self,champName):

        return
