from bs4 import BeautifulSoup
import asyncio
import aiohttp
import json
import time
import pytablewriter
import argparse

start_time = time.time()

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", help="File to parse")
parser.add_argument("-o", "--output", help="Output markdown file")

args = parser.parse_args()


with open(args.file, "r") as importedData:
    data = json.load(importedData)


def validateMetaData(metaEntry):
    if metaEntry:
        return metaEntry["content"]
    return "Missing content"

def generateMarkdown(results):
    writer = pytablewriter.MarkdownTableWriter()
    writer.table_name = "Websites"
    writer.header_list = ["URL","Title", "Description", "Image"]
    writer.value_matrix = results

    with open(args.output, "w") as f:
        writer.stream = f
        writer.write_table()


async def makeRequest(session, url):
    resp = await session.get(url)
    page = await resp.text()
    soup = BeautifulSoup(page, "html.parser")
    title = validateMetaData(soup.find("meta", attrs={"property": "og:title"}))
    description = validateMetaData(soup.find("meta", attrs={"property": "og:description"}))
    image  = validateMetaData(soup.find("meta", attrs={"property": "og:image"}))
    image = "<img src=\"{}\" width=\"200\" />".format(image)
    
    return [url, title, description, image]


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in data["items"]:
            print(url)
            tasks.append(makeRequest(session, url))
        results = await asyncio.gather(*tasks)
        generateMarkdown(results)
        
asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))


