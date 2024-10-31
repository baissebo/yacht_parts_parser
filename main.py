import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://yacht-parts.ru/"


def get_categories(base_url):
    catalog_url = base_url + "catalog/"
    response = requests.get(catalog_url)
    soup = BeautifulSoup(response.text, "html.parser")
    categories = []

    subsections = soup.find_all("ul", class_="subsections")
    for subsection in subsections:
        items = subsection.find_all("li", class_="sect")
        for item in items:
            category_name = item.a.text.strip()
            category_link = item.a["href"]
            categories.append((category_name, base_url + category_link))
    return categories


def get_products_from_category(category_url, category_name):
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, "html.parser")
    product_data_list = []

    products = soup.find_all("td", class_="description_wrapp")
    for product in products:
        product_link = product.find("a")["href"]
        full_product_url = base_url + product_link
        product_data = get_product_data(full_product_url, category_name)
        if product_data:
            product_data_list.append(product_data)

    return product_data_list


def get_product_data(product_url, category_name):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        name = soup.select_one("div.item-title a span").text.strip()
        description = soup.select_one("div.preview_text").text.strip() if soup.select_one(
            "div.preview_text") else "Описание не найдено"
        article_value = soup.select_one("div.article span.value").text.strip() if soup.select_one(
            "div.article") else "Артикул не найден"
        price = soup.select_one("div.cost .price").text.strip() if soup.select_one(
            "div.cost .price") else "Цена не найдена"
        img_links = [img["src"] for img in soup.find_all("img") if "src" in img.attrs]

        return {
            "Категория": category_name,
            "Наименование товара": name,
            "Описание": description,
            "Артикул": article_value,
            "Цена": price,
            "Ссылки на изображения": ', '.join(img_links),
        }

    except Exception as e:
        print(f"Ошибка при парсинге {product_url}: {e}")
    return None


def main():
    categories = get_categories(base_url)
    all_products_data = []

    for category_name, category_url in categories:
        products_data = get_products_from_category(category_url, category_name)
        all_products_data.extend(products_data)

    df_products = pd.DataFrame(all_products_data)
    df_products.to_excel("catalog.xlsx", index=False)


if __name__ == "__main__":
    main()
