import requests
import os
import random

from dotenv import load_dotenv

VK_API_VERSION = 5.131


def get_rand_comics():

    url_last_comics = "https://xkcd.com/info.0.json"
    
    last_comics_response = requests.get(url_last_comics)
    last_comics_response.raise_for_status()
    last_comics_information = last_comics_response.json()
    number_comics = last_comics_information['num']
    
    rand_number_comics = random.randint(1,number_comics)
    comics_url = f"https://xkcd.com/{rand_number_comics}/info.0.json"
    comics_filename = 'comics.png'
    
    comics_response = requests.get(comics_url)
    comics_response.raise_for_status()
    comics_information = comics_response.json()
    img_url = comics_information['img']
    comics_comment = comics_information['alt']
    
    comics_image_response = requests.get(img_url)
    comics_image_response.raise_for_status()
    
    with open(comics_filename, 'wb') as file:
        file.write(comics_image_response.content)

    return comics_comment


def get_upload_url(vk_headers,vk_group_id):

        url_request = 'https://api.vk.com/method/photos.getWallUploadServer'
        params = {
                    'group_id': vk_group_id,
                    'v': VK_API_VERSION
                    }
  
        response = requests.post(url_request,params=params,headers=vk_headers)
        response.raise_for_status()
        response_formatted = response.json()

        return response_formatted['response']['upload_url']


def upload_photo(vk_headers, upload_photo_url):

    with open('comics.png', 'rb') as file:
      
        files = {
            'photo': file, 
        }
      
        upload_photo_response = requests.post(upload_photo_url,files=files,headers=vk_headers)
        upload_photo_response.raise_for_status()
        upload_photo_response_formatted = upload_photo_response.json()

    return upload_photo_response_formatted


def save_photo(vk_headers,upload_photo_response,vk_group_id):

    saved_url_request = 'https://api.vk.com/method/photos.saveWallPhoto'
  
    vk_params_save = {
            'group_id': vk_group_id,
            'v': VK_API_VERSION,
            'photo':upload_photo_response['photo'],
            'hash':upload_photo_response['hash'],
            'server':upload_photo_response['server']
            }
    vk_response_save = requests.post(saved_url_request, params=vk_params_save,headers=vk_headers)
    vk_response_save.raise_for_status()
    vk_response_formatted_save = vk_response_save.json()
    
    person_id = vk_response_formatted_save['response'][0]['owner_id']
    photo_id = vk_response_formatted_save['response'][0]['id']

    return person_id, photo_id


def publish_photo(vk_headers,person_id,photo_id,vk_group_id, comics_comment):

    publish_url = 'https://api.vk.com/method/wall.post'
    publish_params = {
                'owner_id': -int(vk_group_id),
                'from_group': 1,
                'message':comics_comment,
                'attachments':f'photo{person_id}_{photo_id}',
                'v': VK_API_VERSION
                }
  
    response_publish = requests.post(publish_url, params=publish_params,  headers=vk_headers)
    response_publish.raise_for_status()


if __name__ == '__main__':

    load_dotenv()
  
    vk_access_token = os.environ['vk_access_token']
    vk_group_id = os.environ['vk_group_id']
  
    vk_headers = {'Authorization': 'Bearer {}'.format(vk_access_token)}
  
    comics_comment = get_rand_comics()
    upload_photo_url = get_upload_url(vk_headers,vk_group_id)
    upload_photo_response = upload_photo(vk_headers, upload_photo_url)
    person_id, photo_id =  save_photo(vk_headers,upload_photo_response,vk_group_id)
    publish_photo(vk_headers,person_id,photo_id,vk_group_id,comics_comment)
  
    os.remove('comics.png')
  

