import sys

import pandas as pd
import toml


def load_toml(path=None):
    with open(path, "r") as f:
        return toml.load(f)


def get_tag_html(tags):
    color_settings = load_toml("setting.toml")["color"]["badge"]
    if type(tags) == list:
        return "".join(
            [
                f'<span class="badge badge-{color_settings[tag]}">{tag}</span>'
                for tag in tags
            ]
        )
    return ""


def get_code_html(text):
    if type(text) == str:
        text = text.replace("\n", "&#10;")
        return f"<pre><code>{text}</pre></code>"


def get_description_html(text):
    if type(text) == str:
        return f"<p>{text}</p>"
    return ""


def get_link_html(s):
    return f'<a href="{s.link}" target="_blank">{s.link if s.linktext is None else s.linktext}</a>'


def generate_table_html(files=None):
    data = []
    for file_name in files:
        data = data + load_toml(file_name)["tips"]
    df = pd.DataFrame(data)

    # add tag
    df = (
        df.assign(tags=df.tags.map(get_tag_html))
        .assign(code=df.code.map(get_code_html))
        .assign(description=df.description.map(get_description_html))
        .sort_values(by=["tags", "code", "description"], ascending=False)
    )

    # link要素を入れる
    df = df.assign(
        code=df["code"].mask(
            df["code"].isna(), df[["linktext", "link"]].apply(get_link_html, axis=1)
        )
    )

    html = df[["tags", "code", "description"]].to_html(
        index=False, escape=False, classes="table", na_rep="", render_links=True
    )
    return html


def generate_index_html(table_html):

    with open("template.html", "r") as f:
        template = f.read()

    with open("../index.html", "w") as f:
        f.write(template.replace("[TABLE]", table_html))


def main():
    additional_files = sys.argv[1:]

    files = ["tips.toml"]
    if len(additional_files) != 0:
        files = files + additional_files
    html = generate_table_html(files)
    generate_index_html(html)


if __name__ == "__main__":
    main()
