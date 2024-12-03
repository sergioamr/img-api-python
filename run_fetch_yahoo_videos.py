def audio_pipeline():
    api_params = "?source=YFINANCE&limit=20&articles__size=0"
    json_in = api.api_call("/news/query" + api_params)
    for article in json_in['news']:
        if article["publisher"] == "Yahoo Finance Video":
            audio_file = download_file(article["link"])
            transcript = transcribe_file(audio_file)
            delete_file(audio_file)
            text = extract_article(article["link"])

            #update
            article["articles"] = [transcript, text]
            articles["status"] = "INDEXED"

def download_file(video_url):
    video = YouTube(video_url)
    audio = video.streams.get_audio_only()
    audio_file = audio.download(mp3=True)
    audio_file = replace_spaces(audio_file)
    return audio_file

def transcribe_file(audio_file):
    # Set the device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load the model 
    whisper_model = whisper.load_model("large", device=device)
    result = whisper_model.transcribe(audio_file)
    return result["text"]

def extract_article(url):
    html = extract_html(url)
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_ = "body yf-5ef8bf").get_text()
    return article

def delete_file(path):
    try:
        # Check if file exists
        if os.path.isfile(file_path):
            os.remove(file_path)
        else:
            pass
    except Exception as e:
        print(e)

def replace_spaces(text):
    return text.replace(" ", "_")
