from django.shortcuts import render
import requests
from decouple import config
from django.conf import settings
from bs4 import BeautifulSoup as bs
from .models import SearchQuery
from dotenv import load_dotenv

load_dotenv()


def index(request):
    return render(request, "index.html")


def search(request):
    def get_client_ip(req):
        x_forwarded_for = req.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = req.META.get("REMOTE_ADDR")
        return ip

    if request.method == "POST":
        # Get client's IP
        # ! UNCOMMENT WHEN DEPLOYING
        # client_ip = get_client_ip(request)
        # ! COMMENT OUT WHEN BEFORE DEPLOYING
        client_ip = config("PUBLIC_IP")
        print("IP Address:", client_ip)

        # Make a request to ipapi
        location_response = requests.get(f"https://ipapi.co/{client_ip}/json/")
        location_data = location_response.json()
        print("ipapi Response:", location_data)

        # add the city to the search query
        city = location_data.get("city", "")

        # Modify the search query to be specific to the location
        original_search_query = request.POST["search"]
        location_specific_search_query = original_search_query + " in " + city

        search_api = config("SEARCH_URL")
        api_key = config("GOOGLE_SEARCH_API_KEY")
        cse_id = config("GOOGLE_SEARCH_CSE_ID")

        SearchQuery.objects.create(query=location_specific_search_query)

        search_url = (
            f"{search_api}{location_specific_search_query}&key={api_key}&cx={cse_id}"
        )
        print(search_url)

        response = requests.get(search_url)
        search_results = response.json().get("items", [])

        final_result = []

        for result in search_results:
            result_title = result.get("title")
            result_url = result.get("link")
            result_desc = result.get("snippet")

            thumbnail_src = None
            pagemap = result.get("pagemap")
            if pagemap and "cse_thumbnail" in pagemap:
                thumbnail_src = pagemap["cse_thumbnail"][0].get("src")

            final_result.append(
                {
                    "result_title": result_title,
                    "result_url": result_url,
                    "result_desc": result_desc,
                    "thumbnail": thumbnail_src,
                    "original_query": original_search_query,
                }
            )

        context = {
            "final_result": final_result,
            "original_query": original_search_query,
        }
        return render(request, "search.html", context)
    else:
        return render(request, "index.html")


# def search(request):
#     if request.method == "POST":

#         search_query = request.POST["search"]
#         search_api = config("SEARCH_URL")
#         api_key = config("GOOGLE_SEARCH_API_KEY")
#         cse_id = config("GOOGLE_SEARCH_CSE_ID")

#         SearchQuery.objects.create(query=search_query)

#         search_url = f"{search_api}{search_query}&key={api_key}&cx={cse_id}"
#         print(search_url)

#         response = requests.get(search_url)
#         search_results = response.json().get("items", [])

#         final_result = []

#         for result in search_results:
#             result_title = result.get("title")
#             result_url = result.get("link")
#             result_desc = result.get("snippet")

#             thumbnail_src = None
#             pagemap = result.get("pagemap")
#             if pagemap and "cse_thumbnail" in pagemap:
#                 thumbnail_src = pagemap["cse_thumbnail"][0].get("src")

#                 final_result.append(
#                     {
#                         "result_title": result_title,
#                         "result_url": result_url,
#                         "result_desc": result_desc,
#                         "thumbnail": thumbnail_src,
#                     }
#                 )
#         context = {"final_result": final_result}
#         return render(request, "search.html", context)
#     else:
#         return render(request, "index.html")


# def search(request):
#     if request.method == "POST":
#         search = request.POST["search"]
#         search_class = config('SEARCH_CLASS')
#         search_title_class = config('SEARCH_TITLE_CLASS')
#         search_desc_class = config('SEARCH_DESC_CLASS')
#         search_url = config('SEARCH_URL')
#         url = f"{search_url}{search}"
#         print(f"Search Query: {url}")
#         res = requests.get(url)
#         soup = bs(res.text, "lxml")

#         result_listings = soup.find_all("div", {"class": f"{search_class}"})

#         final_result = []

#         for result in result_listings:
#             result_title = result.find(class_=f"{search_title_class}").text
#             result_url = result.find("a").get("href")
#             result_desc = result.find(class_=f"{search_desc_class}").text

#             final_result.append((result_title, result_url, result_desc))

#         context = {"final_result": final_result}

#         return render(request, "search.html", context)
#     else:
#         return render(request, "search.html")
