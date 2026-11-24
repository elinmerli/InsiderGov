
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin

URL = "https://disclosures-clerk.house.gov/FinancialDisclosure/ViewSearch"

class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.links = []
        self.current_form = None
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "form":
            self.current_form = {
                "method": attrs.get("method", "get"),
                "action": urljoin(URL, attrs.get("action", ""))
            }
            self.forms.append(self.current_form)

        elif tag in ("input", "select", "button"):
            if self.current_form is not None:
                name = attrs.get("name")
                if name:
                    self.current_form.setdefault("fields", []).append(name)

        elif tag == "a":
            self.current_link = {
                "url": urljoin(URL, attrs.get("href", "")),
                "text": ""
            }
            self.links.append(self.current_link)

    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link["text"] += data.strip()

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None
        elif tag == "a":
            self.current_link = None

request = Request(
    URL,
    headers={"User-Agent": "InsiderGov research project"}
)

with urlopen(request, timeout=30) as response:
    html = response.read().decode("utf-8", errors="replace")

page = PageInspector()
page.feed(html)

print("HOUSE DISCLOSURE PAGE INSPECTION")
print("URL:", URL)
print("HTTP status: page loaded successfully")
print("\nFORMS:")

for form in page.forms:
    print("Method:", form["method"])
    print("Action:", form["action"])
    print("Fields:", ", ".join(form.get("fields", [])))

print("\nRELEVANT LINKS:")

for link in page.links:
    if link["text"] or "FinancialDisclosure" in link["url"]:
        print(link["text"], "->", link["url"])
