from flask import Flask, jsonify, request,render_template
import requests,json
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv("API_KEY") #'AIzaSyAADqgLLdQqGfWP4eb02ugcsZ2kjjmLvrE'

@app.route('/', methods=['GET'])
def base_template():
    return render_template('index.html',video={},image={})

@app.route('/', methods=['POST'])
def serach_template():
    query = request.form.get('searchbar')
    video_details={}
    image_details=[{}]
    try:
        video_details = search_video(query)
        image_details = search_images(query)
        return render_template('index.html',video=video_details,image=image_details[0])
    except Exception as e:
        return jsonify({'error': 'Not a valid input'}), 400

@app.route('/video', methods=['GET'])
def search_video(q=None):
    try:
        query = q if q else request.args.get('q')
        if query:
            query = query.replace(" ","%20")
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': 1,
                'key': API_KEY
            }
            response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
            if response.status_code == 200:
                data = response.json()
                video={}
                if len(data['items'])>0:
                    video = {
                            'title': data['items'][0]['snippet']['title'],
                            'description': data['items'][0]['snippet']['description'],
                            'videoId': data['items'][0]['id']['videoId'],
                            'url': f"https://www.youtube.com/watch?v={ data['items'][0]['id']['videoId'] }",
                            'thumbnail': data['items'][0]['snippet']['thumbnails']['default']['url']
                        }
                if q:
                    return video
                return jsonify(video)
            else:
                if q:
                    return {}
                return jsonify({'error': 'Failed to retrieve videos'}), response.status_code
        else:
            if q:
                return {}
            return jsonify({'error': 'Query parameter "q" is required'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid query string'}), 400

@app.route('/image', methods=['GET'])
def search_images(q=None):
    search_term = q if q else request.args.get('q')
    if not search_term:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    search_term = search_term.replace(" ","%20")
    url = f'https://www.flickr.com/services/feeds/photos_public.gne?format=json&tags={search_term}'
    response = requests.get(url)
    if response.status_code == 200:
        jsonp_response = response.content.decode('utf-8').replace('jsonFlickrFeed(', '').replace(')', '')
        data = json.loads(jsonp_response)
        items=[]
        if 'items' in data and len(data['items']) > 0:
            for count,value in enumerate(data['items']):
                title = value['title']
                link = value['media']["m"]
                items.append({'title': title, 'link': link})
                if count>=3:
                    break
            if q:
                return items
            return jsonify(items)
        else:
            if q:
                return [{}]
            return jsonify({'error': 'No images found for the given search term'}), 404
    else:
        if q:
            return [{}]
        return jsonify({'error': 'Failed to retrieve images from Flickr'}), response.status_code

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

