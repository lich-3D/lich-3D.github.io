import os
import math
import jinja2

# 模板内容
markdown_template = """# 王叔叔3D打印工坊产品介绍

|序号|模型名称  |模型尺寸|说明  |链接地址|
|----|-------   |-------|--------|----|
{% for product in products %}
|{{ product['index'] }}|{{ product['name'] }}|{{ product['size'] }}|{{ product['description'] }}|[https://3d.lich.tech/{{ product['index'] }}.html](https://3d.lich.tech/{{ product['index'] }}.html)|
{% endfor %}
"""

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D模型 - {{ product['name'] }}</title>
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
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .images-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            flex-grow: 1;
            overflow-y: auto;
        }
        .images-container img {
            max-width: 100%;
            height: auto;
            margin-top: 10px;
            /* 动态设置最大高度 */
            max-height: {{ max_image_height }}cm;
        }
        .product-info {
            margin-top: 20px;
        }
        .product-info p {
            margin: 5px 0;
            font-size: 18px;
        }
        .navigation {
            margin-top: 20px;
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
            .images-container {
                overflow: visible;
            }
        }
    </style>
</head>
<body>
    <div class="page-content">
        <h1>{{ product['name'] }}</h1>
        <div class="images-container">
            {% for image in product['images'] %}
            <img src="{{ image }}" alt="{{ product['name'] }}">
            {% endfor %}
        </div>
        <div class="product-info">
            <p><strong>描述：</strong> {{ product['description'] }}</p>
            <p><strong>尺寸：</strong> {{ product['size'] }}</p>
        </div>
        <div class="navigation">
            {% if product['prev_index'] %}
            <a href="https://3d.lich.tech/{{ product['prev_index'] }}.html">上一页</a>
            {% endif %}
            {% if product['next_index'] %}
            <a href="https://3d.lich.tech/{{ product['next_index'] }}.html">下一页</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# 读取现有的Markdown文件
markdown_file = "README.md"
if os.path.exists(markdown_file):
    with open(markdown_file, "r", encoding="utf-8") as md_file:
        md_content = md_file.read()
else:
    md_content = ""

# 提取现有产品数据
products = {}
if md_content:
    for line in md_content.splitlines():
        if line.startswith("|") and "序号" not in line:
            parts = line.split("|")
            try:
                index = str(int(parts[1].strip()))  # 仅处理有效的数字序号
                products[index] = {
                    "index": index,
                    "name": parts[2].strip(),
                    "size": parts[3].strip(),
                    "description": parts[4].strip(),
                    "images": [],
                    "prev_index": None,
                    "next_index": None
                }
            except ValueError:
                # 忽略无法转换为数字的索引行
                continue

# 更新Markdown内容
new_entries = []
for file in sorted(os.listdir('.')):
    if file.endswith('.jpg'):
        index = file.split('-')[0]
        if index in products:
            products[index]['images'].append(f"https://3d.lich.tech/{file}")
        else:
            product_name = file.split('-')[1].split('.')[0]
            products[index] = {
                "index": index,
                "name": product_name,
                "size": "未知尺寸",
                "description": f"这是一个{product_name}3D打印模型",
                "images": [f"https://3d.lich.tech/{file}"],
                "prev_index": None,
                "next_index": None
            }
            new_entries.append(products[index])

# 将新条目写入Markdown文件
if new_entries:
    with open(markdown_file, "w", encoding="utf-8") as md_file:
        # 重新渲染完整的Markdown内容
        md_file.write(jinja2.Template(markdown_template).render(products=sorted(products.values(), key=lambda x: int(x['index']))))

# 生成HTML文件
product_list = list(sorted(products.values(), key=lambda x: int(x['index'])))
total_available_height_cm = 29.7 - 5  # 减去标题、描述和导航的大致高度（单位：cm）

for i, product in enumerate(product_list):
    if i > 0:
        product['prev_index'] = product_list[i - 1]['index']
    if i < len(product_list) - 1:
        product['next_index'] = product_list[i + 1]['index']

    html_file_path = f"{product['index']}.html"
    if product['images']:  # 如果有图片才生成HTML文件
        num_images = len(product['images'])
        if num_images > 0:
            # 动态计算每张图片的最大高度
            max_image_height = math.floor(total_available_height_cm / num_images * 10) / 10  # 保留一位小数
            # 设置一个最小高度，防止图片过小
            max_image_height = max(max_image_height, 5)
        else:
            max_image_height = 10  # 默认值

        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(jinja2.Template(html_template).render(product=product, max_image_height=max_image_height))
    elif os.path.exists(html_file_path):
        # 如果没有图片且HTML文件存在，则删除HTML文件
        os.remove(html_file_path)
