import requests

def get_random_quote():
    try:
        url = "http://api.forismatic.com/api/1.0/"
        params = {
            'method': 'getQuote',
            'format': 'json',
            'lang': 'en'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            quote_text = data.get("quoteText", "No quote found.")
            quote_author = data.get("quoteAuthor", "Unknown")
            return f'"{quote_text}" - {quote_author}'
        else:
            return "Sorry, I couldn't fetch a quote at the moment."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    print(get_random_quote())
