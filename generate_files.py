import os
import jinja2
import re

# 自然排序函数
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

# 模板内容
markdown_template = """# 王叔叔3D打印工坊产品介绍
----------------------
|序号|模型名称  |模型尺寸|说明  |链接地址|
|----|-------   |-------|--------|----|
{% for product in products -%}
|{{ product.index }}|{{ product.name }}|{{ product.size }}|{{ product.description }}|[https://3d.lich.tech/{{ product.index }}.html](https://3d.lich.tech/{{ product.index }}.html)|
{% endfor %}
"""

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D模型 - {{ product.name }}</title>
    <style>
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .page-content {
            width: 21cm;
            height: 29.7cm;
            padding: 20px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            box-sizing: border-box;
            overflow: hidden;
        }
        .page-content img {
            max-width: 100%;
            height: auto;
            margin-top: 20px;
        }
        .product-info {
            margin-top: 20px;
        }
        .product-info p {
            margin: 5px 0;
            font-size: 18px;
        }
        .navigation {
            margin-top: 30px;
        }
        .navigation a {
            margin-right: 10px;
            text-decoration: none;
            color: #007bff;
            font-size: 18px;
        }
        @media print {
            body, .page-content {
                margin: 0;
                box-shadow: none;
                width: 100%;
                height: 100%;
                page-break-after: avoid;
            }
            .navigation {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="page-content">
        <h1>{{ product.name }}</h1>
        {% for image in product.images %}
        <img src="{{ image }}" alt="{{ product.name }}">
        {% endfor %}
        <div class="product-info">
            <p><strong>描述：</strong> {{ product.description }}</p>
            <p><strong>尺寸：</strong> {{ product.size }}</p>
        </div>
    </div>

    <div class="navigation">
        {% if product.prev_index %}
        <a href="https://3d.lich.tech/{{ product.prev_index }}.html">上一页</a>
        {% endif %}
        {% if product.next_index %}
        <a href="https://3d.lich.tech/{{ product.next_index }}.html">下一页</a>
        {% endif %}
    </div>
</body>
</html>
"""

# 假设模型数据，实际数据可以从文件夹中解析
products = {}

# 收集所有以"-"分隔的图片文件，归类到相应的index
for file in sorted(os.listdir('.'), key=natural_sort_key):
    if file.endswith('.jpg'):
        index = file.split('-')[0]
        if index not in products:
            products[index] = {
                "index": index,
                "name": file.split('-')[1].split('.')[0],  # 使用文件名作为模型名称
                "size": "未知尺寸",  # 你可以根据实际情况解析尺寸
                "description": f"这是一个{file.split('-')[1].split('.')[0]}3D打印模型",  # 简单描述
                "images": [f"https://3d.lich.tech/{file}"]
            }
        else:
            products[index]["images"].append(f"https://3d.lich.tech/{file}")

# 生成 markdown 并写入 README.md
with open("README.md", "w", encoding="utf-8") as md_file:
    md_content = jinja2.Template(markdown_template).render(products=products.values())
    md_file.write(md_content)

# 生成 html 文件
product_list = list(products.values())
for i, product in enumerate(product_list):
    if i > 0:
        product['prev_index'] = product_list[i - 1]['index']
    else:
        product['prev_index'] = None

    if i < len(product_list) - 1:
        product['next_index'] = product_list[i + 1]['index']
    else:
        product['next_index'] = None

    with open(f"{product['index']}.html", "w", encoding="utf-8") as html_file:
        html_content = jinja2.Template(html_template).render(product=product)
        html_file.write(html_content)
