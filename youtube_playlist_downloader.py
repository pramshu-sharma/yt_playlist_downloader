from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import time


def get_html(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(4)
    body = driver.find_element(By.TAG_NAME, 'body')
    previous_videos_count = 0
    while True:
        body.send_keys(Keys.END)
        time.sleep(4)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        new_videos_count = len(soup.find_all('a', id='video-title'))
        if previous_videos_count == new_videos_count:
            print('HTML Returned')
            driver.quit()
            break
        previous_videos_count = new_videos_count
    return soup


def get_links(soup):
    videos = soup.find_all('a', id='video-title')
    videos_list = []
    for video in videos:
        link = 'https://www.youtube.com' + video['href'].split('&')[0]
        videos_list.append(link)
    print('Links Created')
    return videos_list


def get_mp3(video_list, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for idx, video in enumerate(video_list):
        yt = YouTube(video)
        stream = yt.streams.get_lowest_resolution()
        output_path = os.path.join(download_dir)
        stream.download(output_path=output_path)
        print(f'Downloaded ({idx + 1}): {yt.title}')

        files = os.listdir(download_dir)
        for file in files:
            if file.endswith('.mp4'):
                input_file = f'{download_dir}/{file}'
                output_file_name = file.split('.')[0] + '.mp3'
                output_file = f'{download_dir}/{output_file_name}'
                convert_to_mp3(input_file, output_file)


def convert_to_mp3(in_file, out_file):
    video_clip = VideoFileClip(in_file)
    audio = video_clip.audio
    audio.write_audiofile(out_file)
    audio.close()
    video_clip.close()
    os.remove(in_file)


if __name__ == '__main__':
    playlist_url = 'https://www.youtube.com/playlist?list=PLuhDoVPC1wMKYM5Wqq2tyPQMc-GDX3pxE'
    dwnld_dir = 'download_dir'
    page = get_html(playlist_url)
    links = get_links(page)
    get_mp3(links, dwnld_dir)
