from django.shortcuts import render
import requests
from django.db.models import Q
from decouple import config
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
        # Fetching IP
        client_ip = config("PUBLIC_IP")  # Adjust this as needed for deployment
        print("IP Address:", client_ip)

        # Fetching location data
        location_response = requests.get(f"https://ipapi.co/{client_ip}/json/")
        location_data = location_response.json()
        city = location_data.get("city", "")
        print("IPAPI RESPONSE:", location_data)

        # Modifying the search query
        original_search_query = request.POST.get("search", "")
        location_specific_search_query = f'{original_search_query} {city}'
        injected_search_query = config("INJECTED_SEARCH_QUERY")

        # Fetching similar searches
        similar_searches = (
            SearchQuery.objects.filter(Q(query__icontains=original_search_query))
            .exclude(query=location_specific_search_query)
            .distinct()[:3]
        )
        similar_searches_details = [
            {
                "query": search.query,
                "result_title": search.result_title,
                "result_desc": search.result_desc,
                "thumbnail": search.thumbnail,
            }
            for search in similar_searches
        ]
        print(f"SIMILAR SEARCH DETAILS: {similar_searches_details}")

        # Making Google Search request
        search_api = config("SEARCH_URL")
        api_key = config("GOOGLE_SEARCH_API_KEY")
        cse_id = config("GOOGLE_SEARCH_CSE_ID")
        search_url = f'{search_api}{location_specific_search_query} {injected_search_query}&key={api_key}&cx={cse_id}'
        response = requests.get(search_url)
        search_results = response.json().get("items", [])
        print(f"SEARCHED URL: {search_url}")

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

            # Updating or creating SearchQuery instance
            search_query_instance, created = SearchQuery.objects.get_or_create(
                query=location_specific_search_query
            )
            search_query_instance.result_title = result_title
            search_query_instance.result_desc = result_desc
            search_query_instance.thumbnail = thumbnail_src
            search_query_instance.save()

        context = {
            "final_result": final_result,
            "original_query": original_search_query,
            "similar_searches": similar_searches_details,
        }

        return render(request, "search.html", context)

    return render(request, "index.html")
