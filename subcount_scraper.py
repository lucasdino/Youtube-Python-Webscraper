import requests, sys, time, os, argparse, csv, numpy

# List of simple to collect features
channelInfo = ["channelID", "viewCount", "subscriberCount", "videoCount"]

def readcsv(csv_file):

    with open(csv_file, newline='') as csvfile:
        channelArr = list(csv.reader(csvfile))
    
    channelArr.pop(0)
    cleanedArr = []

    for i in range(len(channelArr)):
        cleanedArr.append(channelArr[i][0])


    return cleanedArr


def setup(api_path, channel_path):
    with open(api_path, 'r') as file:
        api_key = file.readline()

    return api_key, readcsv(channel_path)


def api_request(channelID):
    # Builds the URL and requests the JSON from it
    
    request_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channelID}&key={api_key}"
    request = requests.get(request_url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()


def get_channel(channelArr):
    lines = []
    
    for channelID in channelArr:

        # We can assume something is wrong with the channel if it has no statistics, often this means it has been deleted
        # so we can just skip it
        channelData = api_request(channelID)

        try: 
            # Snippet and statistics are sub-dicts of video, containing the most useful info
            viewCount = channelData['items'][0]['statistics']['viewCount']
            subCount = channelData['items'][0]['statistics']['subscriberCount']
            videoCount = channelData['items'][0]['statistics']['videoCount']
            itemData = [channelID, viewCount, subCount, videoCount]
            lines.append(itemData)
        except KeyError: 
            lines.append(["na", "na", "na", "na"])

    return lines


def write_to_file(channelData):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/20.18.12_Subcount.csv", "w+", encoding='utf-8') as file:
        for row in channelData:
            file.write(f"{row}\n")


def get_data():
    channel_data = [",".join(channelInfo)]
    channel_pulleddata = get_channel(channelArr)

    for i in range(len(channel_pulleddata)):
        channel_data += [",".join(channel_pulleddata[i])]
    
    write_to_file(channel_data)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--key_path', help='Path to the file containing the api key, by default will use api_key.txt in the same directory', default='api_key.txt')
    parser.add_argument('--channel_path', help='Path to the csv file containing the different channel IDs, by default will use channels.csv in the same directory', default='channels.csv')
    parser.add_argument('--output_dir', help='Path to save the outputted files in', default='output/')

    args = parser.parse_args()

    output_dir = args.output_dir
    api_key, channelArr = setup(args.key_path, args.channel_path)

    get_data()