import requests
import re
from django.shortcuts import render
from django.db.models import Q
from decouple import config
from django.core.paginator import Paginator, EmptyPage
from .models import SearchQuery
from dotenv import load_dotenv
from .models import ArticlePosts, Tag

load_dotenv()


def index(request):
    article_posts = ArticlePosts.objects.all()
    tags = Tag.objects.all()

    context = {
        "article_posts": article_posts,
        "tags": tags,
    }

    return render(request, "index.html", context)


# Grab client ip / not needed in development
def get_client_ip_address(req):
    x_forwarded_for = req.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = req.META.get("REMOTE_ADDR")
    return ip


# Location data retrieval
def get_location_data(client_ip):
    location_response = requests.get(f"https://ipapi.co/{client_ip}/json/")
    return location_response.json()


# Search query modification
def modify_search_query(original_search_query, country_name):
    location_specific_search_query = f"{original_search_query} in {country_name}"
    return original_search_query, location_specific_search_query


def fetch_unsplash_image(query):
    UNSPLASH_URL = config("UNSPLASH_URL")
    UNSPLASH_API_KEY = config("UNSPLASH_API_KEY")

    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape",
    }

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_API_KEY}",
    }

    response = requests.get(UNSPLASH_URL, params=params, headers=headers)
    data = response.json()

    # Extract the image URL from the response
    image_url = data["results"][0]["urls"]["full"] if data["results"] else None
    print(f"UNSPLASH IMAGE RETRIEVED: {image_url}")

    return image_url


# Fetching similar searches
def fetch_similar_searches(original_search_query, location_specific_search_query):
    similar_searches = (
        SearchQuery.objects.filter(Q(query__icontains=original_search_query))
        .exclude(query=location_specific_search_query)
        .distinct()[:3]
    )
    print(f"SIMILAR SEARCHES: {similar_searches}")
    return [
        {
            "query": search.query,
            "result_title": search.result_title,
            "result_desc": search.result_desc,
            "thumbnail": search.thumbnail,
        }
        for search in similar_searches
    ]


# Google search request
def fetch_google_search_results(injected_search_query, original_search_query, country_name):
    search_api = config("SEARCH_URL")
    api_key = config("GOOGLE_SEARCH_API_KEY")
    cse_id = config("GOOGLE_SEARCH_CSE_ID")
    search_url = f'{search_api}{injected_search_query} "{original_search_query}" in "{country_name}"&key={api_key}&cx={cse_id}'
    # search_url = f"{search_api}{injected_search_query} {location_specific_search_query}&key={api_key}&cx={cse_id}"
    response = requests.get(search_url)
    print(f"ALTERED SEARCH QUERY: {search_url}")
    return response.json()


# Processing search results
def process_search_results(
    search_results, original_search_query, location_specific_search_query
):
    final_result = []
    for result in search_results.get("items", []):
        result_title = result.get("title")
        result_url = result.get("link")
        result_desc = result.get("snippet")
        display_link = result.get("displayLink")
        formatted_url = result.get("formattedUrl")
        mime_type = result.get("mime", None)
        file_format = result.get("fileFormat", None)

        thumbnail_src = None
        pagemap = result.get("pagemap")
        if pagemap and "cse_thumbnail" in pagemap:
            thumbnail_src = pagemap["cse_thumbnail"][0].get("src")
        else:
            # Fetch a random image from Unsplash based on the search query
            thumbnail_src = fetch_unsplash_image(original_search_query)

        # Extract date from result_desc
        date_pattern = re.compile(
            r"([A-Za-z]{3} \d{1,2}, \d{4})"
        )  # This pattern matches "Feb 15, 2023"
        match = date_pattern.search(result_desc)
        result_date = (
            match.group() if match else None
        )  # Stores the date if found, else None

        # Remove the date from the result_desc
        if result_date:
            result_desc = result_desc.replace(result_date, "").strip()
        result_desc = result_desc.strip("...").strip()

        final_result.append(
            {
                "result_title": result_title,
                "result_url": result_url,
                "result_desc": result_desc,
                "thumbnail": thumbnail_src,
                "display_link": display_link,
                "formatted_url": formatted_url,
                "mime_type": mime_type,
                "file_format": file_format,
                "original_query": original_search_query,
                "result_date": result_date,
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

        final_result.append(
            {
                "result_title": result_title,
                "result_url": result_url,
                "result_desc": result_desc,
                "thumbnail": thumbnail_src,
                "display_link": display_link,
                "formatted_url": formatted_url,
                "mime_type": mime_type,
                "file_format": file_format,
                "original_query": original_search_query,
                "result_date": result_date,
            }
        )
    return final_result


def search(request):
    if request.method == "POST":
        # Fetching IP
        # client_ip = get_client_ip_address(request)
        client_ip = config("DEVELOPMENT_IP")

        # Fetching location data
        location_data = get_location_data(client_ip)
        country_name = location_data.get("country_name", "")
        print(f"LOCATION DATA: {location_data}")

        # Modifying the search query
        original_search_query, location_specific_search_query = modify_search_query(
            request.POST.get("search", ""), country_name
        )

        # Fetching similar searches
        similar_searches_details = fetch_similar_searches(
            original_search_query, location_specific_search_query
        )

        # Making Google Search request
        search_response = fetch_google_search_results(
            config("INJECTED_SEARCH_QUERY"), original_search_query, country_name
        )

        # Processing Search Results
        final_result = process_search_results(
            search_response, original_search_query, location_specific_search_query
        )

        page = request.GET.get("page", 1)  # Get the page number from request
        paginator = Paginator(final_result, 300)

        try:
            results_to_show = paginator.page(page)
        except EmptyPage:
            # If the page number exceeds the available pages, return an empty list
            results_to_show = []

        if 'query' in request.GET:
            original_search_query = request.GET['query']
        elif request.method == "POST":
            original_search_query = request.POST.get("search", "")
        else:
            return render(request, "index.html")

        context = {
            "final_result": results_to_show,
            "original_query": original_search_query,
            "similar_searches": similar_searches_details,
            "total_results_count": search_response.get("searchInformation", {}).get(
                "totalResults", 0
            ),
        }
        return render(request, "search.html", context)

    return render(request, "search.html")
