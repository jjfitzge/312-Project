# For user Image upload data
def get_loop_data(template, data):
    loop_start_tag = "{{loop}}"
    loop_end_tag = "{{end_loop}}"

    i_start = template.find(loop_start_tag)
    i_end = template.find(loop_end_tag)
    loop_temp = template[i_start + len(loop_start_tag): i_end]
    content = ""
    for entry in data:
        replaced = loop_temp
        replaced = loop_temp.replace("{{message}}", entry["comment"])
        replaced = replaced.replace("{{image_filename}}", entry["img"])
        content += replaced
    return template[:i_start] + content + template[i_end+len(loop_end_tag):]


def render_template(filename, data, token, visits, username=None):
    with open(filename) as html_file:
        template = html_file.read()
        if data and len(data) != 0:
            template = get_loop_data_chat(template, data)
        if token:
            template = template.replace("{{token}}", token)
        template = template.replace("{{visits_count}}", str(visits))
        if username:
            template = template.replace("{{username}}", str(username))
        return template
# For User Chat Data


def get_loop_data_chat(template, data):
    loop_start_tag = "{{loop}}"
    loop_end_tag = "{{end_loop}}"

    i_start = template.find(loop_start_tag)
    i_end = template.find(loop_end_tag)
    loop_temp = template[i_start + len(loop_start_tag): i_end]
    content = ""
    for entry in data.keys():
        replaced = loop_temp
        replaced = loop_temp.replace("{{comment}}", data[entry])
        replaced = replaced.replace("{{username}}", entry)
        content += replaced
    return template[:i_start] + content + template[i_end+len(loop_end_tag):]
